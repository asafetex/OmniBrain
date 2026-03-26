"""Shared utilities for OmniBrain TRIAD tools."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(tools_dir: Path) -> dict[str, Any]:
    cfg = tools_dir / "config.json"
    if cfg.exists():
        return load_json(cfg)
    return load_json(tools_dir / "config.example.json")


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def markdown_bullets(items: list[str], empty_label: str) -> str:
    if not items:
        return f"- {empty_label}"
    return "\n".join(f"- {item}" for item in items)


def run_git(repo: Path, args: list[str]) -> tuple[bool, str]:
    cmd = ["git", "-C", str(repo), *args]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        message = proc.stderr.strip() or proc.stdout.strip() or f"git failed: {' '.join(cmd)}"
        return False, message
    return True, proc.stdout.strip()


def run_git_strict(repo: Path, args: list[str]) -> str:
    ok, result = run_git(repo, args)
    if not ok:
        raise RuntimeError(result)
    return result


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, cwd=str(cwd))
    return proc.returncode, proc.stdout, proc.stderr


def command_exists(cmd: str) -> bool:
    if not cmd:
        return False
    if os.sep in cmd or (os.altsep and os.altsep in cmd):
        return Path(cmd).exists()
    return shutil.which(cmd) is not None


def get_repo_root(tools_dir: Path) -> Path:
    return tools_dir.parent


def resolve_config_path(cfg_path: Path, repo_root: Path) -> Path:
    if cfg_path.is_absolute():
        return cfg_path
    return (repo_root / cfg_path).resolve()


def find_saved_path(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("Saved: "):
            return line.replace("Saved: ", "", 1).strip()
    return ""


def detect_intent(
    task: str,
    intents: dict[str, Any],
    explicit_intent: str,
) -> tuple[str, dict[str, Any]]:
    if explicit_intent:
        payload = intents.get(explicit_intent)
        if payload is None:
            raise ValueError(f"Intent not found in routing policy: {explicit_intent}")
        return explicit_intent, payload

    text = task.lower()
    best_name = "generic"
    best_score = 0
    best_payload: dict[str, Any] = {}
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
