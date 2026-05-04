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
  - rotear tarefa em politica declarativa (executor/revisores/nos),
  - montar context bundle para handoff de execucao,
  - gerar Change Package por `git diff`,
  - rodar PreGate opcional e Gate principal,
  - bloquear push L3 sem Gate APPROVE via hook local,
  - gerar analytics de memoria (WIN/LESSON/REVIEW),
  - recuperar sessao travada com relatorio de retomada,
  - registrar memoria no ByteRover CLI ou fallback local,
  - promover notas do INBOX para o Graph.
- Politica declarativa de roteamento em `configs/routing.yaml` (humano) e `configs/routing.json` (executavel).
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
6. (Opcional recomendado) roteie a tarefa:
   - `python tools/route_task.py --task "..." --level L3`
7. (Opcional recomendado) rode preflight antes de abrir ciclo:
   - `python tools/preflight_check.py --repo .`
8. (Opcional recomendado) gere os artefatos iniciais em um comando:
   - `python tools/start_task_flow.py --repo . --task "..." --level L3 --preflight`
   - isso ja produz route + context bundle + change package.
9. (Opcional recomendado) monte contexto consolidado:
   - `python tools/build_context_bundle.py --repo . --task "..." --level L3 --auto-route`
   - use `tmp/context-bundles/CTX-*.md` como handoff para executor/auditor.
10. Rode Gate:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
11. (Opcional recomendado) instale enforcement local de push:
   - `python tools/install_pre_push_hook.py --repo .`
   - bloqueia `git push` de L3 sem `APPROVE` no Gate.
12. (Opcional recomendado) gere stats semanais de valor:
   - `python tools/triad_stats.py --days 7`
13. Se Gemini manual:
   - use `tmp/manual-prompts/<Change-ID>/gemini_prompt.md`;
   - salve resposta em `tmp/manual-responses/<Change-ID>/gemini.md`;
   - rode Gate novamente para decisao final.
14. Se sessao travar, gere retomada:
   - `python tools/recover_session.py --repo . --change-id <Change-ID>`
   - use `tmp/recovery-reports/REC-*.md` como prompt de retomada.
15. Registre `WIN` ou `LESSON`:
   - `python tools/record_to_byterover.py --type WIN --project myproj --topic join-explode --file tmp/gate-results/<Change-ID>.md --tags "#discipline/data-engineering,#type/win,#project/myproj"`
16. Promova para o Graph quando reutilizavel:
   - `python tools/promote_to_obsidian.py --list`
   - `python tools/promote_to_obsidian.py --source context-hub/05_INBOX/byterover-imports/<arquivo>.md --target disciplines/data-engineering/skills/spark-sql/`
17. (Opcional) validar testes no sandbox:
   - `.\.venv\Scripts\python.exe -m pytest -q`

## Estrutura

Veja a arvore completa em `docs/00_overview.md`.

## Regras centrais

- Sem API keys e sem HTTP calls custom.
- L3 so finaliza apos Gate obrigatorio Codex + Gemini.
- PreGate DeepSeek/CodeRabbit e opcional e nunca substitui o Gate L3.
- Sem `git diff`, sem revisao.
- Memoria bruta fica em ByteRover ou INBOX; Graph recebe so conhecimento curado.

## Empirically validated (smoke-tested)

Tudo abaixo foi exercitado em smoke tests adversariais e tem evidencia em logs/outputs reais:

| Feature | Status | Evidencia |
|---|---|---|
| `preflight_check.py` | OK | Detecta CLI faltante (FAIL=1), templates OK, tmp writable |
| `route_task.py` | OK | 5 inputs adversariais (normal, keyword colidida, command injection, vazio rejeitado, unicode/emoji) |
| `make_change_package.py` | OK | Diff vazio, 1MB, 5MB (275ms), unicode/emoji, untracked warning, UUID anti-collision |
| `build_context_bundle.py` | OK | Auto-route + nos do Graph + memoria recente |
| `start_task_flow.py` | OK | Pipeline E2E: route + bundle + change package |
| `run_gate.py` | OK | 5 cenarios: APPROVE/APPROVE -> APPROVE; APPROVE/REJECT -> REJECT; REJECT/REJECT -> REJECT; UNKNOWN/UNKNOWN -> CONFLICT; APPROVE/UNKNOWN -> CONFLICT. Path traversal -> ValueError + exit 2 |
| `l3_pre_push_guard.py` | OK | APPROVE permite (exit 0), REJECT bloqueia (exit 1), missing gate bloqueia (exit 1) |
| `record_to_byterover.py` | OK | Fallback INBOX testado (--text e --file) |
| `triad_stats.py` | OK | Janelas de 1d e 30d, contagem por type/project |
| `recover_session.py` | OK | Snapshot + diff + recovery prompt |
| `promote_to_obsidian.py` | OK | --list, --target relativo, --target com prefixo (auto-corrigido) |
| `bootstrap.py` | OK | Cria 76 arquivos em projeto novo; preflight passa |
| Hook audit log | OK | Cada execucao registrada em `.triad-push-audit.log` |
| Templates por dominio | OK | Auto-detecta auth/billing/data_pipeline e usa checklist especializado |
| Race condition | OK | 5 instancias paralelas no mesmo segundo geraram 5 IDs unicos (UUID) |

**Limites conhecidos:**
- `--no-verify` no `git push` ainda bypassa o hook localmente (use GitHub branch protection para enforcement real)
- ByteRover CLI 2.x ativo nao foi validado contra binario real (so fallback INBOX)
- DeepSeek/CodeRabbit PreGate sao opcionais e nao foram testados em ciclo real
