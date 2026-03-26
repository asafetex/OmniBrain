#!/usr/bin/env python3
"""Generate a Change Package from git diff (diff-first)."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

try:
    from tools.utils import run_git_strict
except ModuleNotFoundError:
    from utils import run_git_strict


def comma_to_bullets(raw: str | None, empty_label: str) -> str:
    if not raw:
        return f"- {empty_label}"
    items = [x.strip() for x in raw.split(",") if x.strip()]
    if not items:
        return f"- {empty_label}"
    return "\n".join(f"- {item}" for item in items)


def load_template(template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def fill_template(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Change Package from git diff.")
    parser.add_argument("--repo", required=True, help="Path to git repository.")
    parser.add_argument("--level", required=True, choices=["L1", "L2", "L3"], help="Change level.")
    parser.add_argument("--goal", required=True, help="Goal for this change.")
    parser.add_argument("--graph-links", default="", help="Comma-separated graph links.")
    parser.add_argument("--memory-refs", default="", help="Comma-separated memory refs.")
    parser.add_argument("--context", default="Mudanca solicitada para atender objetivo descrito.")
    parser.add_argument(
        "--acceptance-criteria",
        default="- Mudanca atende objetivo\n- Sem regressao funcional conhecida",
    )
    parser.add_argument("--risks", default="- Impacto em arquivos alterados\n- Necessita revisao de edge cases")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Use staged diff instead of working tree diff.",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo}")

    template_path = Path(__file__).resolve().parent / "templates" / "change_package.md"
    template = load_template(template_path)

    diff_args = ["diff", "--staged"] if args.staged else ["diff"]
    name_only_args = ["diff", "--name-only", "--staged"] if args.staged else ["diff", "--name-only"]

    try:
        git_diff = run_git_strict(repo, diff_args).strip()
        files = run_git_strict(repo, name_only_args).strip()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    change_id = f"CHG-{timestamp}"
    files_impacted = "\n".join(f"- {line}" for line in files.splitlines()) if files else "- (sem arquivos detectados)"
    graph_links = comma_to_bullets(args.graph_links, "sem links informados")
    memory_refs = comma_to_bullets(args.memory_refs, "sem referencias informadas")

    mapping = {
        "CHANGE_ID": change_id,
        "TIMESTAMP": timestamp,
        "LEVEL": args.level,
        "GOAL": args.goal.strip(),
        "REPO_PATH": str(repo),
        "DIFF_MODE": "staged" if args.staged else "working-tree",
        "CONTEXT": args.context.strip(),
        "ACCEPTANCE_CRITERIA": args.acceptance_criteria.strip(),
        "FILES_IMPACTED": files_impacted,
        "RISKS": args.risks.strip(),
        "GRAPH_LINKS": graph_links,
        "MEMORY_REFS": memory_refs,
        "GIT_DIFF": git_diff if git_diff else "# no diff detected",
    }

    content = fill_template(template, mapping)
    output_dir = repo / "tmp" / "change-packages"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{change_id}.md"
    output_path.write_text(content, encoding="utf-8")

    print(content)
    print(f"\nSaved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
