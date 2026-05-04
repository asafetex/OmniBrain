"""3-tier confidence cascade for Gate decisions.

Reduces LLM calls by short-circuiting on rule-based and heuristic tiers.

Tier 1 (rule-based, deterministic, ~0ms):
  - Diff is empty -> AUTO_REJECT (nothing to review)
  - Diff is comments-only -> AUTO_APPROVE (with confidence "high")
  - Diff is whitespace/formatting only -> AUTO_APPROVE
  - Diff contains forbidden patterns (eval, exec, password=, secret=, hardcoded URL with token)
    -> AUTO_REJECT for L3 with security concern

Tier 2 (heuristic, TF-IDF similarity to historical WINs/REJECTs, ~50ms):
  - If diff highly similar to past WIN -> SUGGEST APPROVE (verdict still requires LLM for L3)
  - If diff highly similar to past REJECT -> SUGGEST REJECT
  - Otherwise -> ESCALATE to LLM

Tier 3 (LLM auditors, ~seconds):
  - Existing run_gate flow (codex, gemini)

Output: dict with `tier`, `decision`, `confidence`, `reason`, `escalate_to_llm` (bool).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from search_memory import build_tfidf, cosine, tokenize  # noqa: F401

# Patterns that auto-REJECT for L3 security concerns
SECURITY_REJECT_PATTERNS = [
    re.compile(r"\beval\s*\(", re.IGNORECASE),
    re.compile(r"\bexec\s*\(", re.IGNORECASE),
    re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"secret\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"shell\s*=\s*True"),
    re.compile(r"\bos\.system\s*\("),
    re.compile(r"sudo\s+rm\s+-rf"),
]

DIFF_LINE_RE = re.compile(r"^[+-]")
DIFF_HEADER_RE = re.compile(r"^(diff --git|index |---|\+\+\+|@@ )")
COMMENT_LINE_RE = re.compile(r"^[+-]\s*(#|//|/\*|\*|<!--)")
WHITESPACE_LINE_RE = re.compile(r"^[+-]\s*$")


@dataclass
class CascadeResult:
    tier: int
    decision: str  # "AUTO_APPROVE", "AUTO_REJECT", "SUGGEST_APPROVE", "SUGGEST_REJECT", "ESCALATE"
    confidence: str  # "high", "medium", "low"
    reason: str
    escalate_to_llm: bool
    matched_pattern: str | None = None
    similar_memory: str | None = None
    similarity_score: float | None = None

    def to_dict(self) -> dict:
        return {
            "tier": self.tier,
            "decision": self.decision,
            "confidence": self.confidence,
            "reason": self.reason,
            "escalate_to_llm": self.escalate_to_llm,
            "matched_pattern": self.matched_pattern,
            "similar_memory": self.similar_memory,
            "similarity_score": self.similarity_score,
        }


def extract_diff_lines(change_package: str) -> list[str]:
    """Pull only +/- diff lines from a Change Package markdown."""
    lines = []
    in_diff = False
    for line in change_package.splitlines():
        if line.strip().startswith("```diff"):
            in_diff = True
            continue
        if in_diff and line.strip() == "```":
            in_diff = False
            continue
        if in_diff:
            lines.append(line)
    if not lines:
        # Fallback: pull anything with +/- at start
        lines = [ln for ln in change_package.splitlines() if DIFF_LINE_RE.match(ln) and not DIFF_HEADER_RE.match(ln)]
    return [ln for ln in lines if DIFF_LINE_RE.match(ln)]


def is_diff_empty(diff_lines: list[str]) -> bool:
    if not diff_lines:
        return True
    real_changes = [ln for ln in diff_lines if not WHITESPACE_LINE_RE.match(ln)]
    return not real_changes


def is_comments_only(diff_lines: list[str]) -> bool:
    if not diff_lines:
        return False
    code_lines = [ln for ln in diff_lines if not COMMENT_LINE_RE.match(ln) and not WHITESPACE_LINE_RE.match(ln)]
    return len(code_lines) == 0


def is_whitespace_only(diff_lines: list[str]) -> bool:
    if not diff_lines:
        return False
    real = [ln for ln in diff_lines if not WHITESPACE_LINE_RE.match(ln)]
    if not real:
        return True
    # Compare lines stripped: if + and - have same stripped content -> formatting only
    plus = [ln[1:].strip() for ln in real if ln.startswith("+")]
    minus = [ln[1:].strip() for ln in real if ln.startswith("-")]
    if not plus or not minus:
        return False
    return sorted(plus) == sorted(minus)


def find_security_violations(change_package: str) -> list[tuple[str, str]]:
    """Return list of (pattern_name, matched_text) for forbidden patterns."""
    violations = []
    for pattern in SECURITY_REJECT_PATTERNS:
        m = pattern.search(change_package)
        if m:
            violations.append((pattern.pattern, m.group(0)))
    return violations


def tier1_evaluate(change_package: str, level: str) -> CascadeResult | None:
    """Apply rule-based tier. Return result if decided, None to escalate."""
    diff_lines = extract_diff_lines(change_package)

    if is_diff_empty(diff_lines):
        return CascadeResult(
            tier=1,
            decision="AUTO_REJECT",
            confidence="high",
            reason="Empty diff: nothing to review.",
            escalate_to_llm=False,
        )

    # Security check applies to L2 and L3
    if level in {"L2", "L3"}:
        violations = find_security_violations(change_package)
        if violations:
            pattern, matched = violations[0]
            return CascadeResult(
                tier=1,
                decision="AUTO_REJECT",
                confidence="high",
                reason=f"Security pattern detected: {pattern} matched '{matched[:60]}'",
                escalate_to_llm=False,
                matched_pattern=pattern,
            )

    if is_whitespace_only(diff_lines):
        return CascadeResult(
            tier=1,
            decision="AUTO_APPROVE",
            confidence="high",
            reason="Whitespace/formatting only.",
            escalate_to_llm=False,
        )

    if is_comments_only(diff_lines):
        # L3 still escalates (comments could obscure intent), L1/L2 auto-approve
        if level == "L3":
            return CascadeResult(
                tier=1,
                decision="ESCALATE",
                confidence="low",
                reason="Comments only but L3 requires Gate verification.",
                escalate_to_llm=True,
            )
        return CascadeResult(
            tier=1,
            decision="AUTO_APPROVE",
            confidence="high",
            reason="Comment-only changes.",
            escalate_to_llm=False,
        )

    return None


def tier2_evaluate(
    change_package: str, level: str, memory_corpus: list[tuple[str, str]],
    approve_threshold: float = 0.65, reject_threshold: float = 0.65,
) -> CascadeResult | None:
    """Heuristic tier: TF-IDF similarity to historical WINs/REJECTs.

    memory_corpus: list of (verdict, content) pairs. verdict in {"APPROVE", "REJECT"}.
    """
    if not memory_corpus:
        return None

    # Build corpus including the query (change_package)
    docs = [(Path(f"mem_{i}"), text) for i, (_, text) in enumerate(memory_corpus)]
    docs.append((Path("query"), change_package))
    vectors, _ = build_tfidf(docs)
    query_vec = vectors[-1]

    best_score_approve = 0.0
    best_score_reject = 0.0
    best_match_approve_idx = -1
    best_match_reject_idx = -1
    for i, (verdict, _) in enumerate(memory_corpus):
        score = cosine(query_vec, vectors[i])
        if verdict == "APPROVE" and score > best_score_approve:
            best_score_approve = score
            best_match_approve_idx = i
        elif verdict == "REJECT" and score > best_score_reject:
            best_score_reject = score
            best_match_reject_idx = i

    if best_score_reject >= reject_threshold and best_score_reject > best_score_approve:
        return CascadeResult(
            tier=2,
            decision="SUGGEST_REJECT",
            confidence="medium",
            reason=f"Highly similar to past REJECT (score {best_score_reject:.3f}).",
            escalate_to_llm=(level == "L3"),
            similar_memory=f"reject#{best_match_reject_idx}",
            similarity_score=best_score_reject,
        )

    if best_score_approve >= approve_threshold and best_score_approve > best_score_reject:
        return CascadeResult(
            tier=2,
            decision="SUGGEST_APPROVE",
            confidence="medium",
            reason=f"Highly similar to past APPROVE (score {best_score_approve:.3f}).",
            escalate_to_llm=(level == "L3"),
            similar_memory=f"approve#{best_match_approve_idx}",
            similarity_score=best_score_approve,
        )

    return None


def evaluate_cascade(
    change_package: str, level: str, memory_corpus: list[tuple[str, str]] | None = None,
) -> CascadeResult:
    """Main entry point: run tier1, then tier2, then declare ESCALATE."""
    result = tier1_evaluate(change_package, level)
    if result is not None:
        return result

    if memory_corpus:
        result = tier2_evaluate(change_package, level, memory_corpus)
        if result is not None:
            return result

    return CascadeResult(
        tier=3,
        decision="ESCALATE",
        confidence="low",
        reason="No deterministic rule or heuristic match; LLM verdict required.",
        escalate_to_llm=True,
    )
