# 10 FAQ

## Preciso de API key para usar?

Não. O projeto foi desenhado para CLIs já logados e fallback manual.

## O que acontece se Codex ou Gemini não abrirem?

`tools/run_gate.py` gera prompts de copy/paste e salva em `tmp/manual-prompts/`.

## Posso usar só Codex no L3?

Não. L3 exige Codex + Gemini com verdict explícito.

## PreGate é obrigatório?

Não. DeepSeek/CodeRabbit são opcionais e nunca substituem o Gate principal de L3.

## Onde ficam memórias se ByteRover falhar?

`context-hub/05_INBOX/byterover-imports/`.

## Posso pular Change Package?

Não em L3. Em L2/L1 é tecnicamente possível, mas desaconselhado.

## Esse fluxo substitui CI?

Não. Complementa CI e revisão humana.

## Como evitar poluição no Obsidian?

Promova apenas wins executáveis, com validação e contexto mínimo reutilizável.

