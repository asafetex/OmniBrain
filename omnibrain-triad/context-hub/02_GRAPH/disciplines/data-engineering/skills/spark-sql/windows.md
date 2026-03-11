# Spark SQL Windows

## Quando usar

Quando precisar de ranking, dedupe determinístico, acumulados e comparações intra-grupo.

## Objetivo

Aplicar funções de janela sem introduzir ambiguidade ou custo desnecessário.

## Checklist

- Definir `PARTITION BY` coerente com regra de negócio.
- Definir `ORDER BY` determinístico (sem empate implícito).
- Validar impacto de `ROWS BETWEEN` vs `RANGE BETWEEN`.
- Medir custo de sort e particionamento.

## Snippet mínimo

```sql
SELECT *
FROM (
  SELECT
    t.*,
    ROW_NUMBER() OVER (
      PARTITION BY business_key
      ORDER BY updated_at DESC, ingestion_id DESC
    ) AS rn
  FROM t
) x
WHERE x.rn = 1;
```

## Validação objetiva

- Apenas uma linha por `business_key` após `rn = 1`.
- Resultado idempotente entre execuções.

## Armadilhas

- `ORDER BY` não determinístico.
- janela muito ampla sem necessidade.
- confusão entre `RANGE` e `ROWS`.

## Links relacionados

- [joins](joins.md)
- [incremental](incremental.md)

