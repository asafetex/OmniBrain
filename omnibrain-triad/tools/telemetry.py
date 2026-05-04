"""Lightweight telemetry for TRIAD tools (stdlib only, JSONL).

Emits one JSON event per tool invocation to `tmp/telemetry/events.jsonl`:
- timestamp (UTC ISO)
- tool name
- argv (sanitized: drops --task/--goal/--text values)
- duration_ms
- exit_code
- platform
- python_version

Usage:
    from telemetry import record_run

    def main() -> int:
        with record_run("tool_name") as ev:
            ...
            ev["custom_field"] = "..."
            return 0
"""

from __future__ import annotations

import contextlib
import datetime as dt
import json
import os
import platform
import re
import sys
import time
from pathlib import Path

REDACT_FLAGS = {"--task", "--goal", "--text", "--query", "--context", "--risks"}


def _sanitize_argv(argv: list[str]) -> list[str]:
    """Mask values of sensitive flags to keep telemetry free of free-text content."""
    out: list[str] = []
    skip_next = False
    for token in argv:
        if skip_next:
            out.append("<redacted>")
            skip_next = False
            continue
        out.append(token)
        for flag in REDACT_FLAGS:
            if token == flag or token.startswith(f"{flag}="):
                if "=" in token:
                    name, _ = token.split("=", 1)
                    out[-1] = f"{name}=<redacted>"
                else:
                    skip_next = True
                break
    return out


def telemetry_path(start: Path | None = None) -> Path:
    """Resolve where to write telemetry events. Falls back to repo_root/tmp/telemetry."""
    override = os.environ.get("TRIAD_TELEMETRY_FILE")
    if override:
        return Path(override).expanduser().resolve()
    base = start if start is not None else Path(__file__).resolve().parent.parent
    return base / "tmp" / "telemetry" / "events.jsonl"


def _emit(event: dict) -> None:
    if os.environ.get("TRIAD_TELEMETRY_DISABLED") == "1":
        return
    target = telemetry_path()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        # Telemetry must never break the tool.
        pass


@contextlib.contextmanager
def record_run(tool_name: str):
    """Context manager that records start, end, exit code, duration."""
    started_at = time.monotonic()
    event = {
        "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool": tool_name,
        "argv": _sanitize_argv(list(sys.argv[1:])),
        "platform": platform.system(),
        "python": platform.python_version(),
    }
    exit_code: int | None = None
    try:
        yield event
        exit_code = 0
    except SystemExit as exc:
        code = exc.code
        exit_code = int(code) if isinstance(code, int) else (1 if code else 0)
        raise
    except BaseException:
        exit_code = 1
        raise
    finally:
        event["duration_ms"] = int((time.monotonic() - started_at) * 1000)
        event["exit_code"] = exit_code if exit_code is not None else 0
        _emit(event)


_TOOL_PATTERN = re.compile(r"\.py$")


def tool_name_from_file(file_path: str) -> str:
    """Derive a clean tool name from __file__."""
    stem = Path(file_path).stem
    return _TOOL_PATTERN.sub("", stem)
