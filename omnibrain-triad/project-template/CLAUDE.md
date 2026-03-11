# CLAUDE.md

Você é executor de mudanças neste repositório.

## Regras fixas

- Fluxo obrigatório: `PLAN -> DIFF -> REVIEW -> TEST -> COMMIT`.
- Sempre operar em branch de tarefa.
- Sempre revisar por `git diff`.
- L3 só finaliza após Gate com Codex + Gemini.

## Context Hub

Consuma o hub em:

- `../omnibrain-triad/context-hub/` (pasta ao lado), ou
- `./omnibrain-triad/context-hub/` (submodule local)

Priorize:

- `00_HOME.md`
- `01_MANIFEST/governance-levels.md`
- `02_GRAPH/index.md`

## Roteamento de intent -> nós

- Spark SQL join explode:
  - `disciplines/data-engineering/skills/spark-sql/joins.md`
  - `disciplines/data-engineering/skills/data-quality/duplicates.md`
- Spark performance:
  - `disciplines/data-engineering/skills/spark-sql/performance.md`
- Incremental/merge:
  - `disciplines/data-engineering/skills/spark-sql/incremental.md`
  - `disciplines/data-engineering/skills/spark-sql/windows.md`
- Governança TRIAD:
  - `disciplines/agents/skills/triad-protocol.md`
  - `disciplines/agents/skills/consensus-gate.md`
- Memória e promoção:
  - `disciplines/agents/skills/win-protocol.md`
  - `disciplines/agents/skills/memory-routing.md`

## Procedimento mínimo por tarefa

1. Classificar nível L1/L2/L3.
2. Carregar 2-5 nós do grafo.
3. Implementar em branch.
4. Gerar Change Package por `tools/make_change_package.py`.
5. Rodar Gate por `tools/run_gate.py` quando exigido.
6. Registrar `WIN/LESSON` por `tools/record_to_byterover.py`.

