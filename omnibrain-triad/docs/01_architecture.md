# 01 Architecture

## Diagrama textual

```text
[Developer Task]
      |
      v
[Claude Code Executor]
  - planeja
  - implementa em branch
  - gera diff
      |
      v
[Change Package Builder - tools/make_change_package.py]
      |
      +------------------------------+
      |                              |
      v                              v
[PreGate opcional]              [Gate principal]
DeepSeek + CodeRabbit           Codex + Gemini (obrigatório em L3)
      |                              |
      +---------------+--------------+
                      v
            [Decision Engine]
      APPROVE / REJECT / CONFLICT
                      |
                      v
            [Tests + Commit + Merge]
                      |
                      v
       [Execution Memory - ByteRover CLI 2.0]
               PLAN/REVIEW/LESSON/WIN
                      |
                      v
         [Context Hub - Obsidian Skill Graph]
             promoção apenas de WIN curado
```

## Responsabilidades

- Claude Code:
  - Executar o plano.
  - Manter foco no escopo.
  - Produzir mudança rastreável por diff.
- Codex:
  - Auditoria técnica em cima do Change Package.
  - Verificar blockers, edge cases, testes e riscos locais.
- Gemini:
  - Auditoria sistêmica.
  - Verificar impacto global, arquitetura, contratos e regressões.
- ByteRover:
  - Persistência operacional entre sessões.
  - Query de contexto antes de nova execução.
- Context Hub:
  - Curadoria e reuso.
  - Anti-poluição do conhecimento.
- Tools:
  - Orquestrar artefatos sem API e com fallback manual.

## Fluxo L3 obrigatório

1. `PLAN` com escopo, risco e critérios.
2. Branch dedicada.
3. Implementação `diff-first`.
4. Change Package com `git diff`.
5. Gate Codex + Gemini.
6. Correção até `APPROVE`.
7. Testes mínimos aplicáveis.
8. Commit/Merge.
9. Registro `WIN`/`LESSON`/`DECISION`.
10. Promoção curada para o Graph.

## Limites

- Não garante perfeição.
- Não substitui testes automatizados e CI.
- Não elimina todo bug.
- Reduz risco e retrabalho por disciplina operacional, revisão cruzada e memória persistente.

