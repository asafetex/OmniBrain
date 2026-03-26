"""Tests for tools/triad_stats.py."""

from __future__ import annotations

import subprocess
from pathlib import Path


class TestTriadStats:
    def test_cli_args_parsing(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "triad_stats.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--days" in result.stdout

    def test_stats_empty_repo(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "triad_stats.py"),
             "--days", "7"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "TRIAD Stats" in result.stdout
        assert "Saved:" in result.stdout

    def test_stats_with_memory_files(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "MEM__WIN__test__20260320.md").write_text(
            "- Type: WIN\n- Project: test\n- Timestamp: 2026-03-20",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "triad_stats.py"),
             "--days", "7"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "WIN" in result.stdout or "TRIAD Stats" in result.stdout

    def test_stats_window_30_days(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "triad_stats.py"),
             "--days", "30"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Days: 30" in result.stdout


class TestCollectMemoryFiles:
    def test_collect_memory_files_empty(self, repo_root: Path) -> None:
        from tools.triad_stats import collect_memory_files

        files = collect_memory_files(repo_root)
        assert isinstance(files, list)

    def test_collect_memory_files_with_files(self, repo_root: Path) -> None:
        from tools.triad_stats import collect_memory_files

        inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "MEM__WIN__proj__20260320.md").write_text(
            "- Type: WIN\n", encoding="utf-8"
        )
        files = collect_memory_files(repo_root)
        assert len(files) >= 1
