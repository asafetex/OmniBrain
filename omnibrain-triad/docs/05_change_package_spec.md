# 05 Change Package Spec

## Regra principal

Sem `git diff`, sem Change Package válido.

## Campos obrigatórios

- `Change-ID`
- `Level (L1/L2/L3)`
- `Goal`
- `Context`
- `Acceptance Criteria`
- `Files Impacted`
- `Risks`
- `Skill Graph Links (2-5)`
- `Memory Refs`
- `Git Diff`

## Template markdown exato

```md
# Change Package

## Metadata
- Change-ID: {{CHANGE_ID}}
- Timestamp: {{TIMESTAMP}}
- Level: {{LEVEL}}
- Goal: {{GOAL}}
- Repo: {{REPO_PATH}}
- Diff-Mode: {{DIFF_MODE}}

## Context
{{CONTEXT}}

## Acceptance Criteria
{{ACCEPTANCE_CRITERIA}}

## Files Impacted
{{FILES_IMPACTED}}

## Risks
{{RISKS}}

## Skill Graph Links
{{GRAPH_LINKS}}

## Memory Refs
{{MEMORY_REFS}}

## Git Diff
```diff
{{GIT_DIFF}}
```
```

O mesmo template está em `tools/templates/change_package.md`.

## Regras de qualidade

- Preencher objetivo e critério de aceitação em linguagem verificável.
- Referenciar de 2 a 5 nós do grafo para reduzir contexto irrelevante.
- Não omitir riscos.
- Em L3, Change Package incompleto implica `REJECT`.

