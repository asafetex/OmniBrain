# 02 Setup

## Pre-requisitos

- Sistema: Windows, Linux ou macOS
- `git` no PATH
- `python` 3.10+ no PATH
- Obsidian instalado
- Claude Code no VS Code
- Codex CLI logado
- Gemini CLI logado
- ByteRover CLI 2.x opcional

## Verificacao de CLIs (sem assumir comandos de execucao)

Valide existencia e sintaxe com `--help`:

```bash
git --help
python --help
codex --help
gemini --help
brv --help
```

Se algum comando nao existir, mantenha o fluxo em fallback manual (copy/paste prompts).

Observacao no Windows:
- se `brv` nao estiver no PATH, rode pela entrada Node do pacote:
```powershell
node C:\Users\PC\AppData\Roaming\npm\node_modules\byterover-cli\bin\run.js --help
```

## Abrir o Hub no Obsidian

1. Abra Obsidian.
2. Selecione `Open folder as vault`.
3. Escolha `omnibrain-triad/context-hub/`.
4. Fixe `00_HOME.md` e `02_GRAPH/index.md`.

## Memoria compartilhada (perfis operacionais)

Perfil A (Obsidian-only, free):
- `byterover.enabled = false` em `tools/config.json`;
- registrar memoria no INBOX (`context-hub/05_INBOX/byterover-imports/`);
- sincronizar o vault por GitHub (privado) para compartilhamento entre maquinas.

Perfil B (ByteRover ativo):
- `byterover.enabled = true`;
- `cmd/args` do ByteRover validados via `--help`;
- fallback automatico para INBOX quando a CLI falhar.

Fluxo Git para vault:
1. `git add context-hub/`
2. `git commit -m "docs(memory): update inbox and graph"`
3. `git push`

Obsidian Sync continua opcional (pago). Obsidian Publish tambem e opcional.

## Conectar Hub ao repositorio de trabalho

Opcao A (pasta ao lado do projeto alvo):

```text
workspace/
  my-project/
  omnibrain-triad/
```

Opcao B (submodule no projeto alvo):

```bash
git submodule add <url-ou-path-local> omnibrain-triad
```

## Configuracao dos comandos reais

1. O repositorio ja inclui `tools/config.json` para ciclo 1.
2. Se quiser reiniciar do zero, copie o arquivo de exemplo:

```bash
cp tools/config.example.json tools/config.json
```

No Windows PowerShell:

```powershell
Copy-Item tools/config.example.json tools/config.json
```

3. Rode `--help` de cada CLI e preencha:
   - `cmd`
   - `args` fixos
   - `enabled`
   - `timeout_seconds` por auditor (opcional)
4. Nao invente flags: o script executa exatamente o que estiver no config.
5. Revise a politica em `configs/routing.yaml`:
   - niveis L1/L2/L3
   - revisores padrao
   - intents e graph nodes recomendados.
6. Revise o espelho executavel em `configs/routing.json`:
   - `route_task.py` e `build_context_bundle.py --auto-route` leem esse arquivo.

Config inicial recomendado:
- `codex.enabled = true` com `args = ["review", "-"]`
- `codex.timeout_seconds = 240` para reduzir timeout em reviews maiores
- `gemini.enabled = false` (fallback manual no ciclo 1)
- `deepseek.enabled = false`
- `coderabbit.enabled = false`
- `byterover.enabled = true` quando a CLI estiver validada (senao `false`)

## ByteRover (quando ativar)

Quando for ativar ByteRover:
1. valide CLI e login;
2. configure `byterover.enabled = true` + `cmd/args` reais no `tools/config.json`;
3. rode um teste com `record_to_byterover.py`.

Exemplo de validacao local (ajuste conforme seu `--help`):

```powershell
node C:\Users\PC\AppData\Roaming\npm\node_modules\byterover-cli\bin\run.js status --format json
```

## Smoke test local

```bash
python tools/make_change_package.py --repo . --level L1 --goal "teste de setup"
python tools/route_task.py --task "teste join explode" --level L3
python tools/preflight_check.py --repo .
python tools/start_task_flow.py --repo . --task "teste join explode" --level L3 --preflight
python tools/install_pre_push_hook.py --repo .
python tools/l3_pre_push_guard.py --repo .
python tools/build_context_bundle.py --repo . --task "teste de contexto" --level L2 --graph-links "disciplines/agents/skills/triad-protocol.md"
python tools/build_context_bundle.py --repo . --task "teste de contexto" --level L2 --auto-route
python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md
python tools/recover_session.py --repo . --change-id <Change-ID>
python tools/triad_stats.py --days 7
python tools/record_to_byterover.py --type PLAN --project omnibrain --topic setup --text "setup validado" --tags "#project/omnibrain,#type/plan"
python tools/promote_to_obsidian.py --list
```

Se a CLI nao estiver disponivel, os scripts geram fallback manual e salvam artefatos locais.

## Testes automatizados no sandbox (recomendado)

Se `pytest` nao estiver instalado no Python global:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado esperado no sandbox de exemplo:
- `>= 10 passed` (o total pode aumentar conforme novos testes do drill L3)
