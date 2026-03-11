#!/usr/bin/env python3
"""Record memory items to ByteRover CLI or fallback to local INBOX."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


VALID_TYPES = {"PLAN", "REVIEW", "LESSON", "WIN", "DECISION"}


def slugify(value: str) -> str:
    keep = []
    for ch in value.lower():
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        elif ch.isspace():
            keep.append("-")
    return "".join(keep).strip("-") or "topic"


def load_config(tools_dir: Path) -> dict:
    cfg = tools_dir / "config.json"
    if cfg.exists():
        return json.loads(cfg.read_text(encoding="utf-8"))
    return json.loads((tools_dir / "config.example.json").read_text(encoding="utf-8"))


def parse_csv(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def compose_memory_doc(mem_id: str, mem_type: str, project: str, topic: str, tags: list[str], refs: list[str], body: str) -> str:
    tags_line = " ".join(tags) if tags else "#type/unknown"
    refs_md = "\n".join(f"- {ref}" for ref in refs) if refs else "- (none)"
    return (
        f"# {mem_id}\n\n"
        f"## Metadata\n"
        f"- Type: {mem_type}\n"
        f"- Project: {project}\n"
        f"- Topic: {topic}\n"
        f"- Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"- Tags: {tags_line}\n\n"
        f"## Refs\n{refs_md}\n\n"
        f"## Content\n{body.strip()}\n"
    )


def try_byterover(config: dict, payload: str) -> tuple[bool, str]:
    cfg = config.get("byterover", {})
    enabled = bool(cfg.get("enabled", False))
    cmd = str(cfg.get("cmd", "")).strip()
    args = cfg.get("args", [])
    if not isinstance(args, list):
        args = []
    timeout_seconds = int(config.get("defaults", {}).get("timeout_seconds", 120))

    if not enabled:
        return False, "ByteRover desabilitado em config."
    if not cmd or shutil.which(cmd) is None:
        return False, "Comando ByteRover nao encontrado no PATH."

    try:
        proc = subprocess.run(
            [cmd] + args,
            input=payload,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except Exception as exc:  # pragma: no cover - fallback path
        return False, f"Falha ao executar ByteRover: {exc}"

    if proc.returncode != 0:
        return False, f"ByteRover retornou codigo {proc.returncode}: {proc.stderr.strip()}"
    return True, proc.stdout.strip() or "Registro enviado para ByteRover."


def main() -> int:
    parser = argparse.ArgumentParser(description="Record memory in ByteRover CLI with local fallback.")
    parser.add_argument("--type", required=True, choices=sorted(VALID_TYPES), help="Memory type.")
    parser.add_argument("--project", required=True, help="Project short name.")
    parser.add_argument("--topic", required=True, help="Topic short name.")
    parser.add_argument("--text", default="", help="Inline markdown text.")
    parser.add_argument("--file", default="", help="Path to markdown file to ingest as content.")
    parser.add_argument("--tags", default="", help="Comma-separated tags.")
    parser.add_argument("--refs", default="", help="Comma-separated references.")
    args = parser.parse_args()

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent

    body = args.text.strip()
    if args.file:
        body = Path(args.file).resolve().read_text(encoding="utf-8")
    if not body:
        body = "Sem conteudo adicional."

    mem_type = args.type.upper()
    project = slugify(args.project)
    topic = slugify(args.topic)
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    mem_id = f"MEM::{mem_type}::{project}::{topic}::{ts}"
    tags = parse_csv(args.tags)
    refs = parse_csv(args.refs)
    payload = compose_memory_doc(mem_id, mem_type, project, topic, tags, refs, body)

    config = load_config(tools_dir)
    ok, message = try_byterover(config, payload)
    if ok:
        print(message)
        print(f"Memory ID: {mem_id}")
        return 0

    inbox_dir = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    safe_file_id = mem_id.replace("::", "__")
    out_file = inbox_dir / f"{safe_file_id}.md"
    out_file.write_text(payload, encoding="utf-8")
    print(message)
    print("Fallback ativado. Arquivo salvo em:")
    print(out_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
