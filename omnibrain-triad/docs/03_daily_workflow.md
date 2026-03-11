# 03 Daily Workflow

## Rotina de 5 passos

1. Classificar L1/L2/L3:
   - Use `docs/04_l1_l2_l3.md`.
2. Rotear contexto:
   - Use `project-template/CLAUDE.md`.
   - Abra 2 a 5 nós do Skill Graph.
3. Executar `diff-first` em branch:
   - Planejar, implementar, revisar apenas por `git diff`.
4. Rodar PreGate opcional e Gate obrigatório quando aplicável:
   - L3: Codex + Gemini obrigatório.
5. Capturar memória e promover conhecimento:
   - Registrar `WIN`/`LESSON` no ByteRover.
   - Promover só conteúdo reutilizável para o Graph.

## Exemplo prático: Spark SQL join explode + performance

Contexto:
- Pipeline incrementou custo e dobrou linhas após join.
- Tarefa classificada como `L3` (impacto em dado de produção).

Passo a passo:

1. Roteamento de nós:
   - `disciplines/data-engineering/skills/spark-sql/joins.md`
   - `disciplines/data-engineering/skills/spark-sql/performance.md`
   - `disciplines/data-engineering/skills/data-quality/duplicates.md`
2. Implementação em branch:
   - dedupe de chave no lado direito;
   - validação de contagem antes/depois;
   - ajuste de partição e broadcast seletivo.
3. Gerar Change Package:

```bash
python tools/make_change_package.py \
  --repo . \
  --level L3 \
  --goal "Corrigir join explode e reduzir shuffle em job Spark" \
  --graph-links "disciplines/data-engineering/skills/spark-sql/joins.md,disciplines/data-engineering/skills/spark-sql/performance.md,disciplines/data-engineering/skills/data-quality/duplicates.md"
```

4. Rodar Gate:

```bash
python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md
```

5. Se Gemini estiver em fallback manual:
   - copiar prompt de `tmp/manual-prompts/<Change-ID>/gemini_prompt.md`;
   - executar no Gemini CLI manualmente;
   - salvar resposta em `tmp/manual-responses/<Change-ID>/gemini.md`;
   - rodar `run_gate.py` novamente para consolidar `VERDICT`.
6. Resolver bloqueios, retestar e repetir até `APPROVE`.
7. Registrar memória:

```bash
python tools/record_to_byterover.py \
  --type WIN \
  --project omnibrain \
  --topic spark-join-explode \
  --file tmp/gate-results/<Change-ID>.md \
  --tags "#discipline/data-engineering,#type/win,#project/omnibrain"
```

8. Promover para Graph se replicável:
   - snippet mínimo + validação + armadilhas documentadas.
