# Data Quality Duplicates

## Quando usar

Quando houver duplicidade por chave de negócio em staging, bronze/silver ou dimensão.

## Objetivo

Aplicar estratégia de dedupe explícita e rastreável.

## Checklist

- Definir chave primária de negócio.
- Escolher critério de prioridade (timestamp, versão, fonte).
- Garantir determinismo com tie-breaker.
- Validar contagem de duplicados antes/depois.

## Snippet mínimo

```sql
WITH ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY business_key
      ORDER BY updated_at DESC, ingestion_id DESC
    ) AS rn
  FROM src
)
SELECT * FROM ranked WHERE rn = 1;
```

## Validação objetiva

- `count(*)` de chaves duplicadas deve ser zero no resultado.
- regra de prioridade comprovada por amostra.

## Armadilhas

- dedupe não determinístico.
- perda de registro válido por regra mal definida.
- ignorar duplicidade upstream.

## Links relacionados

- [nulls](nulls.md)
- [spark joins](../spark-sql/joins.md)

