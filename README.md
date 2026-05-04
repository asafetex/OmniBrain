# OmniBrain

Workspace SaaS para governanca de mudancas de codigo via consenso multiagente.

## Estrutura

```
OmniBrain/
├── omnibrain-triad/         <- aplicacao principal (MVP, Python stdlib)
├── sandbox-l3-e2e/          <- repo de validacao end-to-end
├── docs/                    <- documentacao consolidada do SaaS
├── .github/workflows/       <- CI: lint + test + sandbox tests
├── Dockerfile               <- imagem para CI/testes
└── docker-compose.yml       <- servicos test/lint/preflight
```

## Subprojetos

### `omnibrain-triad/` — aplicacao principal
Framework multi-agente diff-first. Veja [omnibrain-triad/README.md](omnibrain-triad/README.md) para detalhes operacionais.

**Status (smoke-tested):** todas as 14 ferramentas (`preflight`, `route`, `bundle`, `change_package`, `gate`, `guard`, `record`, `stats`, `recover`, `promote`, `bootstrap`, `start_flow`, `install_hook`, `utils`) tem evidencia empirica de funcionamento, incluindo testes adversariais (path traversal, command injection, race condition, diff de 5MB, unicode).

### `sandbox-l3-e2e/` — repo de validacao
Repositorio sintetico onde o fluxo L3 do TRIAD foi exercitado em 3 ciclos reais (currency hardening, decimal validation, token format guard). 19 testes pytest passando.

### `docs/` — documentacao SaaS
Consolidacao do ecossistema (AIOS, JARVIS, DATA_BRAIN, OmniBrain).

## Quick start

```bash
cd omnibrain-triad
python tools/preflight_check.py --repo .
python tools/start_task_flow.py --repo . --task "..." --level L3
```

## Licenca

MIT (ver `omnibrain-triad/pyproject.toml`).
