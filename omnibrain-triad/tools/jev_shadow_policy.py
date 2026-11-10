"""Offline Jev decision adapter; typed suggestions, never authority or network."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

MODEL = "jev-1.14.0"
ROUTES = (
    "INSPECT_CODE",
    "REPRODUCE_CI",
    "VERIFY_SOURCE",
    "RECONCILE_ONTOLOGY",
    "HUMAN_REVIEW",
)
SENSITIVITY = "PUBLIC_SYNTHETIC_ONLY"
RISKS = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})


@dataclass(frozen=True)
class Decision:
    status: str
    suggested_route: str | None
    reason: str
    authoritative: bool = False
    can_act: bool = False

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def _prob(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def decide(context: Any, response: Any) -> Decision:
    """Gate synthetically supplied provider outputs; never authorize any action."""
    if not isinstance(context, dict):
        return Decision("HOLD_INVALID_CONTEXT", None, "context must be an object")
    if context.get("sensitivity") != SENSITIVITY:
        return Decision("HOLD_DATA_CLASS", None, "private context is forbidden")
    if context.get("provenance_ok") is not True:
        return Decision("HOLD_PROVENANCE", None, "deterministic evidence missing")
    risk = context.get("risk_level")
    if risk not in RISKS:
        return Decision("HOLD_INVALID_CONTEXT", None, "risk level is invalid")
    if not isinstance(response, dict) or response.get("model") != MODEL:
        return Decision("HOLD_INVALID_RESPONSE", None, "unsupported model")
    answers = response.get("answers")
    if not isinstance(answers, dict):
        return Decision("HOLD_INVALID_RESPONSE", None, "missing answers")
    route, fit = answers.get("route"), answers.get("fits_any_route")
    if not isinstance(route, dict) or not isinstance(fit, dict):
        return Decision("HOLD_INVALID_RESPONSE", None, "missing typed choices")
    if route.get("type") != "choice" or fit.get("type") != "noul":
        return Decision("HOLD_INVALID_RESPONSE", None, "incorrect answer types")
    choice, probabilities = route.get("choice"), route.get("probabilities")
    confidence, applicable = route.get("confidence"), fit.get("noul")
    if choice not in ROUTES or not isinstance(probabilities, dict):
        return Decision("HOLD_INVALID_RESPONSE", None, "unknown choice")
    if set(probabilities) != set(ROUTES):
        return Decision("HOLD_INVALID_RESPONSE", None, "choice set mismatch")
    if not all(_prob(p) for p in probabilities.values()):
        return Decision("HOLD_INVALID_RESPONSE", None, "invalid probabilities")
    if not _prob(confidence) or not _prob(applicable):
        return Decision("HOLD_INVALID_RESPONSE", None, "invalid confidence")
    if abs(sum(probabilities.values()) - 1) > 0.005:
        return Decision("HOLD_INVALID_RESPONSE", None, "mass not normalized")
    if max(probabilities, key=probabilities.get) != choice:
        return Decision("HOLD_INVALID_RESPONSE", None, "choice/probability conflict")
    if risk in ("HIGH", "CRITICAL"):
        return Decision("REVIEW_REQUIRED", choice, "high-stakes human gate")
    if applicable < 0.90:
        return Decision("DEFER", None, "does not match allowed choices")
    if probabilities[choice] < 0.90 or confidence < 0.85:
        return Decision("DEFER", choice, "semantic uncertainty")
    return Decision("SUGGEST_ONLY", choice, "non-authoritative shadow suggestion")
