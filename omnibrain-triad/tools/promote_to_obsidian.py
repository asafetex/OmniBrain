#!/usr/bin/env python3
"""Promote curated notes from INBOX to Obsidian GRAPH."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def list_candidates(inbox: Path) -> list[Path]:
    if not inbox.exists():
        return []
    return sorted([p for p in inbox.glob("*.md") if p.is_file() and p.name.lower() != "readme.md"])


def update_graph_index(graph_index: Path, new_rel_path: str) -> None:
    graph_index.parent.mkdir(parents=True, exist_ok=True)
    if not graph_index.exists():
        graph_index.write_text("# Skill Graph Index\n\n## Promoted Notes\n", encoding="utf-8")
    content = graph_index.read_text(encoding="utf-8")
    forward_path = new_rel_path.replace("\\", "/")
    marker = f"- [{Path(new_rel_path).stem}]({forward_path})"
    promoted_heading = "## Promoted Notes"

    lines = content.splitlines()
    promoted_notes: list[str] = []
    cleaned_lines: list[str] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == promoted_heading:
            idx += 1
            while idx < len(lines) and not lines[idx].startswith("## "):
                item = lines[idx].strip()
                if item.startswith("- [") and item not in promoted_notes:
                    promoted_notes.append(item)
                idx += 1
            continue
        cleaned_lines.append(line)
        idx += 1

    if marker not in promoted_notes:
        promoted_notes.append(marker)

    # Trim trailing blank lines before re-appending canonical promoted section.
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    rebuilt = "\n".join(cleaned_lines)
    if rebuilt:
        rebuilt += "\n\n"
    else:
        rebuilt = ""
    rebuilt += promoted_heading + "\n"
    for item in promoted_notes:
        rebuilt += item + "\n"

    graph_index.write_text(rebuilt, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote INBOX notes into context-hub graph.")
    parser.add_argument("--list", action="store_true", help="List INBOX candidates.")
    parser.add_argument("--source", default="", help="Source markdown file path in INBOX.")
    parser.add_argument(
        "--target",
        default="",
        help="Target directory relative to context-hub/02_GRAPH (example: disciplines/agents/skills).",
    )
    parser.add_argument("--copy", action="store_true", help="Copy instead of move.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
    graph_root = repo_root / "context-hub" / "02_GRAPH"

    if args.list:
        candidates = list_candidates(inbox)
        if not candidates:
            print("Nenhum candidato no INBOX.")
            return 0
        print("Candidatos no INBOX:")
        for idx, path in enumerate(candidates, start=1):
            print(f"{idx}. {path}")
        return 0

    if not args.source or not args.target:
        print("Para promover, informe --source e --target.")
        print("Exemplo: --source context-hub/05_INBOX/byterover-imports/MEM...md --target disciplines/agents/skills")
        return 1

    src = Path(args.source).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Arquivo de origem nao encontrado: {src}")

    target_arg = args.target.replace("\\", "/").strip("/")
    # If user passed full path including 'context-hub/02_GRAPH/...', strip the prefix
    for prefix in ("context-hub/02_GRAPH/", "context-hub/02_graph/"):
        if target_arg.lower().startswith(prefix.lower()):
            target_arg = target_arg[len(prefix):]
            break
    target_dir = (graph_root / target_arg).resolve()
    if graph_root not in target_dir.parents and target_dir != graph_root:
        raise ValueError("Target deve ficar dentro de context-hub/02_GRAPH.")
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / src.name

    if args.copy:
        shutil.copy2(src, dst)
        action = "copiado"
    else:
        shutil.move(str(src), str(dst))
        action = "movido"

    rel = dst.relative_to(graph_root)
    update_graph_index(graph_root / "index.md", str(rel))
    print(f"Arquivo {action}: {dst}")
    print("Index atualizado: context-hub/02_GRAPH/index.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
