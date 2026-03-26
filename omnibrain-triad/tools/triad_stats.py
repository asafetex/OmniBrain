#!/usr/bin/env python3
"""Generate simple TRIAD memory stats from Obsidian graph and inbox."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import Counter
from pathlib import Path

try:
    from tools.utils import get_repo_root
except ModuleNotFoundError:
    from utils import get_repo_root


TYPE_RE = re.compile(r"^- Type:\s*([A-Z]+)\s*$", re.MULTILINE)
PROJECT_RE = re.compile(r"^- Project:\s*([a-zA-Z0-9_.\-]+)\s*$", re.MULTILINE)
TIMESTAMP_RE = re.compile(r"^- Timestamp:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.MULTILINE)
FILE_TS_RE = re.compile(r"__([0-9]{8})-([0-9]{4})")


def parse_date(text: str, fallback_name: str) -> dt.date | None:
    match = TIMESTAMP_RE.search(text)
    if match:
        try:
            return dt.date.fromisoformat(match.group(1))
        except ValueError:
            return None
    file_match = FILE_TS_RE.search(fallback_name)
    if file_match:
        raw = file_match.group(1)
        try:
            return dt.date(int(raw[0:4]), int(raw[4:6]), int(raw[6:8]))
        except ValueError:
            return None
    return None


def collect_memory_files(repo_root: Path) -> list[Path]:
    inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
    graph = repo_root / "context-hub" / "02_GRAPH"
    files: list[Path] = []
    if inbox.exists():
        files.extend([p for p in inbox.glob("*.md") if p.is_file() and p.name.upper().startswith("MEM__")])
    if graph.exists():
        files.extend([p for p in graph.rglob("MEM__*.md") if p.is_file()])
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate TRIAD weekly stats from memory notes.")
    parser.add_argument("--days", type=int, default=7, help="Window in days for recent activity.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = get_repo_root(tools_dir)
    today = dt.date.today()
    since = today - dt.timedelta(days=max(args.days, 1))

    files = collect_memory_files(repo_root)
    type_all = Counter()
    project_all = Counter()
    type_window = Counter()
    project_window = Counter()
    total_window = 0

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        mem_type_match = TYPE_RE.search(text)
        mem_project_match = PROJECT_RE.search(text)
        mem_type = mem_type_match.group(1).strip() if mem_type_match else "UNKNOWN"
        mem_project = mem_project_match.group(1).strip() if mem_project_match else "unknown"
        event_date = parse_date(text, path.name)

        type_all[mem_type] += 1
        project_all[mem_project] += 1
        if event_date and event_date >= since:
            type_window[mem_type] += 1
            project_window[mem_project] += 1
            total_window += 1

    top_types = "\n".join(f"- {name}: {count}" for name, count in type_window.most_common()) or "- (none)"
    top_projects = "\n".join(f"- {name}: {count}" for name, count in project_window.most_common()) or "- (none)"
    wins = type_window.get("WIN", 0)
    lessons = type_window.get("LESSON", 0)
    reviews = type_window.get("REVIEW", 0)

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_id = f"STATS-{ts}"
    report = (
        f"# TRIAD Stats - {report_id}\n\n"
        "## Window\n"
        f"- Days: {args.days}\n"
        f"- Since: {since}\n"
        f"- Until: {today}\n\n"
        "## Activity\n"
        f"- Memory Notes (all time): {sum(type_all.values())}\n"
        f"- Memory Notes (window): {total_window}\n"
        f"- WIN (window): {wins}\n"
        f"- LESSON (window): {lessons}\n"
        f"- REVIEW (window): {reviews}\n\n"
        "## Top Types (window)\n"
        f"{top_types}\n\n"
        "## Top Projects (window)\n"
        f"{top_projects}\n\n"
        "## Notes\n"
        "- Source folders: `context-hub/05_INBOX/byterover-imports` and `context-hub/02_GRAPH/**/MEM__*.md`\n"
        "- Timestamp priority: metadata `- Timestamp:` then filename suffix `__YYYYMMDD-HHMM`.\n"
    )

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_dir = repo_root / "tmp" / "stats"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{report_id}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
