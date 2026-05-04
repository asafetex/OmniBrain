"""End-to-end smoke tests reproducing the manual validations.

Each test exercises a real-world TRIAD workflow scenario and asserts on captured output.
These tests act as regression guard: if a tool drifts behaviorally, CI catches it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


def _make_target_repo(base: Path) -> Path:
    """Create a minimal git repo with a tracked file modification."""
    repo = base / "target_repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "smoke@test.local"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Smoke"], cwd=repo, check=True)
    (repo / "app.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, capture_output=True, check=True)
    (repo / "app.py").write_text("def f():\n    return 2\n", encoding="utf-8")
    return repo


@pytest.fixture
def target_repo(tmp_path: Path) -> Path:
    return _make_target_repo(tmp_path)


class TestSmokePreflight:
    def test_preflight_runs_and_reports(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "preflight_check.py"), "--repo", str(target_repo)],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        # Exit can be 0/1/2 depending on cli availability; we just need a coherent report.
        assert "TRIAD Preflight" in result.stdout
        assert "Summary:" in result.stdout
        assert "PASS=" in result.stdout


class TestSmokeRouteTask:
    def test_route_normal_task(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "Implement OAuth2",
             "--level", "L3",
             "--repo", str(target_repo)],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Gate Required: True" in result.stdout

    def test_route_rejects_empty_task(
        self, python_exe: str, tools_dir: Path, repo_root: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "", "--level", "L1", "--repo", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 2
        assert "cannot be empty" in result.stderr


class TestSmokeChangePackage:
    def test_change_package_with_diff(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "make_change_package.py"),
             "--repo", str(target_repo),
             "--level", "L2",
             "--goal", "smoke goal"],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        assert result.returncode == 0
        cps = list((target_repo / "tmp" / "change-packages").glob("CHG-*.md"))
        assert len(cps) == 1
        content = cps[0].read_text(encoding="utf-8")
        assert "Change-ID:" in content
        assert "smoke goal" in content
        assert "diff --git" in content

    def test_change_package_uuid_anti_collision(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        # Generate two change packages within the same second; UUIDs must keep them unique.
        cmd = [
            python_exe, str(tools_dir / "make_change_package.py"),
            "--repo", str(target_repo),
            "--level", "L1",
            "--goal", "race",
        ]
        a = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env)
        b = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env)
        assert a.returncode == 0 and b.returncode == 0
        cps = sorted(p.name for p in (target_repo / "tmp" / "change-packages").glob("CHG-*.md"))
        assert len(cps) == 2
        assert cps[0] != cps[1]


class TestSmokeGate:
    def _write_cp(self, target_repo: Path, change_id: str, level: str = "L3") -> Path:
        cps = target_repo / "tmp" / "change-packages"
        cps.mkdir(parents=True, exist_ok=True)
        cp = cps / f"{change_id}.md"
        cp.write_text(
            f"# Change Package\n- Change-ID: {change_id}\n- Level: {level}\n- Repo: {target_repo}\n## Git Diff\n```diff\n+ noop\n```\n",
            encoding="utf-8",
        )
        return cp

    def test_gate_unknown_unknown_yields_conflict(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        cp = self._write_cp(target_repo, "CHG-SMOKE-001")
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"),
             "--change-package", str(cp)],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Final Decision: CONFLICT" in result.stdout

    def test_gate_rejects_invalid_change_id(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        evil = target_repo / "evil_cp.md"
        evil.write_text(
            "# CP\n- Change-ID: ../../../../etc/passwd\n- Level: L3\n- Repo: .\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"), "--change-package", str(evil)],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        assert result.returncode == 2
        assert "unsafe characters" in result.stderr

    def test_gate_with_manual_approve_responses_yields_approve(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        cp = self._write_cp(target_repo, "CHG-SMOKE-002")
        # First run: generate manual prompt files.
        subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"), "--change-package", str(cp)],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        resp_dir = repo_root / "tmp" / "manual-responses" / "CHG-SMOKE-002"
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / "codex.md").write_text("Review.\n\nVERDICT: APPROVE\n", encoding="utf-8")
        (resp_dir / "gemini.md").write_text("Review.\n\nVERDICT: APPROVE\n", encoding="utf-8")
        result = subprocess.run(
            [python_exe, str(tools_dir / "run_gate.py"), "--change-package", str(cp)],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Final Decision: APPROVE" in result.stdout


class TestSmokeGuard:
    def test_guard_blocks_when_no_gate(
        self, python_exe: str, tools_dir: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        cps = target_repo / "tmp" / "change-packages"
        cps.mkdir(parents=True, exist_ok=True)
        (cps / "CHG-GUARD-001.md").write_text(
            "# CP\n- Change-ID: CHG-GUARD-001\n- Level: L3\n- Repo: .\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [python_exe, str(tools_dir / "l3_pre_push_guard.py"),
             "--repo", str(target_repo)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 1
        assert "missing gate result" in result.stdout


class TestSmokeFlowE2E:
    def test_start_task_flow_generates_all_artifacts(
        self, python_exe: str, tools_dir: Path, repo_root: Path, target_repo: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "start_task_flow.py"),
             "--repo", str(target_repo),
             "--task", "smoke e2e flow",
             "--level", "L2"],
            capture_output=True, text=True, cwd=str(repo_root), env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Task Flow" in result.stdout
        assert "Route:" in result.stdout
        assert "Context Bundle:" in result.stdout
        assert "Change Package:" in result.stdout


class TestSmokeBootstrap:
    def test_bootstrap_creates_runnable_project(
        self, python_exe: str, tmp_path: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        target = tmp_path / "bootstrapped"
        # Use the canonical bootstrap.py from the source tree (tests/conftest sets SCRIPTS_DIR).
        from pathlib import Path as _P
        bootstrap_script = _P(__file__).resolve().parents[1] / "bootstrap.py"
        if not bootstrap_script.exists():
            pytest.skip("bootstrap.py not present at canonical location")
        result = subprocess.run(
            [python_exe, str(bootstrap_script), "--target", str(target)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert (target / "tools" / "preflight_check.py").exists()
        assert (target / "tools" / "search_memory.py").exists()
        assert (target / "context-hub" / "00_HOME.md").exists()


class TestSmokeTelemetry:
    def test_telemetry_records_run(
        self, python_exe: str, tools_dir: Path, repo_root: Path, tmp_path: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        telemetry_file = tmp_path / "telemetry.jsonl"
        env = dict(subprocess_env)
        env["TRIAD_TELEMETRY_FILE"] = str(telemetry_file)
        subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "telemetry probe",
             "--level", "L1",
             "--repo", str(repo_root)],
            capture_output=True, text=True, env=env,
        )
        assert telemetry_file.exists()
        events = [json.loads(line) for line in telemetry_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(events) >= 1
        ev = events[-1]
        assert ev["tool"] == "route_task"
        assert ev["exit_code"] == 0
        assert "duration_ms" in ev
        assert "<redacted>" in ev["argv"]  # task value masked

    def test_telemetry_disabled_via_env(
        self, python_exe: str, tools_dir: Path, repo_root: Path, tmp_path: Path,
        subprocess_env: dict[str, str]
    ) -> None:
        telemetry_file = tmp_path / "telemetry_off.jsonl"
        env = dict(subprocess_env)
        env["TRIAD_TELEMETRY_FILE"] = str(telemetry_file)
        env["TRIAD_TELEMETRY_DISABLED"] = "1"
        subprocess.run(
            [python_exe, str(tools_dir / "route_task.py"),
             "--task", "should not log",
             "--level", "L1",
             "--repo", str(repo_root)],
            capture_output=True, text=True, env=env,
        )
        assert not telemetry_file.exists()
