# Spark SQL Performance

## Quando usar

Quando jobs apresentam shuffle alto, skew, custo elevado ou runtime instável.

## Objetivo

Reduzir tempo e custo sem quebrar semântica do dado.

## Checklist

- Inspecionar plano físico (`explain`) e estágios de shuffle.
- Revisar particionamento por chave de alto uso.
- Avaliar broadcast join para dimensão pequena.
- Evitar cache indiscriminado; cachear apenas reuse real.
- Medir antes/depois com métrica objetiva.

## Snippet mínimo

```sql
SELECT /*+ BROADCAST(dim) */ f.*
FROM fact f
JOIN dim
  ON f.dim_id = dim.id;
```

## Validação objetiva

- Redução de tempo total do job.
- Redução de bytes embaralhados (shuffle read/write).
- Sem alteração indevida de contagem final.

## Armadilhas

- broadcast em tabela maior que memória disponível.
- repartition excessivo sem necessidade.
- cache sem invalidação.

## Links relacionados

- [joins](joins.md)
- [windows](windows.md)
- [incremental](incremental.md)

