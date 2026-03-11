# 00 Overview

OmniBrain TRIAD unifica três camadas:

1. Governança de execução (TRIAD): Claude executa, Codex audita técnico, Gemini audita sistêmico.
2. Memória dinâmica de execução: ByteRover CLI 2.0 (ou fallback local no INBOX).
3. Hub curado em Obsidian: Skill Graph com notas atômicas e políticas anti-poluição.

## Escopo do MVP

- Funciona sem MCP.
- Funciona sem API keys.
- Usa somente CLIs logados e scripts locais em Python stdlib.
- Implementa fluxo `diff-first` com Gate obrigatório em L3.

## Árvore do repositório

```text
omnibrain-triad/
  README.md
  bootstrap.py
  docs/
  context-hub/
  project-template/
  tools/
```

## Frase guia

Transformar qualquer tarefa em um fluxo diff-first com consenso multiagente, registrando PLAN/REVIEW/LESSON/WIN na memória dinâmica e promovendo apenas vitórias executáveis para o Hub curado.

