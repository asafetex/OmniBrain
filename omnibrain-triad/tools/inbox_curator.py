#!/usr/bin/env python3
"""Curate context-hub INBOX with heuristics: stale, duplicates, promotion candidates.

Generates a markdown report listing:
- STALE: memorias com idade > N dias e tipo PLAN/REVIEW (ruido apos a tarefa terminar)
- DUPLICATES: memorias com similaridade TF-IDF >= threshold (mesmo conteudo curado em multiplos arquivos)
- PROMOTE: WINs e LESSONs no INBOX que deveriam ir pro Skill Graph

Read-only por padrao. Use --apply para mover/arquivar (com confirmacao).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from search_memory import build_tfidf, cosine
from telemetry import record_run, tool_name_from_file
from utils import print_utf8

MEM_FILENAME_RE = re.compile(
    r"^MEM__(?P<type>PLAN|REVIEW|LESSON|WIN|DECISION)__(?P<project>[^_]+(?:_[^_]+)*)__(?P<topic>.+)__(?P<ts>\d{8}-\d{4})\.md$"
)
TYPE_TIMESTAMP_RE = re.compile(r"^- Timestamp:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def parse_mem_age_days(path: Path, now: dt.datetime) -> int | None:
    """Returns age in days or None if unparseable."""
    text = path.read_text(encoding="utf-8", errors="replace")
    ts_match = TYPE_TIMESTAMP_RE.search(text)
    if ts_match:
        try:
            mem_dt = dt.datetime.strptime(ts_match.group(1), "%Y-%m-%d")
            return (now - mem_dt).days
        except ValueError:
            pass
    name_match = MEM_FILENAME_RE.match(path.name)
    if name_match:
        try:
            mem_dt = dt.datetime.strptime(name_match.group("ts")[:8], "%Y%m%d")
            return (now - mem_dt).days
        except ValueError:
            pass
    return None


def parse_mem_type(path: Path) -> str | None:
    name_match = MEM_FILENAME_RE.match(path.name)
    if name_match:
        return name_match.group("type")
    return None


def find_stale(memories: list[Path], now: dt.datetime, max_age_days: int) -> list[tuple[Path, int]]:
    """Stale = old PLAN or REVIEW (operational, not knowledge)."""
    stale = []
    for path in memories:
        age = parse_mem_age_days(path, now)
        if age is None or age <= max_age_days:
            continue
        mem_type = parse_mem_type(path)
        if mem_type in {"PLAN", "REVIEW"}:
            stale.append((path, age))
    return stale


def find_duplicates(memories: list[Path], threshold: float) -> list[tuple[Path, Path, float]]:
    """Pairs of memories with cosine similarity >= threshold."""
    if len(memories) < 2:
        return []
    docs = [(p, p.read_text(encoding="utf-8", errors="replace")) for p in memories]
    vectors, _ = build_tfidf(docs)
    pairs: list[tuple[Path, Path, float]] = []
    for i, (path_a, _) in enumerate(docs):
        for j in range(i + 1, len(docs)):
            path_b, _ = docs[j]
            score = cosine(vectors[i], vectors[j])
            if score >= threshold:
                pairs.append((path_a, path_b, score))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs


def find_promote_candidates(memories: list[Path]) -> list[Path]:
    """WIN and LESSON in INBOX should be promoted to Skill Graph."""
    return [p for p in memories if parse_mem_type(p) in {"WIN", "LESSON"}]


def render_report(
    inbox: Path,
    stale: list[tuple[Path, int]],
    dupes: list[tuple[Path, Path, float]],
    promotes: list[Path],
    max_age_days: int,
    threshold: float,
) -> str:
    lines = [
        f"# INBOX Curation Report - {dt.datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        f"- INBOX: `{inbox}`",
        f"- Stale threshold: {max_age_days} days",
        f"- Duplicate threshold: cosine >= {threshold}",
        "",
        "## Promote Candidates",
    ]
    if promotes:
        for p in promotes:
            lines.append(f"- {p.name}")
            lines.append(
                f"  - Suggested: `python tools/promote_to_obsidian.py "
                f"--source context-hub/05_INBOX/byterover-imports/{p.name} "
                f"--target disciplines/<area>/skills/`"
            )
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Stale (PLAN/REVIEW older than threshold)")
    if stale:
        for path, age in stale:
            lines.append(f"- {path.name} (age={age}d)")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Duplicates (cosine similarity)")
    if dupes:
        for path_a, path_b, score in dupes:
            lines.append(f"- [{score:.3f}] `{path_a.name}` <-> `{path_b.name}`")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def archive_stale(stale: list[tuple[Path, int]], archive_dir: Path) -> int:
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for path, _ in stale:
        target = archive_dir / path.name
        shutil.move(str(path), str(target))
        moved += 1
    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description="Curate INBOX: detect stale, duplicates, promotion candidates.")
    parser.add_argument("--max-age-days", type=int, default=30, help="PLAN/REVIEW older than N days are stale.")
    parser.add_argument("--dup-threshold", type=float, default=0.85, help="Cosine similarity threshold for duplicates.")
    parser.add_argument("--apply", action="store_true", help="Actually archive stale memories (default: dry-run).")
    parser.add_argument("--output", default="", help="Optional report path (defaults to tmp/inbox-curation/CURATE-*.md).")
    parser.add_argument("--repo-root", default="", help="Override TRIAD repo root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else _tools_dir.parent
    inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
    if not inbox.exists():
        print_utf8(f"INBOX not found: {inbox}")
        return 1

    memories = sorted(p for p in inbox.glob("MEM__*.md") if p.is_file())
    if not memories:
        print_utf8(f"INBOX empty: {inbox}")
        return 0

    now = dt.datetime.now()
    stale = find_stale(memories, now, args.max_age_days)
    dupes = find_duplicates(memories, args.dup_threshold)
    promotes = find_promote_candidates(memories)

    report = render_report(inbox, stale, dupes, promotes, args.max_age_days, args.dup_threshold)

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_dir = repo_root / "tmp" / "inbox-curation"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"CURATE-{dt.datetime.now():%Y%m%d-%H%M%S}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print_utf8(report)
    print_utf8(f"\nSaved: {out_path}")

    if args.apply and stale:
        archive_dir = repo_root / "context-hub" / "05_INBOX" / "_archive"
        moved = archive_stale(stale, archive_dir)
        print_utf8(f"\nArchived {moved} stale memorie(s) to {archive_dir}")
    elif stale and not args.apply:
        print_utf8(f"\nDry-run: {len(stale)} stale memorie(s) would be archived. Use --apply to move.")

    return 0


if __name__ == "__main__":
    with record_run(tool_name_from_file(__file__)):
        raise SystemExit(main())
