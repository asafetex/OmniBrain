# Data Science KMeans

## Quando usar

Para segmentação exploratória com variáveis numéricas escaladas.

## Objetivo

Gerar clusters interpretáveis sem assumir rótulos prévios.

## Checklist

- Escalar features (z-score ou similar).
- Testar múltiplos `k` (elbow/silhouette).
- Avaliar estabilidade por seed.
- Revisar interpretabilidade de centroides.

## Snippet mínimo

```python
from sklearn.cluster import KMeans
model = KMeans(n_clusters=4, n_init=20, random_state=42)
labels = model.fit_predict(X_scaled)
```

## Validação objetiva

- `silhouette_score` aceitável para o domínio.
- clusters com tamanho não degenerado.
- coerência semântica mínima por cluster.

## Armadilhas

- usar KMeans com dados categóricos não tratados.
- escolher `k` por conveniência.
- ignorar sensibilidade a escala e outliers.

## Links relacionados

- [sanity-checks](sanity-checks.md)
- [outliers](outliers.md)

