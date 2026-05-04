# Sandbox L3 E2E

Repositorio de validacao do fluxo TRIAD com ciclo L3 completo.

## Objetivo

Validar ponta a ponta:
- branch de tarefa,
- mudanca critica com diff,
- Gate L3 (Codex + Gemini em fallback manual quando necessario),
- testes locais,
- commit final.

## Estado atual

- Branch: `feat/l3-checkout-hardening`
- Commits principais:
  - `8214d3c` hardening numerico (`NaN`, `inf`, `bool`, overflow)
  - `48aeb69` hardening de `currency` para evitar `TypeError`
  - `a7fb7f1` deterministic two-decimal validation
  - `dc2944e` payment_token format validation
- Testes: `19 passed` em `pytest`

## Como rodar localmente (PowerShell)

1. Criar e preparar ambiente:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pytest
```

2. Executar testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

3. Gerar Change Package (a partir do repo omnibrain-triad ao lado):

```powershell
python ..\omnibrain-triad\tools\make_change_package.py --repo . --level L3 --goal "..." --graph-links "disciplines/agents/skills/triad-protocol.md,disciplines/agents/skills/change-package.md,disciplines/agents/skills/consensus-gate.md"
```

4. Rodar Gate:

```powershell
python ..\omnibrain-triad\tools\run_gate.py --change-package .\tmp\change-packages\<Change-ID>.md
```

## Publicacao rapida sem remote configurado

Gerar bundle para transportar historico git:

```powershell
git bundle create ..\sandbox-l3-e2e.bundle --all
```

## L3 Gate Drill
- Last drill: 2026-03-19 using manual fallback (codex verdict consolidado + gemini manual).
- Change-ID: CHG-20260319-181823
- Gate artifact: ..\omnibrain-triad\tmp\gate-results\CHG-20260319-181823.md
- Final decision: APPROVE (codex=APPROVE, gemini=APPROVE).
