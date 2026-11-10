# G7 — Matriz de gates, provas e sequência de integração (10/11/2026)

> **Status: REMOTE_PREFLIGHT_PASS / INTEGRATION_REVIEW_HOLD / LOCAL_UNAVAILABLE / SCIENCE_HOLD.** Esta pasta é material de auditoria, NÃO a autoridade canônica das habilidades humanas.

## Cobertura verificável
- 37 repositórios instalados no conector GitHub; 35 HEADs padrão SHA40 pinados; `asafetex/cognitive-path-engine` e `asafetex/Automation` retornaram 409 `Git Repository is empty`.
- Os HEADs estão nos quatro arquivos `docs/remote_baseline/G7_HEADS_{01,02,03,04}.json`; não foram inventariados stashes, worktrees, todos os branches ou o computador do usuário.
- O G0/G2 anterior já analisava 251 HEADs de branches remotos de 8 repositórios, sem equivaler a uma auditoria semântica exaustiva.
- Nenhum repositório, branch, artefato histórico ou banco foi apagado, reescrito ou mesclado.

## Registros por sistema
| Sistema | Recibo remoto | Estado correto | Dependência |
|---|---|---|---|
| HackerSkill | [PR #10](https://github.com/asafetex/HackerSkill_OS/pull/10), [CI PASS](https://github.com/asafetex/HackerSkill_OS/actions/runs/42837925135) | Ready for review; 50 invariantes otimizados, histórico Wave 3/5 preservado | Revisão/merge humano, ontologia e ciência mantidas em HOLD |
| OmniBrain | [PR #1 MERGED](https://github.com/asafetex/OmniBrain/pull/1), [main CI PASS](https://github.com/asafetex/OmniBrain/actions/runs/42893758464) | Workflow corrigido e integrado à main no commit bfd61f82cb9811601c0707c79d8ff291c2431a95 | Reavaliar PR #3 contra main atual e executar CI pós-merge |
| OmniBrain Sentinel/Jev | [PR #3](https://github.com/asafetex/OmniBrain/pull/3), [CI](https://github.com/asafetex/OmniBrain/actions) | Draft, stacked na #1; read-only/no API Jev | Revisão de segurança, merge ordenado, benchmark REAL futuro |
| Data Skill Compass | [PR #1](https://github.com/asafetex/data-skill-compass/pull/1), [CI scoped PASS](https://github.com/asafetex/data-skill-compass/actions/runs/42863764369), [issue #2](https://github.com/asafetex/data-skill-compass/issues/2) | Draft; ranking determinístico; lint global historicamente falha | GameContext.computeReadiness e unlock_rules, RLS/Postgres e lint completo |
| The Machine | [integration CI PASS](https://github.com/asafetex/machine-sandbox/actions/runs/42740253285); [PR #71 superseded](https://github.com/asafetex/machine-sandbox/pull/71) | Dois erros do G2 reparados por commit próprio, sem merge automático à master | Segurança operacional, testes de deploy e promoção controlada |
| MediaOS | [CI 194 PASS](https://github.com/asafetex/media-os/actions/runs/42837148453), [PR #20](https://github.com/asafetex/media-os/pull/20) | CI reproduzido; PR produto draft | Direitos, revisão editorial, publicação e causa histórica antiga não comprovada |
| ResearchOS | [PR #1](https://github.com/asafetex/research_os/pull/1), [CI PASS](https://github.com/asafetex/research_os/actions/runs/42106315945) | Consumer metadata read-only testado | E2E checkouts multi-repo privados, pesquisa independente |
| BookOS | [PR #182](https://github.com/asafetex/book-os/pull/182), [CI PASS](https://github.com/asafetex/book-os/actions/runs/42106438153) | Pacote BAT-SF-03 com SHA source+packet comprovados | E2E real, direitos, editoria, não promover GOLD |
| Polyglot | [PR #3](https://github.com/asafetex/Polyglot-System/pull/3), [CI PASS](https://github.com/asafetex/Polyglot-System/actions/runs/42808309863) | Candidatos lexicais técnicos, nenhuma equivalência aprovada | 12 tarefas revisão humana, assinatura real, direitos, ensino bloqueado |
| Human Gene/Constituição | Fonte textual em export histórico Special Forces e ADR provisória | Titularidade física e hash autônomo NÃO conferidos | Localizar arquivo original e conferir cláusulas/emenda v1.1, owner assina |
| Repos sem HEAD | cognitive-path-engine, Automation | Remoto vazio | Não inferir que trabalho local inexiste |

## Sequência controlada
1. OmniBrain PR #1 integrada após CI e revisão da alteração apenas de caminhos de CI; outras branches `main/master` permanecem protegidas por seus gates.
2. OmniBrain #1 concluída; PR #3 contém somente additions de G7 contra a nova main e requer CI pós-merge para encerrar o gate técnico.
3. HackerSkill #10 somente após revisar hashes históricos/Wave gates e aprovação do mantenedor.
4. Separar Data Skill Compass scoped CI vs lint full e score legado, sem afirmar paridade universal.
5. E2E BookOS -> ResearchOS -> HackerSkill: checkouts read-only em SHAs fixados, verificar worktree+blob e consumir em SQLite descartável. Testes estruturais e SHA remotos NÃO equivalem a esse E2E.
6. Dar destino canônico à Constituição original e Emenda; QLEAP (5 pilares), F0 e D01–D10 permanecem com funções distintas; nenhuma criação de novo owner por impulso.
7. Polyglot: completar revisão humana, identidade de fontes, direitos e assinatura em ambiente privado. Nenhuma aprovação por automação.
8. Quando houver Codex/VS Code: executar coletores G1/G2 em raízes locais, fora de todas as trees Git, comparar refs/hashes, stashes/arquivos não rastreados/DB schema, **nunca publicar segredos ou dados pessoais**.
9. Só então: benchmark real Jev em dataset sintético, label humano, regras baseline, falsos negativos críticos, custo/latência, privacidade, rollback. Não integrar provedor até aprovação.

## Contratos proibidos
- `CI PASS != HUMAN APPROVAL != SCIENTIFIC VALIDATION != TRAINING EFFECT`.
- `PASS_REPORTED != REMOTE_ATTESTED`.
- `GIT REMOTE EMPTY != NO LOCAL WORK`.
- `JEV SUGGEST != AUTHORIZATION`.
- `READ-ONLY RECONCILIATION != AUTOMATIC MERGE`.

**Nenhum trabalho pós-Codex foi presumido concluído.**