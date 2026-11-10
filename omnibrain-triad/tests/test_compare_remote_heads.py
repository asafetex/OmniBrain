"""Only structural, name-based comparison; no real local repo attached."""

from __future__ import annotations

from copy import deepcopy

import pytest

from tools.compare_remote_heads import InvalidBaseline, evaluate


def row(name="OmniBrain", status="PINNED", sha="a" * 40):
    return {"repository": "asafetex/" + name, "default_branch": "main",
            "head_sha": sha if status == "PINNED" else "", "status": status}


def local(ref="a" * 40):
    return {"repos": [{"repo_directory_name": "OmniBrain", "checkout_path": "SECRET",
                       "ref_heads": [{"ref": "refs/remotes/origin/main", "sha": ref}]}]}


def test_sha_equal_is_not_attested_identity():
    result = evaluate([row()], local())
    assert result["results"][0]["finding"] == "SHA_MATCH_BY_DIRECTORY_NAME_ONLY"
    assert not result["identity_attested"]
    assert "SECRET" not in str(result)


def test_changed_head_cannot_guess_ahead_or_behind():
    result = evaluate([row()], local("b" * 40))
    assert result["results"][0]["finding"] == "SHA_DIFF_REQUIRES_GIT_ANCESTRY"


def test_empty_remote_does_not_imply_missing_local_work():
    result = evaluate([row(status="EMPTY_REMOTE")], local())
    assert result["results"][0]["finding"] == "REMOTE_EMPTY_LOCAL_CHECKOUT_EXISTS"


def test_unavailable_checkout_is_unknown():
    result = evaluate([row()], {"repos": []})
    assert result["results"][0]["finding"] == "LOCAL_CHECKOUT_UNAVAILABLE"


def test_ambiguous_local_directory_names_are_not_resolved_automatically():
    dataset = local()
    dataset["repos"].append(deepcopy(dataset["repos"][0]))
    assert evaluate([row()], dataset)["results"][0]["finding"] == "AMBIGUOUS_LOCAL_CHECKOUT_NAME"


def test_missing_default_ref_needs_investigation():
    dataset = local()
    dataset["repos"][0]["ref_heads"] = []
    assert evaluate([row()], dataset)["results"][0]["finding"] == "DEFAULT_REF_NOT_PRESENT_LOCALLY"


@pytest.mark.parametrize("rows", [
    [row(), row()],
    [row(sha="bad")],
    [row(status="UNKNOWN")],
    [row(name="other/forged")],
])
def test_invalid_remote_baseline_fails_closed(rows):
    with pytest.raises(InvalidBaseline):
        evaluate(rows, local())
