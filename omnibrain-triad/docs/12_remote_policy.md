# 12 Remote Policy — `OmniBrain-remote/`

Politica operacional para a pasta `OmniBrain-remote/` no workspace pai.

---

## Status

**Vestigial.** Pode ser deletada com seguranca.

A pasta existiu durante a fase de validacao para servir como "espelho de deploy". Hoje e:
- Gitignored (`.gitignore` linha: `OmniBrain-remote/`)
- Nao versionada no GitHub
- Nao gerada automaticamente por nenhum tool
- Pode estar desatualizada em relacao a `omnibrain-triad/` (canonico)

---

## Regras operacionais

### 1. Fonte unica da verdade

Todo codigo, doc, teste, template entra **apenas em `omnibrain-triad/`**. Esse e o canonico.

### 2. OmniBrain-remote nao recebe edicoes diretas

Se voce editar um arquivo em `OmniBrain-remote/omnibrain-triad/tools/X.py`:
- A mudanca e silenciosa (gitignored)
- Nao vai pro GitHub
- Sera perdida no proximo sync (ou nunca aplicada se nao houver sync)

**Regra dura:** nao edite nada dentro de `OmniBrain-remote/`. Periodo.

### 3. Como produzir um deploy real

Se voce quer um snapshot deployavel:

```bash
# Opcao A: bootstrap em diretorio limpo
cd omnibrain-triad
python bootstrap.py --target /caminho/deploy
```

```bash
# Opcao B: rsync apenas dos arquivos canonicos
rsync -av --delete --exclude '.git' --exclude 'tmp/' \
  omnibrain-triad/ /caminho/deploy/
```

```bash
# Opcao C: clone do GitHub
git clone git@github.com:asafetex/OmniBrain.git /caminho/deploy
```

### 4. Limpeza

A qualquer momento voce pode:

```bash
rm -rf OmniBrain-remote/
```

Sem perda. A pasta nao tem dados unicos — apenas arquivos antigos divergentes do canonico.

---

## Por que existiu

Historicamente, a pasta foi criada para:
- Backup local antes do GitHub estar configurado
- Espelho para rodar `bootstrap.py --target ../OmniBrain-remote/omnibrain-triad`
- Sandbox de "como o projeto fica apos bootstrap"

Todos esses casos hoje tem ferramentas melhores:
- Backup: `git push origin main`
- Bootstrap test: `bootstrap.py --target /tmp/test`
- Sandbox: usar `sandbox-l3-e2e/` (que e oficial)

---

## Checklist para futuras decisoes

Se voce esta considerando criar uma copia paralela do `omnibrain-triad/`, pergunte:

| Pergunta | Resposta esperada |
|---|---|
| Vou versionar essa copia? | Se sim, **NAO crie**. Use branches no canonico. |
| E backup? | Use `git push` ou clone do GitHub. |
| E ambiente de teste? | Use `bootstrap.py --target /tmp/test`. |
| E variante customizada? | Use git branch ou fork formal no GitHub. |
| Nenhum desses? | A copia provavelmente nao deveria existir. |

**Sintoma de bonsai:** voce tem >2 copias do mesmo codigo no workspace local. Cada copia divergente e divida tecnica.

---

## Status historico (para referencia)

```
Antes (sessao 2026-04 a 2026-05):
  omnibrain-triad/             (canonico)
  OmniBrain-remote/omnibrain-triad/  (copia divergente — varios arquivos diferentes)

Apos sync (2026-05):
  omnibrain-triad/             (canonico)
  OmniBrain-remote/omnibrain-triad/  (sincronizado, mas nao versionado)

Apos esta politica (2026-05):
  omnibrain-triad/             (canonico, unica fonte)
  OmniBrain-remote/            (vestigial, pode ser deletada)
```

---

## Owner

asafetex@gmail.com

## Date

2026-05-05
