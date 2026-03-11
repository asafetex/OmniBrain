# AGENTS.md

## Codex Review Contract

Ao revisar um Change Package, responda exatamente nesta estrutura:

1. Blockers
2. Edge cases
3. Missing tests
4. Suggestions
5. VERDICT: APPROVE ou REJECT

## Regras

- Revisão sempre baseada em Change Package e `git diff`.
- Referencie riscos e critérios de aceitação.
- Para L3, seja objetivo: sem verdict implícito.
- Se não houver evidência suficiente, retornar `VERDICT: REJECT`.

## Contexto obrigatório

Use links relevantes do hub:

- `../omnibrain-triad/context-hub/02_GRAPH/...`

No mínimo:

- `disciplines/agents/skills/change-package.md`
- `disciplines/agents/skills/consensus-gate.md`

