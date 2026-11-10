"""Synthetic decision contract tests: not a benchmark of Jev accuracy."""

from __future__ import annotations

from copy import deepcopy

import pytest

from tools.jev_shadow_policy import MODEL, ROUTES, decide


def context(**changes):
    data = {"sensitivity": "PUBLIC_SYNTHETIC_ONLY", "provenance_ok": True,
            "risk_level": "LOW"}
    data.update(changes)
    return data


def provider():
    return {"model": MODEL, "answers": {
        "route": {"type": "choice", "choice": "REPRODUCE_CI",
                  "confidence": 0.98, "probabilities": {
                      route: (0.96 if route == "REPRODUCE_CI" else 0.01)
                      for route in ROUTES}},
        "fits_any_route": {"type": "noul", "noul": 0.99},
    }}


def test_shadow_cannot_act():
    result = decide(context(), provider())
    assert result.status == "SUGGEST_ONLY"
    assert result.suggested_route == "REPRODUCE_CI"
    assert not result.can_act
    assert not result.authoritative


@pytest.mark.parametrize("risk", ["HIGH", "CRITICAL"])
def test_high_risk_must_be_reviewed(risk):
    result = decide(context(risk_level=risk), provider())
    assert result.status == "REVIEW_REQUIRED"
    assert not result.can_act


def test_private_and_unverified_blocked():
    assert decide(context(sensitivity="PRIVATE"), provider()).status == "HOLD_DATA_CLASS"
    assert decide(context(provenance_ok=False), provider()).status == "HOLD_PROVENANCE"


@pytest.mark.parametrize("field", ["probabilities", "confidence", "choice"])
def test_mutated_provider_does_not_act(field):
    result = deepcopy(provider())
    result["answers"]["route"][field] = None
    assert decide(context(), result).status == "HOLD_INVALID_RESPONSE"


def test_unpinned_and_missing_response_blocked():
    data = provider()
    data["model"] = "jev-latest"
    assert decide(context(), data).status == "HOLD_INVALID_RESPONSE"
    assert decide(context(), None).status == "HOLD_INVALID_RESPONSE"


def test_invalid_probabilities_hold():
    for value in (float("nan"), float("inf"), True, -1, 2):
        data = provider()
        data["answers"]["route"]["confidence"] = value
        assert decide(context(), data).status == "HOLD_INVALID_RESPONSE"


def test_ood_and_weak_fit_defer():
    data = provider()
    data["answers"]["fits_any_route"]["noul"] = 0.12
    assert decide(context(), data).status == "DEFER"
    data = provider()
    data["answers"]["route"]["probabilities"]["HUMAN_REVIEW"] = 0.4
    assert decide(context(), data).status == "HOLD_INVALID_RESPONSE"
