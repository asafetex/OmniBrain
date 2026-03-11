# Security Policy

## Regras obrigatórias

- Não armazenar secrets, tokens ou chaves em markdown.
- Não incluir dumps com dados sensíveis.
- Não copiar logs com PII para o Graph.
- Redigir payload sensível antes de registrar memória.

## Em revisões L3

Rejeitar automaticamente quando houver:
- vazamento de segredo;
- validação de entrada ausente em fluxo crítico;
- risco de permissão indevida;
- mudança de auth sem teste mínimo.

## Higiene operacional

- usar variáveis de ambiente para segredos;
- preferir exemplos sintéticos;
- revisar anexos antes de promoção.

