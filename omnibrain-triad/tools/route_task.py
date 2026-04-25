#!/usr/bin/env python3
"""Route a task using routing policy and generate actionable recommendations."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import sys
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from utils import detect_intent, get_repo_root, load_json, resolve_config_path


def load_policy(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Routing config not found: {path}")
    return load_json(path)


def to_markdown(route: dict) -> str:
    graph_nodes = route.get("graph_nodes", [])
    if graph_nodes:
        graph_md = "\n".join(f"- {node}" for node in graph_nodes)
    else:
        graph_md = "- (no graph nodes suggested)"

    reviewers = route.get("reviewers", [])
    reviewers_md = ", ".join(reviewers) if reviewers else "(none)"

    q = shlex.quote
    cmd_graph_links = ",".join(graph_nodes)
    if cmd_graph_links:
        bundle_cmd = (
            f'python tools/build_context_bundle.py --repo {q(route["repo"])} '
            f'--task {q(route["task"])} --level {q(route["level"])} '
            f'--intent {q(route["intent"])} --graph-links {q(cmd_graph_links)}'
        )
    else:
        bundle_cmd = (
            f'python tools/build_context_bundle.py --repo {q(route["repo"])} '
            f'--task {q(route["task"])} --level {q(route["level"])} --intent {q(route["intent"])}'
        )

    change_cmd = (
        f'python tools/make_change_package.py --repo {q(route["repo"])} '
        f'--level {q(route["level"])} --goal {q(route["task"])}'
    )
    gate_cmd = 'python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md'

    return (
        f"# Task Route - {route['route_id']}\n\n"
        "## Summary\n"
        f"- Task: {route['task']}\n"
        f"- Level: {route['level']}\n"
        f"- Intent: {route['intent']}\n"
        f"- Executor: {route['executor']}\n"
        f"- Gate Required: {route['gate_required']}\n"
        f"- PreGate Optional: {route['pregate_optional']}\n"
        f"- Reviewers: {reviewers_md}\n"
        f"- Decision Rule: {route['decision_rule']}\n\n"
        "## Suggested Graph Nodes\n"
        f"{graph_md}\n\n"
        "## Recommended Commands\n"
        "```bash\n"
        f"{bundle_cmd}\n"
        f"{change_cmd}\n"
        + (f"{gate_cmd}\n" if route["gate_required"] else "")
        + "```\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Route task intent and policy for OmniBrain TRIAD.")
    parser.add_argument("--task", required=True, help="Task description.")
    parser.add_argument("--level", default="L2", choices=["L1", "L2", "L3"], help="Task level.")
    parser.add_argument("--intent", default="", help="Explicit intent id from routing policy.")
    parser.add_argument("--repo", default=".", help="Target repository path for command suggestions.")
    parser.add_argument("--routing-config", default="configs/routing.json", help="Routing config path (JSON).")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"], help="Output format.")
    parser.add_argument("--output", default="", help="Optional output file path.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent
    cfg_path = Path(args.routing_config)
    if not cfg_path.is_absolute():
        cfg_path = (repo_root / cfg_path).resolve()
    policy = load_policy(cfg_path)

    level_cfg = policy.get("levels", {}).get(args.level, {})
    intent_name, intent_payload = detect_intent(args.task, policy.get("intents", {}), args.intent.strip())

    route_id = f"ROUTE-{dt.datetime.now():%Y%m%d-%H%M%S}"
    reviewers = level_cfg.get("reviewers", policy.get("default_reviewers", []))
    route = {
        "route_id": route_id,
        "timestamp": f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}",
        "task": args.task.strip(),
        "level": args.level,
        "intent": intent_name,
        "executor": intent_payload.get("preferred_executor", policy.get("default_executor", "claude_code")),
        "graph_nodes": intent_payload.get("graph_nodes", []),
        "reviewers": reviewers,
        "gate_required": bool(level_cfg.get("gate_required", False)),
        "pregate_optional": bool(level_cfg.get("pregate_optional", False)),
        "decision_rule": level_cfg.get("decision_rule", "not_defined"),
        "repo": str(Path(args.repo)),
        "routing_config": str(cfg_path),
    }

    if args.format == "json":
        rendered = json.dumps(route, ensure_ascii=True, indent=2)
    else:
        rendered = to_markdown(route)

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_dir = repo_root / "tmp" / "task-routes"
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = "json" if args.format == "json" else "md"
        out_path = out_dir / f"{route_id}.{ext}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")

    print(rendered)
    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
