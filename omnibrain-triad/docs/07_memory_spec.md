# 07 Memory Spec

## Tipos de memória

- `PLAN`
- `REVIEW`
- `LESSON`
- `WIN`
- `DECISION`

## Padrão de ID

`MEM::<TYPE>::<PROJECT>::<TOPIC>::<YYYYMMDD-HHMM>`

Exemplo:
`MEM::WIN::omnibrain::spark-join-explode::20260310-0942`

## Tags

- `#discipline/<disciplina>`
- `#type/<tipo>`
- `#project/<projeto>`

Exemplo:
`#discipline/data-engineering #type/win #project/omnibrain`

## Registro

Prioridade:
1. ByteRover CLI 2.0 (quando disponível e configurado).
2. Fallback local em `context-hub/05_INBOX/byterover-imports/`.

O script `tools/record_to_byterover.py` tenta CLI e faz fallback automático.

Observação para Windows:
- o ID interno permanece `MEM::<TYPE>::...`,
- o nome do arquivo fallback usa `__` no lugar de `::` por restrição do filesystem.

## Recuperação (sem inventar flags)

Use `brv --help` para descobrir o comando de busca da sua versão e configure em `tools/config.json`.

Fluxo recomendado:

1. consultar memórias por tags e tópico antes de iniciar L2/L3;
2. anexar IDs relevantes em `Memory Refs` do Change Package;
3. após Gate, registrar `REVIEW` + `WIN`/`LESSON`.
