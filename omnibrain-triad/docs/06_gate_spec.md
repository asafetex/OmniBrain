# 06 Gate Spec

## Objetivo

Decidir de forma objetiva se uma mudanca pode seguir para commit/merge.

## Entrada minima

- Change Package valido.
- Diff presente.
- Nivel (`L1/L2/L3`) informado.

## Criterios objetivos de REJECT

- Falha funcional evidente no diff.
- Violacao de seguranca, privacidade ou compliance.
- Regressao provavel sem mitigacao.
- Falta de teste/validacao para cenario critico.
- Change Package incompleto em L3.
- Contradicao com contrato/ADR conhecido.

## Criterios de APPROVE

- Sem blockers criticos.
- Riscos documentados e aceitaveis.
- Testes/validacoes minimas definidos.
- Implementacao atende criterios de aceitacao.

## Regra L3 (obrigatoria)

- Rodar Codex + Gemini.
- Se qualquer um retornar `VERDICT: REJECT` => `REJECT`.
- Se ambos retornarem `VERDICT: APPROVE` => `APPROVE`.
- Se faltar verdict ou houver ambiguidade => `CONFLICT` e decisao humana.
- Precedencia por auditor:
  - `VERDICT` explicito da CLI (stdout/stderr);
  - se nao houver `VERDICT`, inferencia da CLI (`cli_inferred`);
  - se ainda nao houver, resposta manual em `tmp/manual-responses/<Change-ID>/<auditor>.md`;
  - senao `UNKNOWN`.

## Fluxo manual oficial (fallback)

1. Rodar:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`
2. O script salva prompts em:
   - `tmp/manual-prompts/<Change-ID>/`
3. Cole o prompt do auditor no CLI correspondente (ex.: Gemini ou Codex).
4. Salve resposta manual em:
   - `tmp/manual-responses/<Change-ID>/gemini.md`
   - `tmp/manual-responses/<Change-ID>/codex.md` (quando Codex nao trouxer `VERDICT` explicito)
5. A resposta manual precisa ser mais nova que o prompt da execucao atual.
6. Rode o Gate novamente:
   - `python tools/run_gate.py --change-package tmp/change-packages/<Change-ID>.md`

## Regra pratica para `UNKNOWN`

Se um auditor terminar com `Verdict: UNKNOWN`:
- resultado e inconclusivo;
- complete fallback manual para esse mesmo auditor;
- rerode o Gate;
- em L3, sem dois `APPROVE` validos, nao finalize commit.

## Saida padronizada por auditor

```text
Blockers:
- ...

Edge cases:
- ...

Missing tests:
- ...

Suggestions:
- ...

VERDICT: APPROVE|REJECT
```

O resultado em `tmp/gate-results/<Change-ID>.md` inclui:
- `Verdict Source: cli|cli_inferred|manual|none`
- caminho do prompt manual
- caminho da resposta manual

## PreGate (opcional)

- DeepSeek e CodeRabbit podem rodar antes.
- PreGate nao fecha L3 sozinho.
- Gate principal de L3 continua sendo Codex + Gemini.

## Enforcement local de push (opcional recomendado)

1. Instale o hook:
   - `python tools/install_pre_push_hook.py --repo .`
2. O hook chama:
   - `tools/l3_pre_push_guard.py`
3. Regra aplicada no push:
   - se o ultimo Change Package for L3, exige `Final Decision: APPROVE` no gate correspondente.
4. Bypass emergencial:
   - `git push --no-verify` (somente em excecao).
