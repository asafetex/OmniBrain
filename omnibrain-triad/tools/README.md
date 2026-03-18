# Tools

Scripts locais para orquestracao sem API.

## Arquivos

- `make_change_package.py`: gera Change Package com base em `git diff`.
- `route_task.py`: aplica politica de roteamento e sugere executor/revisores/nos de grafo.
- `start_task_flow.py`: executa `route -> context bundle -> change package` em um comando.
- `build_context_bundle.py`: monta bundle de contexto (repo + grafo + memoria recente).
- `run_gate.py`: roda PreGate opcional e Gate principal por CLIs configuradas.
- `record_to_byterover.py`: registra memoria no ByteRover ou fallback INBOX.
- `promote_to_obsidian.py`: promove notas do INBOX para o Graph.
- `recover_session.py`: reconstrui estado de sessao a partir de gate-results e repositorio atual.
- `config.example.json`: templates de comando (copiar para `config.json`).
- `templates/`: markdown de Change Package e prompts de review.

## Configuracao

1. Copie:
   - `tools/config.example.json` -> `tools/config.json`
2. Preencha comandos reais após consultar `--help` de cada CLI.
3. Os scripts nunca inventam flags.
4. Opcional: ajuste `timeout_seconds` por auditor quando uma CLI demora mais para responder (ex.: Codex).

Modo recomendado agora:
- `byterover.enabled = false` (Obsidian-only);
- memoria vai para `context-hub/05_INBOX/byterover-imports/`;
- compartilhe o vault por Git.

## Uso rapido

```bash
python tools/make_change_package.py --repo . --level L3 --goal "..."
python tools/route_task.py --task "join explode no spark" --level L3
python tools/start_task_flow.py --repo . --task "join explode no spark" --level L3
python tools/build_context_bundle.py --repo . --task "..." --level L3 --graph-links "disciplines/agents/skills/triad-protocol.md,disciplines/agents/skills/consensus-gate.md"
python tools/build_context_bundle.py --repo . --task "join explode no spark" --level L3 --auto-route
python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md
python tools/record_to_byterover.py --type WIN --project myproj --topic mytopic --file tmp/gate-results/<Change-ID>.md --tags "#project/myproj,#type/win"
python tools/recover_session.py --repo . --change-id <Change-ID>
python tools/promote_to_obsidian.py --list
```

## Routing policy

- Arquivos declarativos: `configs/routing.yaml` (humano) e `configs/routing.json` (executavel).
- Define politica por nivel (`L1/L2/L3`), revisores padrao e roteamento por intent.
- `route_task.py` e `build_context_bundle.py --auto-route` usam `configs/routing.json`.

## Gate com resposta manual

Quando uma CLI de auditor nao estiver disponivel:

1. Rode:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
2. O script gera prompts em `tmp/manual-prompts/<Change-ID>/`.
3. Cole o prompt no auditor manualmente.
4. Salve a resposta em `tmp/manual-responses/<Change-ID>/<auditor>.md`.
5. Rode novamente o Gate para consolidar decisao.

Observacao importante:
- respostas manuais antigas (timestamp anterior ao prompt gerado na rodada atual) sao ignoradas.

Tambem e possivel customizar o diretorio de respostas:

- `python tools/run_gate.py --change-package ... --manual-responses-dir <dir>`

## Fallback manual

Se CLI nao existir ou falhar:

- `run_gate.py` salva prompts em `tmp/manual-prompts/`.
- `run_gate.py` lê respostas de `tmp/manual-responses/`.
- `record_to_byterover.py` salva markdown em `context-hub/05_INBOX/byterover-imports/`.
