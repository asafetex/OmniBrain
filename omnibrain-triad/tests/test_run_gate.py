"""Tests for tools/run_gate.py."""

from __future__ import annotations

import subprocess
from pathlib import Path


class TestRunGate:
    def test_cli_args_parsing(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--change-package" in result.stdout

    def test_missing_change_package(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"),
             "--change-package", "/nonexistent/change.md"],
            capture_output=True,
            text=True,
            env=subprocess_env,
        )
        assert result.returncode != 0

    def test_gate_writes_result(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        cp = repo_root / "tmp" / "change-packages" / "CHG-TEST.md"
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_text(
            "- Change-ID: CHG-TEST\n- Level: L3\n- Repo: \n- Goal: test",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"),
             "--change-package", str(cp)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Gate Result" in result.stdout
        out = repo_root / "tmp" / "gate-results" / "CHG-TEST.md"
        assert out.exists()

    def test_gate_l2_with_codex_only(
        self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]
    ) -> None:
        cp = repo_root / "tmp" / "change-packages" / "CHG-L2.md"
        cp.write_text(
            "- Change-ID: CHG-L2\n- Level: L2\n- Repo: \n- Goal: test",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"),
             "--change-package", str(cp)],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Gate Result" in result.stdout


class TestDecide:
    def test_l3_reject_if_any_reject(self) -> None:
        from tools.run_gate import AuditorResult, decide

        results = {
            "codex": AuditorResult("codex", True, "completed", "REJECT", "cli", "", "", "", "", ""),
            "gemini": AuditorResult("gemini", True, "completed", "APPROVE", "cli", "", "", "", "", ""),
        }
        assert decide("L3", results) == "REJECT"

    def test_l3_approve_if_both_approve(self) -> None:
        from tools.run_gate import AuditorResult, decide

        results = {
            "codex": AuditorResult("codex", True, "completed", "APPROVE", "cli", "", "", "", "", ""),
            "gemini": AuditorResult("gemini", True, "completed", "APPROVE", "cli", "", "", "", "", ""),
        }
        assert decide("L3", results) == "APPROVE"

    def test_l3_conflict_on_mixed(self) -> None:
        from tools.run_gate import AuditorResult, decide

        results = {
            "codex": AuditorResult("codex", True, "completed", "UNKNOWN", "cli", "", "", "", "", ""),
            "gemini": AuditorResult("gemini", True, "completed", "APPROVE", "cli", "", "", "", "", ""),
        }
        assert decide("L3", results) == "CONFLICT"

    def test_l2_reject_on_any_reject(self) -> None:
        from tools.run_gate import AuditorResult, decide

        results = {
            "codex": AuditorResult("codex", True, "completed", "REJECT", "cli", "", "", "", "", ""),
        }
        assert decide("L2", results) == "REJECT"

    def test_l2_needs_human_on_unknown(self) -> None:
        from tools.run_gate import AuditorResult, decide

        results = {
            "codex": AuditorResult("codex", True, "completed", "UNKNOWN", "cli", "", "", "", "", ""),
        }
        assert decide("L2", results) == "NEEDS_HUMAN"

    def test_l1_not_required(self) -> None:
        from tools.run_gate import decide

        assert decide("L1", {}) == "NOT_REQUIRED"


class TestParseVerdict:
    def test_parse_verdict_approve(self) -> None:
        from tools.run_gate import parse_verdict

        assert parse_verdict("Some text\nVERDICT: APPROVE\n") == "APPROVE"

    def test_parse_verdict_reject(self) -> None:
        from tools.run_gate import parse_verdict

        assert parse_verdict("VERDICT: REJECT") == "REJECT"

    def test_parse_verdict_unknown(self) -> None:
        from tools.run_gate import parse_verdict

        assert parse_verdict("No verdict here") == "UNKNOWN"

    def test_parse_verdict_case_insensitive(self) -> None:
        from tools.run_gate import parse_verdict

        assert parse_verdict("verdict: approve") == "APPROVE"


class TestInferVerdict:
    def test_infer_reject_from_p0(self) -> None:
        from tools.run_gate import infer_verdict_from_cli_text

        assert infer_verdict_from_cli_text("This has a [P0] blocker") == "REJECT"

    def test_infer_approve_from_no_blocking(self) -> None:
        from tools.run_gate import infer_verdict_from_cli_text

        assert infer_verdict_from_cli_text("no blocking issues found") == "APPROVE"

    def test_infer_reject_from_insufficient(self) -> None:
        from tools.run_gate import infer_verdict_from_cli_text

        assert infer_verdict_from_cli_text("insufficient evidence") == "REJECT"
