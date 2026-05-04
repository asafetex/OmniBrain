#!/usr/bin/env python3
"""Search TRIAD memories using TF-IDF similarity (stdlib only).

Indexes:
- context-hub/05_INBOX/byterover-imports/MEM__*.md
- context-hub/02_GRAPH/**/MEM__*.md (promoted)

Returns top-K memories ranked by cosine similarity to the query.
No external dependencies (no FAISS, no transformers): pure Python math.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from utils import print_utf8

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+", re.UNICODE)
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "at", "for", "is",
    "are", "was", "were", "be", "by", "with", "as", "this", "that", "it",
    "from", "but", "not", "no", "do", "does", "did", "can", "will",
    "para", "com", "que", "uma", "uns", "umas", "ser", "ter", "fazer",
    "este", "esta", "ele", "ela", "como", "por", "isso", "nao", "sim",
    "mas", "mem", "type", "project", "topic", "tags", "timestamp", "refs",
    "metadata", "content",
}


def tokenize(text: str) -> list[str]:
    tokens = [t.lower() for t in TOKEN_RE.findall(text or "")]
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]


def collect_memories(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []
    inbox = repo_root / "context-hub" / "05_INBOX" / "byterover-imports"
    graph = repo_root / "context-hub" / "02_GRAPH"
    if inbox.exists():
        candidates.extend(p for p in inbox.glob("MEM__*.md") if p.is_file())
    if graph.exists():
        candidates.extend(p for p in graph.rglob("MEM__*.md") if p.is_file())
    return sorted(set(candidates))


def build_tfidf(documents: list[tuple[Path, str]]) -> tuple[list[dict[str, float]], dict[str, float]]:
    """Return list of TF-IDF vectors (per doc) and document frequency map."""
    n_docs = len(documents)
    if n_docs == 0:
        return [], {}

    doc_tokens = [tokenize(text) for _, text in documents]
    df: Counter[str] = Counter()
    for tokens in doc_tokens:
        for term in set(tokens):
            df[term] += 1

    idf = {term: math.log((1 + n_docs) / (1 + freq)) + 1.0 for term, freq in df.items()}

    vectors: list[dict[str, float]] = []
    for tokens in doc_tokens:
        if not tokens:
            vectors.append({})
            continue
        tf = Counter(tokens)
        max_tf = max(tf.values())
        vec = {term: (count / max_tf) * idf.get(term, 0.0) for term, count in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vec = {term: v / norm for term, v in vec.items()}
        vectors.append(vec)
    return vectors, idf


def vectorize_query(query: str, idf: dict[str, float]) -> dict[str, float]:
    tokens = tokenize(query)
    if not tokens:
        return {}
    tf = Counter(tokens)
    max_tf = max(tf.values())
    vec = {term: (count / max_tf) * idf.get(term, 1.0) for term, count in tf.items()}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {term: v / norm for term, v in vec.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    return sum(a[t] * b[t] for t in common)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search TRIAD memories by semantic similarity (TF-IDF stdlib).",
    )
    parser.add_argument("--query", required=True, help="Free-text query.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return.")
    parser.add_argument("--min-score", type=float, default=0.05, help="Minimum cosine similarity threshold.")
    parser.add_argument("--repo-root", default="", help="OmniBrain triad repo root (defaults to parent of tools/).")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    if not args.query.strip():
        print("Error: --query cannot be empty.", file=sys.stderr)
        return 2

    repo_root = Path(args.repo_root).resolve() if args.repo_root else _tools_dir.parent
    if not repo_root.exists():
        print(f"Error: repo root not found: {repo_root}", file=sys.stderr)
        return 2

    memory_paths = collect_memories(repo_root)
    if not memory_paths:
        print_utf8(f"No memories found under {repo_root / 'context-hub'}.")
        return 0

    documents = [(p, p.read_text(encoding="utf-8", errors="replace")) for p in memory_paths]
    vectors, idf = build_tfidf(documents)
    query_vec = vectorize_query(args.query, idf)

    scored = []
    for (path, _), vec in zip(documents, vectors, strict=False):
        score = cosine(query_vec, vec)
        if score >= args.min_score:
            scored.append((score, path))
    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[: args.top_k]

    if args.format == "json":
        import json
        out = {
            "query": args.query,
            "total_indexed": len(memory_paths),
            "results": [
                {"score": round(score, 4), "path": str(path)}
                for score, path in top
            ],
        }
        print_utf8(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print_utf8("# Memory Search Results")
    print_utf8("")
    print_utf8(f"- Query: {args.query}")
    print_utf8(f"- Indexed: {len(memory_paths)} memories")
    print_utf8(f"- Returned: {len(top)} (min_score={args.min_score})")
    print_utf8("")
    if not top:
        print_utf8("No memories matched.")
        return 0
    for rank, (score, path) in enumerate(top, start=1):
        rel = path.name
        print_utf8(f"{rank}. [{score:.3f}] {rel}")
        print_utf8(f"   Path: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
