"""Tests for tools/recover_session.py."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


class TestRecoverSession:
    def test_cli_args_parsing(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "recover_session.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--repo" in result.stdout

    def test_missing_gate_results(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "recover_session.py"),
             "--repo", str(repo_root)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 1

    def test_recover_from_gate_result(
        self, python_exe: str, tools_dir: Path, repo_root: Path, git_repo: Path, subprocess_env: dict[str, str]
    ) -> None:
        gate_file = repo_root / "tmp" / "gate-results" / "CHG-20260101-120000.md"
        gate_file.parent.mkdir(parents=True, exist_ok=True)
        gate_file.write_text(
            "# Gate Result - CHG-20260101-120000\n\n"
            "- Change-ID: CHG-20260101-120000\n"
            "- Level: L3\n"
            "- Final Decision: APPROVE\n\n"
            "## Auditor: codex\n"
            "- Ran: True\n"
            "- Status: completed\n"
            "- Verdict: APPROVE\n"
            "- Verdict Source: cli\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "recover_session.py"),
             "--repo", str(git_repo), "--change-id", "CHG-20260101-120000"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Recovery Report" in result.stdout
        assert "CHG-20260101-120000" in result.stdout
        assert "APPROVE" in result.stdout

    def test_recover_with_reject_decision(
        self, python_exe: str, tools_dir: Path, repo_root: Path, git_repo: Path, subprocess_env: dict[str, str]
    ) -> None:
        gate_file = repo_root / "tmp" / "gate-results" / "CHG-REJECT.md"
        gate_file.write_text(
            "- Change-ID: CHG-REJECT\n"
            "- Level: L3\n"
            "- Final Decision: REJECT\n\n"
            "## Auditor: codex\n"
            "- Verdict: REJECT\n"
            "- Status: completed\n\n"
            "[P0] Critical blocker found\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "recover_session.py"),
             "--repo", str(git_repo), "--change-id", "CHG-REJECT"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "REJECT" in result.stdout
        assert "P0" in result.stdout


class TestParseSummary:
    def test_parse_summary_full(self) -> None:
        from tools.recover_session import parse_summary

        content = (
            "- Change-ID: CHG-123\n"
            "- Level: L2\n"
            "- Final Decision: APPROVE\n"
        )
        result = parse_summary(content)
        assert result["change_id"] == "CHG-123"
        assert result["level"] == "L2"
        assert result["decision"] == "APPROVE"

    def test_parse_summary_missing_fields(self) -> None:
        from tools.recover_session import parse_summary

        content = "No structured data here"
        result = parse_summary(content)
        assert result["change_id"] == "CHG-UNKNOWN"
        assert result["level"] == "L3"
        assert result["decision"] == "UNKNOWN"


class TestBuildNextActions:
    def test_approve_actions(self) -> None:
        from tools.recover_session import build_next_actions

        actions = build_next_actions("APPROVE", [], [])
        assert any("test" in a.lower() for a in actions)
        assert any("commit" in a.lower() for a in actions)

    def test_reject_actions(self) -> None:
        from tools.recover_session import build_next_actions

        actions = build_next_actions("REJECT", ["[P0] blocker"], [])
        assert any("blocker" in a.lower() or "P0" in a for a in actions)

    def test_conflict_actions(self) -> None:
        from tools.recover_session import build_next_actions

        actions = build_next_actions("CONFLICT", [], [
            {"name": "codex", "verdict": "UNKNOWN"},
        ])
        assert any("missing" in a.lower() for a in actions)
