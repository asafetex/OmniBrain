#!/usr/bin/env python3
"""Build a compact context bundle for execution handoff."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"JSON config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def detect_intent(task: str, intents: dict, explicit_intent: str) -> tuple[str, list[str]]:
    if explicit_intent:
        payload = intents.get(explicit_intent, {})
        return explicit_intent, payload.get("graph_nodes", [])

    text = task.lower()
    best_name = ""
    best_score = 0
    best_nodes: list[str] = []
    for name, payload in intents.items():
        score = 0
        for kw in payload.get("keywords", []):
            if str(kw).lower() in text:
                score += 1
        if score > best_score:
            best_score = score
            best_name = name
            best_nodes = payload.get("graph_nodes", [])
    if best_name:
        return best_name, best_nodes
    return "generic", []


def run_git(repo: Path, args: list[str]) -> tuple[bool, str]:
    cmd = ["git", "-C", str(repo)] + args
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        message = proc.stderr.strip() or proc.stdout.strip() or f"git failed: {' '.join(cmd)}"
        return False, message
    return True, proc.stdout.strip()


def excerpt_file(path: Path, max_lines: int, max_chars: int) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()[:max_lines]
    clipped = "\n".join(lines)
    if len(clipped) > max_chars:
        clipped = clipped[: max_chars - 3] + "..."
    return clipped.strip() or "(empty)"


def list_recent_markdown(paths: list[Path], limit: int) -> list[Path]:
    files: list[Path] = []
    for base in paths:
        if base.exists():
            files.extend([p for p in base.glob("*.md") if p.is_file()])
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def markdown_bullets(items: list[str], empty_label: str) -> str:
    if not items:
        return f"- {empty_label}"
    return "\n".join(f"- {item}" for item in items)


def build_repo_snapshot(repo: Path, max_diff_chars: int) -> dict[str, str]:
    branch_ok, branch = run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    status_ok, status = run_git(repo, ["status", "--short"])
    commits_ok, commits = run_git(repo, ["log", "--oneline", "-n", "5"])
    diff_ok, diff = run_git(repo, ["diff"])

    changed_files: list[str] = []
    if status_ok and status:
        for line in status.splitlines():
            if len(line) >= 4:
                changed_files.append(line[3:].strip())
            else:
                changed_files.append(line.strip())

    diff_text = diff if diff_ok else f"(diff unavailable) {diff}"
    if len(diff_text) > max_diff_chars:
        diff_text = diff_text[: max_diff_chars - 3] + "..."

    return {
        "branch": branch if branch_ok else f"(branch unavailable) {branch}",
        "status": status if status_ok else f"(status unavailable) {status}",
        "changed_files": markdown_bullets(changed_files, "no changed files"),
        "commits": commits if commits_ok else f"(log unavailable) {commits}",
        "diff": diff_text or "(no diff)",
    }


def load_graph_nodes(graph_root: Path, links: list[str], max_lines: int, max_chars: int) -> str:
    if not links:
        return "- (no graph links provided)"

    blocks: list[str] = []
    for link in links:
        rel = link
        if not rel.endswith(".md"):
            rel = rel + ".md"
        node = (graph_root / rel).resolve()
        if not node.exists():
            blocks.append(f"### {link}\nPath: {node}\n\nMissing node file.\n")
            continue
        content = excerpt_file(node, max_lines=max_lines, max_chars=max_chars)
        blocks.append(f"### {link}\nPath: {node}\n\n```text\n{content}\n```\n")
    return "\n".join(blocks).strip()


def load_recent_memory(repo_root: Path, limit: int, max_lines: int, max_chars: int) -> str:
    gate_dir = repo_root / "tmp" / "gate-results"
    inbox_dir = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
    recent = list_recent_markdown([gate_dir, inbox_dir], limit=limit)
    if not recent:
        return "- (no memory artifacts found)"

    sections: list[str] = []
    for item in recent:
        rel = item.relative_to(repo_root)
        snippet = excerpt_file(item, max_lines=max_lines, max_chars=max_chars)
        sections.append(f"### {rel}\n\n```text\n{snippet}\n```\n")
    return "\n".join(sections).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a context bundle for task execution.")
    parser.add_argument("--repo", required=True, help="Target repository path to inspect.")
    parser.add_argument("--task", required=True, help="Task description.")
    parser.add_argument("--level", default="L2", choices=["L1", "L2", "L3"], help="Task level.")
    parser.add_argument("--intent", default="", help="Intent label (optional).")
    parser.add_argument("--graph-links", default="", help="Comma-separated graph node links.")
    parser.add_argument("--auto-route", action="store_true", help="Auto-select intent and graph nodes from routing policy.")
    parser.add_argument("--routing-config", default="configs/routing.json", help="Routing config path (JSON).")
    parser.add_argument("--memory-limit", type=int, default=4, help="Max memory artifacts to embed.")
    parser.add_argument("--max-diff-chars", type=int, default=12000, help="Max chars for diff section.")
    parser.add_argument("--max-node-lines", type=int, default=40, help="Max lines per graph node excerpt.")
    parser.add_argument("--max-memory-lines", type=int, default=30, help="Max lines per memory excerpt.")
    parser.add_argument("--output", default="", help="Optional explicit output file path.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent
    target_repo = Path(args.repo).resolve()
    if not target_repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {target_repo}")

    graph_root = repo_root / "context-hub" / "02_GRAPH"
    graph_links = parse_csv(args.graph_links)

    intent_value = args.intent.strip()
    if args.auto_route:
        cfg_path = Path(args.routing_config)
        if not cfg_path.is_absolute():
            cfg_path = (repo_root / cfg_path).resolve()
        policy = load_json(cfg_path)
        detected_intent, detected_nodes = detect_intent(args.task, policy.get("intents", {}), intent_value)
        intent_value = detected_intent
        if not graph_links:
            graph_links = list(detected_nodes)

    snapshot = build_repo_snapshot(target_repo, args.max_diff_chars)
    graph_section = load_graph_nodes(graph_root, graph_links, args.max_node_lines, 4000)
    memory_section = load_recent_memory(repo_root, args.memory_limit, args.max_memory_lines, 4000)

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    bundle_id = f"CTX-{ts}"
    content = (
        f"# Context Bundle - {bundle_id}\n\n"
        "## Metadata\n"
        f"- Bundle-ID: {bundle_id}\n"
        f"- Timestamp: {dt.datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"- Task: {args.task.strip()}\n"
        f"- Level: {args.level}\n"
        f"- Intent: {intent_value or '(not set)'}\n"
        f"- Repo: {target_repo}\n\n"
        "## Repo Snapshot\n"
        f"- Branch: {snapshot['branch']}\n\n"
        "### Changed Files\n"
        f"{snapshot['changed_files']}\n\n"
        "### Git Status\n"
        "```text\n"
        f"{snapshot['status'] or '(clean)'}\n"
        "```\n\n"
        "### Recent Commits\n"
        "```text\n"
        f"{snapshot['commits']}\n"
        "```\n\n"
        "## Graph Context\n"
        f"{graph_section}\n\n"
        "## Recent Memory\n"
        f"{memory_section}\n\n"
        "## Git Diff (Excerpt)\n"
        "```diff\n"
        f"{snapshot['diff']}\n"
        "```\n\n"
        "## Execution Prompt Seed\n"
        "1. Restate objective and constraints.\n"
        "2. Propose minimal plan tied to changed files.\n"
        "3. Identify top risks and validation checks.\n"
        "4. Implement diff-first and prepare Change Package.\n"
    )

    if args.output:
        output_path = Path(args.output).resolve()
    else:
        out_dir = repo_root / "tmp" / "context-bundles"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{bundle_id}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    print(content)
    print(f"Saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
