# OmniBrain TRIAD

MVP executavel para governanca de mudancas com fluxo `diff-first`, consenso multiagente e memoria operacional.

Objetivo operacional:
Transformar qualquer tarefa em um fluxo diff-first com consenso multiagente, registrando `PLAN/REVIEW/LESSON/WIN` na memoria de execucao e promovendo apenas vitorias executaveis para o Hub curado.

## O que vem pronto

- TRIAD Governance:
  - Claude Code como executor.
  - Codex CLI como auditor tecnico.
  - Gemini CLI como auditor sistemico.
- Context Hub em Obsidian (`context-hub/`) com Skill Graph inicial.
- Ferramentas locais sem API (`tools/`) para:
  - gerar Change Package por `git diff`,
  - rodar PreGate opcional e Gate principal,
  - registrar memoria no ByteRover CLI ou fallback local,
  - promover notas do INBOX para o Graph.
- Template de projeto (`project-template/`) com `CLAUDE.md` e `AGENTS.md`.
- `bootstrap.py` para recriar toda a estrutura automaticamente.

## Modos de memoria

- Modo padrao recomendado agora: `Obsidian-only (free)`.
  - `byterover.enabled = false` em `tools/config.json`.
  - `record_to_byterover.py` salva em `context-hub/05_INBOX/byterover-imports/`.
  - Vault sincroniza por Git (ou Obsidian Sync, se voce assinar).
- Modo opcional: `ByteRover ativo`.
  - `byterover.enabled = true`.
  - Defina `byterover.cmd` e `byterover.args` com base no `--help` real da sua CLI.

## Quick Start (15 minutos)

1. Pre-requisitos:
   - `git`, `python` (3.10+), Obsidian
   - Claude Code, Codex CLI, Gemini CLI (logados)
   - ByteRover CLI 2.x opcional
2. Verifique CLIs:
   - `codex --help`
   - `gemini --help`
   - `brv --help` (opcional)
3. Abra `context-hub/` como Vault no Obsidian.
4. Ajuste `tools/config.json`:
   - mantenha `byterover.enabled = false` para modo Obsidian-only;
   - deixe `gemini.enabled = false` no ciclo 1 se usar fallback manual.
5. No repositorio alvo, gere Change Package:
   - `python tools/make_change_package.py --repo . --level L3 --goal "..." --graph-links "agents/triad-protocol.md,disciplines/data-engineering/skills/spark-sql/joins.md"`
6. Rode Gate:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
7. Se Gemini manual:
   - use `tmp/manual-prompts/<Change-ID>/gemini_prompt.md`;
   - salve resposta em `tmp/manual-responses/<Change-ID>/gemini.md`;
   - rode Gate novamente para decisao final.
8. Registre `WIN` ou `LESSON`:
   - `python tools/record_to_byterover.py --type WIN --project myproj --topic join-explode --file tmp/gate-results/<Change-ID>.md --tags "#discipline/data-engineering,#type/win,#project/myproj"`
9. Promova para o Graph quando reutilizavel:
   - `python tools/promote_to_obsidian.py --list`
   - `python tools/promote_to_obsidian.py --source context-hub/05_INBOX/byterover-imports/<arquivo>.md --target disciplines/data-engineering/skills/spark-sql/`

## Estrutura

Veja a arvore completa em `docs/00_overview.md`.

## Regras centrais

- Sem API keys e sem HTTP calls custom.
- L3 so finaliza apos Gate obrigatorio Codex + Gemini.
- PreGate DeepSeek/CodeRabbit e opcional e nunca substitui o Gate L3.
- Sem `git diff`, sem revisao.
- Memoria bruta fica em ByteRover ou INBOX; Graph recebe so conhecimento curado.
