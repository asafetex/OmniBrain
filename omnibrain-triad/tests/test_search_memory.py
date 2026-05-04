"""Tests for tools/search_memory.py."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class TestSearchMemory:
    def _seed_memories(self, repo_root: Path) -> None:
        inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
        inbox.mkdir(parents=True, exist_ok=True)
        graph = repo_root / "context-hub" / "02_GRAPH" / "disciplines" / "agents" / "skills"
        graph.mkdir(parents=True, exist_ok=True)
        (inbox / "MEM__WIN__alpha__spark-join-explode__20260101-1000.md").write_text(
            "Spark SQL join explode optimization with broadcast hint.", encoding="utf-8"
        )
        (inbox / "MEM__LESSON__beta__currency-hardening__20260101-1100.md").write_text(
            "Currency hardening for payment validation, supports BRL USD EUR.", encoding="utf-8"
        )
        (graph / "MEM__WIN__gamma__gate-manual-fallback__20260101-1200.md").write_text(
            "Gate manual fallback when CLI is offline. Verdict APPROVE recorded.", encoding="utf-8"
        )

    def test_help_works(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "search_memory.py"), "--help"],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--query" in result.stdout

    def test_empty_query_rejected(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "search_memory.py"), "--query", "", "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 2
        assert "cannot be empty" in result.stderr

    def test_no_memories_returns_zero(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "search_memory.py"), "--query", "anything", "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "No memories" in result.stdout

    def test_relevant_memory_ranked_first(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        self._seed_memories(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "search_memory.py"),
             "--query", "currency payment validation",
             "--repo-root", str(repo_root),
             "--format", "json"],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total_indexed"] == 3
        assert len(data["results"]) >= 1
        top_result = data["results"][0]
        assert "currency-hardening" in top_result["path"]
        assert top_result["score"] > 0.05

    def test_irrelevant_query_returns_empty(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        self._seed_memories(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "search_memory.py"),
             "--query", "quantum cryptography blockchain xyz123",
             "--repo-root", str(repo_root),
             "--format", "json"],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total_indexed"] == 3
        assert data["results"] == []

    def test_top_k_respected(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        self._seed_memories(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "search_memory.py"),
             "--query", "spark currency gate fallback",
             "--repo-root", str(repo_root),
             "--top-k", "2",
             "--format", "json"],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["results"]) <= 2
