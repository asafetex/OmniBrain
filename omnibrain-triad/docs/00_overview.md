# 00 Overview

OmniBrain TRIAD unifica tres camadas:

1. Governanca de execucao (TRIAD): Claude executa, Codex audita tecnico, Gemini audita sistemico.
2. Memoria dinamica de execucao: ByteRover CLI 2.0 (ou fallback local no INBOX).
3. Hub curado em Obsidian: Skill Graph com notas atomicas e politica anti-poluicao.

## Escopo do MVP

- Funciona sem MCP.
- Funciona sem API keys.
- Usa somente CLIs logados e scripts locais em Python stdlib.
- Implementa fluxo `diff-first` com Gate obrigatorio em L3.
- Inclui preflight (`tools/preflight_check.py`), roteamento de tarefa (`tools/route_task.py`), fluxo inicial unificado (`tools/start_task_flow.py`), enforcement de push L3 (`tools/install_pre_push_hook.py` + `tools/l3_pre_push_guard.py`), analytics (`tools/triad_stats.py`), bundle de contexto (`tools/build_context_bundle.py`) e recuperacao de sessao (`tools/recover_session.py`).

## Arvore do repositorio

```text
omnibrain-triad/
  README.md
  bootstrap.py
  docs/
  context-hub/
  project-template/
  tools/
  configs/
```

## Frase guia

Transformar qualquer tarefa em um fluxo diff-first com consenso multiagente, registrando PLAN/REVIEW/LESSON/WIN na memoria dinamica e promovendo apenas vitorias executaveis para o Hub curado.
