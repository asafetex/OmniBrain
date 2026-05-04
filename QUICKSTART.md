# QUICKSTART — 5 minutos pra usar o TRIAD

Voce nao precisa entender tudo. Faz **apenas estes 4 passos**.

---

## 0. Pre-requisitos (1 min)

```bash
python --version   # >= 3.10
git --version
```

So isso. **Nao precisa instalar nada.** TRIAD usa stdlib pura.

---

## 1. Validar ambiente (30 segundos)

```bash
cd c:/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/SAAS/OmniBrain/omnibrain-triad
python tools/preflight_check.py --repo .
```

Voce vai ver algo assim:
```
Summary: PASS=12 WARN=4 FAIL=1
```

`FAIL=1` provavelmente e o `codex` CLI nao instalado. **Nao tem problema** — TRIAD funciona com fallback manual.

---

## 2. Seu primeiro fluxo (3 minutos)

Vamos rodar o TRIAD em algum projeto seu. Pega qualquer um:

```bash
# Substitui pelo caminho do SEU projeto
PROJECT=/c/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/TRADING/CRIPTO-FOREX\ BOT

# Pipeline completo: route + bundle + change package, em 1 comando
python tools/start_task_flow.py \
  --repo "$PROJECT" \
  --task "Sua tarefa aqui em uma frase" \
  --level L2
```

**Output esperado:** 3 arquivos gerados em `$PROJECT/tmp/` e `omnibrain-triad/tmp/`:
- Route Artifact (sugere revisores e nos do Skill Graph)
- Context Bundle (snapshot do repo + memoria relevante)
- Change Package (com seu git diff atual)

---

## 3. Decidir se aprova (1 minuto)

Se a tarefa e **L2 ou L3**, roda o Gate:

```bash
# Pega o Change-ID gerado no passo 2 (formato CHG-YYYYMMDD-HHMMSS-XXXXXX)
CP_FILE=$(ls -t "$PROJECT/tmp/change-packages/" | head -1)

python tools/run_gate.py --change-package "$PROJECT/tmp/change-packages/$CP_FILE"
```

**Se voce nao tem Codex/Gemini CLIs**, o Gate vai dizer:
> "Comando da CLI nao encontrado. Use fallback manual."

E gerar prompts em `tmp/manual-prompts/<Change-ID>/`. Voce abre o prompt no Codex web (ou Claude/ChatGPT), cola, e salva a resposta em `tmp/manual-responses/<Change-ID>/codex.md`. Roda o Gate de novo.

---

## 4. Decidir o que fazer com a memoria

Se aprovou, registra a vitoria:

```bash
python tools/record_to_byterover.py \
  --type WIN \
  --project meu-projeto \
  --topic "o-que-eu-fiz" \
  --file "$PROJECT/tmp/gate-results/$CP_FILE" \
  --tags "#discipline/auth,#type/win"
```

Se a vitoria for **reutilizavel em outros contextos**, promove ao Skill Graph:

```bash
python tools/promote_to_obsidian.py --list   # ve candidatos
python tools/promote_to_obsidian.py \
  --source context-hub/05_INBOX/byterover-imports/<arquivo>.md \
  --target disciplines/agents/skills/
```

---

## Pronto. Voce usou o TRIAD.

A primeira vez parece complicado. Da segunda em diante voce so digita 1 comando: `start_task_flow.py`.

---

## Como continuar

| Voce quer... | Leia |
|---|---|
| Ver caso real do inicio ao fim | `TUTORIAL.md` |
| Saber o que cada tool faz | `TOOLS.md` |
| Cenarios praticos (auth, bug, refactor) | `PLAYBOOKS.md` |
| Filosofia e arquitetura | `omnibrain-triad/docs/00_overview.md` |
| Customizar (config, templates, hooks) | `omnibrain-triad/docs/02_setup.md` |

---

## Cheat sheet (cole numa aba do navegador)

```bash
# Validar
python tools/preflight_check.py --repo .

# Rodar fluxo completo
python tools/start_task_flow.py --repo <repo> --task "..." --level L2

# Gate
python tools/run_gate.py --change-package <cp>.md

# Buscar memoria
python tools/search_memory.py --query "..." --top-k 5

# Consultar oraculo
python tools/triad_oracle.py --query "..."

# Sugerir padroes
python tools/suggest_pattern.py --change-package <cp>.md

# Curar INBOX
python tools/inbox_curator.py --max-age-days 30

# Stats semanais
python tools/triad_stats.py --days 7

# Recuperar sessao travada
python tools/recover_session.py --repo <repo> --change-id <CHG-ID>
```
