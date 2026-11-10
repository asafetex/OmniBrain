"""Fail-closed, read-only preflight: checks reported gates, never approves releases."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SCHEMA = "sentinel.preflight.v0.1"
GATES = (
    "GIT_REMOTE", "LOCAL_RECONCILIATION", "CANON_AUTHORITY",
    "CROSS_SYSTEM_E2E", "HUMAN_SCIENTIFIC_REVIEW",
    "RIGHTS_PRIVACY", "SECURITY_RELEASE",
)
HUMAN_GATES = frozenset({"CANON_AUTHORITY", "HUMAN_SCIENTIFIC_REVIEW", "RIGHTS_PRIVACY", "SECURITY_RELEASE"})
STATUSES = frozenset({"PASS_REPORTED", "FAIL", "HOLD", "NOT_CHECKED"})
_SHA = re.compile(r"[a-f0-9]{40}\Z")
_GH_PATH = re.compile(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(actions/runs/[0-9]+|pull/[0-9]+|commit/[a-f0-9]{40})/?\Z")


class InvalidManifest(ValueError):
    """Invalid or incomplete gate record."""


def _github_link(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return (parsed.scheme == "https" and parsed.netloc == "github.com"
            and not parsed.username and not parsed.password
            and not parsed.query and not parsed.fragment
            and bool(_GH_PATH.fullmatch(parsed.path)))


def evaluate(manifest: Any) -> dict[str, Any]:
    """Only internal manifest validation; no claim of independent GitHub attestation."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA:
        raise InvalidManifest("unsupported manifest schema")
    checks = manifest.get("checks")
    if not isinstance(checks, list) or len(checks) != len(GATES):
        raise InvalidManifest("exactly seven program gates required")
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for record in checks:
        if not isinstance(record, dict):
            raise InvalidManifest("gate must be an object")
        gate, status = record.get("gate_id"), record.get("status")
        if gate not in GATES or gate in seen or status not in STATUSES:
            raise InvalidManifest("unknown, missing or duplicate gate/status")
        seen.add(gate)
        evidence = record.get("evidence")
        if status == "PASS_REPORTED":
            if not isinstance(evidence, dict):
                raise InvalidManifest("pass needs an evidence object")
            url, sha = evidence.get("url"), evidence.get("head_sha")
            if not _github_link(url) or not isinstance(sha, str) or not _SHA.fullmatch(sha):
                raise InvalidManifest("pass needs a pinned GitHub URL and SHA")
            evidence_status = "DECLARED_NOT_INDEPENDENTLY_VERIFIED"
        else:
            if evidence is not None:
                raise InvalidManifest("non-pass must omit evidence")
            evidence_status = "NO_PASS_EVIDENCE"
        if gate in HUMAN_GATES and status == "PASS_REPORTED":
            effective = "HOLD_HUMAN_REVIEW"
        elif status == "PASS_REPORTED":
            effective = "REVERIFY_EXTERNAL"
        else:
            effective = status
        results.append({"gate_id": gate, "reported_status": status,
                        "effective_status": effective, "evidence_status": evidence_status})
    if seen != set(GATES):
        raise InvalidManifest("missing gate")
    return {
        "schema_version": SCHEMA,
        "read_only": True,
        "automatic_merge_allowed": False,
        "automatic_release_allowed": False,
        "independent_remote_verification_performed": False,
        "scientific_approval_granted": False,
        "overall_status": "REVIEW_REQUIRED" if all(x["reported_status"] == "PASS_REPORTED" for x in results) else "BLOCKED",
        "open_gates": [x["gate_id"] for x in results],
        "checks": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["overall_status"] == "REVIEW_REQUIRED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
