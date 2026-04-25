# Consolidated SAAS Projects Overview

## 1. AIOS ( Jarvis AIOX)

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\AIOS`

**Type:** Universal AI Agent Framework (Node.js/NPM)

**Description:**
Framework de Desenvolvimento Auto-Modificável Alimentado por IA. Fundado em Desenvolvimento Ágil Dirigido por Agentes. Transforma qualquer domínio com expertise especializada de IA: desenvolvimento de software, entretenimento, escrita criativa, estratégia de negócios, bem-estar pessoal.

**Features:**
- Context Hub (conhecimento curado em `docs/context-hub/`)
- Multi-IDE support (Claude Code, Gemini CLI, Codex CLI, Cursor, Copilot, AntiGravity)
- Hooks lifecycle para automação
- CLI-first (jarvis_aiox commands)

**Key Packages:**
- `aios-install`
- `aios-pro-cli`
- `gemini-aios-extension`
- `installer`

**Dependencies:** Node.js 18+, NPM

---

## 2. AIOS_ci_repro

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\AIOS_ci_repro`

**Type:** CI/Reprodução do AIOS

**Description:**
Clone do AIOS para testes de CI e reprodução. Mesma estrutura base.

---

## 3. JARVIS OS

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\JARVIS Os\jarvis_os`

**Type:** Sistema Operacional de Agentes (Full-stack)

**Description:**
Jarvis OS - Sistema Operacional de Agentes do Asafe (BTW Data). UX-first sandbox.

**Stack:**
- Backend: Node/Express + Socket.IO
- Frontend: React + Vite
- Persistence: Local JSON (`data/kanban_state.json`)

**Key Files:**
- `server.js` - Main server
- `agent_worker.js` - Agent worker
- `agents/` - Agent definitions

**Current Phase:** SANDBOX_MODE=1 (sem OpenClaw calls, sem agents execution, sem Postgres)

---

## 4. JARVIS OS v1

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\JARVIS Os\jarvis_os_v1`

**Type:** Versão 1 do Jarvis OS

**Description:**
Versão anterior/alternativa com mais documentação de integração.

**Documents:**
- `ARCHITECTURE.md`
- `CLAWDOS_CATALOG.md`
- `INTEGRATION_COMPLETE.md`
- `HIERARCHY_TEST.md`

---

## 5. OmniBrain TRIAD

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\OmniBrain\OmniBrain-remote\omnibrain-triad`

**Type:** Framework de Governança Multi-Agent

**Description:**
MVP executável para governança de mudanças com fluxo `diff-first`, consenso multiagente e memória operacional.

**TRIAD Governance:**
- Claude Code como executor
- Codex CLI como auditor técnico
- Gemini CLI como auditor sistêmico

**Features:**
- Context Hub via Obsidian
- Ferramentas para routing, context bundle, change package, gates
- Pre-push hook para enforcement de L3
- Memory stats (WIN/LESSON/REVIEW)

---

## 6. AUTO ANALYSYS (DATA_BRAIN)

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\AUTO ANALYSYS`

**Type:** Worker Plane para Analytics e ML

**Description:**
DATA_BRAIN is a production-first worker plane for analytics and ML execution. Designed to be called by Jarvis/AIOS control plane using versioned JSON contracts.

**Features:**
- Multi-agent architecture
- Contract-first integration (10+ contratos v1)
- Idempotent execution por run_id
- SLO, observability, incident management
- Tenant isolation
- Scheduler e DLQ

**Stack:**
- Backend, workers, services
- Databricks integration
- Observability (Prometheus, etc)

---

## 7. OmniBrain + Estratégia de AI (Novo)

**Path:** `C:\Users\PC\Desktop\ASAFE\PROJETOS\DESENVOLVIMENTO\SAAS\OmniBrain\omnibrain-triad\docs\11_strategy_merged.md`

**Type:** Documento de Estratégia

**Description:**
Estratégia otimizada para uso de ferramentas AI via CLI, focando em minimizar custo de contexto.

**Workflow 3-Step:**
1. Claude (1 prompt) → Especificação completa + tasks identificadas
2. Opencode → Execução das tasks em bulk (free)
3. Claude + Codex → Review final + validação multi-agent

**Princípios:**
- Context window como recurso escasso
- Execução única (single sprint) → validação corrige
- Consenso multi-agent (diferentes LLMs = diferentes视角)
- Memória via Obsidian

---

## Relationships / Arquitetura Proposta

```
                    ┌─────────────────────┐
                    │  OMNIBRAIN (Orq.)  │
                    │  (Governança +     │
                    │   Memória)          │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ↓                      ↓                      ↓
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  JARVIS OS    │    │   DATA_BRAIN    │    │   OUTROS        │
│  (Agentes)    │    │  (Analytics/ML) │    │  (Trading, etc) │
└───────────────┘    └─────────────────┘    └─────────────────┘
        ↑                      ↑                      ↑
        │                      │                      │
   AIOS (Framework        AIOS (Framework       AIOS (Framework
   de Agents)             de Agents)              de Agents)
```

**Resumo:**
- **OmniBrain** = Orquestrador + Governança + Memória
- **AIOS** = Framework base de agentes (usado por Jarvis + DATA_BRAIN)
- **JARVIS OS** = Sistema operacional de agentes (UX-first)
- **DATA_BRAIN** = Worker para analytics/ML (chamado por Jarvis/AIOS)
- **Estratégia** = Workflow otimizado de AI (Claude → Opencode → Claude+Codex)

---

*Consolidado: 26/03/2026*