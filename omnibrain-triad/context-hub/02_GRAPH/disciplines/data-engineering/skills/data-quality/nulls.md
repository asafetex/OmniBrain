# Data Quality Nulls

## Quando usar

Quando colunas chave ou campos críticos apresentam null.

## Objetivo

Preservar integridade de chave e evitar erro silencioso de join/agregação.

## Checklist

- Identificar colunas críticas (join key, PK, FK, métricas).
- Definir política por coluna:
  - rejeitar,
  - preencher default controlado,
  - encaminhar para quarantena.
- Medir taxa de null por lote.
- Validar impacto em joins e contagens.

## Snippet mínimo

```sql
SELECT *
FROM src
WHERE business_key IS NOT NULL;
```

## Validação objetiva

- `null_rate(business_key) == 0` no dataset final esperado.
- registros descartados/quarentenados contabilizados.

## Armadilhas

- preencher null com valor ambíguo sem rastreio.
- aceitar null em chave de merge.

## Links relacionados

- [duplicates](duplicates.md)
- [spark incremental](../spark-sql/incremental.md)

