"""Shared fixtures for omnibrain-triad tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "tools"
_tools_root = SCRIPTS_DIR.parent
if str(_tools_root) not in sys.path:
    sys.path.insert(0, str(_tools_root))


@pytest.fixture
def tools_dir(tmp_path: Path) -> Path:
    td = tmp_path / "tools"
    td.mkdir()
    shutil.copytree(SCRIPTS_DIR, td, dirs_exist_ok=True)
    (td / "config.example.json").write_text(
        json.dumps({
            "version": "1.0",
            "defaults": {"timeout_seconds": 120, "encoding": "utf-8"},
            "auditors": {
                "codex": {"enabled": False, "cmd": "codex", "args": [], "timeout_seconds": 240},
                "gemini": {"enabled": False, "cmd": "gemini", "args": [], "timeout_seconds": 120},
            },
            "byterover": {"enabled": False, "cmd": "brv", "args": []},
        }), encoding="utf-8"
    )
    return td


@pytest.fixture
def repo_root(tmp_path: Path, tools_dir: Path) -> Path:
    root = tmp_path
    tmp = root / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "change-packages").mkdir(exist_ok=True)
    (tmp / "gate-results").mkdir(exist_ok=True)
    (tmp / "manual-prompts").mkdir(exist_ok=True)
    (tmp / "manual-responses").mkdir(exist_ok=True)
    (tmp / "task-routes").mkdir(exist_ok=True)
    (tmp / "context-bundles").mkdir(exist_ok=True)
    (root / "context-hub").mkdir(exist_ok=True)
    configs = root / "configs"
    configs.mkdir(exist_ok=True)
    (configs / "routing.json").write_text(
        json.dumps({
            "version": 1,
            "default_executor": "claude_code",
            "default_reviewers": [],
            "levels": {
                "L1": {"gate_required": False, "pregate_optional": False, "reviewers": [], "decision_rule": "not_required"},
                "L2": {"gate_required": False, "pregate_optional": True, "reviewers": ["codex"], "decision_rule": "any_reject"},
                "L3": {"gate_required": True, "pregate_optional": True, "reviewers": ["codex", "gemini"], "decision_rule": "both_approve"},
            },
            "intents": {
                "generic": {"keywords": [], "graph_nodes": []},
                "spark_sql_join": {"keywords": ["join", "explode"], "graph_nodes": ["joins.md"]},
            },
        }), encoding="utf-8"
    )
    subprocess.run(["git", "init"], cwd=root, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=root, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, capture_output=True, text=True)
    (root / "README.md").write_text("test", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, capture_output=True, text=True)
    return root


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "git_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo, capture_output=True, text=True
    )
    (repo / "README.md").write_text("test", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, capture_output=True, text=True)
    return repo


@pytest.fixture
def python_exe() -> str:
    return sys.executable


@pytest.fixture
def subprocess_env(tools_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tools_dir.parent)
    return env
