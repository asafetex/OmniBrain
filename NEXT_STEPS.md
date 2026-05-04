# NEXT STEPS — Checklist apos a sessao de construcao

Voce **terminou de construir**. Agora **comeca a usar**. Este arquivo e seu guia para os proximos 30 dias.

---

## Regra principal

**NAO ADICIONE NOVAS FEATURES AO TRIAD.** O sistema esta em 8.2/10. Cada feature nova adiciona menos valor que a anterior. Voce vai entrar em armadilha de bonsai.

So volta a construir depois de ter **dados reais de uso** (telemetria de 30 dias).

---

## Semana 1 — Primeira aplicacao real (1h total ao longo da semana)

### Checkpoint 1.1 — Escolher problema real (10 min)

Abra o vault e responda:
- Qual o problema mais consequencial que esta parado?
- Posso descreve-lo em 1 frase?
- Tem `git diff` envolvido (codigo) ou e decisao pura?

**Se for codigo:** vai pra checkpoint 1.2.
**Se for decisao:** roda apenas o oraculo (`triad_oracle.py --query "..."`). 5 min, fim.

### Checkpoint 1.2 — Setup do projeto-alvo (5 min)

```bash
# Substitua pelo SEU projeto
PROJ="/caminho/projeto-real"
cd "$PROJ"
git status        # esta limpo? esta em repo git?

# Se nao for repo git:
git init && git add . && git commit -m "initial"

# Valida
cd c:/Users/PC/Desktop/ASAFE/PROJETOS/DESENVOLVIMENTO/SAAS/OmniBrain/omnibrain-triad
python tools/preflight_check.py --repo "$PROJ"
```

**Criterio de sucesso:** `Summary: PASS=>=10 FAIL=0`.

### Checkpoint 1.3 — Primeiro fluxo real (30 min)

Faz a tarefa em branch dedicada. Quando terminar a implementacao:

```bash
python tools/start_task_flow.py \
  --repo "$PROJ" \
  --task "<descricao da tarefa em 1 frase>" \
  --level L2

# Roda Gate (provavelmente manual fallback)
python tools/run_gate.py --change-package "$PROJ/tmp/change-packages/CHG-XXX.md"
```

Se for manual fallback:
1. Abra o prompt em `omnibrain-triad/tmp/manual-prompts/CHG-XXX/codex_prompt.md`
2. Cole no Claude.ai (voce esta logado)
3. Salve resposta em `tmp/manual-responses/CHG-XXX/codex.md`
4. Repita pra Gemini ou pula (deixa UNKNOWN)
5. Roda Gate de novo

### Checkpoint 1.4 — Registrar memoria (5 min)

```bash
python tools/record_to_byterover.py \
  --type WIN \
  --project <projeto> \
  --topic "<topico-curto>" \
  --file "<gate-result>.md" \
  --tags "#discipline/<area>,#type/win"
```

### Checkpoint 1.5 — Anotar atrito (5 min)

Crie `tmp/dogfood-feedback.md` no projeto e anote:

```markdown
## Sessao 1 — <data>

### O que funcionou
- ...

### O que atrapalhou
- ...

### O que faltou
- ...

### Tempo gasto vs valor entregue
- ...
```

**Esta anotacao e o input mais valioso pra calibrar o TRIAD.**

---

## Semana 2 — Segunda e terceira aplicacao (acumular dados)

Repete o fluxo da semana 1 em **mais 2 tarefas reais**. Acumula notas em `dogfood-feedback.md`.

Apos 3 sessoes voce ja tem dados pra:
- Identificar 2-3 atritos recorrentes
- Saber se manual fallback e tolerable ou desistir
- Sentir se o oraculo ajuda ou e overhead

---

## Semana 3 — Calibrar baseado em telemetria

### Checkpoint 3.1 — Olhar telemetria

```bash
cd omnibrain-triad
tail -100 tmp/telemetry/events.jsonl | python -c "
import json, sys
from collections import Counter
events = [json.loads(l) for l in sys.stdin]
counter = Counter(e['tool'] for e in events)
print('Tools mais usadas (3 semanas):')
for tool, count in counter.most_common():
    print(f'  {tool:25s} {count}')
print(f\"\\nFalhas: {sum(1 for e in events if e['exit_code'] != 0)}\")
print(f\"Tempo medio: {sum(e['duration_ms'] for e in events) / len(events):.0f}ms\")
"
```

### Checkpoint 3.2 — Decidir o que manter

Para cada tool, classifica:
- **CORE** (usei 5+ vezes) — mantem, talvez melhora
- **OK** (usei 1-4 vezes) — mantem, deixa quieta
- **MORTA** (0 uso) — remove ou marca como deprecated

### Checkpoint 3.3 — Calibrar thresholds

Cole o conteudo do `dogfood-feedback.md` em uma sessao Claude e me peca:
> "Aqui estao 3 sessoes reais de uso do TRIAD. Calibre os thresholds e me sugira 1 melhoria especifica."

---

## Semana 4 — Decisao estrategica

Apos 3 semanas de uso real, voce tem evidencia pra decidir:

### Se TRIAD ajudou (>= 70% das sessoes acelerou ou trouxe insight)
- Mantem como ferramenta principal
- Configura CLIs reais (Codex, Gemini) para automatizar
- Considera evoluir cascade tier 2 com mais memorias
- Reabra o backlog Tier C/D com dados na mao

### Se TRIAD atrapalhou (>= 50% das sessoes adicionou overhead sem valor)
- Identifica os atritos especificos
- Reduz escopo: mantem so as 5 tools que voce usou
- Os outros 15 viram opcionais
- Descarta sem culpa — voce **provou empiricamente** que nao serve

### Se foi neutro (ambiguo)
- Considera que voce ainda nao deu chance suficiente
- Estende mais 2 semanas
- OU descarta agora — neutro = nao agrega

---

## Sinais de alerta (red flags)

### "Voltei a construir o TRIAD em vez de usar"
**Por que e ruim:** voce esta procurando excusa pra nao dogfoodar.
**Acao:** fecha o repo do OmniBrain e abre o projeto onde tem trabalho real.

### "Manual fallback me cansa"
**Por que e ruim:** o overhead nao compensa.
**Acao:** ou instala Codex/Gemini CLIs, ou aceita que TRIAD e so para mudancas L3 criticas (nao L1/L2 cotidianas).

### "INBOX esta com 100+ memorias e eu nunca abro"
**Por que e ruim:** memoria sem uso e dump.
**Acao:** roda `inbox_curator.py --apply --max-age-days 14` agressivamente.

### "Pulei o Gate em mudanca L3 com `--no-verify`"
**Por que e ruim:** quebrou o contrato. Hook foi instalado por motivo.
**Acao:** ou voce confia no Gate, ou desinstala. Inconsistencia destroi o sistema.

---

## O que NAO fazer (anti-padroes)

❌ **Adicionar feature porque "seria legal ter"** — espera dado de uso  
❌ **Refatorar tools que ja funcionam** — frigobar pode ate estar feio mas resfria  
❌ **Documentar mais** — ja tem 4 docs cobrindo 95% dos casos  
❌ **Criar mais testes sem motivo** — ja tem 123  
❌ **Voltar a esta sessao perguntando "mais alguma coisa?"** — a resposta e nao  
❌ **Usar TRIAD em mudanca trivial** (typo, rename) — overhead nao compensa  
❌ **Esperar Codex/Gemini CLIs** — manual fallback funciona, comeca com ele  
❌ **Promover toda memoria pro Skill Graph** — so promove o que e reusavel mesmo  

---

## O que fazer (padroes a seguir)

✅ **Usar TRIAD em pelo menos 1 mudanca por semana** (mesmo que pequena, pra manter habito)  
✅ **Sempre consultar o oraculo antes de comecar** (5 segundos)  
✅ **Sempre registrar WIN apos approve** (10 segundos)  
✅ **Olhar telemetria toda sexta** (1 minuto)  
✅ **Curar INBOX uma vez por mes** (5 minutos)  
✅ **Anotar atritos em dogfood-feedback.md** (1 minuto por sessao)  

---

## Quando me chamar de volta

Volta aqui (ou em outra sessao Claude) **apenas se**:

1. ✅ Voce dogfoodou >= 5 vezes em projeto real
2. ✅ Voce tem `dogfood-feedback.md` com observacoes
3. ✅ Voce identificou 1-3 atritos recorrentes
4. ✅ Voce quer **calibrar com base em dado real**

**Nao volta antes.** Se voltar antes, vou te pedir pra dogfoodar primeiro.

---

## Resumo em 1 frase

> Voce tem ferramenta excelente. Falta voce **usa-la**.

Nada que voce le aqui substitui o ato de abrir um projeto e rodar `python tools/start_task_flow.py` numa tarefa real.

**Boa sorte.**

---

*Gerado ao final da sessao de construcao em 2026-05-04. Score do sistema: 8.2/10. Score do operador: a definir nas proximas 4 semanas.*
