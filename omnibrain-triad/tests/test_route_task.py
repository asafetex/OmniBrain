"""Tests for tools/route_task.py."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


class TestRouteTask:
    def test_cli_args_parsing(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--task" in result.stdout
        assert "--level" in result.stdout

    def test_route_task_markdown_output(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "Add a new feature", "--level", "L2",
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Task Route" in result.stdout
        assert "Level: L2" in result.stdout
        assert "Saved:" in result.stdout

    def test_route_task_json_output(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "fix bug", "--level", "L3",
             "--repo", str(repo_root), "--format", "json"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        json_text = result.stdout.split("Saved:")[0].strip()
        data = json.loads(json_text)
        assert data["level"] == "L3"
        assert data["task"] == "fix bug"
        assert "route_id" in data

    def test_route_task_intent_auto_detection(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "I need to join two dataframes with explode",
             "--level", "L3", "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "spark_sql_join" in result.stdout or "generic" in result.stdout

    def test_route_task_explicit_intent(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "do something", "--level", "L2",
             "--repo", str(repo_root), "--intent", "spark_sql_join"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Intent: spark_sql_join" in result.stdout

    def test_route_task_l3_gate_required(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "critical refactor", "--level", "L3",
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Gate Required: True" in result.stdout

    def test_route_task_writes_file(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "test task", "--level", "L1",
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        routes_dir = repo_root / "tmp" / "task-routes"
        assert list(routes_dir.glob("ROUTE-*.md")) != []

    def test_route_task_invalid_intent(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "test", "--level", "L2",
             "--repo", str(repo_root), "--intent", "nonexistent_intent"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode != 0
