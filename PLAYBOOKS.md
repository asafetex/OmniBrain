# PLAYBOOKS — Cenarios praticos

Receitas testadas para situacoes que voce vai encontrar.

---

## Playbook 1: "Adicionar feature critica" (ex: auth, billing, payments)

**Por que e L3:** mexe com seguranca, dinheiro ou dados sensiveis.

```bash
# 1. Consulta historico antes de comecar
python tools/triad_oracle.py --query "OAuth2 JWT token validation"

# 2. Pipeline
python tools/start_task_flow.py --repo <projeto> --task "..." --level L3 --preflight

# 3. Implementa em branch (diff-first)
cd <projeto>
git checkout -b feat/auth-feature
# ...edit, test...
git add .

# 4. Change Package staged
cd /path/to/omnibrain-triad
python tools/make_change_package.py --repo <projeto> --level L3 --goal "..." --staged

# 5. Pre-validacao com cascade (deteta security violations)
python -c "
import sys; sys.path.insert(0, 'tools')
from confidence_cascade import evaluate_cascade
cp = open('<projeto>/tmp/change-packages/CHG-XXX.md').read()
r = evaluate_cascade(cp, 'L3')
print(f'{r.tier}: {r.decision} - {r.reason}')
"

# 6. Sugestoes de padroes existentes
python tools/suggest_pattern.py --change-package <cp>.md

# 7. Gate (L3 obrigatorio)
python tools/run_gate.py --change-package <cp>.md
# Se manual fallback: copia prompts, cola no LLM, salva responses, roda Gate de novo

# 8. Commit + push (hook valida)
cd <projeto> && git commit -am "feat(auth): ..." && git push

# 9. Memoria
cd /path/to/omnibrain-triad
python tools/record_to_byterover.py --type WIN --project <p> --topic <t> --file <gate-result>.md
```

**Tempo total:** 30-60min (dependendo de quanto manual fallback voce faz).

---

## Playbook 2: "Bug fix critico em producao"

**Cenario:** algo quebrou, voce precisa corrigir RAPIDO mas com qualidade.

```bash
# 1. Pula oraculo (urgente). Vai direto pra implementacao.
cd <projeto>
git checkout -b fix/<descricao-bug>
# ... corrige, escreve teste de regressao...
git add .

# 2. Change Package
cd /path/to/omnibrain-triad
python tools/make_change_package.py --repo <projeto> --level L3 \
  --goal "fix: <descricao>" \
  --context "Bug em producao impactando X usuarios" \
  --risks "- Regressao se fix muda comportamento existente\n- Side effects em Y"

# 3. Cascade pre-validation (evita escalar pro LLM se fix e trivial)
python -c "..."  # como playbook 1

# 4. Se cascade diz AUTO_APPROVE: pula Gate, commit direto
# Se ESCALATE: roda Gate

# 5. Apos merge, registra LESSON (nao WIN — o bug existir e a licao)
python tools/record_to_byterover.py --type LESSON --project <p> \
  --topic "bug-Y-em-Z" \
  --text "Causa raiz: ... Como detectar antes: ..." \
  --tags "#discipline/<area>,#type/lesson,#severity/high"
```

---

## Playbook 3: "Refactor de modulo grande"

**Cenario:** voce vai mexer em 50+ arquivos. Risco alto de regressao.

```bash
# 1. Verifica se ja fizeram refactor parecido
python tools/search_memory.py --query "refactor module restructure"

# 2. PLAN antes de mexer
python tools/record_to_byterover.py --type PLAN --project <p> \
  --topic "refactor-modulo-X" \
  --text "Escopo: arquivos A,B,C
Risco: regressao em testes Y,Z
Criterio sucesso: pytest passa + lint clean + sem mudanca de comportamento" \
  --tags "#type/plan"

# 3. Branch
cd <projeto>
git checkout -b refactor/modulo-X
# ... refactor + testes existentes passando ...

# 4. Como diff e gigante, gera com --staged pra controlar escopo
git add <arquivos-relacionados-apenas>
cd /path/to/omnibrain-triad
python tools/make_change_package.py --repo <projeto> --level L2 \
  --goal "refactor: modulo X" \
  --graph-links "disciplines/agents/skills/refactor-protocol.md" \
  --staged

# 5. Performance: diff de 5MB+ pode estourar prompt. Se sim:
# - Split em multiplos Change Packages por subdiretorio
# - Use --level L2 (mais permissivo) e roda multiplos Gates pequenos

# 6. Gate
python tools/run_gate.py --change-package <cp>.md

# 7. Apos merge, WIN se for um pattern reutilizavel
python tools/record_to_byterover.py --type WIN --project <p> --topic "refactor-pattern"
```

---

## Playbook 4: "Sessao travou, voltei dias depois"

**Cenario:** voce parou no meio, nao lembra o que estava fazendo.

```bash
# 1. Lista Change Packages recentes
ls -lt <projeto>/tmp/change-packages/ | head -5

# 2. Recover na que voce estava
python tools/recover_session.py --repo <projeto> --change-id CHG-XXX

# Saida: relatorio com:
# - Branch atual
# - Diff atual vs Change Package original
# - Gate decision anterior (se rodou)
# - Recovery prompt seed (cola no LLM pra continuar)

# 3. Se Gate ja deu APPROVE, voce so precisa commit + push
# Se REJECT, le os blockers e corrige
```

---

## Playbook 5: "Comecar projeto novo do zero"

```bash
# 1. Bootstrap
cd /path/to/omnibrain-triad
python bootstrap.py --target /caminho/novo-projeto

# 2. Inicializa git no novo projeto
cd /caminho/novo-projeto
git init && git add . && git commit -m "initial scaffold"

# 3. Instala hook L3
cd /path/to/omnibrain-triad
python tools/install_pre_push_hook.py --repo /caminho/novo-projeto

# 4. Copia config.example.json -> config.json no NOVO projeto e ajusta
cd /caminho/novo-projeto/tools
cp config.example.json config.json
# edita pra ativar Codex/Gemini/byterover se voce tem

# 5. Valida
python tools/preflight_check.py --repo /caminho/novo-projeto
```

---

## Playbook 6: "Auditoria mensal do TRIAD"

**Quando:** primeira sexta de cada mes.

```bash
# 1. Stats do mes
python tools/triad_stats.py --days 30 > tmp/stats-mensal.md

# 2. Curator
python tools/inbox_curator.py --max-age-days 30 --apply

# 3. Telemetria — quais tools sao usadas?
python -c "
import json
from collections import Counter
events = [json.loads(l) for l in open('tmp/telemetry/events.jsonl')]
counter = Counter(e['tool'] for e in events)
for tool, count in counter.most_common():
    print(f'{tool:30s} {count}')
"

# 4. Tools nunca usadas? Considera deprecar
# Tools com exit_code != 0 frequente? Investiga

# 5. Promote candidates do INBOX
python tools/promote_to_obsidian.py --list
# Para cada WIN/LESSON util, promove
```

---

## Playbook 7: "Como decidir se promove ou nao"

**Pergunta-se:**
1. Esse padrao se aplica em **outros projetos**?
2. Tem **snippet executavel** ou pattern claro?
3. Foi **validado em uso real**?
4. Ainda vai ser **relevante daqui a 6 meses**?

**4 sins -> promove para `disciplines/<area>/skills/`**
**3 sins -> deixa no INBOX, marca para revisao em 30 dias**
**0-2 sins -> arquiva (nao promove)**

---

## Playbook 8: "Como configurar o sistema com CLIs reais"

### Codex CLI

1. Instala: `npm install -g @openai/codex` (ou similar)
2. Login: `codex login`
3. Edita `tools/config.json`:
```json
{
  "auditors": {
    "codex": {
      "enabled": true,
      "cmd": "codex",
      "args": ["review", "-"],
      "timeout_seconds": 240,
      "input_mode": "stdin"
    }
  }
}
```

### Gemini CLI

Similar, mas:
```json
{
  "gemini": {
    "enabled": true,
    "cmd": "gemini",
    "args": ["-"],
    "timeout_seconds": 120
  }
}
```

### ByteRover CLI

```json
{
  "byterover": {
    "enabled": true,
    "cmd": "brv",
    "args": ["curate"],
    "timeout_seconds": 30
  }
}
```

### Sem CLI — modo manual

Mantem tudo `enabled: false`. TRIAD vai gerar prompts em `tmp/manual-prompts/<CHG-ID>/` e voce cola onde quiser (ChatGPT web, Claude, qualquer LLM).

---

## Playbook 9: "Quero usar TRIAD em CI/GitHub Actions"

```yaml
# .github/workflows/triad-l3.yml
name: TRIAD L3 Gate
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  l3-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      
      - name: Generate Change Package
        run: |
          python omnibrain-triad/tools/make_change_package.py \
            --repo . --level L3 --goal "${{ github.event.pull_request.title }}"
      
      - name: Run Cascade pre-validation
        run: |
          python -c "
          import sys; sys.path.insert(0, 'omnibrain-triad/tools')
          from confidence_cascade import evaluate_cascade
          import glob
          cp = open(glob.glob('tmp/change-packages/CHG-*.md')[0]).read()
          r = evaluate_cascade(cp, 'L3')
          print(f'Cascade: {r.decision}')
          if r.decision == 'AUTO_REJECT':
              exit(1)
          "
      
      - name: Run Gate (manual mode if no CLIs)
        run: |
          python omnibrain-triad/tools/run_gate.py \
            --change-package $(ls -t tmp/change-packages/CHG-*.md | head -1)
```

---

## Playbook 10: "Quero ver se sistema esta saudavel"

```bash
# 1. Lint + tests
cd omnibrain-triad
python -m ruff check tools/ tests/ bootstrap.py
python -m pytest tests/ -q -p no:anchorpy

# 2. Smoke test rapido
python tools/preflight_check.py --repo .

# 3. Telemetria recente
tail -20 tmp/telemetry/events.jsonl

# 4. Tamanho do INBOX (red flag se >100 itens)
ls context-hub/05_INBOX/byterover-imports/ | wc -l

# 5. Memorias por tipo
python tools/triad_stats.py --days 90
```

---

## Erros comuns e fix rapido

| Sintoma | Provavel causa | Fix |
|---|---|---|
| `Change-ID contains unsafe characters` | Voce inventou ID | Use o ID gerado pelo `make_change_package.py` |
| `WARNING: untracked files detected` | Arquivos novos nao add'ed | `git add` antes ou use `--staged` |
| `Final Decision: CONFLICT` | Auditores discordam | Le ambas reviews em `tmp/manual-responses/`, decide manual |
| `Comando da CLI nao encontrado` | CLI nao instalado | Use fallback manual: cola prompt em LLM web |
| Hook bloqueia push | Sem Gate APPROVE | Roda `run_gate.py`, ou pula com `--no-verify` (auditado em log) |
| Stale memorias acumulando | Voce nao curou | Roda `inbox_curator.py --apply` |
| `No memories matched` no oraculo | Nao tem historico ainda | Continue trabalhando, registra WINs/LESSONs, eventualmente acumula |

---

## Quando NAO usar TRIAD

- **L1 trivial** (typo fix, rename) — overhead nao compensa. Commit direto.
- **Exploratorio/spike** — voce ainda nao sabe o que vai fazer. TRIAD e pra mudancas com escopo claro.
- **Hotfix sob pressao extrema** — se cada minuto conta, pula gate. Registra WIN/LESSON depois.

TRIAD e pra mudancas que **valem ser auditadas e lembradas**.
