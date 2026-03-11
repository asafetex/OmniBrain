# 02 Setup

## Pré-requisitos

- Sistema: Windows, Linux ou macOS
- `git` no PATH
- `python` 3.10+ no PATH
- Obsidian instalado
- Claude Code no VS Code
- Codex CLI logado
- Gemini CLI logado
- ByteRover CLI 2.0 logado

## Verificação de CLIs (sem assumir comandos de execução)

Valide existência e sintaxe com `--help`:

```bash
git --help
python --help
codex --help
gemini --help
brv --help
```

Se algum comando não existir, mantenha o fluxo em fallback manual (copiar/colar prompts).

Observação prática no Windows:
- se `brv` não estiver no PATH, rode pela entrada Node do pacote:
```powershell
node C:\Users\PC\AppData\Roaming\npm\node_modules\byterover-cli\bin\run.js --help
```

## Abrir o Hub no Obsidian

1. Abra Obsidian.
2. Selecione `Open folder as vault`.
3. Escolha `omnibrain-triad/context-hub/`.
4. Fixe `00_HOME.md` e `02_GRAPH/index.md`.

## Obsidian Cloud para documentação

Você pode usar dois modos de nuvem:

1. Obsidian Sync (privado, sincroniza o vault entre dispositivos):
   - Abra `Settings -> Sync`.
   - Faça login na sua conta Obsidian.
   - Crie ou conecte um remote vault.
   - Vincule o vault local `omnibrain-triad/context-hub/`.
2. Obsidian Publish (público, publica documentação em site):
   - Abra `Publish`.
   - Escolha as notas/pastas para publicar.
   - Gere o site de docs.

Recomendação operacional:
- Use `Sync` para trabalho privado e colaboração fechada.
- Use `Publish` apenas para documentação que pode ser pública.

## Conectar Hub ao repositório de trabalho

Opção A (pasta ao lado do projeto alvo):

```text
workspace/
  my-project/
  omnibrain-triad/
```

Opção B (submodule no projeto alvo):

```bash
git submodule add <url-ou-path-local> omnibrain-triad
```

## Configuração dos comandos reais

1. O repositório já inclui `tools/config.json` inicial para ciclo 1.
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
4. Não invente flags: o script executa exatamente o que estiver no config.

Config inicial sugerido (já aplicado em `tools/config.json`):
- `codex.enabled = true` com `args = ["review", "-"]`
- `gemini.enabled = false` (fallback manual no ciclo 1)
- `deepseek.enabled = false`
- `coderabbit.enabled = false`
- `byterover.enabled = true` com `cmd = "node"` + `args = ["...byterover-cli\\bin\\run.js","curate","--format","json"]` no Windows

### Ativação local do provider ByteRover (sem chave)

Para uso local de memória no CLI 2.x:

```powershell
node C:\Users\PC\AppData\Roaming\npm\node_modules\byterover-cli\bin\run.js providers connect byterover --format json
```

Depois valide:

```powershell
node C:\Users\PC\AppData\Roaming\npm\node_modules\byterover-cli\bin\run.js status --format json
```

## Smoke test local

```bash
python tools/make_change_package.py --repo . --level L1 --goal "teste de setup"
python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md
python tools/record_to_byterover.py --type PLAN --project omnibrain --topic setup --text "setup validado" --tags "#project/omnibrain,#type/plan"
python tools/promote_to_obsidian.py --list
```

Se a CLI não estiver disponível, os scripts geram fallback manual e salvam artefatos locais.
