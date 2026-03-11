# Data Science Sanity Checks

## Quando usar

No início e no fim de qualquer experimento/modelagem.

## Objetivo

Detectar erro básico cedo (schema, contagem, distribuição, leakage).

## Checklist

- Confirmar shape e tipos.
- Validar distribuição de alvo e features-chave.
- Verificar valores extremos e nulos.
- Confirmar split treino/validação sem vazamento temporal.

## Snippet mínimo

```python
assert df.shape[0] > 0
assert "target" in df.columns
print(df["target"].describe())
```

## Validação objetiva

- Nenhuma checagem crítica falhou.
- Relatório mínimo de contagens e distribuição registrado.

## Armadilhas

- iniciar modelagem sem baseline.
- ignorar drift básico entre treino e validação.

## Links relacionados

- [outliers](outliers.md)
- [kmeans](kmeans.md)

