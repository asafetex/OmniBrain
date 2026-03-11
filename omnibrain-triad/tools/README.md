# Tools

Scripts locais para orquestração sem API.

## Arquivos

- `make_change_package.py`: gera Change Package com base em `git diff`.
- `run_gate.py`: roda PreGate opcional e Gate principal por CLIs configuradas.
- `record_to_byterover.py`: registra memória no ByteRover ou fallback INBOX.
- `promote_to_obsidian.py`: promove notas do INBOX para o Graph.
- `config.example.json`: templates de comando (copiar para `config.json`).
- `templates/`: markdown de Change Package e prompts de review.

## Configuração

1. Copie:
   - `tools/config.example.json` -> `tools/config.json`
2. Preencha comandos reais após consultar `--help` de cada CLI.
3. Os scripts nunca inventam flags.

## Uso rápido

```bash
python tools/make_change_package.py --repo . --level L3 --goal "..."
python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md
python tools/record_to_byterover.py --type WIN --project myproj --topic mytopic --file tmp/gate-results/<Change-ID>.md --tags "#project/myproj,#type/win"
python tools/promote_to_obsidian.py --list
```

## Gate com resposta manual

Quando uma CLI de auditor não estiver disponível:

1. Rode:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
2. O script gera prompts em `tmp/manual-prompts/<Change-ID>/`.
3. Cole o prompt no auditor manualmente.
4. Salve a resposta em `tmp/manual-responses/<Change-ID>/<auditor>.md`.
5. Rode novamente o Gate para consolidar decisão.

Também é possível customizar o diretório de respostas:

- `python tools/run_gate.py --change-package ... --manual-responses-dir <dir>`

## Fallback manual

Se CLI não existir ou falhar:

- `run_gate.py` salva prompts em `tmp/manual-prompts/`.
- `run_gate.py` lê respostas de `tmp/manual-responses/`.
- `record_to_byterover.py` salva markdown em `context-hub/05_INBOX/byterover-imports/`.
