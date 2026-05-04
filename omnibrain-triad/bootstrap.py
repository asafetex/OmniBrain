#!/usr/bin/env python3
"""Bootstrap OmniBrain TRIAD by copying canonical scaffold files."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

FILES = [
    "README.md",
    "docs/00_overview.md",
    "docs/01_architecture.md",
    "docs/02_setup.md",
    "docs/03_daily_workflow.md",
    "docs/04_l1_l2_l3.md",
    "docs/05_change_package_spec.md",
    "docs/06_gate_spec.md",
    "docs/07_memory_spec.md",
    "docs/08_promotion_spec.md",
    "docs/09_mcp_optional.md",
    "docs/10_faq.md",
    "docs/migration_byterover_cli_2.md",
    "configs/routing.json",
    "configs/routing.yaml",
    "context-hub/README.md",
    "context-hub/00_HOME.md",
    "context-hub/01_MANIFEST/manifest.md",
    "context-hub/01_MANIFEST/taxonomy.md",
    "context-hub/01_MANIFEST/ids-and-naming.md",
    "context-hub/01_MANIFEST/governance-levels.md",
    "context-hub/01_MANIFEST/promotion-policy.md",
    "context-hub/01_MANIFEST/security-policy.md",
    "context-hub/01_MANIFEST/memory-hygiene.md",
    "context-hub/02_GRAPH/index.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/index.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/spark-sql/index.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/spark-sql/joins.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/spark-sql/windows.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/spark-sql/incremental.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/spark-sql/performance.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/data-quality/index.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/data-quality/duplicates.md",
    "context-hub/02_GRAPH/disciplines/data-engineering/skills/data-quality/nulls.md",
    "context-hub/02_GRAPH/disciplines/data-science/index.md",
    "context-hub/02_GRAPH/disciplines/data-science/skills/sanity-checks.md",
    "context-hub/02_GRAPH/disciplines/data-science/skills/outliers.md",
    "context-hub/02_GRAPH/disciplines/data-science/skills/kmeans.md",
    "context-hub/02_GRAPH/disciplines/agents/index.md",
    "context-hub/02_GRAPH/disciplines/agents/skills/triad-protocol.md",
    "context-hub/02_GRAPH/disciplines/agents/skills/change-package.md",
    "context-hub/02_GRAPH/disciplines/agents/skills/consensus-gate.md",
    "context-hub/02_GRAPH/disciplines/agents/skills/win-protocol.md",
    "context-hub/02_GRAPH/disciplines/agents/skills/memory-routing.md",
    "context-hub/05_INBOX/byterover-imports/README.md",
    "project-template/README.md",
    "project-template/CLAUDE.md",
    "project-template/AGENTS.md",
    "project-template/context-hub/README.md",
    "tools/README.md",
    "tools/config.example.json",
    "tools/utils.py",
    "tools/config_env.py",
    "tools/build_context_bundle.py",
    "tools/install_pre_push_hook.py",
    "tools/l3_pre_push_guard.py",
    "tools/make_change_package.py",
    "tools/preflight_check.py",
    "tools/route_task.py",
    "tools/start_task_flow.py",
    "tools/triad_stats.py",
    "tools/run_gate.py",
    "tools/recover_session.py",
    "tools/record_to_byterover.py",
    "tools/promote_to_obsidian.py",
    "tools/search_memory.py",
    "tools/inbox_curator.py",
    "tools/telemetry.py",
    "tools/confidence_cascade.py",
    "tools/suggest_pattern.py",
    "tools/triad_oracle.py",
    "tools/templates/change_package.md",
    "tools/templates/codex_review_prompt.md",
    "tools/templates/codex_review_prompt_auth.md",
    "tools/templates/codex_review_prompt_billing.md",
    "tools/templates/codex_review_prompt_data_pipeline.md",
    "tools/templates/gemini_review_prompt.md",
    "tools/templates/gemini_review_prompt_auth.md",
    "tools/templates/gemini_review_prompt_billing.md",
    "tools/templates/gemini_review_prompt_data_pipeline.md",
    "tools/templates/deepseek_review_prompt.md",
    "tools/templates/coderabbit_review_prompt.md",
    "tests/__init__.py",
    "tests/conftest.py",
    "pyproject.toml",
    "ruff.toml",
    ".env.example",
]


def copy_file(src_root: Path, dst_root: Path, rel_path: str) -> None:
    src = src_root / rel_path
    dst = dst_root / rel_path
    if not src.exists():
        raise FileNotFoundError(f"Missing source file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create omnibrain-triad scaffold in target directory.")
    parser.add_argument(
        "--target",
        default="omnibrain-triad",
        help="Output directory for generated repository.",
    )
    args = parser.parse_args()

    src_root = Path(__file__).resolve().parent
    dst_root = Path(args.target).resolve()

    for rel in FILES:
        copy_file(src_root, dst_root, rel)

    shutil.copy2(src_root / "bootstrap.py", dst_root / "bootstrap.py")
    print(f"Repository scaffold created at: {dst_root}")
    print(f"Files written: {len(FILES) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
