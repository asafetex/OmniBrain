#!/usr/bin/env python3
"""Run the first operational TRIAD steps in one command.

Flow:
1) route task
2) build context bundle
3) generate change package
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"JSON config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def detect_intent(task: str, intents: dict, explicit_intent: str) -> tuple[str, dict]:
    if explicit_intent:
        payload = intents.get(explicit_intent)
        if payload is None:
            raise ValueError(f"Intent not found in routing policy: {explicit_intent}")
        return explicit_intent, payload

    text = task.lower()
    best_name = "generic"
    best_score = 0
    best_payload: dict = {}
    for name, payload in intents.items():
        score = 0
        for kw in payload.get("keywords", []):
            if str(kw).lower() in text:
                score += 1
        if score > best_score:
            best_score = score
            best_name = name
            best_payload = payload
    return best_name, best_payload


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, cwd=str(cwd))
    return proc.returncode, proc.stdout, proc.stderr


def find_saved_path(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("Saved: "):
            return line.replace("Saved: ", "", 1).strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Start TRIAD task flow (route + bundle + change package).")
    parser.add_argument("--repo", required=True, help="Target repository path.")
    parser.add_argument("--task", required=True, help="Task description.")
    parser.add_argument("--level", required=True, choices=["L1", "L2", "L3"], help="Task level.")
    parser.add_argument("--intent", default="", help="Explicit intent id.")
    parser.add_argument("--graph-links", default="", help="Comma-separated graph links override.")
    parser.add_argument("--routing-config", default="configs/routing.json", help="Routing JSON path.")
    parser.add_argument("--preflight", action="store_true", help="Run preflight checks before generating artifacts.")
    parser.add_argument("--staged", action="store_true", help="Use staged diff for change package.")
    parser.add_argument("--skip-route", action="store_true", help="Skip route artifact generation.")
    parser.add_argument("--skip-bundle", action="store_true", help="Skip context bundle generation.")
    parser.add_argument("--skip-change-package", action="store_true", help="Skip change package generation.")
    parser.add_argument("--output", default="", help="Optional flow summary output file.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent
    target_repo = Path(args.repo).resolve()
    if not target_repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {target_repo}")

    cfg_path = Path(args.routing_config)
    if not cfg_path.is_absolute():
        cfg_path = (repo_root / cfg_path).resolve()
    routing = load_json(cfg_path)

    intent_name, intent_payload = detect_intent(args.task, routing.get("intents", {}), args.intent.strip())
    graph_links = parse_csv(args.graph_links) or intent_payload.get("graph_nodes", [])

    if args.preflight:
        preflight_cmd = [
            sys.executable,
            str(tools_dir / "preflight_check.py"),
            "--repo",
            str(target_repo),
        ]
        rc, out, err = run_command(preflight_cmd, cwd=repo_root)
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)
        if rc != 0:
            return rc

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    flow_id = f"FLOW-{ts}"
    route_out = repo_root / "tmp" / "task-routes" / f"{flow_id}.md"
    bundle_out = repo_root / "tmp" / "context-bundles" / f"{flow_id}.md"

    route_saved = ""
    bundle_saved = ""
    cp_saved = ""

    if not args.skip_route:
        route_cmd = [
            sys.executable,
            str(tools_dir / "route_task.py"),
            "--task",
            args.task,
            "--level",
            args.level,
            "--repo",
            str(target_repo),
            "--routing-config",
            str(cfg_path),
            "--format",
            "markdown",
            "--output",
            str(route_out),
        ]
        if args.intent.strip():
            route_cmd.extend(["--intent", args.intent.strip()])
        rc, out, err = run_command(route_cmd, cwd=repo_root)
        if rc != 0:
            print(out)
            print(err, file=sys.stderr)
            return rc
        route_saved = find_saved_path(out) or str(route_out)

    if not args.skip_bundle:
        bundle_cmd = [
            sys.executable,
            str(tools_dir / "build_context_bundle.py"),
            "--repo",
            str(target_repo),
            "--task",
            args.task,
            "--level",
            args.level,
            "--intent",
            intent_name,
            "--output",
            str(bundle_out),
        ]
        if graph_links:
            bundle_cmd.extend(["--graph-links", ",".join(graph_links)])
        rc, out, err = run_command(bundle_cmd, cwd=repo_root)
        if rc != 0:
            print(out)
            print(err, file=sys.stderr)
            return rc
        bundle_saved = find_saved_path(out) or str(bundle_out)

    if not args.skip_change_package:
        cp_cmd = [
            sys.executable,
            str(tools_dir / "make_change_package.py"),
            "--repo",
            str(target_repo),
            "--level",
            args.level,
            "--goal",
            args.task,
        ]
        if graph_links:
            cp_cmd.extend(["--graph-links", ",".join(graph_links)])
        if args.staged:
            cp_cmd.append("--staged")
        rc, out, err = run_command(cp_cmd, cwd=repo_root)
        if rc != 0:
            print(out)
            print(err, file=sys.stderr)
            return rc
        cp_saved = find_saved_path(out)

    level_cfg = routing.get("levels", {}).get(args.level, {})
    gate_required = bool(level_cfg.get("gate_required", False))
    decision_rule = level_cfg.get("decision_rule", "not_defined")
    reviewers = level_cfg.get("reviewers", routing.get("default_reviewers", []))

    summary = (
        f"# Task Flow - {flow_id}\n\n"
        "## Summary\n"
        f"- Task: {args.task}\n"
        f"- Level: {args.level}\n"
        f"- Intent: {intent_name}\n"
        f"- Repo: {target_repo}\n"
        f"- Gate Required: {gate_required}\n"
        f"- Reviewers: {', '.join(reviewers) if reviewers else '(none)'}\n"
        f"- Decision Rule: {decision_rule}\n\n"
        "## Artifacts\n"
        f"- Route: {route_saved or '(skipped)'}\n"
        f"- Context Bundle: {bundle_saved or '(skipped)'}\n"
        f"- Change Package: {cp_saved or '(skipped)'}\n\n"
        "## Next Commands\n"
        "```bash\n"
        + (f"python tools/run_gate.py --change-package {cp_saved}\n" if cp_saved else "")
        + ("# if session fails:\npython tools/recover_session.py --repo . --change-id <Change-ID>\n")
        + "```\n"
    )

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_dir = repo_root / "tmp" / "task-flows"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{flow_id}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(summary, encoding="utf-8")

    print(summary)
    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
