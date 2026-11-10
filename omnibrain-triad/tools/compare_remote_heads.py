"""Compare G7 default HEAD snapshot to G1 local inventory (metadata only).

It never reads Git credentials, origin URLs, files, databases or personal data.
Matching a local folder name is NOT proof of repository identity. No Git calls.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

_SHA = re.compile(r"[a-f0-9]{40}\Z")


class InvalidBaseline(ValueError):
    """Remote baseline is incomplete or malformed."""


def evaluate(rows: list[dict[str, str]], inventory: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(inventory, dict) or not isinstance(inventory.get("repos"), list):
        raise InvalidBaseline("invalid G1 local inventory")
    local = defaultdict(list)
    for item in inventory["repos"]:
        if not isinstance(item, dict) or not isinstance(item.get("repo_directory_name"), str):
            raise InvalidBaseline("invalid local repository record")
        local[item["repo_directory_name"].casefold()].append(item)
    seen = set()
    results = []
    for row in rows:
        if not isinstance(row, dict):
            raise InvalidBaseline("invalid remote record")
        repository = row.get("repository", "")
        branch = row.get("default_branch", "")
        sha = row.get("head_sha", "")
        status = row.get("status")
        if not repository.startswith("asafetex/") or "/" in repository[len("asafetex/"):]:
            raise InvalidBaseline("unexpected remote repository")
        if repository in seen or not branch:
            raise InvalidBaseline("duplicate repo or missing default branch")
        seen.add(repository)
        if status not in ("PINNED", "EMPTY_REMOTE"):
            raise InvalidBaseline("unknown remote status")
        if (status == "PINNED" and not _SHA.fullmatch(sha)) or (status == "EMPTY_REMOTE" and sha):
            raise InvalidBaseline("invalid remote SHA/status")
        matches = local.get(repository.split("/", 1)[1].casefold(), [])
        if len(matches) > 1:
            finding = "AMBIGUOUS_LOCAL_CHECKOUT_NAME"
        elif not matches:
            finding = "LOCAL_CHECKOUT_UNAVAILABLE"
        elif status == "EMPTY_REMOTE":
            finding = "REMOTE_EMPTY_LOCAL_CHECKOUT_EXISTS"
        else:
            tracked = {x.get("ref"): x.get("sha") for x in (matches[0].get("ref_heads") or []) if isinstance(x, dict)}
            origin = tracked.get("refs/remotes/origin/" + branch)
            local_branch = tracked.get("refs/heads/" + branch)
            if origin == sha or local_branch == sha:
                finding = "SHA_MATCH_BY_DIRECTORY_NAME_ONLY"
            elif origin or local_branch:
                finding = "SHA_DIFF_REQUIRES_GIT_ANCESTRY"
            else:
                finding = "DEFAULT_REF_NOT_PRESENT_LOCALLY"
        results.append({"repository": repository, "remote_sha": sha or None,
                        "status": status, "finding": finding,
                        "identity_proven": False, "release_approved": False})
    counts = Counter(x["finding"] for x in results)
    return {"schema": "sentinel.remote_local.v0.1", "read_only": True,
            "identity_attested": False, "release_approved": False,
            "local_inventory_is_complete": False, "remote_repositories": len(results),
            "findings_count": dict(counts), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-csv", type=Path, required=True)
    parser.add_argument("--local-inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        with args.remote_csv.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        inventory = json.loads(args.local_inventory.read_text(encoding="utf-8"))
        report = evaluate(rows, inventory)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
