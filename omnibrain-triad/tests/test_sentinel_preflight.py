"""Read-only program preflight must fail closed on incomplete/manipulated inputs."""

from __future__ import annotations

from copy import deepcopy

import pytest

from tools.sentinel_preflight import GATES, InvalidManifest, evaluate

URL = "https://github.com/asafetex/OmniBrain/actions/runs/42862492279"


def m(status="NOT_CHECKED"):
    return {"schema_version": "sentinel.preflight.v0.1", "checks": [
        {"gate_id": gate, "status": status,
         **({"evidence": {"url": URL, "head_sha": "a" * 40}} if status == "PASS_REPORTED" else {})}
        for gate in GATES
    ]}


def test_unknown_does_not_pass():
    report = evaluate(m())
    assert report["overall_status"] == "BLOCKED"
    assert len(report["open_gates"]) == 7
    assert not report["automatic_merge_allowed"]
    assert not report["automatic_release_allowed"]


def test_all_green_declarations_do_not_equal_verified():
    report = evaluate(m("PASS_REPORTED"))
    assert report["overall_status"] == "REVIEW_REQUIRED"
    assert len(report["open_gates"]) == 7
    assert report["checks"][0]["effective_status"] == "REVERIFY_EXTERNAL"
    assert report["checks"][2]["effective_status"] == "HOLD_HUMAN_REVIEW"
    assert not report["independent_remote_verification_performed"]


def test_explicit_failure_remains_blocker():
    report = m("PASS_REPORTED")
    report["checks"][3] = {"gate_id": GATES[3], "status": "FAIL"}
    assert evaluate(report)["overall_status"] == "BLOCKED"


@pytest.mark.parametrize("mutate", [
    lambda x: x["checks"].pop(),
    lambda x: x["checks"].append(deepcopy(x["checks"][0])),
    lambda x: x["checks"][0].update(gate_id="OTHER"),
    lambda x: x["checks"][0].update(status="APPROVED"),
    lambda x: x.update(schema_version="other"),
])
def test_invalid_contract_rejected(mutate):
    doc = m()
    mutate(doc)
    with pytest.raises(InvalidManifest):
        evaluate(doc)


@pytest.mark.parametrize("url", [
    "http://github.com/asafetex/OmniBrain/actions/runs/1",
    "https://github.com.evil.test/asafetex/OmniBrain/actions/runs/1",
    "https://github.com@evil.test/asafetex/OmniBrain/actions/runs/1",
    "https://github.com/asafetex/OmniBrain/actions/runs/1?token=x",
    "https://github.com/asafetex/OmniBrain/issues/1",
    "https://github.com/asafetex/OmniBrain/actions/runs/no",
])
def test_untrusted_url_rejected(url):
    doc = m("PASS_REPORTED")
    doc["checks"][0]["evidence"]["url"] = url
    with pytest.raises(InvalidManifest):
        evaluate(doc)


def test_nonpass_evidence_and_unpinned_shas_rejected():
    doc = m()
    doc["checks"][0]["evidence"] = {"url": URL, "head_sha": "a" * 40}
    with pytest.raises(InvalidManifest):
        evaluate(doc)
    doc = m("PASS_REPORTED")
    doc["checks"][0]["evidence"]["head_sha"] = "not-sha"
    with pytest.raises(InvalidManifest):
        evaluate(doc)
