# Consensus Gate

## Quando usar

L3 obrigatório; L2 recomendado sob risco.

## Objetivo

Tomar decisão determinística de aprovação/rejeição.

## Checklist

- executar revisores configurados;
- exigir seções padrão por auditor;
- extrair `VERDICT` de cada saída;
- aplicar regra de decisão por nível.

## Snippet mínimo

```text
if L3 and (codex == REJECT or gemini == REJECT): REJECT
elif L3 and (codex == APPROVE and gemini == APPROVE): APPROVE
else: CONFLICT
```

## Validação objetiva

- decisão final gravada.
- evidências por auditor anexadas.

## Armadilhas

- aceitar output sem parse de verdict;
- ignorar ausência de auditor obrigatório.

## Links relacionados

- [triad-protocol](triad-protocol.md)
- [win-protocol](win-protocol.md)

