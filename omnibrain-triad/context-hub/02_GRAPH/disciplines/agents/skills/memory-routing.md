# Memory Routing

## Quando usar

No início de L2/L3 para escolher contexto mínimo necessário.

## Objetivo

Selecionar 2 a 5 nós do Graph e memórias relevantes sem poluir o contexto.

## Checklist

- classificar a intent da tarefa;
- mapear intent para disciplina principal;
- selecionar de 2 a 5 nós atômicos;
- recuperar 1 a 3 memórias (`WIN/LESSON/DECISION`) do ByteRover/INBOX;
- anexar links no Change Package.

## Snippet mínimo

```text
intent -> disciplina -> 2-5 nós -> 1-3 memórias -> change package
```

## Validação objetiva

- change package contém links do grafo e referências de memória.
- contexto carregado é suficiente para executar sem reexplicação longa.

## Armadilhas

- abrir nós demais e perder foco.
- ignorar DECISION anterior e repetir erro.

## Links relacionados

- [triad-protocol](triad-protocol.md)
- [change-package](change-package.md)

