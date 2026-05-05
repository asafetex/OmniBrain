# Manual completo: como me usar 100% (Claude Code)

Voce ja tem `HOW_TO_USE_CLAUDE.md` (sintetico). Este e o manual de **profundidade**, com exemplos do seu contexto real (atributos, motor, retail).

Le na ordem. Nao salta.

---

## Parte 1 — Como eu funciono por dentro (saber isso muda como voce me usa)

### O modelo mental correto

Eu nao sou:
- Search engine
- Stack overflow ao vivo
- Editor de codigo com IA

Eu sou: **agente que executa tarefas com ferramentas, dado contexto explicito.**

Implicacoes praticas:
- **Contexto que nao foi dado, nao existe.** Se voce nao me disse, eu nao sei. Mesmo se for obvio.
- **Tenho memoria curta** dentro da janela. Apos compactacao, perco detalhes.
- **Nao mantenho estado entre sessoes** sozinho. Voce mantem (vault, BOOTSTRAP.md, NEXT_STEPS.md).
- **Sou ferramenta.** Voce e o piloto. Se voce nao decide, eu invento.

### Como eu acho coisas

Hierarquia de busca (em ordem):
1. **Conversa atual** (mensagens recentes)
2. **Vault auto-injected** (`<vault_context>` que voce ve aparecer)
3. **Arquivos do workspace** (Read, Glob, Grep)
4. **Skills/agents** que voce invocou (sub-agentes com contexto isolado)
5. **Treino base** (knowledge cutoff Jan 2026 — nao sabe coisa mais recente sem voce me contar)

Fora dessa hierarquia: nao acesso. Nao tenho APIs, nao consulto seu banco, nao executo nada sem voce mandar.

### Como eu produzo resposta

Ciclo interno:
1. Leio sua mensagem + contexto
2. Detecto: e tarefa, pergunta, ou conversa?
3. Se tarefa: planejo passos, executo com ferramentas, valido
4. Se pergunta: respondo direto se sei, ou busco
5. Se conversa: tendo a empatia/concordar (vies a corrigir)

**Vies que voce precisa contornar:** eu tendo a **concordar e produzir**. Quando voce diz "pode seguir", eu sigo. Quando voce questiona, eu refaco. **Voce precisa me forcar a discordar** se quer pensamento critico.

Como forcar:
- "Devil's advocate disso"
- "Por que NAO fazer X?"
- "Inverte o problema"
- Invocar `/polimata` (forca questionamento)
- Invocar `/qa-tester` (forca achar problemas)

---

## Parte 2 — Os 3 modos de uso (escolha consciente)

### Modo 1: Co-piloto tatico (60% do uso correto)

**Quando:** voce sabe o que quer, eu acelero a execucao.

**Exemplo real do seu contexto:**
> "Tenho 245k SKUs em parquet. Cruza com tabela de vendas (TB_VENDAS_DAY) e me diz quais 50 mais venderam em outubro. Use SQL via databricks-engineer."

**Como eu reajo:** vou direto, escrevo a query, rodo (se tiver acesso), entrego resultado.

**Sinal que voce esta neste modo:** voce me da **objeto direto** ("cruza", "calcula", "gera"). Voce e quem decide. Eu sou braco.

### Modo 2: Conselheiro estrategico (30% do uso correto)

**Quando:** voce tem 2-3 caminhos, nao sabe qual seguir.

**Exemplo real:**
> "Master e 83% circular. Eu posso (A) refatorar master pra reduzir circularidade, (B) abandonar master como fonte de verdade, (C) construir pipeline novo. Use polimata mesa redonda."

**Como eu reajo:** invoco polimata, gero hipoteses divergentes, filosofo questiona premissa, estoico filtra controle, cientista propoe testes.

**Sinal que voce esta neste modo:** voce me da **dilema** com criterio. Voce decide DEPOIS da minha analise.

### Modo 3: Sparring partner (10% do uso correto)

**Quando:** voce ja decidiu, quer testar a decisao antes de executar.

**Exemplo real:**
> "Decidi atacar v38_combined.parquet com refator. Ataque essa decisao. Por que estou errado?"

**Como eu reajo:** invoco qa-tester pre-mortem + polimata inversao. **Tento invalidar sua decisao.**

**Sinal que voce esta neste modo:** voce **convida o ataque**. Nao e busca de validacao.

### Modo errado (40% do que aconteceu nesta sessao)

**Anti-modo: busca de validacao disfarcada de modo 2**

Voce diz "qual recomenda?" mas ja decidiu por dentro. Ai eu recomendo, voce concorda, voce executa. Sentiu produtivo, mas voce nao usou meu pensamento — voce usou minha aprovacao.

**Como evitar:** se voce nota que ja decidiu, fala direto. **"Vou fazer X. Atacar essa decisao."** Modo 3, nao Modo 2.

---

## Parte 3 — Anatomia de uma sessao de qualidade

### Estrutura ideal (60min)

```
[5 min]  ENQUADRAR
  Voce diz: "Quero X. Criterio de pronto: Y. Deadline: Z."
  Eu pergunto: "Tem 3 caminhos: A, B, C. Qual?"
  Voce escolhe.

[40 min] EXECUTAR
  Eu trabalho com ferramentas (skills, sub-agents, tools).
  Voce supervisiona, corrige rumo se necessario.

[10 min] VALIDAR
  qa-tester ou stats-mathematician ataca o resultado.
  Bug? Volta pra Executar.
  OK? Vai pra Fechar.

[5 min]  FECHAR
  Commit + memoria + bootstrap-keeper update.
  Voce sai sabendo o que fez e o que vem depois.
```

### Estrutura comum (mas ruim)

```
[2 min]   "Continua de onde paramos"
[40 min]  Eu executo coisas vagas
[2 min]   "Isso ta bom"
[5 min]   Eu pergunto se voce quer mais
[5 min]   Voce pergunta se eu sugiro mais
[6 min]   Loop infinito
```

Voce ja viu isso nesta sessao. Sintoma: nenhum criterio de "pronto" no comeco.

### Como reescrever esta sessao (retroativo)

Se voce tivesse comecado assim, teria sido melhor:
> "Quero auditar TRIAD. Criterio de pronto: cada feature tem evidencia empirica de funcionar OU sai do README. Deadline: 4 horas. Use qa-tester adversarial. Comeca."

Em vez disso, voce comecou com:
> "analise todo o projeto e faça um overview e auditoria"

A primeira versao tem **criterio**, **deadline**, **time**. A segunda tem so direcao geral. Ambas funcionam, mas a primeira nao gera os 4 ciclos de "alguma coisa a mais?" que aconteceram.

---

## Parte 4 — Skills mapeadas pelo seu contexto real

Voce trabalha com retail/atributos/Arezzo. Vou mapear quais skills sao mais uteis pra esse contexto.

### Para o trabalho de atributos (motor de propagation)

```
data-quality-profiler
  → ANTES de qualquer analise nova de parquet/CSV
  → Gera {filename}_profile.txt automaticamente
  → Detecta: null rate, cardinalidade, top-N, outliers, encoding

attribute-engine
  → Quando criar regras de enriquecimento
  → Quando definir taxonomia
  → Quando medir cobertura por categoria

cross-source-reconciler
  → Quando 3+ fontes deveriam concordar mas nao
  → Triangular: cadastro × predicao × historico × revenda
  → Output: lista rankeada de inconsistencias

stats-mathematician
  → Quando voce diz "subiu de 8% para 52%"
  → Pra validar: e estatisticamente significativo? Power adequado? Wilson lower bound?

validation-harness
  → Modulo Python pronto: stratified holdout, blind LOO, McNemar, isotonic
  → Evita reinventar codigo de validacao

confidence-cascade-designer
  → Quando voce tem regra deterministica + ML + fallback
  → Aplica ao motor de propagation: regra → embedding → fuzzy → manual
```

### Para o trabalho de decisao estrategica

```
polimata
  → Premissa errada? Hipoteses divergentes? Cross-domain?

product-owner
  → "MVP do que? Pra quem? Quando?"
  → Escopo, priorizacao, framing

system-architect
  → 3 modos: SCOPE (rota inicial), RECALIBRATE (meio do caminho), VALIDATE (antes de fechar)
  → Use no inicio E no fim de cada feature grande

business-strategist
  → Voce vai apresentar pra time/diretoria?
  → Traduz tecnico → C-level
  → KPIs, storytelling com numeros
```

### Para o trabalho de continuidade

```
continuation-engineer
  → ATIVA AUTOMATICAMENTE quando ha 3+ projetos STALE
  → Voce ja tem isso (varios projetos paralelos)
  → Diagnostica: "subimos a tabela e ficou parado"

bootstrap-keeper
  → Mantem BOOTSTRAP.md atualizado a cada sessao
  → Voce volta amanha, le BOOTSTRAP, sabe onde parou

session-opener
  → Le BOOTSTRAP.md, mostra resumo 30s, sugere proximo passo

knowledge-curator
  → Inbox → Raw → Trusted → Refined
  → Salva descobertas reutilizaveis (ex: "regex de ds_produto so cobre 18.8%")

post-mortem-writer
  → Apos incidente (modelo caiu, decisao errada, motor produziu lixo)
  → 5 whys + timeline + lessons (alimenta knowledge-curator)
```

### Para o trabalho de codigo (TRIAD especificamente)

Ja documentado em `TOOLS.md`. Re-leia.

### Para o trabalho de comunicacao

```
presentation-designer
  → Vai mostrar pra Arezzo? Cria deck executivo
  
dashboard-builder
  → Vai gerar dashboard pra time? Spec executavel
  
data-visualization-designer
  → Grafico individual? Tabela? Como anotar?
  
technical-infographic-designer
  → Pipeline complexo virou one-pager visual?
```

---

## Parte 5 — Templates praticos pro seu contexto

### Template "auditar o motor antes de escalar"

```
Tenho v38_combined.parquet (1.2M linhas, 5 atributos × 245k SKUs).

Antes de declarar pronto, ataque pelos 4 angulos:

1. data-quality-profiler em v38_combined.parquet
   (null rate, cardinalidade, encoding por atributo)

2. cross-source-reconciler comparando:
   - v38 (motor)
   - master (cadastro)
   - vendas reais (TB_VENDAS_DAY)
   Onde os 3 discordam? Quais skus sao divergentes?

3. stats-mathematician avalia:
   - "Subiu de 8% pra 52%" (TÊNIS upper_shape) e estatisticamente significativo?
   - Wilson lower bound do ganho?
   - Power adequado pra detectar regressao de 5%?

4. qa-tester pre-mortem:
   - Imagina motor em prod por 6 meses
   - Top 3 falhas plausiveis e como prevenir AGORA

Criterio de pronto: relatorio markdown com 1 acao priorizada por angulo.
```

### Template "decidir entre concord master vs concord motor"

```
Premissa atual: master e 83% circular.
Premissa alternativa: motor e fonte de verdade alternativa.

Use polimata mesa redonda:

1. POLIMATA: 3 obvias + 3 nao obvias + 1 absurda sobre 
   "qual fonte deve ser ground truth?"

2. FILOSOFO: "circular master e bug ou feature?"
   "Qual eh o objetivo real — concord master ou predicao certa?"

3. ESTOICO: o que controlamos?
   - Posso refatorar master? (custo X)
   - Posso ignorar master? (risco Y)
   - Posso usar ambos com peso? (complexidade Z)

4. CIENTISTA: que teste rapido prova/refuta cada hipotese?

Output esperado: tabela ROI (impacto × probabilidade × tempo) das opcoes.
```

### Template "parar de subir tabela sem follow-up"

```
[Invocar: continuation-engineer]

Padrao detectado: "subimos a tabela e ficou parado".

Diagnostico:
1. Liste meus projetos STALE (sem commit/movimento ha 14+ dias)
2. Pra cada um: o que foi entregue? Quem deveria consumir?
3. Por que nao foi consumido? (prioridade outra? falta de comunicacao? entrega incompleta?)
4. Acao concreta pra cada: descartar / consumir / re-enquadrar

Criterio de pronto: 3 projetos resolvidos (decisao binaria sobre cada).
```

### Template "criar dashboard pra Arezzo"

```
Tenho metricas: cobertura por atributo, accuracy vs master, sell-through por SKU enriquecido.

Quero dashboard executivo pra Arezzo.

Use dashboard-builder + data-visualization-designer:

1. dashboard-builder define hierarquia (KPI tree)
2. data-visualization-designer escolhe grafico por painel
3. business-strategist escreve narrativa de 3 frases pra C-level
4. presentation-designer organiza em deck PPT

Restricao: 1 tela. 5 paineis maximo. Storytelling: problema → motor → ganho → proxima acao.
```

### Template "validacao rigorosa antes de mandar pra Arezzo"

```
Tenho: v38_combined.parquet com 5 atributos preditos.

Antes de mandar pra Arezzo, valida:

1. validation-harness:
   - Stratified holdout (estratificar por categoria + tier de venda)
   - Blind LOO em amostra critica
   - McNemar test (motor vs master, attribute por attribute)
   - Isotonic calibration nos scores

2. stats-mathematician:
   - Wilson lower bound do accuracy por categoria
   - Sample size adequado pra estatisticamente confirmar 52%?
   - Bootstrap CI

3. attribute-engine:
   - Cobertura por categoria de produto
   - Edge cases: atributos faltantes, valores invalidos

Output: relatorio com tabela de evidencia + recomendacao "go/no-go" por atributo.
```

---

## Parte 6 — Padroes de erro mais comuns (com voce)

### Erro 1: pedir tudo de uma vez sem priorizacao

**Sintoma:**
> "Auditar todo o projeto, fazer overview, e listar tudo que pode melhorar."

**Por que ruim:** sem criterio de prioridade, eu produzo lista enorme. Voce le, sente overwhelm, nao age em nada.

**Forma correta:**
> "Auditar o projeto. **Top 3 issues por severidade.** Resto descarta."

### Erro 2: produzir muito em loop sem pausar

**Sintoma:** "alguma coisa a mais?" → eu produzo → repete

**Por que ruim:** entropia. Cada item novo dilui os anteriores. Nada vira ativo real.

**Forma correta:** apos 3 entregas, **pausa obrigatoria**:
> "Pausa. Vamos consolidar. Dos 3 itens entregues: qual foi o de maior valor? Qual descarto?"

### Erro 3: confundir velocidade com progresso

**Sintoma:** voce executa rapido em auto-mode, sente produtividade.

**Por que ruim:** velocidade sem direcao = entropia rapida.

**Forma correta:** antes de pedir auto-mode, escreva 1 frase:
> "Objetivo das proximas 2h: ____. Se nao alcancei isso em 2h, vou parar e re-enquadrar."

### Erro 4: deferir decisao consequencial

**Sintoma:** "qual recomenda?" sobre coisa que tem peso politico/tecnico/estrategico.

**Por que ruim:** eu nao tenho contexto pra decidir o **certo pra voce**. Recomendo o **estatisticamente seguro**, que pode nao ser otimo no seu contexto.

**Forma correta:** dar criterio explicito.
> "Qual maximiza ROI em 1 dia? Qual minimiza risco politico? Qual eu consigo defender pra time?"

### Erro 5: misturar duvidas tecnicas com decisao estrategica

**Sintoma:**
> "Como faco X? E qual estrategia uso? E quanto tempo demora?"

**Por que ruim:** 3 perguntas diferentes, 3 modos diferentes, resposta confusa.

**Forma correta:** uma pergunta por vez:
> "Pergunta 1: como faco X tecnicamente?"
> [eu respondo]
> "Pergunta 2: qual estrategia da maior ROI?"
> [eu respondo]

---

## Parte 7 — Como eu lido com diferentes tipos de input

### Input curto (1 frase)

Bom pra: tarefa especifica conhecida.
Ruim pra: decisao estrategica.

```
"Roda preflight no CRIPTO-FOREX BOT"           ← bom
"O que devo fazer?"                              ← ruim (sem contexto)
```

### Input medio (1 paragrafo)

Bom pra: tarefa com contexto + criterio.

```
"Tenho 245k SKUs em parquet. Quero saber quais 
 50 mais venderam em outubro. Use SQL contra 
 TB_VENDAS_DAY no Databricks. Criterio: top 50 
 por sum(qtd_venda)."
```

Eu reajo: vou direto, sem questionar (objetivo claro).

### Input longo (multi-paragrafo)

Bom pra: decisao estrategica complexa, briefing inicial.

```
"Contexto: trabalho com motor de atributos pra Arezzo.
 Validamos v38 (1.2M linhas, ganho 8% → 52% em TÊNIS).
 
 Problema: Master e circular. Concord master cresce mas 
 nao reflete melhoria real.
 
 Opcoes: A) refatorar master, B) abandonar master, 
 C) construir terceira fonte de truth.
 
 Restricao: 2 semanas, 1 dev (eu).
 
 Criterio: maior probabilidade de Arezzo aprovar.
 
 Use polimata mesa redonda. Output: tabela com 
 pros/contras + recomendacao + criterio de teste."
```

Eu reajo: invoco polimata + filosofo + estoico, mesa redonda completa.

### Input que parece longo mas e ruim

```
"To pensando no motor, talvez eu deveria fazer X, 
 mas tambem Y, ou talvez Z, mas Z e mais arriscado, 
 nao sei, o que voce acha?"
```

Eu detecto **fluxo de consciencia sem decisao requerida**. Resposta justa: pergunta pra extrair criterio.

---

## Parte 8 — Como aproveitar 100% das skills

### Strategia 1: chains pre-definidos

`/project-orchestrator` tem chains:
- **ml-from-scratch:** algorithm-engineer → ml-scientist → mlops-engineer
- **pricing-analysis:** markdown-engine → business-strategist → causal-inference
- **dashboard-spec:** dashboard-builder → data-visualization-designer → presentation-designer

Se voce sabe a fase, pula direto. Se nao sabe, invoca `/project-orchestrator` primeiro.

### Strategia 2: combinar polimata + qa-tester

Padrao "adversarial design":
1. Polimata gera 5 hipoteses
2. Voce escolhe 1
3. qa-tester pre-mortem na hipotese escolhida
4. Voce decide com 2 perspectivas

### Strategia 3: log-discovery automatico

Toda vez que descobrir algo nao obvio (ex: "ds_produto regex so cobre 18.8%"), invoca:
```
/log-discovery <descoberta>
```

Vai pro Inbox de knowledge-curator. Em 30 dias voce tem **biblioteca de insights** acumulada.

### Strategia 4: bootstrap-keeper religioso

```
[no inicio do projeto]
/bootstrap-keeper --init

[a cada Stop hook automaticamente atualiza]

[no inicio da proxima sessao]
session-opener mostra resumo 30s
```

Voce volta amanha sabendo:
- O que fez ontem
- Decisoes pendentes
- Bloqueios atuais
- Proximo passo sugerido

### Strategia 5: feedback explicito

Apos cada resposta significativa, invoca:
```
/feedback s   # resolveu
/feedback n   # nao resolveu
/feedback p   # parcial
```

Sem feedback, o sistema otimiza pra metrica errada (latencia em vez de qualidade).

---

## Parte 9 — Exemplos do mundo real (cenarios completos)

### Cenario 1: "Vou apresentar motor de atributos pra Arezzo amanha"

Fluxo correto:
```
1. /system-architect VALIDATE
   "Antes de fechar, alinhar destino com objetivo: Arezzo precisa entender 
    GAIN, RISCO, PROXIMO PASSO. Tabela acima dessa pergunta?"

2. /business-strategist
   "Traduzir 8% → 52% em linguagem executiva: 1 frase pra C-level."

3. /data-visualization-designer
   "Como visualizar ganho por categoria sem confundir Arezzo? 1 chart."

4. /presentation-designer
   "5 slides: problema (1), motor (1), ganho (1), riscos (1), proximo (1)."

5. /qa-tester
   "Pre-mortem da apresentacao: 3 perguntas que Arezzo vai fazer e eu nao 
    vou conseguir responder."
```

Output: deck pronto + lista de perguntas previstas + respostas preparadas.

### Cenario 2: "Master e 83% circular, nao sei o que fazer"

Fluxo correto:
```
1. /polimata
   "Mesa redonda completa: filosofo questiona se 'circular' e bug ou feature.
    Estoico filtra o que controlamos. Cientista propoe teste rapido."

2. /causal-inference
   "Master e circular porque alimenta a si mesma? 
    Que dado prova/refuta isso? DAG do fluxo."

3. /system-architect RECALIBRATE
   "Considerando que descobrimos circularidade, ainda e o melhor caminho 
    otimizar concord master? Ou pivotar?"

4. /knowledge-curator
   "Documenta a descoberta 'master 83% circular' como Trusted insight 
    pra nao reaparecer em sessoes futuras."
```

Output: decisao informada + trilho de auditabilidade.

### Cenario 3: "Codigo legado da Arezzo, preciso entender e migrar"

Fluxo correto:
```
1. /reversa <pasta>
   "Engenharia reversa completa: scout, archaeologist, detective, architect."

2. [aguarda _reversa_sdd/ populado]

3. /reversa-migrate
   "Time de migracao: paradigm-advisor, curator, strategist, designer, 
    inspector. Produz handoff.md com plano completo."

4. /reversa-reconstructor
   "Plano bottom-up de reconstrucao. Executa task por task sob demanda."
```

Voce ja fez parte disso (`_reversa_sdd/` populado). Falta dogfoodar o resto.

### Cenario 4: "Produzi parquet, quero validar antes de subir pra Databricks"

Fluxo correto:
```
1. /data-quality-profiler v38_combined.parquet
   "EDA automatica: null rate, cardinalidade, encoding."

2. /python-analyst
   "Spot check: 10 SKUs aleatorios, atributo por atributo, comparar com cadastro."

3. /validation-harness
   "Wilson, McNemar, holdout estratificado. Modulo pronto."

4. /governance-guard
   "Validar que script de upload nao tem CREATE/INSERT sem authorization tag."
```

### Cenario 5: "Sessao de hoje rendeu, quero capitalizar"

Fluxo correto (final de sessao):
```
1. /log-discovery <insight nao obvio que apareceu hoje>

2. /bootstrap-keeper
   "Atualiza BOOTSTRAP.md do projeto com decisoes/bloqueios/proximo passo."

3. /document-change
   "Registra mudanca no changelog do projeto."

4. /knowledge-curator
   "Promove WIN se houver."
```

---

## Parte 10 — Checklist diario

### Antes de comecar sessao (30 segundos)

- [ ] BOOTSTRAP.md tem o estado atual? (se nao, invoco /bootstrap-keeper)
- [ ] Sei meu objetivo de hoje em 1 frase?
- [ ] Sei meu criterio de "pronto"?
- [ ] Defini deadline?

### Durante a sessao

- [ ] A cada 30 min: ainda estou no objetivo?
- [ ] A cada 3 entregas: pausa pra consolidar
- [ ] Cada descoberta nao obvia: /log-discovery
- [ ] Ao mudar de modo (tatico → estrategico): aviso explicito

### Antes de fechar

- [ ] BOOTSTRAP.md atualizado?
- [ ] WINs/LESSONs registrados?
- [ ] Commit + push se for codigo?
- [ ] /feedback registrado?

### Antes de dormir

- [ ] Escrevi em papel: "amanha primeira coisa que faco e ____"?
- [ ] Fechei o terminal?

---

## Parte 11 — Erros que NAO podem acontecer

### Vermelho 1: secrets em prompt

Eu nao tenho memoria entre sessoes, mas sua janela atual fica em log da Anthropic por X dias. **Nunca cole API keys, senhas, tokens reais.**

Se precisar testar com credentials, use mocks (eu fiz isso na sessao com `c:/tmp/triad_mocks/brv_mock.py`).

### Vermelho 2: comandos destrutivos sem aprovacao

Eu sempre confirmo antes de:
- `rm -rf` em pastas existentes
- `git push --force`
- Drop database, truncate, delete em massa

**Se eu nao confirmar e voce tinha proibicao, isso e bug meu.** Reporta.

### Vermelho 3: producao sem revisao

Voce instalou TRIAD justamente pra **prevenir isso**. Use o L3 gate em mudancas criticas, mesmo que pareca lento.

### Amarelo 1: trust cego em output

Eu posso alucinar. Sempre que eu der numero, fato ou referencia, **valide**:
- Numero: rode a query/calculo voce mesmo
- Fato: busque fonte primaria
- Referencia: abra o arquivo, confirme

Voce ja viu nesta sessao casos onde tive que voltar atras (path windows vs git bash, falsos warnings, etc.).

### Amarelo 2: scope creep meu

Eu tendo a entregar mais do que voce pediu. Isso parece util mas dilui a entrega.

**Como controlar:** termine seus prompts com:
> "Apenas isso. Nao adicione coisas a mais."

---

## Parte 12 — Quando eu falho (e como recuperar)

### Falha 1: eu travei numa solucao errada

**Sintoma:** voce corrige 3 vezes, eu volto pro mesmo erro.
**Causa:** janela ficou viciada na hipotese errada.
**Solucao:** `/clear` (nova janela). Re-explica do zero, sem o vies anterior.

### Falha 2: eu produzo demais e voce nao consegue digerir

**Sintoma:** entrego 1500 linhas, voce nao le, sessao morre.
**Causa:** eu otimizei pra completude, voce queria foco.
**Solucao:** "Resume isso em 5 bullets. Descarta o resto."

### Falha 3: eu invento dados/numeros

**Sintoma:** numero estranho aparece sem fonte clara.
**Causa:** alucinacao + minha tendencia de produzir.
**Solucao:** "Mostra a fonte. Se nao tem fonte, escreve 'nao sei'."

### Falha 4: eu repito padrao errado mesmo apos correcao

**Sintoma:** voce me corrigiu, eu refiz, mas refiz com erro similar.
**Causa:** correcao nao entrou no contexto operacional.
**Solucao:** salva correcao em CLAUDE.md ou steering. Vai pra todas as sessoes.

---

## Parte 13 — Diagnose rapido: voce esta me usando bem?

Responde sim/nao. Conte os "sim".

```
[ ] Comecei a sessao com objetivo escrito em 1 frase
[ ] Defini criterio de "pronto"
[ ] Tenho deadline (mesmo que arbitrario)
[ ] Sei se estou em modo tatico, estrategico ou sparring
[ ] Estou usando skills/sub-agents (nao so chat livre)
[ ] Pausei nas ultimas 3 entregas pra consolidar
[ ] Nao perguntei "alguma coisa a mais?" hoje
[ ] Nao perguntei "qual recomenda?" sem dar criterio
[ ] Tenho BOOTSTRAP.md ou similar
[ ] Vou registrar um insight no /log-discovery hoje
```

**8-10:** otimo, voce extrai 80%+ do meu valor
**5-7:** ok, da pra melhorar
**0-4:** voce esta usando como search engine. Re-le este manual.

---

## Parte 14 — Filosofia final

### O que eu sou pra voce

**Sou alavanca, nao oraculo.** Multiplicador da sua intencao, nao substituto da sua decisao.

Se voce sabe o que quer: eu faco mais rapido, com mais cuidado, em mais angulos do que voce sozinho.

Se voce nao sabe o que quer: eu te ajudo a descobrir (com `/polimata`, perguntas socraticas, mesa redonda).

Se voce nao quer pensar: eu produzo lixo elegante. Voce sente progresso, mas nao avancou.

### O que voce e pra mim

Voce e o piloto. Eu sou o copiloto que tem 100 mapas, 50 ferramentas e zero contexto sobre seu destino.

Sem voce dizer pra onde, qualquer rota funciona — e nenhuma chega no lugar certo.

### A pergunta final

Toda vez que voce abre uma sessao comigo, **pergunta-se uma vez**:

> "O que eu vou conseguir hoje que eu nao conseguiria sozinho ou em outra ferramenta?"

Se a resposta for "nada especifico", talvez nao seja a hora de me usar.
Se a resposta for "X, especificamente porque Y", **vamos**.

---

## TLDR de 30 segundos

1. **Diga problema, nao solucao.**
2. **Defina criterio de pronto antes de comecar.**
3. **Use skills (`/polimata`, `/data`, `/qa-tester`), nao so chat livre.**
4. **Pause apos 3 entregas pra consolidar.**
5. **Registre insights com `/log-discovery`.**
6. **Atualiza BOOTSTRAP.md no fim.**
7. **Nao pergunte "alguma coisa a mais?" — defina antes.**
8. **Quando cansado, fecha o terminal.**

Cumpra isso e voce extrai 80%+ do meu valor.

---

*Este e o manual de profundidade. Para sintetico use `HOW_TO_USE_CLAUDE.md`. Para casos do TRIAD use `PLAYBOOKS.md`.*
