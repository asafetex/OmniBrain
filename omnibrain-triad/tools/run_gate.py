#!/usr/bin/env python3
"""Run PreGate (optional) and Gate (mandatory for L3) using CLI command templates."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from config_env import load_config
from telemetry import record_run, tool_name_from_file

SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
VERDICT_RE = re.compile(r"^\s*VERDICT\s*:\s*(APPROVE|REJECT)\s*$", re.IGNORECASE | re.MULTILINE)
BLOCKER_SIGNAL_RE = re.compile(r"\[(P0|P1|P2)\]", re.IGNORECASE)
APPROVE_SIGNAL_RE = re.compile(
    r"(no blocking|no blocking defects|no blocking issues|"
    r"no functional regressions? (are )?evident|no regressions? (are )?evident|"
    r"did not find regressions? or blocking issues|did not find .*blocking issues|"
    r"did not find .*defect(s)? introduced|did not find a discrete, actionable defect|"
    r"nao ha regressao evidente|sem regressao evidente|sem bloqueios?|"
    r"nao ha evidencia de regressao( funcional)?|nao ha evidencia de bug( introduzido)?|"
    r"nao ha inconsistenc(i|ia)s? acionave(i|is)|atende ao criterio de aceitacao)",
    re.IGNORECASE,
)
REJECT_SIGNAL_RE = re.compile(
    r"(should not be considered correct yet|this is a functional regression|"
    r"insufficient evidence|insufficiently auditable|falta evidencia|evidencia insuficiente)",
    re.IGNORECASE,
)


@dataclass
class AuditorResult:
    name: str
    ran: bool
    status: str
    verdict: str
    verdict_source: str
    command: str
    stdout: str
    stderr: str
    manual_prompt_path: str
    manual_response_path: str


def _validate_safe_id(value: str, label: str) -> str:
    if not SAFE_ID_RE.match(value):
        raise ValueError(f"Invalid {label}: contains unsafe characters: {value!r}")
    return value


def parse_change_metadata(change_package: str) -> tuple[str, str, str]:
    change_id_match = re.search(r"^- Change-ID:\s*(.+)$", change_package, re.MULTILINE)
    level_match = re.search(r"^- Level:\s*(L1|L2|L3)$", change_package, re.MULTILINE)
    repo_match = re.search(r"^- Repo:\s*(.+)$", change_package, re.MULTILINE)
    if not change_id_match:
        raise ValueError("Change Package is missing 'Change-ID' field. Cannot proceed.")
    if not level_match:
        raise ValueError("Change Package is missing 'Level' field (expected L1, L2, or L3). Cannot proceed.")
    change_id = _validate_safe_id(change_id_match.group(1).strip(), "Change-ID")
    level = level_match.group(1).strip()
    repo = repo_match.group(1).strip() if repo_match else ""
    return change_id, level, repo


def parse_verdict(text: str) -> str:
    matches = VERDICT_RE.findall(text or "")
    if not matches:
        return "UNKNOWN"
    return matches[-1].upper()


def normalize_for_inference(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip().lower()


def infer_verdict_from_cli_text(text: str) -> str:
    normalized = normalize_for_inference(text)
    if BLOCKER_SIGNAL_RE.search(text or ""):
        return "REJECT"
    if REJECT_SIGNAL_RE.search(normalized):
        return "REJECT"
    if APPROVE_SIGNAL_RE.search(normalized):
        return "APPROVE"
    return "UNKNOWN"


def build_prompt(template_path: Path, change_package: str) -> str:
    template = template_path.read_text(encoding="utf-8")
    return template.replace("{{CHANGE_PACKAGE}}", change_package)


DOMAIN_KEYWORDS = {
    "auth": ["auth", "oauth", "jwt", "login", "password", "session", "mfa", "credential", "token", "rbac"],
    "billing": ["billing", "payment", "stripe", "invoice", "subscription", "checkout", "refund", "tax", "currency", "charge"],
    "data_pipeline": ["pipeline", "etl", "spark", "delta", "incremental", "watermark", "join explode", "shuffle", "partition", "broadcast", "merge"],
}


def detect_domain(change_package: str) -> str | None:
    """Return domain key if change package matches well-known domain keywords."""
    text = change_package.lower()
    best_domain = None
    best_score = 0
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_domain = domain
    return best_domain if best_score >= 2 else None


def select_template(tools_dir: Path, auditor_name: str, change_package: str) -> Path:
    """Choose domain-specific template if it exists and domain detected."""
    domain = detect_domain(change_package)
    if domain:
        domain_template = tools_dir / "templates" / f"{auditor_name}_review_prompt_{domain}.md"
        if domain_template.exists():
            return domain_template
    return tools_dir / "templates" / f"{auditor_name}_review_prompt.md"


def run_cli(cmd: str, args: list[str], prompt: str, timeout_seconds: int, cwd: Path | None) -> tuple[int, str, str]:
    proc = subprocess.run(
        [cmd, *args],
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout_seconds,
        cwd=str(cwd) if cwd else None,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_auditor(
    auditor_name: str,
    change_package: str,
    tools_dir: Path,
    tmp_manual_dir: Path,
    manual_responses_dir: Path,
    config: dict,
    execution_cwd: Path | None,
) -> AuditorResult:
    auditor_cfg = config.get("auditors", {}).get(auditor_name, {})
    defaults = config.get("defaults", {})
    timeout_seconds = int(auditor_cfg.get("timeout_seconds", defaults.get("timeout_seconds", 120)))
    template_file = select_template(tools_dir, auditor_name, change_package)
    prompt = build_prompt(template_file, change_package)

    prompt_path = tmp_manual_dir / f"{auditor_name}_prompt.md"
    if prompt_path.exists():
        existing_prompt = prompt_path.read_text(encoding="utf-8")
        if existing_prompt != prompt:
            prompt_path.write_text(prompt, encoding="utf-8")
    else:
        prompt_path.write_text(prompt, encoding="utf-8")
    manual_response_path = manual_responses_dir / f"{auditor_name}.md"
    manual_response = ""
    manual_verdict = "UNKNOWN"
    manual_stale = False
    if manual_response_path.exists():
        prompt_mtime = prompt_path.stat().st_mtime
        response_mtime = manual_response_path.stat().st_mtime
        if response_mtime >= prompt_mtime:
            manual_response = manual_response_path.read_text(encoding="utf-8")
            manual_verdict = parse_verdict(manual_response)
        else:
            manual_stale = True

    enabled = bool(auditor_cfg.get("enabled", False))
    cmd = str(auditor_cfg.get("cmd", "")).strip()
    args = auditor_cfg.get("args", [])
    if not isinstance(args, list):
        args = []

    if not enabled:
        final_verdict = manual_verdict if manual_verdict != "UNKNOWN" else "UNKNOWN"
        stale_note = " Resposta manual existente esta desatualizada para este prompt." if manual_stale else ""
        return AuditorResult(
            name=auditor_name,
            ran=False,
            status="manual_loaded_disabled" if manual_verdict != "UNKNOWN" else "manual_required_disabled",
            verdict=final_verdict,
            verdict_source="manual" if manual_verdict != "UNKNOWN" else "none",
            command=f"{cmd} {' '.join(args)}".strip(),
            stdout="",
            stderr=f"Auditor desabilitado em config. Use fallback manual com prompt salvo.{stale_note}",
            manual_prompt_path=str(prompt_path),
            manual_response_path=str(manual_response_path),
        )

    if not cmd or shutil.which(cmd) is None:
        final_verdict = manual_verdict if manual_verdict != "UNKNOWN" else "UNKNOWN"
        stale_note = " Resposta manual existente esta desatualizada para este prompt." if manual_stale else ""
        return AuditorResult(
            name=auditor_name,
            ran=False,
            status="manual_loaded_command_not_found" if manual_verdict != "UNKNOWN" else "manual_required_command_not_found",
            verdict=final_verdict,
            verdict_source="manual" if manual_verdict != "UNKNOWN" else "none",
            command=f"{cmd} {' '.join(args)}".strip(),
            stdout="",
            stderr=f"Comando da CLI nao encontrado no PATH.{stale_note}",
            manual_prompt_path=str(prompt_path),
            manual_response_path=str(manual_response_path),
        )

    try:
        rc, out, err = run_cli(cmd, args, prompt, timeout_seconds, execution_cwd)
    except Exception as exc:  # pragma: no cover - fallback path
        final_verdict = manual_verdict if manual_verdict != "UNKNOWN" else "UNKNOWN"
        stale_note = " Resposta manual existente esta desatualizada para este prompt." if manual_stale else ""
        return AuditorResult(
            name=auditor_name,
            ran=False,
            status="manual_loaded_execution_error" if manual_verdict != "UNKNOWN" else "manual_required_execution_error",
            verdict=final_verdict,
            verdict_source="manual" if manual_verdict != "UNKNOWN" else "none",
            command=f"{cmd} {' '.join(args)}".strip(),
            stdout="",
            stderr=f"Falha ao executar CLI: {exc}.{stale_note}",
            manual_prompt_path=str(prompt_path),
            manual_response_path=str(manual_response_path),
        )

    combined_text = out + "\n" + err
    cli_verdict = parse_verdict(combined_text)
    inferred_cli_verdict = infer_verdict_from_cli_text(combined_text) if cli_verdict == "UNKNOWN" else "UNKNOWN"
    verdict = cli_verdict
    verdict_source = "cli"
    status = "completed" if rc == 0 else f"cli_exit_{rc}"

    # Precedencia: verdict explicito da CLI > verdict inferido da CLI > verdict manual > UNKNOWN.
    if cli_verdict == "UNKNOWN" and inferred_cli_verdict != "UNKNOWN":
        verdict = inferred_cli_verdict
        verdict_source = "cli_inferred"
        status = f"{status}_inferred"

    if verdict == "UNKNOWN" and manual_verdict != "UNKNOWN":
        verdict = manual_verdict
        verdict_source = "manual"
        status = f"{status}_manual_fallback"

    if verdict == "UNKNOWN":
        verdict_source = "none"

    return AuditorResult(
        name=auditor_name,
        ran=True,
        status=status,
        verdict=verdict,
        verdict_source=verdict_source,
        command=f"{cmd} {' '.join(args)}".strip(),
        stdout=out.strip(),
        stderr=err.strip(),
        manual_prompt_path=str(prompt_path),
        manual_response_path=str(manual_response_path),
    )


def decide(level: str, results: dict[str, AuditorResult]) -> str:
    if level == "L3":
        codex = results.get("codex", AuditorResult("codex", False, "missing", "UNKNOWN", "none", "", "", "", "", "")).verdict
        gemini = results.get("gemini", AuditorResult("gemini", False, "missing", "UNKNOWN", "none", "", "", "", "", "")).verdict
        if "REJECT" in {codex, gemini}:
            return "REJECT"
        if codex == "APPROVE" and gemini == "APPROVE":
            return "APPROVE"
        return "CONFLICT"

    if level == "L2":
        verdicts = [r.verdict for r in results.values() if r.verdict in {"APPROVE", "REJECT"}]
        if "REJECT" in verdicts:
            return "REJECT"
        return "NEEDS_HUMAN"

    return "NOT_REQUIRED"


def _sanitize_cli_output(text: str) -> str:
    """Remove ANSI escape sequences and null bytes from CLI output."""
    text = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)
    text = text.replace("\x00", "")
    return text


def result_to_markdown(change_id: str, level: str, decision: str, results: list[AuditorResult]) -> str:
    lines = [
        f"# Gate Result - {change_id}",
        "",
        "## Summary",
        f"- Change-ID: {change_id}",
        f"- Level: {level}",
        f"- Final Decision: {decision}",
        f"- Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
    ]
    for r in results:
        lines.extend(
            [
                f"## Auditor: {r.name}",
                f"- Ran: {r.ran}",
                f"- Status: {r.status}",
                f"- Verdict: {r.verdict}",
                f"- Verdict Source: {r.verdict_source}",
                f"- Command: `{r.command}`",
                f"- Manual Prompt: `{r.manual_prompt_path}`",
                f"- Manual Response: `{r.manual_response_path}`",
                "",
                "### Stdout",
                "```text",
                _sanitize_cli_output(r.stdout) or "(empty)",
                "```",
                "",
                "### Stderr",
                "```text",
                _sanitize_cli_output(r.stderr) or "(empty)",
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def print_utf8(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    if not text.endswith("\n"):
        sys.stdout.buffer.write(b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gate from a Change Package.")
    parser.add_argument("--change-package", required=True, help="Path to Change Package markdown file.")
    parser.add_argument(
        "--manual-responses-dir",
        default="",
        help="Directory with optional manual auditor responses (codex.md, gemini.md, deepseek.md, coderabbit.md).",
    )
    args = parser.parse_args()

    change_path = Path(args.change_package).resolve()
    if not change_path.exists():
        raise FileNotFoundError(f"Change Package not found: {change_path}")

    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent
    config = load_config(tools_dir)
    change_package = change_path.read_text(encoding="utf-8")
    try:
        change_id, level, repo_in_package = parse_change_metadata(change_package)
    except ValueError as exc:
        print(f"ERROR: invalid Change Package metadata: {exc}", file=sys.stderr)
        return 2

    execution_cwd: Path | None = None
    if repo_in_package:
        candidate = Path(repo_in_package)
        if not candidate.is_absolute():
            candidate = (change_path.parent / candidate).resolve()
        if candidate.exists() and candidate.is_dir():
            execution_cwd = candidate

    manual_dir = repo_root / "tmp" / "manual-prompts" / change_id
    manual_dir.mkdir(parents=True, exist_ok=True)
    manual_responses_dir = (
        Path(args.manual_responses_dir).resolve()
        if args.manual_responses_dir
        else (repo_root / "tmp" / "manual-responses" / change_id)
    )
    manual_responses_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, AuditorResult] = {}

    for name in ("deepseek", "coderabbit"):
        cfg = config.get("auditors", {}).get(name, {})
        if bool(cfg.get("enabled", False)):
            results[name] = run_auditor(
                name,
                change_package,
                tools_dir,
                manual_dir,
                manual_responses_dir,
                config,
                execution_cwd,
            )

    required_gate = ["codex", "gemini"] if level == "L3" else []
    optional_gate = ["codex", "gemini"] if level == "L2" else []
    gate_targets = required_gate if required_gate else optional_gate

    for name in gate_targets:
        results[name] = run_auditor(
            name,
            change_package,
            tools_dir,
            manual_dir,
            manual_responses_dir,
            config,
            execution_cwd,
        )

    decision = decide(level, results)
    ordered = [results[k] for k in ("deepseek", "coderabbit", "codex", "gemini") if k in results]
    markdown = result_to_markdown(change_id, level, decision, ordered)

    out_dir = repo_root / "tmp" / "gate-results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{change_id}.md"
    out_path.write_text(markdown, encoding="utf-8")

    print_utf8(markdown)
    print_utf8(f"Saved: {out_path}")
    if decision in {"CONFLICT", "NEEDS_HUMAN"}:
        print_utf8("Decision requires human action.")
    return 0


if __name__ == "__main__":
    with record_run(tool_name_from_file(__file__)):
        raise SystemExit(main())
