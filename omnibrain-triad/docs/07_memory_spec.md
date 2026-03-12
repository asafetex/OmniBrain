# 07 Memory Spec

## Tipos de memoria

- `PLAN`
- `REVIEW`
- `LESSON`
- `WIN`
- `DECISION`

## Padrao de ID

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

Modo padrao atual:
1. Obsidian-only com fallback local em `context-hub/05_INBOX/byterover-imports/`.
2. Versionamento e compartilhamento via Git do vault.

Modo opcional:
1. ByteRover CLI 2.x (quando habilitado e validado no config).

O script `tools/record_to_byterover.py` tenta CLI e faz fallback automatico.

Observacao para Windows:
- o ID interno permanece `MEM::<TYPE>::...`,
- o nome do arquivo fallback usa `__` no lugar de `::` por restricao do filesystem.

## Recuperacao

No modo Obsidian-only:
1. busque no vault por `MEM::`, `#type/...`, `#project/...`;
2. referencie IDs em `Memory Refs` do Change Package;
3. apos Gate, registre `REVIEW` + `WIN`/`LESSON`.

No modo ByteRover:
1. use `brv --help` para descobrir o comando de busca da sua versao;
2. configure os comandos reais no `tools/config.json`;
3. siga o mesmo contrato de IDs e tags.
