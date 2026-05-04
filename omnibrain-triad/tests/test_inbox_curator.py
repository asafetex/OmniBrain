"""Tests for tools/inbox_curator.py."""

from __future__ import annotations

import datetime as dt
import subprocess
from pathlib import Path


class TestInboxCurator:
    def _seed(self, repo_root: Path) -> Path:
        inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
        inbox.mkdir(parents=True, exist_ok=True)
        # OLD plan (stale)
        old_ts = (dt.datetime.now() - dt.timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S")
        (inbox / "MEM__PLAN__alpha__old-task__20250301-1000.md").write_text(
            f"# MEM\n## Metadata\n- Type: PLAN\n- Project: alpha\n- Topic: old-task\n- Timestamp: {old_ts}\n## Content\nPlan stuff",
            encoding="utf-8",
        )
        # RECENT review (not stale)
        recent_ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        (inbox / "MEM__REVIEW__alpha__recent__20260504-1000.md").write_text(
            f"# MEM\n## Metadata\n- Type: REVIEW\n- Project: alpha\n- Topic: recent\n- Timestamp: {recent_ts}\n## Content\nReview stuff",
            encoding="utf-8",
        )
        # WIN (promotion candidate)
        (inbox / "MEM__WIN__beta__big-win__20260504-1100.md").write_text(
            "# WIN\n## Content\nWinning solution to data problem.",
            encoding="utf-8",
        )
        # DUPLICATES
        dup_text = "# MEM\n## Content\nspark sql join broadcast hint reduces shuffle."
        (inbox / "MEM__LESSON__gamma__dup-a__20260504-1200.md").write_text(dup_text, encoding="utf-8")
        (inbox / "MEM__LESSON__gamma__dup-b__20260504-1300.md").write_text(dup_text, encoding="utf-8")
        return inbox

    def test_help_works(self, python_exe: str, tools_dir: Path, subprocess_env: dict[str, str]) -> None:
        result = subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"), "--help"],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "--max-age-days" in result.stdout

    def test_empty_inbox(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        # repo_root has context-hub/ already created in fixture
        result = subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"), "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        # INBOX may not exist (returns 1) or be empty (returns 0). Both acceptable.
        assert result.returncode in (0, 1)

    def test_detects_stale(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        self._seed(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"),
             "--max-age-days", "30",
             "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "old-task" in result.stdout
        assert "recent" not in result.stdout.split("Stale")[1].split("Duplicates")[0]

    def test_detects_duplicates(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        self._seed(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"),
             "--dup-threshold", "0.7",
             "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "dup-a" in result.stdout or "dup-b" in result.stdout

    def test_detects_promote_candidates(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        self._seed(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"), "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "big-win" in result.stdout

    def test_dry_run_does_not_move(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        inbox = self._seed(repo_root)
        before = sorted(p.name for p in inbox.glob("MEM__*.md"))
        subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"),
             "--max-age-days", "30",
             "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        after = sorted(p.name for p in inbox.glob("MEM__*.md"))
        assert before == after

    def test_apply_archives_stale(self, python_exe: str, tools_dir: Path, repo_root: Path, subprocess_env: dict[str, str]) -> None:
        inbox = self._seed(repo_root)
        result = subprocess.run(
            [python_exe, str(tools_dir / "inbox_curator.py"),
             "--max-age-days", "30",
             "--apply",
             "--repo-root", str(repo_root)],
            capture_output=True, text=True, env=subprocess_env,
        )
        assert result.returncode == 0
        assert "Archived" in result.stdout
        assert not (inbox / "MEM__PLAN__alpha__old-task__20250301-1000.md").exists()
        archive = repo_root / "context-hub" / "05_INBOX" / "_archive"
        assert (archive / "MEM__PLAN__alpha__old-task__20250301-1000.md").exists()
