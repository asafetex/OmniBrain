"""Tests for tools/preflight_check.py."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


class TestPreflightCheck:
    def test_cli_args_parsing(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--repo" in result.stdout
        assert "--strict" in result.stdout

    def test_preflight_missing_repo(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", "/nonexistent/repo"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 1
        assert "FAIL" in result.stdout

    def test_preflight_valid_repo(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "TRIAD Preflight" in result.stdout
        assert "Summary:" in result.stdout
        assert "repo.exists" in result.stdout
        assert "git.cmd" in result.stdout

    def test_preflight_strict_warns_become_fail(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root), "--strict"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "Summary:" in result.stdout

    def test_preflight_checks_python_cmd(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "python.cmd" in result.stdout

    def test_preflight_checks_git_cmd(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "git.cmd" in result.stdout

    def test_preflight_checks_vault_path(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "vault.path" in result.stdout

    def test_preflight_checks_routing_config(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "routing.json" in result.stdout

    def test_preflight_checks_tmp_write(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "tmp.write" in result.stdout

    def test_preflight_summary_line(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert "Summary:" in result.stdout
