#!/usr/bin/env python3
"""Reconstruct session state from gate artifacts and produce a recovery brief."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from utils import get_repo_root, run_git


def choose_gate_result(gate_dir: Path, change_id: str) -> Path:
    if change_id:
        candidate = gate_dir / f"{change_id}.md"
        if not candidate.exists():
            raise FileNotFoundError(f"Gate result not found for Change-ID: {change_id}")
        return candidate

    files = sorted([p for p in gate_dir.glob("*.md") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No gate result files found in: {gate_dir}")
    return files[0]


def parse_summary(content: str) -> dict[str, str]:
    change_id = re.search(r"- Change-ID:\s*(.+)", content)
    level = re.search(r"- Level:\s*(L1|L2|L3)", content)
    decision = re.search(r"- Final Decision:\s*([A-Z_]+)", content)
    return {
        "change_id": change_id.group(1).strip() if change_id else "CHG-UNKNOWN",
        "level": level.group(1).strip() if level else "L3",
        "decision": decision.group(1).strip() if decision else "UNKNOWN",
    }


def parse_auditors(content: str) -> list[dict[str, str]]:
    lines = content.splitlines()
    auditors: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_code = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        if stripped.startswith("## Auditor:"):
            if current is not None:
                auditors.append(current)
            name = stripped.split(":", 1)[1].strip()
            current = {"name": name, "status": "unknown", "verdict": "UNKNOWN", "source": "none"}
            continue

        if current is None:
            continue

        if stripped.startswith("## "):
            auditors.append(current)
            current = None
            continue

        if stripped.startswith("- Status:"):
            current["status"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- Verdict:"):
            current["verdict"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- Verdict Source:"):
            current["source"] = stripped.split(":", 1)[1].strip()

    if current is not None:
        auditors.append(current)

    deduped: list[dict[str, str]] = []
    seen_names: set[str] = set()
    for item in auditors:
        name = item["name"]
        if name in seen_names:
            continue
        seen_names.add(name)
        deduped.append(item)
    return deduped


def extract_blocker_signals(content: str) -> list[str]:
    lines = []
    for line in content.splitlines():
        if "[P0]" in line or "[P1]" in line or "[P2]" in line:
            lines.append(line.strip())
    return lines[:10]


def list_manual_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted([p.name for p in path.glob("*.md") if p.is_file()])


def build_next_actions(decision: str, blockers: list[str], auditors: list[dict[str, str]]) -> list[str]:
    if decision == "APPROVE":
        return [
            "Run tests relevant to changed files.",
            "If tests pass, commit and merge according to branch policy.",
            "Record WIN and DECISION memory entries.",
        ]
    if decision == "REJECT":
        actions = [
            "Address blockers from auditors before any commit.",
            "Regenerate Change Package from updated diff.",
            "Rerun Gate until decision is APPROVE or justified CONFLICT.",
        ]
        if blockers:
            actions.insert(1, "Prioritize P0/P1 blockers first.")
        return actions
    if decision in {"CONFLICT", "NEEDS_HUMAN"}:
        missing = [a["name"] for a in auditors if a["verdict"] == "UNKNOWN"]
        if missing:
            missing_text = ", ".join(missing)
        else:
            missing_text = "auditor inputs"
        return [
            f"Resolve missing/ambiguous verdicts ({missing_text}).",
            "Collect manual responses when CLI output is unavailable.",
            "Rerun Gate and document final decision.",
        ]
    return [
        "Review gate-result details manually.",
        "Collect missing evidence and rerun Gate.",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Recover session state from Gate artifacts.")
    parser.add_argument("--repo", required=True, help="Target repository path for current worktree context.")
    parser.add_argument("--change-id", default="", help="Specific Change-ID to recover.")
    parser.add_argument("--gate-results-dir", default="tmp/gate-results", help="Gate result directory.")
    parser.add_argument("--manual-prompts-dir", default="tmp/manual-prompts", help="Manual prompts directory.")
    parser.add_argument("--manual-responses-dir", default="tmp/manual-responses", help="Manual responses directory.")
    parser.add_argument("--max-diff-chars", type=int, default=8000, help="Diff excerpt size.")
    parser.add_argument("--output", default="", help="Optional output file path.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent
    target_repo = Path(args.repo).resolve()
    if not target_repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {target_repo}")

    gate_dir = (repo_root / args.gate_results_dir).resolve() if not Path(args.gate_results_dir).is_absolute() else Path(args.gate_results_dir).resolve()
    prompt_base = (repo_root / args.manual_prompts_dir).resolve() if not Path(args.manual_prompts_dir).is_absolute() else Path(args.manual_prompts_dir).resolve()
    response_base = (repo_root / args.manual_responses_dir).resolve() if not Path(args.manual_responses_dir).is_absolute() else Path(args.manual_responses_dir).resolve()

    try:
        gate_file = choose_gate_result(gate_dir, args.change_id.strip())
    except FileNotFoundError as exc:
        print(str(exc))
        print("Tip: run tools/run_gate.py first to generate gate-results, or omit --change-id to use latest.")
        return 1
    gate_content = gate_file.read_text(encoding="utf-8", errors="replace")
    summary = parse_summary(gate_content)
    auditors = parse_auditors(gate_content)
    blockers = extract_blocker_signals(gate_content)

    prompt_dir = prompt_base / summary["change_id"]
    response_dir = response_base / summary["change_id"]
    prompt_files = list_manual_files(prompt_dir)
    response_files = list_manual_files(response_dir)

    branch_ok, branch = run_git(target_repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    status_ok, status = run_git(target_repo, ["status", "--short"])
    diff_ok, diff = run_git(target_repo, ["diff"])
    diff_excerpt = diff if diff_ok else f"(diff unavailable) {diff}"
    if len(diff_excerpt) > args.max_diff_chars:
        diff_excerpt = diff_excerpt[: args.max_diff_chars - 3] + "..."

    actions = build_next_actions(summary["decision"], blockers, auditors)
    auditors_md = "\n".join(
        f"- {a['name']}: verdict={a['verdict']}, status={a['status']}, source={a['source']}" for a in auditors
    ) or "- (no auditor sections parsed)"
    blockers_md = "\n".join(f"- {b}" for b in blockers) if blockers else "- (no explicit P0/P1/P2 lines found)"
    prompt_files_md = "\n".join(f"- {name}" for name in prompt_files) if prompt_files else "- (none)"
    response_files_md = "\n".join(f"- {name}" for name in response_files) if response_files else "- (none)"
    actions_md = "\n".join(f"{idx}. {step}" for idx, step in enumerate(actions, start=1))

    report_ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_id = f"REC-{summary['change_id']}-{report_ts}"
    report = (
        f"# Recovery Report - {report_id}\n\n"
        "## Gate Snapshot\n"
        f"- Change-ID: {summary['change_id']}\n"
        f"- Level: {summary['level']}\n"
        f"- Final Decision: {summary['decision']}\n"
        f"- Gate Artifact: {gate_file}\n\n"
        "## Auditor State\n"
        f"{auditors_md}\n\n"
        "## Blocker Signals\n"
        f"{blockers_md}\n\n"
        "## Manual Artifact State\n"
        f"- Prompt Directory: {prompt_dir}\n"
        f"- Response Directory: {response_dir}\n\n"
        "### Prompt Files\n"
        f"{prompt_files_md}\n\n"
        "### Response Files\n"
        f"{response_files_md}\n\n"
        "## Repo Snapshot\n"
        f"- Repo: {target_repo}\n"
        f"- Branch: {branch if branch_ok else f'(branch unavailable) {branch}'}\n\n"
        "### Git Status\n"
        "```text\n"
        f"{status if status_ok else f'(status unavailable) {status}'}\n"
        "```\n\n"
        "### Git Diff (Excerpt)\n"
        "```diff\n"
        f"{diff_excerpt or '(no diff)'}\n"
        "```\n\n"
        "## Recommended Next Actions\n"
        f"{actions_md}\n\n"
        "## Recovery Prompt Seed\n"
        "```text\n"
        f"You are resuming Change-ID {summary['change_id']}.\n"
        f"Current gate decision is {summary['decision']}.\n"
        "Use the gate artifact and repo diff to continue from the exact current state.\n"
        "Return: (1) concise plan, (2) required edits, (3) validation checklist.\n"
        "```\n"
    )

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_dir = repo_root / "tmp" / "recovery-reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{report_id}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
