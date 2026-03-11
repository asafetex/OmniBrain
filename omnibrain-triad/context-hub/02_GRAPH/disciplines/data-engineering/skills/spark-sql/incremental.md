# Spark SQL Incremental

## Quando usar

Em cargas incrementais com merge/upsert, CDC ou watermark de processamento.

## Objetivo

Garantir idempotência e consistência temporal.

## Checklist

- Definir chave natural/técnica de upsert.
- Garantir dedupe de eventos por chave + timestamp.
- Definir watermark e regra de atraso permitido.
- Validar reprocessamento sem duplicar resultado.

## Snippet mínimo

```sql
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED AND s.updated_at >= t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

## Validação objetiva

- Reexecutar mesmo lote não altera total final indevidamente.
- Sem duplicidade de chave após merge.
- Registros atrasados obedecem regra de watermark.

## Armadilhas

- merge sem condição temporal.
- watermark agressivo que perde dado válido.
- update cego sobre registro mais novo.

## Links relacionados

- [windows](windows.md)
- [duplicates](../data-quality/duplicates.md)

