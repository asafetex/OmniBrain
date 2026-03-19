#!/usr/bin/env python3
"""Block push when latest L3 Change Package is not APPROVED in Gate results."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHANGE_ID_RE = re.compile(r"^- Change-ID:\s*(.+)$", re.MULTILINE)
LEVEL_RE = re.compile(r"^- Level:\s*(L1|L2|L3)$", re.MULTILINE)
DECISION_RE = re.compile(r"^- Final Decision:\s*([A-Z_]+)$", re.MULTILINE)


def parse_change_package(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    change_id_match = CHANGE_ID_RE.search(text)
    level_match = LEVEL_RE.search(text)
    change_id = change_id_match.group(1).strip() if change_id_match else ""
    level = level_match.group(1).strip() if level_match else "L3"
    return change_id, level


def parse_gate_decision(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = DECISION_RE.search(text)
    return match.group(1).strip() if match else "UNKNOWN"


def latest_markdown(path: Path) -> Path | None:
    if not path.exists():
        return None
    files = [p for p in path.glob("*.md") if p.is_file()]
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate latest L3 gate before git push.")
    parser.add_argument("--repo", required=True, help="Target project repository path.")
    parser.add_argument(
        "--change-packages-dir",
        default="tmp/change-packages",
        help="Directory containing Change Packages relative to --repo (or absolute).",
    )
    parser.add_argument(
        "--gate-results-dir",
        default="tmp/gate-results",
        help="Directory containing Gate results relative to OmniBrain root (or absolute).",
    )
    parser.add_argument(
        "--strict-missing-change-package",
        action="store_true",
        help="Fail if no Change Package exists.",
    )
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    omnibrain_root = tools_dir.parent
    target_repo = Path(args.repo).resolve()
    if not target_repo.exists():
        print(f"[FAIL] repo not found: {target_repo}")
        return 1

    cp_dir = Path(args.change_packages_dir)
    if not cp_dir.is_absolute():
        cp_dir = (target_repo / cp_dir).resolve()
    gate_dir = Path(args.gate_results_dir)
    if not gate_dir.is_absolute():
        gate_dir = (omnibrain_root / gate_dir).resolve()

    latest_cp = latest_markdown(cp_dir)
    if latest_cp is None:
        if args.strict_missing_change_package:
            print(f"[FAIL] no Change Package found in {cp_dir}")
            print("Run start_task_flow.py or make_change_package.py before pushing.")
            return 1
        print(f"[PASS] no Change Package found in {cp_dir}; skipping L3 gate check.")
        return 0

    change_id, level = parse_change_package(latest_cp)
    if not change_id:
        print(f"[FAIL] could not parse Change-ID from {latest_cp}")
        return 1

    print(f"[INFO] latest Change Package: {latest_cp.name} (Level={level}, Change-ID={change_id})")
    if level != "L3":
        print("[PASS] latest Change Package is not L3; push allowed.")
        return 0

    gate_file = gate_dir / f"{change_id}.md"
    if not gate_file.exists():
        print(f"[FAIL] missing gate result for L3 Change-ID: {change_id}")
        print(f"Expected: {gate_file}")
        print("Run: python tools/run_gate.py --change-package <path-to-change-package>")
        return 1

    decision = parse_gate_decision(gate_file)
    if decision != "APPROVE":
        print(f"[FAIL] gate decision is {decision} for L3 Change-ID: {change_id}")
        print(f"Gate file: {gate_file}")
        print("Push blocked until decision is APPROVE.")
        return 1

    print(f"[PASS] gate decision is APPROVE for L3 Change-ID: {change_id}.")
    return 0


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("Python 3.10+ required.")
        raise SystemExit(1)
    raise SystemExit(main())
