# 06 Gate Spec

## Objetivo

Decidir de forma objetiva se uma mudança pode seguir para commit/merge.

## Entrada mínima

- Change Package válido.
- Diff presente.
- Nível (`L1/L2/L3`) informado.

## Critérios objetivos de REJECT

- Falha funcional evidente no diff.
- Violação de segurança, privacidade ou compliance.
- Regressão provável sem mitigação.
- Falta de teste/validação para cenário crítico.
- Change Package incompleto em L3.
- Contradição com contrato/ADR conhecido.

## Critérios de APPROVE

- Sem blockers críticos.
- Riscos documentados e aceitáveis.
- Testes/validações mínimas foram definidos.
- A implementação atende os critérios de aceitação.

## Regra L3 (obrigatória)

- Rodar Codex + Gemini.
- Se qualquer um retornar `VERDICT: REJECT` => `REJECT`.
- Se ambos retornarem `VERDICT: APPROVE` => `APPROVE`.
- Se faltou verdict ou houve ambiguidade => `CONFLICT` e decisão humana.
- Precedência de verdict por auditor:
  - `VERDICT` vindo da CLI (stdout/stderr),
  - se não houver `VERDICT`, inferência da CLI:
    - `REJECT` quando houver sinal claro de blocker (ex.: `[P1]`, regressão funcional explícita),
    - `APPROVE` quando houver sinal explícito de ausência de blockers (ex.: "no blocking defects"),
  - senão `VERDICT` vindo de resposta manual em `tmp/manual-responses/<Change-ID>/<auditor>.md`,
  - senão `UNKNOWN`.

## Fluxo manual oficial (fallback)

1. Rodar:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
2. O script salva prompts em:
   - `tmp/manual-prompts/<Change-ID>/`.
3. Cole o prompt do auditor no CLI correspondente (ex.: Gemini).
4. Salve a resposta completa em:
   - `tmp/manual-responses/<Change-ID>/gemini.md`
   - a resposta manual deve ser mais nova que o prompt da execução atual (o script ignora resposta antiga).
5. Rode o Gate novamente para consolidar decisão:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`

## Saída padronizada por auditor

```text
Blockers:
- ...

Edge cases:
- ...

Missing tests:
- ...

Security/Compliance:
- ...

VERDICT: [APPROVE | REJECT]