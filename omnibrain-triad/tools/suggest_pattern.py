#!/usr/bin/env python3
"""Cross-domain pattern transfer: given a Change Package, find applicable WINs.

Suggests proven patterns from the Skill Graph that share structural similarity
with the current task, even across disciplines. Helps developers reuse solutions
they wouldn't naturally search for.

Output: ranked list of WINs with similarity score, snippet excerpt, and rationale.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from search_memory import build_tfidf, cosine
from telemetry import record_run, tool_name_from_file
from utils import print_utf8

WIN_FILENAME_RE = re.compile(r"^MEM__(?:WIN|LESSON)__")


def collect_wins(repo_root: Path) -> list[Path]:
    """Find WIN/LESSON memories in the Skill Graph (curated knowledge)."""
    candidates: list[Path] = []
    graph = repo_root / "context-hub" / "02_GRAPH"
    if graph.exists():
        for path in graph.rglob("MEM__*.md"):
            if path.is_file() and WIN_FILENAME_RE.match(path.name):
                candidates.append(path)
    return sorted(set(candidates))


def extract_discipline(path: Path, graph_root: Path) -> str:
    """Infer discipline from path. Returns 'agents', 'data-engineering', etc."""
    try:
        rel = path.relative_to(graph_root).parts
        if rel and rel[0] == "disciplines" and len(rel) > 1:
            return rel[1]
    except ValueError:
        pass
    return "unknown"


def excerpt_content(text: str, max_chars: int = 200) -> str:
    """Pull the Content section of a memory, fall back to first non-empty paragraph."""
    in_content = False
    buf = []
    for line in text.splitlines():
        if line.strip().startswith("## Content"):
            in_content = True
            continue
        if in_content:
            if line.startswith("## "):
                break
            if line.strip():
                buf.append(line.strip())
            if sum(len(x) for x in buf) >= max_chars:
                break
    if not buf:
        for line in text.splitlines():
            if line.strip() and not line.startswith("#") and not line.startswith("- "):
                buf.append(line.strip())
                break
    excerpt = " ".join(buf)
    return excerpt[:max_chars] + ("..." if len(excerpt) > max_chars else "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest applicable WIN patterns for a Change Package.")
    parser.add_argument("--change-package", required=True, help="Path to Change Package markdown.")
    parser.add_argument("--top-k", type=int, default=3, help="How many WINs to suggest.")
    parser.add_argument("--min-score", type=float, default=0.10, help="Cosine threshold.")
    parser.add_argument("--cross-discipline-only", action="store_true",
                        help="Only suggest WINs from disciplines OTHER than the obvious one.")
    parser.add_argument("--repo-root", default="", help="TRIAD repo root override.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    cp_path = Path(args.change_package).resolve()
    if not cp_path.exists():
        print(f"Error: Change Package not found: {cp_path}", file=sys.stderr)
        return 2

    repo_root = Path(args.repo_root).resolve() if args.repo_root else _tools_dir.parent
    graph_root = repo_root / "context-hub" / "02_GRAPH"

    cp_text = cp_path.read_text(encoding="utf-8", errors="replace")
    wins = collect_wins(repo_root)
    if not wins:
        if args.format == "json":
            print_utf8(json.dumps({"change_package": str(cp_path), "suggestions": []}, indent=2))
        else:
            print_utf8(f"No WIN/LESSON memories found in {graph_root}.")
        return 0

    # Build TF-IDF over WINs + the change package as the query
    documents = [(p, p.read_text(encoding="utf-8", errors="replace")) for p in wins]
    documents.append((cp_path, cp_text))
    vectors, _ = build_tfidf(documents)
    query_vec = vectors[-1]

    # Detect "obvious" discipline: most similar discipline by counting keywords in CP
    cp_lower = cp_text.lower()
    discipline_hits: dict[str, int] = {}
    for path in wins:
        d = extract_discipline(path, graph_root)
        if d in cp_lower:
            discipline_hits[d] = discipline_hits.get(d, 0) + 1
    obvious_discipline = max(discipline_hits.items(), key=lambda x: x[1])[0] if discipline_hits else None

    suggestions = []
    for (path, _), vec in zip(documents[:-1], vectors[:-1], strict=False):
        score = cosine(query_vec, vec)
        if score < args.min_score:
            continue
        discipline = extract_discipline(path, graph_root)
        if args.cross_discipline_only and obvious_discipline and discipline == obvious_discipline:
            continue
        suggestions.append({
            "score": round(score, 4),
            "path": str(path),
            "name": path.name,
            "discipline": discipline,
            "excerpt": excerpt_content(path.read_text(encoding="utf-8", errors="replace")),
        })
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    suggestions = suggestions[: args.top_k]

    if args.format == "json":
        print_utf8(json.dumps({
            "change_package": str(cp_path),
            "obvious_discipline": obvious_discipline,
            "cross_discipline_only": args.cross_discipline_only,
            "suggestions": suggestions,
        }, ensure_ascii=False, indent=2))
        return 0

    print_utf8(f"# Pattern Suggestions for {cp_path.name}")
    print_utf8("")
    print_utf8(f"- Obvious discipline detected: {obvious_discipline or '(none)'}")
    print_utf8(f"- Cross-discipline only: {args.cross_discipline_only}")
    print_utf8(f"- Suggestions returned: {len(suggestions)}")
    print_utf8("")
    if not suggestions:
        print_utf8("No applicable patterns found above threshold.")
        return 0
    for rank, s in enumerate(suggestions, start=1):
        print_utf8(f"{rank}. [{s['score']:.3f}] {s['name']} (discipline: {s['discipline']})")
        print_utf8(f"   Path: {s['path']}")
        print_utf8(f"   Excerpt: {s['excerpt']}")
        print_utf8("")
    return 0


if __name__ == "__main__":
    with record_run(tool_name_from_file(__file__)):
        raise SystemExit(main())
