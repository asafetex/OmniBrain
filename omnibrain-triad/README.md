# OmniBrain TRIAD

MVP executável para governança de mudanças com fluxo `diff-first`, consenso multiagente e memória operacional.

Objetivo operacional:
Transformar qualquer tarefa em um fluxo diff-first com consenso multiagente, registrando `PLAN/REVIEW/LESSON/WIN` na memória dinâmica e promovendo apenas vitórias executáveis para o Hub curado.

## O que vem pronto

- TRIAD Governance:
  - Claude Code como executor.
  - Codex CLI como auditor técnico.
  - Gemini CLI como auditor sistêmico.
- Context Hub em Obsidian (`context-hub/`) com Skill Graph inicial.
- Ferramentas locais sem API (`tools/`) para:
  - gerar Change Package por `git diff`,
  - rodar PreGate opcional e Gate principal,
  - registrar memória no ByteRover CLI ou fallback local,
  - promover notas do INBOX para o Graph.
- Template de projeto (`project-template/`) com `CLAUDE.md` e `AGENTS.md`.
- `bootstrap.py` para recriar toda a estrutura automaticamente.

## Quick Start (15 minutos)

1. Pré-requisitos:
   - `git`, `python` (3.10+), Obsidian
   - Claude Code, Codex CLI, Gemini CLI, ByteRover CLI 2.0 (logados)
2. Verifique cada CLI sem assumir flags de execução:
   - `codex --help`
   - `gemini --help`
   - `brv --help`
   - se `brv` não responder no Windows, use:
     - `node C:\Users\PC\AppData\Roaming\npm\node_modules\byterover-cli\bin\run.js --help`
3. Abra `context-hub/` como Vault no Obsidian.
4. Copie `tools/config.example.json` para `tools/config.json` e ajuste comandos reais.
5. No repositório alvo, gere um Change Package:
   - `python tools/make_change_package.py --repo . --level L3 --goal "..." --graph-links "agents/triad-protocol.md,disciplines/data-engineering/skills/spark-sql/joins.md"`
6. Rode Gate:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
7. Registre `WIN` ou `LESSON`:
   - `python tools/record_to_byterover.py --type WIN --project myproj --topic join-explode --file tmp/gate-results/<Change-ID>.md --tags "#discipline/data-engineering,#type/win,#project/myproj"`
8. Promova para o Graph quando reutilizável:
   - `python tools/promote_to_obsidian.py --list`
   - `python tools/promote_to_obsidian.py --source context-hub/05_INBOX/byterover-imports/<arquivo>.md --target disciplines/data-engineering/skills/spark-sql/`

## Estrutura

Veja a árvore completa em `docs/00_overview.md`.

## Regras centrais

- Sem API keys e sem HTTP calls.
- L3 só finaliza após Gate obrigatório Codex + Gemini.
- PreGate DeepSeek/CodeRabbit é opcional e nunca substitui o Gate L3.
- Sem `git diff`, sem revisão.
- Memória bruta fica em ByteRover/INBOX; Graph recebe só conhecimento curado.
