# G7 — Sentinel Preflight + Jev Shadow (proposta aditiva)

> **Escopo de laboratório.** Estes módulos não criam um novo owner do HUMAN GENE, não alteram a Constituição Cognitiva, não integram PRs, não consultam APIs, não autorizam publicação e não tomam decisões humanas.

## Por que existe

- O **Sentinel Preflight** garante que relatórios de reconciliação não declarem `PASS` sem estrutura mínima e não confundam um recibo informado com comprovação independente. Seus **7 gates** são: Git remoto, Git local, autoridade canônica, E2E multiprojeto, ciência humana, direitos/privacidade, segurança/release.
- O **Jev Shadow** aceita apenas respostas sintéticas tipadas com modelo fixado e responde `SUGGEST_ONLY`, `DEFER`, `REVIEW_REQUIRED` ou `HOLD_*`. Não chama a TypeSafe e não pode executar ações. `can_act` e `authoritative` são sempre falsos.

## Como reproduzir

No diretório `omnibrain-triad`:

```bash
python -m pytest tests/test_sentinel_preflight.py tests/test_jev_shadow_policy.py -v
python tools/sentinel_preflight.py --manifest configs/sentinel_preflight_SYNTHETIC.json
```

**Exit code 2 do CLI é esperado enquanto o programa permanecer BLOCKED**, e jamais deve ser contornado para pintar os gates de verde. A URL da primeira evidência no exemplo não é consultada pelo script. É uma declaração de recibo: `DECLARED_NOT_INDEPENDENTLY_VERIFIED`.

## Fronteiras de confiança

1. Input não é atestado: o preflight verifica apenas tipos, completude, nomes de gates, SHA de formato e domínio/path de recibos.
2. `PASS_REPORTED` **não** equivale a `VERIFIED`. Todos os gates continuam abertos até um verificador independente autenticado e as revisões necessárias.
3. Outputs do Jev são material de **triagem**, nunca bloqueios determinísticos substituídos, score de habilidade, prova de eficácia ou revisão científica.
4. Não enviar código privado, dados pessoais, prompt interno, credenciais ou amostras reais à API do Jev antes de definir coleta, retenção, direitos e owner.
5. `model=jev-1.14.0` no parser é um **contrato sintético pinado**, não indicação de que o produto foi contratado ou de que a API foi testada.

## Integração segura, adiada por gates

- G7 é **stacked sobre OmniBrain PR #1** (a correção independente do workflow). A PR G7 mirando `main` poderá incluir essa correção até a aprovação/integração da #1. Não fazer merge em ordem invertida.
- Após revisar/mergir a #1, validar o diff remanescente da G7, rerodar CI e solicitar revisão de desenho de API/segurança.
- A execução de E2E real entre BookOS, ResearchOS e HackerSkill e a conciliação local continuam fora deste escopo.
- Adotar Jev somente após benchmark cego/estratificado, análise de falso-negativo crítico, custo, privacidade e rollback.

Referência do piloto: [OmniBrain issue #2](https://github.com/asafetex/OmniBrain/issues/2). Fonte do estudo offline: G6 `PACOTE_G6_JEV_FECHAMENTO_2026-11-10.zip`.
