"""Tests for tools/utils.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import tools.utils as utils


class TestLoadJson:
    def test_load_json_success(self, tmp_path: Path) -> None:
        p = tmp_path / "test.json"
        p.write_text(json.dumps({"key": "value"}), encoding="utf-8")
        result = utils.load_json(p)
        assert result == {"key": "value"}

    def test_load_json_missing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "missing.json"
        with pytest.raises(FileNotFoundError):
            utils.load_json(p)


class TestLoadConfig:
    def test_load_config_with_example(self, tools_dir: Path) -> None:
        result = utils.load_config(tools_dir)
        assert "auditors" in result
        assert "defaults" in result

    def test_load_config_with_local(self, tools_dir: Path, tmp_path: Path) -> None:
        local_cfg = tools_dir / "config.json"
        local_cfg.write_text(json.dumps({"version": "1.0", "custom": True}), encoding="utf-8")
        result = utils.load_config(tools_dir)
        assert result.get("custom") is True


class TestParseCsv:
    def test_parse_csv_normal(self) -> None:
        result = utils.parse_csv("a, b, c")
        assert result == ["a", "b", "c"]

    def test_parse_csv_empty(self) -> None:
        result = utils.parse_csv("")
        assert result == []

    def test_parse_csv_with_whitespace(self) -> None:
        result = utils.parse_csv("  alpha  ,  beta  ")
        assert result == ["alpha", "beta"]


class TestMarkdownBullets:
    def test_markdown_bullets_with_items(self) -> None:
        result = utils.markdown_bullets(["a", "b"], "empty")
        assert result == "- a\n- b"

    def test_markdown_bullets_empty(self) -> None:
        result = utils.markdown_bullets([], "nothing")
        assert result == "- nothing"


class TestRunGit:
    def test_run_git_ok(self, git_repo: Path) -> None:
        ok, result = utils.run_git(git_repo, ["status"])
        assert ok is True
        assert "On branch" in result or "HEAD" in result

    def test_run_git_failure(self, git_repo: Path) -> None:
        ok, result = utils.run_git(git_repo, ["nonexistent-command"])
        assert ok is False
        assert result != ""


class TestRunGitStrict:
    def test_run_git_strict_ok(self, git_repo: Path) -> None:
        result = utils.run_git_strict(git_repo, ["rev-parse", "--abbrev-ref", "HEAD"])
        assert result == "master" or result == "main"

    def test_run_git_strict_failure(self, git_repo: Path) -> None:
        with pytest.raises(RuntimeError):
            utils.run_git_strict(git_repo, ["bad-command"])


class TestCommandExists:
    def test_command_exists_python(self) -> None:
        assert utils.command_exists("python") is True

    def test_command_exists_empty(self) -> None:
        assert utils.command_exists("") is False

    def test_command_exists_nonexistent(self) -> None:
        assert utils.command_exists("nonexistent_command_xyz123") is False

    def test_command_exists_path_absolute(self, tmp_path: Path) -> None:
        p = tmp_path / "test.exe"
        p.touch()
        assert utils.command_exists(str(p)) is True


class TestGetRepoRoot:
    def test_get_repo_root(self, tools_dir: Path, repo_root: Path) -> None:
        result = utils.get_repo_root(tools_dir)
        assert result == repo_root


class TestResolveConfigPath:
    def test_resolve_config_absolute(self, tmp_path: Path, repo_root: Path) -> None:
        abs_path = tmp_path / "test.json"
        result = utils.resolve_config_path(abs_path, repo_root)
        assert result == abs_path

    def test_resolve_config_relative(self, tmp_path: Path, repo_root: Path) -> None:
        rel_path = Path("configs/test.json")
        result = utils.resolve_config_path(rel_path, repo_root)
        assert result == repo_root / rel_path


class TestFindSavedPath:
    def test_find_saved_path_simple(self) -> None:
        stdout = "Some output\nSaved: /path/to/file.txt\nMore output"
        result = utils.find_saved_path(stdout)
        assert result == "/path/to/file.txt"

    def test_find_saved_path_no_match(self) -> None:
        result = utils.find_saved_path("No saved path here")
        assert result == ""


class TestDetectIntent:
    def test_detect_intent_explicit(self) -> None:
        intents = {
            "spark": {"keywords": ["sql"], "graph_nodes": ["sql.md"]},
        }
        name, payload = utils.detect_intent("do something", intents, "spark")
        assert name == "spark"
        assert payload == {"keywords": ["sql"], "graph_nodes": ["sql.md"]}

    def test_detect_intent_explicit_not_found(self) -> None:
        intents = {"spark": {"keywords": [], "graph_nodes": []}}
        with pytest.raises(ValueError, match="Intent not found"):
            utils.detect_intent("task", intents, "missing")

    def test_detect_intent_auto(self) -> None:
        intents = {
            "generic": {"keywords": [], "graph_nodes": []},
            "spark": {"keywords": ["join", "spark"], "graph_nodes": ["spark.md"]},
        }
        name, payload = utils.detect_intent("I need a spark join", intents, "")
        assert name == "spark"
        assert "join" in payload["keywords"]

    def test_detect_intent_fallback_generic(self) -> None:
        intents = {"generic": {"keywords": [], "graph_nodes": []}}
        name, _ = utils.detect_intent("random task xyz", intents, "")
        assert name == "generic"
