# Migration ByteRover CLI 1.x -> 2.0

## Objetivo

Migrar fluxos antigos para ByteRover CLI 2.0 sem quebrar operação diária.

## Princípios de migração

- Daemon-first quando disponível.
- Preferir JSON estruturado quando a CLI suportar.
- Descobrir comandos reais sempre por `--help`.
- Manter fallback local no INBOX.

## Mudanças esperadas de 1.x para 2.0

- comandos podem ter sido renomeados;
- contratos de entrada/saída podem exigir novo formato;
- pode existir etapa de `daemon`/`service` para performance;
- resposta textual pode mudar para JSON (ou vice-versa).

## Procedimento recomendado

1. Mapeie comandos atuais:
   - `brv --help`
   - `brv <subcomando> --help`
2. Atualize `tools/config.json`:
   - `byterover.cmd`
   - `byterover.args`
   - `byterover.enabled`
3. Teste registro mínimo:
   - `PLAN` simples.
4. Teste consulta de contexto:
   - busca por tags/projeto.
5. Valide fallback:
   - desligue `byterover.enabled` e confirme escrita em INBOX.

## Estratégia de compatibilidade

- Não codificar flags no script.
- Centralizar comando e argumentos no `config.json`.
- Se necessário, manter dois perfis de config (`config.v1.json` e `config.v2.json`) durante transição.

## Patches opcionais para repo "Byterover-Claude-Codex-Collaboration-"

Sem depender de conteúdo local, aplique estes passos conceituais:

1. Introduzir camada `CommandTemplate` em config.
2. Trocar chamadas hardcoded de CLI por execução dinâmica do config.
3. Adicionar fallback de persistência em markdown local.
4. Adicionar parser de verdict resiliente para output textual.
5. Adicionar rotina de smoke test (`--help`) para cada CLI configurada.

## Checklist de conclusão

- [ ] Registro de `PLAN` funciona em 2.0.
- [ ] Registro de `WIN` funciona em 2.0.
- [ ] Query de memória retorna resultados úteis.
- [ ] Fallback INBOX continua funcionando.
- [ ] Nenhum script depende de API/HTTP.

