#!/usr/bin/env python3
"""Run operational preflight checks before TRIAD execution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from config_env import load_config
from telemetry import record_run, tool_name_from_file
from utils import command_exists, run_git


def check_list_item(results: list[tuple[str, str, str]], status: str, name: str, detail: str) -> None:
    results.append((status, name, detail))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate environment/config before running TRIAD flow.")
    parser.add_argument("--repo", required=True, help="Target repository path.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent
    target_repo = Path(args.repo).resolve()
    results: list[tuple[str, str, str]] = []

    if target_repo.exists():
        check_list_item(results, "PASS", "repo.exists", str(target_repo))
    else:
        check_list_item(results, "FAIL", "repo.exists", f"Missing repository path: {target_repo}")

    git_ok, git_out = run_git(target_repo, ["rev-parse", "--is-inside-work-tree"]) if target_repo.exists() else (False, "")
    if git_ok and git_out.lower() == "true":
        check_list_item(results, "PASS", "repo.git", "Target repo is a git worktree")
    else:
        detail = git_out or "Target repo is not a git worktree"
        check_list_item(results, "FAIL", "repo.git", detail)

    if command_exists("python"):
        check_list_item(results, "PASS", "python.cmd", "python available in PATH")
    else:
        check_list_item(results, "FAIL", "python.cmd", "python command not found in PATH")

    if command_exists("git"):
        check_list_item(results, "PASS", "git.cmd", "git available in PATH")
    else:
        check_list_item(results, "FAIL", "git.cmd", "git command not found in PATH")

    vault_path = repo_root / "context-hub"
    if vault_path.exists():
        check_list_item(results, "PASS", "vault.path", str(vault_path))
    else:
        check_list_item(results, "FAIL", "vault.path", "context-hub folder missing")

    routing_json = repo_root / "configs" / "routing.json"
    routing_yaml = repo_root / "configs" / "routing.yaml"
    if routing_json.exists():
        check_list_item(results, "PASS", "routing.json", str(routing_json))
    else:
        check_list_item(results, "FAIL", "routing.json", "configs/routing.json missing")
    if routing_yaml.exists():
        check_list_item(results, "PASS", "routing.yaml", str(routing_yaml))
    else:
        check_list_item(results, "WARN", "routing.yaml", "configs/routing.yaml missing")

    config = load_config(tools_dir)
    check_list_item(results, "PASS", "tools.config", "Loaded tools config")

    auditors = config.get("auditors", {})
    for name, item in auditors.items():
        enabled = bool(item.get("enabled", False))
        cmd = str(item.get("cmd", "")).strip()
        exists = command_exists(cmd)
        if enabled and not exists:
            check_list_item(results, "FAIL", f"cli.{name}", f"Enabled but command not found: {cmd}")
        elif enabled and exists:
            check_list_item(results, "PASS", f"cli.{name}", f"Enabled and found: {cmd}")
        elif not enabled and exists:
            check_list_item(results, "WARN", f"cli.{name}", f"Disabled but command exists: {cmd}")
        else:
            check_list_item(results, "WARN", f"cli.{name}", f"Disabled and command not found: {cmd}")

    byterover = config.get("byterover", {})
    brv_enabled = bool(byterover.get("enabled", False))
    brv_cmd = str(byterover.get("cmd", "")).strip()
    brv_exists = command_exists(brv_cmd)
    if brv_enabled and not brv_exists:
        check_list_item(results, "FAIL", "cli.byterover", f"Enabled but command not found: {brv_cmd}")
    elif brv_enabled and brv_exists:
        check_list_item(results, "PASS", "cli.byterover", f"Enabled and found: {brv_cmd}")
    elif not brv_enabled and brv_exists:
        check_list_item(results, "WARN", "cli.byterover", f"Disabled but command exists: {brv_cmd}")
    else:
        check_list_item(results, "WARN", "cli.byterover", f"Disabled and command not found: {brv_cmd}")

    brv_args = byterover.get("args", [])
    if isinstance(brv_args, list) and brv_args:
        first_arg = str(brv_args[0])
        if first_arg.endswith(".js") and Path(first_arg).exists():
            check_list_item(results, "PASS", "byterover.script", f"Node script found: {first_arg}")
        elif first_arg.endswith(".js"):
            check_list_item(results, "WARN", "byterover.script", f"Node script not found: {first_arg}")

    templates = [
        "templates/change_package.md",
        "templates/codex_review_prompt.md",
        "templates/gemini_review_prompt.md",
    ]
    for rel in templates:
        p = tools_dir / rel
        if p.exists():
            check_list_item(results, "PASS", f"template.{rel}", "ok")
        else:
            check_list_item(results, "FAIL", f"template.{rel}", f"missing: {p}")

    tmp_probe = repo_root / "tmp" / "preflight"
    try:
        tmp_probe.mkdir(parents=True, exist_ok=True)
        probe_file = tmp_probe / "write-test.tmp"
        probe_file.write_text("ok", encoding="utf-8")
        probe_file.unlink(missing_ok=True)
        check_list_item(results, "PASS", "tmp.write", f"Writable: {tmp_probe}")
    except Exception as exc:  # pragma: no cover
        check_list_item(results, "FAIL", "tmp.write", f"Cannot write tmp probe: {exc}")

    print("# TRIAD Preflight")
    print("")
    for status, name, detail in results:
        print(f"- [{status}] {name}: {detail}")

    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]
    print("")
    print(f"Summary: PASS={len([r for r in results if r[0]=='PASS'])} WARN={len(warns)} FAIL={len(fails)}")

    if fails:
        return 1
    if args.strict and warns:
        return 2
    return 0


if __name__ == "__main__":
    with record_run(tool_name_from_file(__file__)):
        raise SystemExit(main())
