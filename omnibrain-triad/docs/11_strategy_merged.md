# 11 Strategy Merged

## Objetivo

Definir uma estrategia unica de uso de agentes no OmniBrain TRIAD sem quebrar as regras de governanca.

## Principios fixos

- Diff-first sempre.
- Sem API keys e sem HTTP custom.
- L3 sempre com Gate principal Codex + Gemini.
- PreGate (DeepSeek/CodeRabbit) e opcional e nunca substitui Gate L3.
- Memoria operacional em ByteRover quando disponivel; fallback em INBOX quando necessario.

## Matriz de uso dos agentes

- Claude Code:
  - executor principal no editor;
  - planejamento, implementacao e correcoes.
- Codex CLI:
  - auditor tecnico;
  - bloqueios, edge cases, testes faltantes, sugestoes.
- Gemini CLI:
  - auditor sistemico;
  - impacto global, coerencia arquitetural, regressao.
- DeepSeek/CodeRabbit:
  - PreGate opcional para smells e melhorias rapidas.

## Fluxo recomendado (operacional)

1. Classificar tarefa em L1/L2/L3.
2. Rodar preflight:
   - `python tools/preflight_check.py --repo <repo>`
3. Rotear contexto:
   - `python tools/route_task.py --task "..." --level L3`
4. Montar pacote:
   - `python tools/make_change_package.py --repo <repo> --level L3 --goal "..."`
5. Executar Gate:
   - `python tools/run_gate.py --change-package <change-package.md>`
6. Em fallback manual:
   - usar `tmp/manual-prompts/<Change-ID>/`;
   - salvar respostas em `tmp/manual-responses/<Change-ID>/`.
7. Reexecutar Gate ate decisao final.
8. Rodar testes locais.
9. Commit apenas apos `Final Decision: APPROVE` em L3.
10. Registrar memoria:
    - `python tools/record_to_byterover.py ...`
11. Promover conhecimento reutilizavel:
    - `python tools/promote_to_obsidian.py --source ... --target ...`

## Perfis de operacao

### Perfil A - Obsidian only (free)

- `byterover.enabled = false` em `tools/config.json`.
- Memoria cai no INBOX local para curadoria.

### Perfil B - ByteRover ativo

- `byterover.enabled = true` com `cmd/args` validados via `--help`.
- Memoria vai para ByteRover; fallback para INBOX se houver falha.

## Regras que nao podem ser violadas

- Nao pular Gate em L3.
- Nao commitar L3 com `CONFLICT`, `REJECT` ou `UNKNOWN`.
- Nao promover nota sem snippet + validacao + quando usar.

## Anti-padroes

- Usar apenas um auditor em L3.
- Basear aprovacao em conversa sem Change Package.
- Ignorar prompts manuais gerados pelo `run_gate.py`.

## Referencias

- `docs/03_daily_workflow.md`
- `docs/04_l1_l2_l3.md`
- `docs/06_gate_spec.md`
- `tools/README.md`
