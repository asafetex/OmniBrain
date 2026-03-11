# 09 MCP Optional

## Status no MVP

MCP/Connectors é opcional. O MVP funciona sem MCP.

## Quando habilitar

- quando quiser reduzir copy/paste entre ferramentas;
- quando sua stack já tem servidor MCP confiável;
- quando o ganho operacional justificar manutenção extra.

## Passos de habilitação (genéricos)

1. Verifique suporte da sua ferramenta com `--help`.
2. Configure endpoint/cliente MCP conforme documentação oficial da própria ferramenta.
3. Faça teste de leitura de recurso simples.
4. Nunca substitua o fallback local:
   - scripts Python + markdown + INBOX devem continuar funcionando.

## Regras

- Não transformar MCP em dependência crítica do fluxo L3.
- Se MCP cair, operar por arquivos locais e CLIs.
- Registrar em `DECISION` quando ativar/desativar MCP.

