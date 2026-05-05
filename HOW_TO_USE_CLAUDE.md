# Como me usar (Claude Code)

Tutorial pratico baseado nos padroes que **funcionaram** com voce nesta sessao e nas anteriores. Sem teoria. So o que da resultado.

---

## A regra mestra: 1 frase

**Diga o problema, nao a solucao.**

| Forma fraca | Forma forte |
|---|---|
| "Adiciona uma feature de X" | "Tenho problema Y, pode ser que X resolva mas nao sei" |
| "Cria um teste pra Z" | "Z quebrou ontem, quero saber se vai quebrar de novo" |
| "Refatora esse modulo" | "Esse modulo esta confuso, dificultando manutencao em Y" |
| "Mais features" | "Onde esta meu maior atrito hoje?" |

Quando voce me da problema, eu posso questionar. Quando voce me da solucao, eu so executo.

---

## Os 5 padroes que funcionaram com voce

### Padrao 1: Mesa redonda dos 4 pensadores (`/polimata`)

**Quando usar:** decisao com mais de 1 caminho viavel.

**Como invocar:**
```
/polimata <descricao do problema>
```

**O que voce ganha:**
- Polimata gera 3 obvias + 3 nao obvias + 1 absurda-mas-testavel
- Filosofo questiona se a premissa esta certa
- Estoico filtra o que voce controla vs nao controla
- Cientista propoe testes empiricos rapidos

**Exemplo real desta sessao:**
> "alguma coisa a mais que poderiamos melhorar?"

→ Polimata respondeu: A1 (curacao auto INBOX), B2 (telemetria), B3 (smoke pytest), A2 (templates Gemini), priorizadas com ROI.

### Padrao 2: Roteamento por especialista (`/data`)

**Quando usar:** problema tecnico que precisa de competencia especifica.

**Como invocar:**
```
/data <descricao>
```

**O que acontece:** o roteador classifica complexidade (1-5) e monta time:
- Score 1-2: 1-2 agents flat
- Score 3-5: arvore com qa-tester + stats + polimata na validacao

**Exemplo real:**
> "auditoria do TRIAD"

→ score 5 → time: qa-tester (security review) + python-analyst (refactor sugerido) + stats-mathematician (metricas)

### Padrao 3: Engenharia reversa (`/reversa`)

**Quando usar:** voce **nao escreveu** o codigo e precisa entender ou migrar.

**Como invocar:**
```
/reversa <pasta-do-projeto>
```

**O que da:** documentacao executavel completa — C4, ERD, dominio, lifecycle, gaps, design system. Voce ja tem `_reversa_sdd/` populado nesta workspace.

### Padrao 4: Skill especifica explicita

**Quando usar:** voce sabe exatamente qual ferramenta resolve.

**Como invocar:**
```
/security-review              <- audita branch atual
/init                         <- gera CLAUDE.md
/dashboard-spec               <- vira analise em spec de dashboard
/pricing-diagnosis            <- workpad de pricing
/log-discovery                <- registra insight pra nao perder
```

Tem 70+ skills disponiveis. Os mais uteis pra voce:
- `polimata` — pensar lateral
- `data` — orchestrator
- `qa-tester` — pre-mortem
- `stats-mathematician` — validacao numerica
- `business-strategist` — traduzir tecnico pra C-level
- `causal-inference` — provar X causou Y
- `forecaster-simulator` — Monte Carlo, what-if
- `cross-source-reconciler` — triangular 3+ fontes
- `post-mortem-writer` — apos incidente
- `knowledge-curator` — promover insight
- `bootstrap-keeper` — manter BOOTSTRAP.md do projeto

### Padrao 5: Auto-mode + comando vazio

**Quando usar:** voce esta cansado mas tem energia pra UMA coisa.

**Como invocar:**
```
[auto-mode ja ativo]
"continue"  ou  "pode seguir"
```

**Risco:** se voce nao tem foco, eu invento trabalho. Use so quando ja tem direcao definida na frase anterior.

---

## Como me dar contexto eficiente

### Vault auto-injection

Voce ja tem hook que injeta notas relevantes do vault Obsidian em cada mensagem (`<vault_context>`). **Funciona.** Eu li sua nota sobre concord master, sobre attribute propagation, sobre fase de enquadrar — tudo via vault context. Voce nao precisa colar.

### Quando colar arquivo manualmente

So quando o vault nao injetou. Use formato:

```
"Le este arquivo: <caminho-absoluto>"
```

Ou:

```
"O arquivo X tem isso:
[cola conteudo]"
```

### Quando referenciar codigo

Use markdown link com caminho relativo:
```
Vai em [omnibrain-triad/tools/run_gate.py](omnibrain-triad/tools/run_gate.py) e ...
```

Eu abro automaticamente. Mais eficiente que descrever.

---

## Os 4 sinais de que voce esta me usando errado

### Sinal 1: voce pergunta "qual recomenda?" sem dar criterios

**Sintoma:** ja ocorreu 4 vezes nesta sessao.
**Diagnostico:** voce esta deferindo decisao, nao pedindo conselho.
**Cura:** especifique o criterio.

Exemplo:
- Errado: "qual recomenda?"
- Certo: "qual da maior ROI em 1 dia de trabalho?"
- Certo: "qual e o menor risco?"
- Certo: "qual eu consigo fazer sozinho sem CLI X?"

### Sinal 2: voce pergunta "alguma coisa a mais?"

**Sintoma:** ocorreu 3 vezes.
**Diagnostico:** voce nao sabe se esta pronto.
**Cura:** defina criterio de "pronto" antes de comecar.

Pergunta antes de comecar:
- "Como vou saber que terminei isto?"
- "Que evidencia me convence?"

### Sinal 3: voce so executa, nunca pausa

**Sintoma:** auto-mode + "pode seguir" repetido.
**Diagnostico:** producao virou substituto pra decisao.
**Cura:** force pausa apos N tarefas. Pergunta: "e isto ainda esta servindo o objetivo X?"

### Sinal 4: voce constroi mais do que usa

**Sintoma:** TRIAD com 20 tools, 0 uso real seu.
**Diagnostico:** bonsai mode.
**Cura:** regra "nada novo ate dogfood completo de 3 sessoes".

---

## Quando eu sou especialmente util vs quando atrapalho

### Sou util quando

- Voce tem **problema concreto com diff/codigo**
- Voce quer **questionar premissa** (filosofo)
- Voce quer **gerar hipoteses divergentes** (polimata)
- Voce quer **validacao adversarial** (qa-tester)
- Voce esta em **incerteza tecnica especifica**
- Voce precisa **traduzir tecnico → executivo**
- Voce quer **post-mortem blameless** depois de incidente

### Atrapalho quando

- Voce esta cansado e quer eu decidir por voce
- Voce esta procurando **distracao produtiva**
- O problema e **politico/social/emocional** (eu nao acesso seu time, seus stakeholders)
- Voce ja sabe a resposta e quer validacao (vies de confirmacao — uso `/polimata` pra forcar contradicao)
- A decisao depende de **dados que so voce tem na cabeca**

---

## Exemplos copiaveis (templates)

### Template 1: dogfood do TRIAD

```
Pega [tarefa real do projeto Y, descrita em 1 frase] e:
1. Roda triad_oracle pra checar historico
2. Cria branch
3. Implementa
4. Gera Change Package L[1/2/3]
5. Roda Gate (manual fallback ok)
6. Me ajuda interpretar resultado
```

### Template 2: investigacao causal

```
Observei [fato concreto com numero].
Hipotese atual: [explicacao].
Use causal-inference pra validar:
- Que outros fatores poderiam explicar isso?
- Que teste rapido refutaria a hipotese atual?
- Que dado contraditorio devo procurar?
```

### Template 3: decisao estrategica

```
Tenho 2-3 caminhos: A, B, C.
Criterio: [especifico, mensuravel].
Restricao: [tempo/budget/risco].
Use polimata mesa redonda + estoico (filtro do que controlo).
Quero ranking final por (impacto × probabilidade × testabilidade).
```

### Template 4: pre-mortem

```
Vou implementar X em Y semanas.
Use qa-tester pre-mortem:
- Imagina que falhou em 6 meses
- Liste top 5 causas plausiveis
- Pra cada uma: como prevenir AGORA com baixo custo?
```

### Template 5: post-mortem (apos incidente)

```
Incidente: [o que aconteceu, quando, impacto].
Use post-mortem-writer:
- Timeline objetivo
- 5 whys
- Contributing factors (sem culpado)
- Action items mensuraveis
- Lessons pra knowledge-curator
```

### Template 6: refactor sem quebrar

```
Modulo X tem [N] arquivos, eu quero refatorar pra Y motivo.
Quero:
1. spec-driven-developer escreve spec antes do codigo
2. qa-tester pre-mortem do refactor
3. stats-mathematician define criterio "nao houve regressao"
4. So entao implementacao
```

### Template 7: traducao tecnico → executivo

```
Tenho [analise tecnica X com numeros].
Use business-strategist:
- 3 frases que C-level entende
- 1 grafico que conta a historia
- 3 acoes concretas com timeline e owner
- 1 risco que ele precisa decidir
```

### Template 8: cruzamento Sudoku (3+ fontes)

```
Tenho fonte A diz X, fonte B diz Y, fonte C diz Z.
Nao bate.
Use cross-source-reconciler:
- Cada fonte e restricao, nao verdade
- Onde elas concordam? Onde discordam?
- Qual interseccao explica todas?
- Qual fonte provavelmente esta errada e por que?
```

---

## Hierarquia de quando me invocar

```
Tenho duvida pequena (5min)
  → pergunta direta no chat. nao precisa skill.

Tenho problema medio (1-2h)
  → /data ou skill especifica.

Tenho decisao com tradeoffs
  → /polimata mesa redonda.

Vou comecar feature/refactor consequencial
  → /spec-driven-developer (spec antes de codigo).

Algo quebrou em prod
  → /post-mortem-writer (blameless).

Estou perdido sobre o que fazer
  → NAO me invoque. Para. Volta com clareza.
```

---

## Anti-padroes que vi nesta sessao

### "Build more"

Voce ja sabe. Nao repito.

### "Polimata como martelo"

Polimata e otimo pra **questionar premissa** e **gerar hipoteses divergentes**. Ruim pra:
- Codar implementacao linha-a-linha (use `python-analyst`)
- Decisao binaria simples (uso direto, sem mesa redonda)
- Quando voce ja decidiu (pra que questionar?)

### "Auto-mode como muleta"

Auto-mode e otimo quando voce tem **direcao clara mas falta tempo**. E pessimo quando voce nao sabe o que fazer — eu so vou inventar trabalho.

### "Pedir score"

Toda vez que voce me pediu score nesta sessao, voce ja sabia a resposta — queria validacao externa. **Eu nao deveria substituir seu julgamento.** Se voce precisa de score externo, peca review de humano (nao IA).

---

## Comandos cheat sheet

```
# Pensamento lateral
/polimata <problema>

# Roteamento inteligente
/data <pedido>

# Engenharia reversa
/reversa <pasta>

# Spec antes de codigo
/spec-driven-developer

# Validacao adversarial
/qa-tester <coisa pra quebrar>

# Estatistica rigorosa
/stats-mathematician

# Post-mortem
/post-mortem-writer

# Curar conhecimento
/log-discovery   ou   /knowledge-curator

# Traducao C-level
/business-strategist

# Init projeto
/init

# Health check workspace
/audit
```

---

## Limites meus que voce precisa saber

### Nao acesso

- Suas conversas em outras IAs (ChatGPT, Gemini, etc.)
- Seu calendario, email, slack
- APIs externas (a menos que voce me passe credenciais — nao recomendado)
- Estado de runtime (containers rodando, jobs em execucao) — so o que voce me diz

### Sou bom mas nao perfeito em

- Estimativa de tempo (overestimo trivial, subestimo complexo)
- Estimativa de complexidade (calibro com base em cdoigo, nao em politica organizacional)
- Detectar quando voce esta cansado vs focado (so vejo padroes do texto)

### Sou ruim em

- Te conhecer profundamente fora desta janela (memoria reseta entre sessoes)
- Decisao com peso emocional/politico (nao tenho contexto)
- Substituir conversa com humano que esta no mesmo problema que voce

---

## Ultimo conselho

Voce me usou bem nesta sessao quando:
- Trouxe **problema concreto** (auditar TRIAD, smoke test todas as features)
- Me deu **criterio** ("so pode dizer que faz X se testar")
- Me **interrompeu** quando eu desviou ("acho que voce confundiu")
- Pediu **honestidade** ("seu score e veredito")

Voce me usou mal quando:
- Perguntou "alguma coisa a mais?" sem criterio
- Perguntou "qual recomenda?" sem definir o "qual" comparativo
- Pediu pra eu seguir em auto-mode sem direcao

**Padrao geral:** sou util quando voce me da problema com criterio. Sou armadilha quando voce me da espaco vazio pra preencher.

---

## TLDR

| Situacao | Acao |
|---|---|
| Sei o problema, nao a solucao | `/polimata` ou pergunta direta |
| Sei a solucao tecnica, falta executar | `/data` ou skill especifica |
| Tenho 2+ caminhos | `/polimata` mesa redonda |
| Vou comecar coisa grande | `/spec-driven-developer` |
| Algo quebrou | `/post-mortem-writer` |
| Estou perdido | **nao me invoque, para** |
| Cansado mas com 1 hora | tarefa concreta + auto-mode |
| Cansado sem direcao | fecha o terminal |

---

*Salve este arquivo. Re-leia antes de comecar sessoes longas. Use os templates copiando-colando.*
