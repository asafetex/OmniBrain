# MEM::WIN::sandbox-l3-e2e::deterministic-two-decimal-validation::20260319-1827

## Metadata
- Type: WIN
- Project: sandbox-l3-e2e
- Topic: deterministic-two-decimal-validation
- Timestamp: 2026-03-19 18:27:00
- Tags: #type/win #project/sandbox-l3-e2e #discipline/agents

## Refs
- CHG-20260319-181823
- tmp/gate-results/CHG-20260319-181823.md
- sandbox-l3-e2e/checkout.py
- sandbox-l3-e2e/test_checkout.py

## Content
Regra vencedora: para validar float monetario em L3 sem falso positivo/falso negativo numerico, aplicar `Decimal(str(valor))` e exigir expoente >= -2.

Checklist reaproveitavel:
- aplicar regra no ponto de validacao de entrada;
- cobrir testes de aceite/rejeicao para 2 e 3 casas decimais;
- cobrir casos de artefato float (`0.1 + 0.2`) e sub-centavo;
- rodar Gate L3 ate `Final Decision: APPROVE`.