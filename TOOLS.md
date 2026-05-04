# TOOLS — Referencia de cada ferramenta

20 ferramentas, agrupadas por funcao. Cada uma tem: **o que faz**, **quando usar**, **comando minimo**, **flags importantes**.

---

## Mapa mental: quando usar o que

```
COMECEI UMA TAREFA               -> start_task_flow.py
TENHO DUVIDA SE VAI DAR CERTO    -> triad_oracle.py (consulta historico)
QUERO INSPIRACAO DE OUTROS CASOS -> suggest_pattern.py (cross-domain)
JA TENHO O CODIGO PRONTO         -> make_change_package.py
PRECISO DE REVIEW                -> run_gate.py
VOU FAZER PUSH                   -> install_pre_push_hook.py + git push
TERMINEI A TAREFA                -> record_to_byterover.py
TEM ALGO REUTILIZAVEL?           -> promote_to_obsidian.py
SESSAO TRAVOU                    -> recover_session.py
SISTEMA TA OK?                   -> preflight_check.py
INBOX TA CHEIO?                  -> inbox_curator.py
QUERO VER METRICAS               -> triad_stats.py
QUERO BUSCAR MEMORIA             -> search_memory.py
QUERO VER USO DAS TOOLS          -> tail tmp/telemetry/events.jsonl
QUERO PRE-VALIDAR ANTES DO LLM   -> confidence_cascade (import)
NOVO PROJETO DO ZERO             -> bootstrap.py
```

---

## Categoria 1: Validacao e setup

### `preflight_check.py`
**Faz:** valida 17 itens (git, python, CLIs, configs, templates, tmp writable).
**Quando:** antes de comecar a sessao, ou quando algo da errado.
**Comando:**
```bash
python tools/preflight_check.py --repo <caminho>
```
**Saida:** `Summary: PASS=12 WARN=4 FAIL=1`. Exit 1 se FAIL, 2 se --strict e WARN.

---

### `install_pre_push_hook.py`
**Faz:** instala hook git que bloqueia push se Change Package L3 nao tem Gate APPROVE.
**Quando:** uma vez por repositorio, no setup inicial.
**Comando:**
```bash
python tools/install_pre_push_hook.py --repo <caminho>
```
**Bonus:** cada execucao do hook escreve em `<repo>/.triad-push-audit.log`. Para enforcement real, configure GitHub branch protection.

---

### `bootstrap.py`
**Faz:** copia 88 arquivos canonicos (docs, tools, templates, configs) para um diretorio novo.
**Quando:** comecar um projeto novo que vai usar TRIAD.
**Comando:**
```bash
python bootstrap.py --target /caminho/novo-projeto
```

---

## Categoria 2: Pipeline principal

### `start_task_flow.py`
**Faz:** pipeline em 1 comando: route + bundle + change_package + summary.
**Quando:** comecar qualquer tarefa nao-trivial. **Esta e a ferramenta principal.**
**Comando:**
```bash
python tools/start_task_flow.py \
  --repo <projeto> \
  --task "descricao" \
  --level L1|L2|L3
```
**Flags uteis:**
- `--preflight` — valida ambiente antes de comecar
- `--staged` — usa git diff staged em vez de working-tree
- `--skip-route`, `--skip-bundle`, `--skip-change-package` — pula etapas

---

### `route_task.py`
**Faz:** detecta intent da tarefa e sugere executor + revisores + nos do Skill Graph.
**Quando:** voce quer ver as recomendacoes sem rodar tudo. Ou em CI.
**Comando:**
```bash
python tools/route_task.py --task "..." --level L3 --repo .
```
**Flags:**
- `--intent <id>` — forca um intent especifico do `routing.json`
- `--format json|markdown` — saida estruturada vs legivel

---

### `build_context_bundle.py`
**Faz:** consolida snapshot do repo + nos relevantes do Graph + memorias recentes em 1 markdown.
**Quando:** voce quer dar contexto rico pro LLM (Codex/Claude/GPT) sem copiar arquivos manualmente.
**Comando:**
```bash
python tools/build_context_bundle.py --repo . --task "..." --level L3 --auto-route
```

---

### `make_change_package.py`
**Faz:** captura `git diff` + metadata (Change-ID, Level, Goal, etc.) num markdown estruturado.
**Quando:** apos terminar a implementacao em branch.
**Comando:**
```bash
python tools/make_change_package.py \
  --repo <projeto> \
  --level L3 \
  --goal "o que voce fez"
```
**Flags:**
- `--staged` — usa diff staged (pega arquivos com `git add`)
- `--graph-links "node1,node2"` — referencia nos do Skill Graph
- `--memory-refs "ref1,ref2"` — referencia memorias relacionadas

**Cuidado:** **arquivos untracked sao IGNORADOS** pelo git diff. Se voce criou arquivos novos, faz `git add` antes ou usa `--staged`.

---

### `run_gate.py`
**Faz:** orquestra auditores (codex, gemini, deepseek, coderabbit) e decide APPROVE/REJECT/CONFLICT.
**Quando:** apos `make_change_package.py`. Obrigatorio em L3.
**Comando:**
```bash
python tools/run_gate.py --change-package <path>.md
```
**Como funciona:**
1. Detecta dominio (auth/billing/data_pipeline) e usa template especializado se existir
2. Tenta rodar CLI auditor; se falhar, gera prompt em `tmp/manual-prompts/<CHG-ID>/`
3. Procura resposta manual em `tmp/manual-responses/<CHG-ID>/<auditor>.md`
4. Decide pelo decision_rule do nivel (L3 = ambos APPROVE; L2 = nenhum REJECT)

---

### `l3_pre_push_guard.py`
**Faz:** chamado pelo hook git pre-push. Bloqueia se Change Package L3 nao tem Gate APPROVE.
**Quando:** automatico via hook. Voce nao chama direto.
**Comando direto (debug):**
```bash
python tools/l3_pre_push_guard.py --repo <projeto>
```

---

## Categoria 3: Inteligencia (NOVO)

### `triad_oracle.py`
**Faz:** dado um CP ou query livre, retorna decisoes historicas similares + recomendacao agregada.
**Quando:** **antes** de comecar uma tarefa. Pra saber se "ja fizemos isso antes e como foi".
**Comando:**
```bash
python tools/triad_oracle.py --query "OAuth2 JWT refresh tokens"
```
**Output principal:**
- `verdict_hint`: LIKELY_APPROVE / LIKELY_REJECT / MIXED_HISTORY / NO_HISTORICAL_VERDICT / INSUFFICIENT_DATA
- `confidence`: high / medium / low
- `top_similar`: top-K memorias com score
**Flags:**
- `--change-package <path>` em vez de `--query`
- `--top-k 10`
- `--format json` para consumir programaticamente

---

### `suggest_pattern.py`
**Faz:** sugere WINs aplicaveis ao Change Package atual. Inclui transferencia cross-domain.
**Quando:** apos gerar Change Package, antes do Gate. Pode te poupar tempo descobrindo padroes.
**Comando:**
```bash
python tools/suggest_pattern.py --change-package <cp>.md --top-k 3
```
**Flag interessante:**
- `--cross-discipline-only` — filtra WINs da disciplina obvia, forca transferencia entre dominios

---

### `confidence_cascade.py` (modulo, nao CLI)
**Faz:** evaluator 3-tier que retorna decisao + se precisa escalar pra LLM.
**Quando:** **antes** de chamar `run_gate.py`. Reduz custos LLM em ~42%.
**Como usar:**
```python
import sys; sys.path.insert(0, 'tools')
from confidence_cascade import evaluate_cascade

with open('change_package.md') as f:
    cp = f.read()

result = evaluate_cascade(cp, level="L3", memory_corpus=None)
print(f"Tier {result.tier}: {result.decision}")
print(f"Reason: {result.reason}")
print(f"Escalate to LLM: {result.escalate_to_llm}")
```
**Tier 1 (regras):** detecta empty diff, comments-only, whitespace-only, security violations.
**Tier 2 (heuristica):** TF-IDF similarity contra historico APPROVE/REJECT.
**Tier 3:** ESCALATE pra Gate normal.

---

### `search_memory.py`
**Faz:** busca semantica TF-IDF nas memorias (INBOX + Graph).
**Quando:** voce lembra "ja vi algo sobre X" mas nao sabe onde.
**Comando:**
```bash
python tools/search_memory.py --query "currency hardening" --top-k 5
```
**Flags:**
- `--min-score 0.05` — threshold de similaridade
- `--format json`

---

## Categoria 4: Memoria

### `record_to_byterover.py`
**Faz:** registra memoria (PLAN/REVIEW/LESSON/WIN/DECISION). Tenta ByteRover CLI; cai no INBOX se nao tem.
**Quando:** apos cada decisao significativa.
**Comando:**
```bash
python tools/record_to_byterover.py \
  --type WIN \
  --project meu-projeto \
  --topic "topic-curto" \
  --file <gate-result>.md \
  --tags "#discipline/auth,#type/win"
```
**Tipos:**
- **PLAN** — antes de comecar (escopo, riscos, criterios)
- **REVIEW** — apos Gate (verdict + rationale)
- **WIN** — solucao validada e reutilizavel
- **LESSON** — algo deu errado, aprendizado
- **DECISION** — escolha entre opcoes (registra o "porque")

---

### `promote_to_obsidian.py`
**Faz:** move memoria curada do INBOX para o Skill Graph (organiza por disciplina).
**Quando:** apos um WIN que e reutilizavel em outros projetos. **So promove o que e geral.**
**Comandos:**
```bash
# Lista candidatos
python tools/promote_to_obsidian.py --list

# Promove (target relativo a context-hub/02_GRAPH/)
python tools/promote_to_obsidian.py \
  --source context-hub/05_INBOX/byterover-imports/<arquivo>.md \
  --target disciplines/agents/skills/
```
**Bonus:** aceita target com prefixo completo `context-hub/02_GRAPH/...` — auto-corrige.

---

### `inbox_curator.py`
**Faz:** detecta stale (PLAN/REVIEW velho), duplicates (cosine >=0.85), promote candidates (WIN/LESSON no INBOX).
**Quando:** semanal. Mantem INBOX limpo.
**Comandos:**
```bash
# Dry-run (so relatorio)
python tools/inbox_curator.py --max-age-days 30

# Aplicar (move stale para _archive/)
python tools/inbox_curator.py --max-age-days 30 --apply
```

---

## Categoria 5: Recovery e analytics

### `recover_session.py`
**Faz:** dado um Change-ID, gera relatorio de retomada com snapshot do repo, diff atual, gate decision.
**Quando:** voce voltou no dia seguinte e nao lembra onde parou.
**Comando:**
```bash
python tools/recover_session.py --repo <projeto> --change-id CHG-XXX
```

---

### `triad_stats.py`
**Faz:** analytics da janela (memorias por tipo, top projects, top topics).
**Quando:** sextas pra ver o que rolou na semana.
**Comando:**
```bash
python tools/triad_stats.py --days 7
```
**Flag:** `--days 30` para ver mes inteiro.

---

### `telemetry.py` (modulo, nao CLI)
**Faz:** registra cada execucao de tool em `tmp/telemetry/events.jsonl`.
**Quando:** automatico nos tools instrumentados.
**Como ler:**
```bash
tail -20 tmp/telemetry/events.jsonl | python -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line)
    print(f\"{e['ts']} {e['tool']:25s} exit={e['exit_code']} dur={e['duration_ms']}ms\")
"
```
**Flags de ambiente:**
- `TRIAD_TELEMETRY_DISABLED=1` — desliga telemetria
- `TRIAD_TELEMETRY_FILE=<path>` — caminho customizado

---

## Categoria 6: Internas (importadas, nao chamadas)

### `utils.py`
Funcoes compartilhadas: `print_utf8`, `run_git`, `parse_csv`, `detect_intent`, `load_json`.

### `config_env.py`
Loader de config com overrides via `TRIAD_*` env vars.

---

## Tabela: complexidade × frequencia de uso

| Tool | Complexidade | Frequencia |
|---|:---:|:---:|
| `start_task_flow.py` | Baixa | Diaria |
| `run_gate.py` | Baixa | Diaria (L2/L3) |
| `record_to_byterover.py` | Baixa | Por tarefa |
| `triad_oracle.py` | Baixa | Por tarefa (NOVO) |
| `preflight_check.py` | Baixa | Por sessao |
| `search_memory.py` | Baixa | Quando esquece algo |
| `inbox_curator.py` | Baixa | Semanal |
| `triad_stats.py` | Baixa | Semanal |
| `make_change_package.py` | Media | Diaria |
| `route_task.py` | Media | Diaria |
| `build_context_bundle.py` | Media | Quando precisa contexto |
| `recover_session.py` | Media | Quando trava |
| `suggest_pattern.py` | Media | Por tarefa |
| `promote_to_obsidian.py` | Media | Por WIN |
| `confidence_cascade` (import) | Alta | Por tarefa (CI) |
| `install_pre_push_hook.py` | Alta | 1x por repo |
| `bootstrap.py` | Alta | 1x por projeto |

---

## Configuracao

### `tools/config.json` (gitignored)
Configuracao real de auditores. Copie de `config.example.json` e ative os CLIs disponiveis.

### `tools/config.example.json` (versionado)
Template seguro com tudo desabilitado.

### `configs/routing.json`
Politica de roteamento: niveis L1/L2/L3, intents, decision_rules.

### `configs/routing.yaml`
Mesma politica em YAML (mais legivel pra editar).

### Env vars
- `TRIAD_TIMEOUT_SECONDS=120` — timeout default
- `TRIAD_ENCODING=utf-8`
- `TRIAD_TELEMETRY_DISABLED=1` — desliga telemetria
- `TRIAD_TELEMETRY_FILE=<path>` — telemetria custom path
- `TRIAD_PYTHON=<python>` — python usado pelos hooks
