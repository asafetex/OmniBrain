# TUTORIAL — Caso real do inicio ao fim

Vamos passar pelo **fluxo completo do TRIAD** com uma tarefa fictícia mas realista.

**Cenario:** voce precisa adicionar autenticacao OAuth2 num projeto existente. E uma mudanca **L3 (critica)** porque mexe com seguranca.

---

## Fase 0 — Antes de comecar

### Pre-requisitos
- Python 3.10+
- Git configurado
- Um projeto target (vou usar `/tmp/meu-projeto` como exemplo)

### Estrutura mental
TRIAD tem **5 fases**:

```
1. PLAN     -> classificar nivel e contexto
2. EXEC     -> implementar em branch (diff-first)
3. PACKAGE  -> capturar diff + metadata
4. GATE     -> revisao multi-agente
5. MEMORY   -> registrar e promover
```

Cada fase tem 1-3 comandos. Nao tem mais.

---

## Fase 1 — PLAN (5 minutos)

### Passo 1.1: validar ambiente

```bash
cd c:/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/SAAS/OmniBrain/omnibrain-triad
python tools/preflight_check.py --repo /tmp/meu-projeto
```

**Saida esperada:**
```
# TRIAD Preflight
- [PASS] repo.exists: /tmp/meu-projeto
- [PASS] repo.git: Target repo is a git worktree
- [PASS] python.cmd: python available in PATH
- [WARN] cli.codex: Disabled and command not found: codex
...
Summary: PASS=12 WARN=4 FAIL=0
```

**Se tem FAIL:** corrija antes. Se so tem WARN: pode prosseguir (CLIs auditores sao opcionais, fallback manual funciona).

---

### Passo 1.2: consultar o oraculo (NOVO)

Antes de comecar, pergunta pra historia:

```bash
python tools/triad_oracle.py --query "OAuth2 authentication JWT refresh token"
```

**Saida possivel:**
```
# TRIAD Oracle Report
- Indexed memories: 11
- Top similar (>= 0.05): 3

## Recommendation
- Verdict hint: **LIKELY_APPROVE**
- Confidence: medium
- Rationale: Past similar work was approved 2 time(s) vs rejected 0 time(s)

## Top Similar Memories
1. [0.471] DECISION verdict=-        MEM__DECISION__sandbox-l3-e2e__checkout-currency-hardening-approve...
2. [0.466] WIN      verdict=-        MEM__WIN__sandbox-l3-e2e__gate-manual-fallback...
```

**Como interpretar:**
- `LIKELY_APPROVE` = trabalho similar foi aprovado antes. Continue.
- `LIKELY_REJECT` = leia as memorias antes de prosseguir, descobre o que deu errado.
- `MIXED_HISTORY` = revisao manual obrigatoria.
- `INSUFFICIENT_DATA` = primeiro do tipo, voce esta abrindo caminho.

---

### Passo 1.3: rotear a tarefa

```bash
python tools/route_task.py \
  --task "Implement OAuth2 with JWT and refresh tokens" \
  --level L3 \
  --repo /tmp/meu-projeto
```

**Saida:** um arquivo markdown em `tmp/task-routes/ROUTE-*.md` com:
- Intent detectado (`generic` ou `governance_l3`)
- Revisores recomendados (codex, gemini)
- Nos sugeridos do Skill Graph
- Comandos prontos pra copiar

---

## Fase 2 — EXEC (tempo da implementacao real)

### Passo 2.1: branch dedicada

```bash
cd /tmp/meu-projeto
git checkout -b feat/oauth2-auth
```

### Passo 2.2: implementar diff-first

Faz a mudanca normalmente. **Regra:** todo arquivo que voce mexe deve ser visivel via `git diff`.

```bash
# editar arquivos...
git status
git diff
```

### Passo 2.3: testar localmente

```bash
pytest tests/  # ou seu comando de teste
```

---

## Fase 3 — PACKAGE (1 minuto)

### Passo 3.1: gerar Change Package

```bash
cd c:/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/SAAS/OmniBrain/omnibrain-triad

python tools/make_change_package.py \
  --repo /tmp/meu-projeto \
  --level L3 \
  --goal "Implement OAuth2 with JWT and refresh tokens" \
  --graph-links "disciplines/agents/skills/triad-protocol.md,disciplines/agents/skills/consensus-gate.md"
```

**Saida:** `Saved: /tmp/meu-projeto/tmp/change-packages/CHG-20260504-XXXXXX-XXXXXX.md`

**Atencao:** se voce tem **arquivos novos nao adicionados ao git**, vai aparecer warning:
> "WARNING: 3 untracked file(s) detected and NOT included in Change Package."

Nesse caso, **`git add`** primeiro e roda com `--staged`:

```bash
cd /tmp/meu-projeto && git add .
cd c:/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/SAAS/OmniBrain/omnibrain-triad
python tools/make_change_package.py --repo /tmp/meu-projeto --level L3 --goal "..." --staged
```

---

### Passo 3.2 (opcional): pre-validacao com confidence cascade

```bash
python -c "
import sys; sys.path.insert(0, 'tools')
from confidence_cascade import evaluate_cascade
cp = open('/tmp/meu-projeto/tmp/change-packages/CHG-XXX.md').read()
r = evaluate_cascade(cp, 'L3')
print(f'Tier {r.tier}: {r.decision} ({r.confidence})')
print(f'Reason: {r.reason}')
print(f'Escalate to LLM: {r.escalate_to_llm}')
"
```

**Se `decision=AUTO_REJECT`:** o cascade detectou problema (ex: hardcoded password). Corrige antes de seguir.

**Se `decision=AUTO_APPROVE`:** mudanca trivial (so comments/whitespace), pode pular Gate.

**Se `decision=ESCALATE`:** precisa do Gate. Continua.

---

### Passo 3.3 (opcional): sugestoes de padroes

```bash
python tools/suggest_pattern.py \
  --change-package /tmp/meu-projeto/tmp/change-packages/CHG-XXX.md \
  --top-k 3
```

**Saida:** WINs aplicaveis ao seu caso. Pode te ajudar a evitar reinventar a roda.

---

## Fase 4 — GATE (5-30 minutos dependendo do fallback)

### Passo 4.1: rodar Gate

```bash
python tools/run_gate.py \
  --change-package /tmp/meu-projeto/tmp/change-packages/CHG-XXX.md
```

### Caso A: voce tem Codex + Gemini CLIs

Os auditores rodam automaticamente. Voce ve:
```
## Auditor: codex
- Verdict: APPROVE
## Auditor: gemini
- Verdict: APPROVE

- Final Decision: APPROVE
```

**Pula direto pra Fase 5.**

### Caso B: voce NAO tem CLIs (fallback manual)

```
## Auditor: codex
- Verdict: UNKNOWN
- Manual Prompt: tmp/manual-prompts/CHG-XXX/codex_prompt.md

- Final Decision: CONFLICT
- Decision requires human action.
```

**O que fazer:**

1. **Abre** `tmp/manual-prompts/CHG-XXX/codex_prompt.md`
2. **Copia o conteudo todo** (e um prompt formatado)
3. **Cola no ChatGPT/Claude/Gemini web** que voce tiver acesso
4. **Recebe a resposta** (deve ter `VERDICT: APPROVE` ou `VERDICT: REJECT` no fim)
5. **Salva a resposta** em `tmp/manual-responses/CHG-XXX/codex.md`
6. **Repete pra Gemini** em `tmp/manual-responses/CHG-XXX/gemini.md`
7. **Roda Gate de novo**:

```bash
python tools/run_gate.py --change-package /tmp/meu-projeto/tmp/change-packages/CHG-XXX.md
```

Agora deve aparecer:
```
- Final Decision: APPROVE
```

---

### Passo 4.2: o que fazer com cada decisao

| Decision | O que fazer |
|---|---|
| **APPROVE** | Vai pra Fase 5 |
| **REJECT** | Le os blockers em `tmp/gate-results/CHG-XXX.md`, corrige, gera novo Change Package, roda Gate de novo |
| **CONFLICT** (L3) | 1 auditor APPROVE outro REJECT. Le ambas reviews, decide manualmente, ou pede uma terceira opiniao |
| **NEEDS_HUMAN** (L2) | Auditores nao deram verdict claro. Decisao e sua |

---

## Fase 5 — MEMORY (2 minutos)

### Passo 5.1: commit + push

```bash
cd /tmp/meu-projeto
git add .
git commit -m "feat(auth): add OAuth2 with JWT refresh"

# Se voce instalou o pre-push hook do TRIAD:
git push   # hook valida que Gate APPROVE existe pra L3
```

### Passo 5.2: registrar memoria

```bash
cd c:/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/SAAS/OmniBrain/omnibrain-triad

# WIN se foi vitoria reutilizavel
python tools/record_to_byterover.py \
  --type WIN \
  --project meu-projeto \
  --topic "oauth2-jwt-implementation" \
  --file /tmp/meu-projeto/tmp/gate-results/CHG-XXX.md \
  --tags "#discipline/agents,#type/win,#project/meu-projeto"

# DECISION se voce escolheu uma de varias opcoes (registra o "porque")
python tools/record_to_byterover.py \
  --type DECISION \
  --project meu-projeto \
  --topic "chose-jwt-over-session" \
  --text "Preferimos JWT stateless porque escala horizontalmente sem session store" \
  --tags "#discipline/agents,#type/decision"
```

### Passo 5.3: promover ao Skill Graph (se vale a pena)

**So promova se:**
- O conteudo e reutilizavel em outros projetos
- Voce validou que funciona
- Tem snippet executavel ou pattern claro

```bash
# Lista candidatos
python tools/promote_to_obsidian.py --list

# Promove (path relativo a context-hub/02_GRAPH/)
python tools/promote_to_obsidian.py \
  --source context-hub/05_INBOX/byterover-imports/MEM__WIN__meu-projeto__oauth2-jwt-implementation__*.md \
  --target disciplines/agents/skills/
```

---

## Fase 6 — Cuidar do sistema (semanal, 5 min)

### Passo 6.1: ver stats da semana

```bash
python tools/triad_stats.py --days 7
```

**Saida:**
```
- Memory Notes (window): 12
- WIN (window): 4
- LESSON (window): 2
- REVIEW (window): 6

## Top Projects (window)
- meu-projeto: 8
- outro-projeto: 4
```

### Passo 6.2: curar INBOX

```bash
# Dry-run (so mostra)
python tools/inbox_curator.py --max-age-days 30

# Aplicar (move stale para _archive/)
python tools/inbox_curator.py --max-age-days 30 --apply
```

### Passo 6.3: ler telemetria

```bash
# Ultimas 20 execucoes
tail -20 tmp/telemetry/events.jsonl | python -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line)
    print(f\"{e['ts']} {e['tool']:25s} exit={e['exit_code']} dur={e['duration_ms']}ms\")
"
```

---

## Cenarios de erro mais comuns

### "Cannot find Change Package"
- Verifica se voce passou caminho **absoluto**: `/tmp/meu-projeto/tmp/change-packages/CHG-XXX.md`

### "Change-ID contains unsafe characters"
- Voce ta passando um Change-ID inventado. Use o ID **gerado** pelo `make_change_package.py`

### "Gate decision: CONFLICT" recorrente
- Auditores discordam. Le ambos os arquivos em `tmp/manual-responses/CHG-XXX/` e decide manualmente

### "WARNING: untracked files detected"
- Faz `git add` no repo target antes de gerar o Change Package, ou usa `--staged`

### "Hook bloqueia push"
- Significa que voce nao rodou Gate, ou Gate nao deu APPROVE. Veja `tmp/gate-results/<CHG-ID>.md`

---

## TLDR — workflow no dia a dia

Apos a primeira vez, sua rotina e:

```bash
# 1. Pipeline completo (route + bundle + change_package)
python tools/start_task_flow.py --repo /tmp/projeto --task "..." --level L3

# 2. Gate
python tools/run_gate.py --change-package /tmp/projeto/tmp/change-packages/CHG-XXX.md

# 3. (se manual fallback) abre prompts, cola no Claude/GPT, salva responses

# 4. Gate de novo
python tools/run_gate.py --change-package ...

# 5. Commit + memoria
git commit -am "..." && git push
python tools/record_to_byterover.py --type WIN ...
```

5 comandos. **Isso e o TRIAD na pratica.**
