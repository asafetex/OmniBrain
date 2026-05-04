"""Tests for tools/build_context_bundle.py."""

from __future__ import annotations

import subprocess
from pathlib import Path


class TestBuildContextBundle:
    def test_cli_args_parsing(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "build_context_bundle.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--repo" in result.stdout
        assert "--task" in result.stdout
        assert "--level" in result.stdout

    def test_missing_repo(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "build_context_bundle.py"),
             "--repo", "/nonexistent", "--task", "test", "--level", "L2"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode != 0

    def test_basic_bundle(
        self, python_exe: str, tools_dir: Path, git_repo: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "file.txt").write_text("content", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "build_context_bundle.py"),
             "--repo", str(git_repo), "--task", "Add file", "--level", "L2"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Context Bundle" in result.stdout
        assert "Saved:" in result.stdout

    def test_bundle_with_graph_links(
        self, python_exe: str, tools_dir: Path, git_repo: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "f.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "build_context_bundle.py"),
             "--repo", str(git_repo), "--task", "test", "--level", "L1",
             "--graph-links", "joins.md"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Graph Context" in result.stdout

    def test_bundle_auto_route(
        self, python_exe: str, tools_dir: Path, git_repo: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "f.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        result = subprocess.run(
            [python_exe, str(tools_dir / "build_context_bundle.py"),
             "--repo", str(git_repo), "--task", "join with explode", "--level", "L2",
             "--auto-route"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0

    def test_bundle_writes_file(
        self, python_exe: str, tools_dir: Path, git_repo: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        (git_repo / "f.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_repo), "add", "."], capture_output=True, env=subprocess_env)
        subprocess.run(
            [python_exe, str(tools_dir / "build_context_bundle.py"),
             "--repo", str(git_repo), "--task", "test", "--level", "L1"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        bundles_dir = repo_root / "tmp" / "context-bundles"
        assert list(bundles_dir.glob("CTX-*.md")) != []


class TestBuildRepoSnapshot:
    def test_excerpt_file_truncates_lines(self, tmp_path: Path) -> None:
        from tools.build_context_bundle import excerpt_file

        p = tmp_path / "long.md"
        p.write_text("\n".join([f"line {i}" for i in range(100)]), encoding="utf-8")
        result = excerpt_file(p, max_lines=10, max_chars=10000)
        lines = result.splitlines()
        assert len(lines) <= 10

    def test_excerpt_file_truncates_chars(self, tmp_path: Path) -> None:
        from tools.build_context_bundle import excerpt_file

        p = tmp_path / "wide.md"
        p.write_text("x" * 1000, encoding="utf-8")
        result = excerpt_file(p, max_lines=100, max_chars=50)
        assert len(result) <= 53
        assert "..." in result
