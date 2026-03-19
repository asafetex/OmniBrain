# 03 Daily Workflow

## Rotina de 5 passos

1. Classificar L1/L2/L3:
   - Use `docs/04_l1_l2_l3.md`.
2. Rotear contexto:
   - Use `project-template/CLAUDE.md`.
   - Abra 2 a 5 nos do Skill Graph.
   - Opcional: rode `tools/route_task.py` para escolher intent/executor/revisores.
   - Opcional: gerar bundle consolidado com `tools/build_context_bundle.py`.
3. Executar `diff-first` em branch:
   - Planejar, implementar, revisar apenas por `git diff`.
4. Rodar PreGate opcional e Gate obrigatorio quando aplicavel:
   - L3: Codex + Gemini obrigatorio.
5. Capturar memoria e promover conhecimento:
   - Modo padrao: INBOX do Obsidian (`05_INBOX/byterover-imports`).
   - Opcional: ByteRover CLI ativo.
   - Promover so conteudo reutilizavel para o Graph.

## Exemplo pratico: Spark SQL join explode + performance

Contexto:
- Pipeline incrementou custo e dobrou linhas apos join.
- Tarefa classificada como `L3` (impacto em dado de producao).

Passo a passo:

1. Roteamento de nós:
   - `disciplines/data-engineering/skills/spark-sql/joins.md`
   - `disciplines/data-engineering/skills/spark-sql/performance.md`
   - `disciplines/data-engineering/skills/data-quality/duplicates.md`
2. Implementacao em branch:
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
6. Resolver bloqueios, retestar e repetir ate `APPROVE`.
7. Registrar memoria:

```bash
python tools/record_to_byterover.py \
  --type WIN \
  --project omnibrain \
  --topic spark-join-explode \
  --file tmp/gate-results/<Change-ID>.md \
  --tags "#discipline/data-engineering,#type/win,#project/omnibrain"
```

8. No modo Obsidian-only, confirme arquivo novo em `context-hub/05_INBOX/byterover-imports/`.
9. Promover para Graph se replicavel:
   - snippet minimo + validacao + armadilhas documentadas.

## Retomada de sessao travada

Quando a execucao interromper no meio:

1. Rode:

```bash
python tools/recover_session.py --repo . --change-id <Change-ID>
```

2. Leia o relatorio gerado em `tmp/recovery-reports/REC-*.md`.
3. Use o bloco `Recovery Prompt Seed` para reiniciar em novo executor.
4. Se houver `CONFLICT` ou `UNKNOWN`, complete respostas manuais faltantes e rerode o Gate.

## Roteamento automatico (opcional)

Para tarefas repetitivas, rode:

```bash
python tools/preflight_check.py --repo .
python tools/route_task.py --task "join explode em spark" --level L3
python tools/start_task_flow.py --repo . --task "join explode em spark" --level L3 --preflight
python tools/build_context_bundle.py --repo . --task "join explode em spark" --level L3 --auto-route
python tools/install_pre_push_hook.py --repo .
```

Isso aplica `configs/routing.json` e preenche nos de grafo automaticamente quando `--graph-links` nao for informado.

## Governanca no push (opcional recomendado)

Para reduzir bypass humano em L3:

1. Instale hook:

```bash
python tools/install_pre_push_hook.py --repo .
```

2. O `git push` passa a validar:
   - ultimo Change Package,
   - se for L3, exige Gate `APPROVE`.

3. Relatorio de valor semanal:

```bash
python tools/triad_stats.py --days 7
```
