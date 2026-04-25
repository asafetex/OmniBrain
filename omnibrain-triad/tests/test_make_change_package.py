"""Tests for tools/make_change_package.py."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


class TestMakeChangePackage:
    def test_cli_args_parsing(
        self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--repo" in result.stdout
        assert "--level" in result.stdout

    def test_missing_repo(
        self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"),
             "--repo", "/nonexistent/repo", "--level", "L2", "--goal", "test"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 1

    def test_generates_change_package(
        self, python_exe: str, tools_dir: Path, git_repo: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "test.txt").write_text("hello", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"),
             "--repo", str(git_repo), "--level", "L2", "--goal", "Add test file",
             "--graph-links", "docs/test.md",
             "--memory-refs", "MEM-001"],
            capture_output=True,
            text=True,
            cwd=str(git_repo),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Saved:" in result.stdout

    def test_generates_change_package_staged(
        self, python_exe: str, tools_dir: Path, git_repo: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "staged.txt").write_text("staged content", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"),
             "--repo", str(git_repo), "--level", "L3", "--goal", "Staged change",
             "--staged"],
            capture_output=True,
            text=True,
            cwd=str(git_repo),
            env=subprocess_env,
        )
        assert result.returncode == 0

    def test_change_package_contains_goal(
        self, python_exe: str, tools_dir: Path, git_repo: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "x.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"),
             "--repo", str(git_repo), "--level", "L1", "--goal", "My custom goal"],
            capture_output=True,
            text=True,
            cwd=str(git_repo),
            env=subprocess_env,
        )
        assert "My custom goal" in result.stdout

    def test_change_package_graph_links_bullets(
        self, python_exe: str, tools_dir: Path, git_repo: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "x.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"),
             "--repo", str(git_repo), "--level", "L2", "--goal", "test",
             "--graph-links", "node1.md, node2.md"],
            capture_output=True,
            text=True,
            cwd=str(git_repo),
            env=subprocess_env,
        )
        assert "- node1.md" in result.stdout
        assert "- node2.md" in result.stdout
