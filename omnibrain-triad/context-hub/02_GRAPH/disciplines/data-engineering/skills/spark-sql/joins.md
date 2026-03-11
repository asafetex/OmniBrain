# Spark SQL Joins

## Quando usar

Quando houver join entre datasets médios/grandes ou sinais de `join explode`.

## Objetivo

Evitar many-to-many acidental e garantir cardinalidade esperada.

## Checklist

- Validar unicidade da chave de join em cada lado.
- Medir contagem antes e depois do join.
- Tratar duplicidade antes do join (dedupe).
- Confirmar tipo de join adequado (`inner`, `left`, `semi`, `anti`).
- Em L3, anexar validações no Change Package.

## Snippet mínimo

```sql
WITH right_dedup AS (
  SELECT key, MAX(updated_at) AS max_updated_at
  FROM right_table
  GROUP BY key
)
SELECT l.*, r.max_updated_at
FROM left_table l
LEFT JOIN right_dedup r
  ON l.key = r.key;
```

## Validação objetiva

- `count_after_join <= count_left * fator_esperado`
- `% keys matched` dentro da faixa definida
- `count(distinct left_pk)` preservado quando esperado

## Armadilhas

- many-to-many silencioso.
- join por chave com null sem regra explícita.
- dedupe não determinístico.

## Links relacionados

- [performance](performance.md)
- [duplicates](../data-quality/duplicates.md)
- [nulls](../data-quality/nulls.md)

