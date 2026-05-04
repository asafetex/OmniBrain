#!/usr/bin/env python3
"""TRIAD Oracle: query historical decisions for similar Change Packages.

Given a Change Package or free-text question, retrieves top-K most similar
historical memories (PLAN/REVIEW/DECISION/WIN/LESSON), groups by verdict,
and provides an evidence-backed recommendation.

Output:
  - top_similar: ranked list of memories with score
  - aggregation: counts by type (APPROVE/REJECT/UNKNOWN, WIN/LESSON)
  - recommendation: data-backed recommendation with confidence band
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from search_memory import build_tfidf, collect_memories, cosine
from telemetry import record_run, tool_name_from_file
from utils import print_utf8

VERDICT_RE = re.compile(r"VERDICT\s*:\s*(APPROVE|REJECT)", re.IGNORECASE)
TYPE_RE = re.compile(r"^- Type:\s*(\w+)\s*$", re.MULTILINE)
TOPIC_RE = re.compile(r"^- Topic:\s*(.+)$", re.MULTILINE)


def parse_memory_metadata(path: Path) -> dict:
    """Extract type, verdict (if any), topic, content excerpt."""
    text = path.read_text(encoding="utf-8", errors="replace")
    type_match = TYPE_RE.search(text)
    verdict_match = VERDICT_RE.search(text)
    topic_match = TOPIC_RE.search(text)
    return {
        "path": str(path),
        "name": path.name,
        "type": type_match.group(1).upper() if type_match else "UNKNOWN",
        "verdict": verdict_match.group(1).upper() if verdict_match else None,
        "topic": topic_match.group(1).strip() if topic_match else "",
        "text": text,
    }


def build_recommendation(scored: list[tuple[float, dict]]) -> dict:
    """From top similar memories, derive a recommendation."""
    if not scored:
        return {
            "verdict_hint": "INSUFFICIENT_DATA",
            "confidence": "none",
            "rationale": "No similar memories found.",
            "approve_count": 0,
            "reject_count": 0,
            "win_count": 0,
            "lesson_count": 0,
        }

    type_counter: Counter[str] = Counter()
    verdict_counter: Counter[str] = Counter()
    weight_approve = 0.0
    weight_reject = 0.0
    for score, meta in scored:
        type_counter[meta["type"]] += 1
        if meta["verdict"]:
            verdict_counter[meta["verdict"]] += 1
            if meta["verdict"] == "APPROVE":
                weight_approve += score
            elif meta["verdict"] == "REJECT":
                weight_reject += score

    approve = verdict_counter.get("APPROVE", 0)
    reject = verdict_counter.get("REJECT", 0)
    total_with_verdict = approve + reject

    if total_with_verdict == 0:
        verdict_hint = "NO_HISTORICAL_VERDICT"
        confidence = "low"
        rationale = (
            f"Found {len(scored)} similar memories but none carry an explicit VERDICT marker. "
            f"Type breakdown: {dict(type_counter)}."
        )
    elif weight_approve > 1.5 * weight_reject:
        verdict_hint = "LIKELY_APPROVE"
        confidence = "high" if approve >= 3 else "medium"
        rationale = (
            f"Past similar work was approved {approve} time(s) vs rejected {reject} time(s) "
            f"(weighted: approve={weight_approve:.2f}, reject={weight_reject:.2f})."
        )
    elif weight_reject > 1.5 * weight_approve:
        verdict_hint = "LIKELY_REJECT"
        confidence = "high" if reject >= 3 else "medium"
        rationale = (
            f"Past similar work was rejected {reject} time(s) vs approved {approve} time(s) "
            f"(weighted: approve={weight_approve:.2f}, reject={weight_reject:.2f}). "
            f"Inspect the rejection reasons before proceeding."
        )
    else:
        verdict_hint = "MIXED_HISTORY"
        confidence = "low"
        rationale = (
            f"History is mixed: {approve} APPROVE, {reject} REJECT. "
            f"Manual review strongly recommended."
        )

    return {
        "verdict_hint": verdict_hint,
        "confidence": confidence,
        "rationale": rationale,
        "approve_count": approve,
        "reject_count": reject,
        "win_count": type_counter.get("WIN", 0),
        "lesson_count": type_counter.get("LESSON", 0),
        "type_breakdown": dict(type_counter),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="TRIAD Oracle: query historical decisions.")
    parser.add_argument("--change-package", help="Path to Change Package markdown.")
    parser.add_argument("--query", help="Free-text query (alternative to --change-package).")
    parser.add_argument("--top-k", type=int, default=10, help="Top-K memories to consider.")
    parser.add_argument("--min-score", type=float, default=0.05, help="Cosine threshold.")
    parser.add_argument("--repo-root", default="", help="TRIAD repo root override.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if not args.change_package and not args.query:
        print("Error: provide --change-package or --query.", file=sys.stderr)
        return 2

    repo_root = Path(args.repo_root).resolve() if args.repo_root else _tools_dir.parent

    if args.change_package:
        cp_path = Path(args.change_package).resolve()
        if not cp_path.exists():
            print(f"Error: Change Package not found: {cp_path}", file=sys.stderr)
            return 2
        query_text = cp_path.read_text(encoding="utf-8", errors="replace")
        query_label = str(cp_path)
    else:
        query_text = args.query
        query_label = args.query

    if not query_text.strip():
        print("Error: query is empty.", file=sys.stderr)
        return 2

    memories = collect_memories(repo_root)
    if not memories:
        if args.format == "json":
            print_utf8(json.dumps({"query": query_label, "results": []}, indent=2))
        else:
            print_utf8(f"No memories found under {repo_root / 'context-hub'}.")
        return 0

    documents = [(p, p.read_text(encoding="utf-8", errors="replace")) for p in memories]
    documents.append((Path("query"), query_text))
    vectors, _ = build_tfidf(documents)
    query_vec = vectors[-1]

    scored = []
    for (path, _), vec in zip(documents[:-1], vectors[:-1], strict=False):
        score = cosine(query_vec, vec)
        if score >= args.min_score:
            meta = parse_memory_metadata(path)
            scored.append((score, meta))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[: args.top_k]

    recommendation = build_recommendation(top)

    if args.format == "json":
        print_utf8(json.dumps({
            "query": query_label,
            "total_indexed": len(memories),
            "top_similar": [
                {
                    "score": round(score, 4),
                    "name": meta["name"],
                    "type": meta["type"],
                    "verdict": meta["verdict"],
                    "topic": meta["topic"],
                    "path": meta["path"],
                }
                for score, meta in top
            ],
            "recommendation": recommendation,
        }, ensure_ascii=False, indent=2))
        return 0

    print_utf8("# TRIAD Oracle Report")
    print_utf8("")
    print_utf8(f"- Query: {query_label[:100]}")
    print_utf8(f"- Indexed memories: {len(memories)}")
    print_utf8(f"- Top similar (>= {args.min_score}): {len(top)}")
    print_utf8("")
    print_utf8("## Recommendation")
    print_utf8(f"- Verdict hint: **{recommendation['verdict_hint']}**")
    print_utf8(f"- Confidence: {recommendation['confidence']}")
    print_utf8(f"- Rationale: {recommendation['rationale']}")
    print_utf8(f"- WINs in history: {recommendation['win_count']}")
    print_utf8(f"- LESSONs in history: {recommendation['lesson_count']}")
    print_utf8("")
    print_utf8("## Top Similar Memories")
    if not top:
        print_utf8("- (none)")
    for rank, (score, meta) in enumerate(top, start=1):
        verdict = meta["verdict"] or "-"
        print_utf8(f"{rank}. [{score:.3f}] {meta['type']:<8} verdict={verdict:<8} {meta['name']}")
    return 0


if __name__ == "__main__":
    with record_run(tool_name_from_file(__file__)):
        raise SystemExit(main())
