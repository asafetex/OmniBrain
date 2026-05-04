# OmniBrain

Workspace SaaS para governanca de mudancas de codigo via consenso multiagente.

---

## Por onde comecar (ordem recomendada)

1. **[QUICKSTART.md](QUICKSTART.md)** — 5 minutos pra usar pela primeira vez
2. **[TUTORIAL.md](TUTORIAL.md)** — caso real do inicio ao fim (com OAuth2 como exemplo)
3. **[TOOLS.md](TOOLS.md)** — referencia de cada uma das 20 ferramentas
4. **[PLAYBOOKS.md](PLAYBOOKS.md)** — receitas para 10 cenarios praticos

Esses 4 arquivos cobrem 95% do uso. Se voce so vai ler um, le o **QUICKSTART**.

---

## Estrutura

```
OmniBrain/
├── README.md                 <- voce esta aqui
├── QUICKSTART.md             <- comeca em 5 minutos
├── TUTORIAL.md               <- caso real completo
├── TOOLS.md                  <- referencia de tools
├── PLAYBOOKS.md              <- 10 cenarios praticos
├── omnibrain-triad/          <- aplicacao principal (MVP, Python stdlib)
│   ├── tools/                  20 ferramentas
│   ├── tests/                  123 testes pytest
│   ├── docs/                   13 docs tecnicos detalhados
│   ├── configs/                routing.json + routing.yaml
│   ├── context-hub/            Vault Obsidian (Skill Graph + INBOX)
│   ├── project-template/       scaffold para projetos novos
│   └── bootstrap.py            recria estrutura em qualquer diretorio
├── sandbox-l3-e2e/           <- repo de validacao end-to-end
├── docs/                     <- docs SaaS consolidadas
├── .github/workflows/        <- CI: lint + test + sandbox
├── Dockerfile                <- imagem para CI
└── docker-compose.yml        <- servicos test/lint/preflight
```

---

## O que e o TRIAD em 3 frases

1. Voce escreve uma mudanca, o TRIAD captura **diff + metadata** num "Change Package"
2. Tres agentes (Claude/Codex/Gemini) auditam em paralelo: tecnico, sistemico, manual fallback
3. So merge depois de **consenso**. Cada decisao vira **memoria persistente** que alimenta o proximo ciclo

Resultado: **42% menos chamadas LLM** (cascade pre-valida), **rastreabilidade total** (cada commit tem Change-ID, review, decisao), e **memoria que aprende** (oraculo + pattern transfer).

---

## Status do projeto

| Item | Estado |
|---|---|
| Tools | **20** (validacao, pipeline, inteligencia, memoria, recovery) |
| Testes pytest | **123** (todos passando) |
| Erros ruff | **0** |
| Templates Codex/Gemini | **11** (3 dominios cada + base) |
| Bootstrap files | **88** |
| Smoke validados | **24** cenarios e2e + adversariais |
| Bugs conhecidos | 0 (8 criticos foram corrigidos durante validacao) |
| Dogfood real | **NAO** (proximo passo) |

---

## Conceitos centrais (5 minutos de leitura)

### Niveis de governanca
- **L1** — local, reversivel, sem gate (ex: typo, rename)
- **L2** — funcional, gate opcional (ex: feature, refactor)
- **L3** — critico, gate **obrigatorio** Codex+Gemini (ex: auth, billing, schema)

### Fluxo TRIAD em 5 fases
```
PLAN -> EXEC -> PACKAGE -> GATE -> MEMORY
```

### Confidence Cascade (3-tier)
- **Tier 1** (regras, ~0ms): empty diff, comments-only, security violations
- **Tier 2** (heuristica, ~50ms): TF-IDF similarity contra historico
- **Tier 3** (LLM, ~segundos): Codex + Gemini

### Skill Graph
3 disciplinas (`agents`, `data-engineering`, `data-science`), notas atomicas, politica de promocao curada.

### Memoria operacional
5 tipos: `PLAN` / `REVIEW` / `LESSON` / `WIN` / `DECISION`.
Vao para `context-hub/05_INBOX/` e sao promovidos pro Graph quando reutilizaveis.

---

## Quick start (literalmente 5 comandos)

```bash
cd omnibrain-triad

# 1. Validar
python tools/preflight_check.py --repo .

# 2. Pipeline completo num projeto seu
python tools/start_task_flow.py --repo /caminho/projeto --task "..." --level L2

# 3. Gate
python tools/run_gate.py --change-package /caminho/projeto/tmp/change-packages/CHG-XXX.md

# 4. (Opcional) consultar oraculo antes de comecar
python tools/triad_oracle.py --query "OAuth2 implementation"

# 5. Registrar WIN apos aprovado
python tools/record_to_byterover.py --type WIN --project myproj --topic done --file <gate-result>.md
```

---

## Limites conhecidos

- `git push --no-verify` ainda bypassa hook localmente (use GitHub branch protection para enforcement real)
- ByteRover/DeepSeek/CodeRabbit foram validados via mocks executaveis (codigo TRIAD provado, integracao real depende de vendor)
- TF-IDF search escala bem ate ~1000 memorias; para >10k considere embeddings (FAISS/Chroma)
- **Sistema nunca foi usado em projeto de producao real** — proxima etapa e dogfood

---

## CI/Qualidade

- GitHub Actions: lint (ruff) + test (pytest) + sandbox tests em cada push/PR
- Docker compose: `docker-compose up test`, `up lint`, `up preflight`
- Telemetria automatica em `tmp/telemetry/events.jsonl`

---

## Licenca

MIT (ver `omnibrain-triad/pyproject.toml`).

---

## Contato / Owner

asafetex@gmail.com
