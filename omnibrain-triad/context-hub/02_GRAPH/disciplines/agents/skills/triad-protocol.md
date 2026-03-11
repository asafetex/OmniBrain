# TRIAD Protocol

## Quando usar

Em mudanças L3 e em L2 com risco relevante.

## Objetivo

Garantir consenso multiagente com critério objetivo de liberação.

## Checklist

- Classificar nível L1/L2/L3.
- Gerar Change Package com diff completo.
- Rodar PreGate opcional (DeepSeek/CodeRabbit).
- Rodar Gate principal:
  - Codex review
  - Gemini review
- Consolidar decisão:
  - ambos approve => APPROVE
  - qualquer reject => REJECT
  - ambíguo => CONFLICT

## Snippet mínimo

```text
L3:
  codex_verdict + gemini_verdict -> decision
```

## Validação objetiva

- arquivo de gate gerado em `tmp/gate-results/<Change-ID>.md`.
- decisão final explícita.

## Armadilhas

- usar PreGate como substituto do Gate principal.
- aceitar review sem `VERDICT`.

## Links relacionados

- [change-package](change-package.md)
- [consensus-gate](consensus-gate.md)

