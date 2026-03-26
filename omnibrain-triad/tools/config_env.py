"""Environment-aware configuration loader for OmniBrain TRIAD.

Environment variables take precedence over config.json values.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    from tools.utils import load_json
except ModuleNotFoundError:
    from utils import load_json


DEFAULT_TIMEOUT = int(os.environ.get("TRIAD_TIMEOUT_SECONDS", "120"))
DEFAULT_ENCODING = os.environ.get("TRIAD_ENCODING", "utf-8")
BYTEROVER_CMD = os.environ.get("TRIAD_BYTEROVER_CMD", "")
CODEX_CMD = os.environ.get("TRIAD_CODEX_CMD", "codex")
GEMINI_CMD = os.environ.get("TRIAD_GEMINI_CMD", "gemini")
DEEPSEEK_CMD = os.environ.get("TRIAD_DEEPSEEK_CMD", "deepseek")
CODERABBIT_CMD = os.environ.get("TRIAD_CODERABBIT_CMD", "coderabbit")


def load_config(tools_dir: Path) -> dict[str, Any]:
    cfg_file = tools_dir / "config.json"
    if cfg_file.exists():
        config = load_json(cfg_file)
    else:
        config = load_json(tools_dir / "config.example.json")

    _apply_env_overrides(config)
    return config


def _apply_env_overrides(config: dict[str, Any]) -> None:
    defaults = config.setdefault("defaults", {})
    if "TRIAD_TIMEOUT_SECONDS" in os.environ:
        defaults["timeout_seconds"] = DEFAULT_TIMEOUT
    if "TRIAD_ENCODING" in os.environ:
        defaults["encoding"] = DEFAULT_ENCODING

    auditors = config.get("auditors", {})
    if "TRIAD_CODEX_CMD" in os.environ and "codex" in auditors:
        auditors["codex"]["cmd"] = CODEX_CMD
    if "TRIAD_GEMINI_CMD" in os.environ and "gemini" in auditors:
        auditors["gemini"]["cmd"] = GEMINI_CMD
    if "TRIAD_DEEPSEEK_CMD" in os.environ and "deepseek" in auditors:
        auditors["deepseek"]["cmd"] = DEEPSEEK_CMD
    if "TRIAD_CODERABBIT_CMD" in os.environ and "coderabbit" in auditors:
        auditors["coderabbit"]["cmd"] = CODERABBIT_CMD

    byterover = config.get("byterover", {})
    if "TRIAD_BYTEROVER_CMD" in os.environ:
        byterover["cmd"] = BYTEROVER_CMD
