# MEM::WIN::sandbox-l3-e2e::checkout-currency-hardening-safe-validation::20260312-0108

## Metadata
- Type: WIN
- Project: sandbox-l3-e2e
- Topic: checkout-currency-hardening-safe-validation
- Timestamp: 2026-03-12 01:08:57
- Tags: #discipline/agents #type/win #project/sandbox-l3-e2e

## Refs
- CHG-20260312-010613
- tmp/gate-results/CHG-20260312-010613.md

## Content
WIN: validação de currency agora rejeita entrada não-string e normaliza lowercase antes da checagem de allowlist, evitando TypeError em payload inválido.
