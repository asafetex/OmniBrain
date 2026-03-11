# Data Science Outliers

## Quando usar

Em features numéricas com cauda longa ou suspeita de erro de coleta.

## Objetivo

Detectar e tratar outliers sem apagar sinal útil.

## Checklist

- Medir IQR e percentis (p1, p99).
- Separar outlier plausível de erro de medição.
- Definir política:
  - winsorizar,
  - transformar log,
  - excluir com justificativa.
- Validar impacto no modelo.

## Snippet mínimo

```python
q1, q3 = s.quantile(0.25), s.quantile(0.75)
iqr = q3 - q1
mask = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
print(mask.mean())
```

## Validação objetiva

- Taxa de outlier medida e registrada.
- Política aplicada melhora estabilidade sem degradar métrica principal.

## Armadilhas

- remover extremos sem avaliar contexto de negócio.
- usar a mesma regra para todas as features.

## Links relacionados

- [sanity-checks](sanity-checks.md)
- [kmeans](kmeans.md)

