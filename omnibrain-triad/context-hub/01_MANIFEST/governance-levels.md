# Governance Levels

## L1

Mudança simples, baixo impacto.

Checklist:
- escopo local;
- rollback fácil;
- sem impacto de segurança.

Gate:
- não obrigatório.

## L2

Mudança moderada.

Checklist:
- impacto funcional local/regional;
- critérios de aceitação claros;
- testes mínimos definidos.

Gate:
- opcional (Codex ou Gemini), PreGate opcional.

## L3

Mudança crítica.

Checklist:
- impacto sistêmico ou risco alto;
- Change Package completo;
- risco e mitigação explícitos.

Gate:
- obrigatório com Codex + Gemini.
- regra: qualquer `REJECT` => rejeitado.

