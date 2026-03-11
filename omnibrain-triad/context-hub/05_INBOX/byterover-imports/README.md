# ByteRover Imports INBOX

Fallback local para memórias quando ByteRover CLI estiver indisponível.

## Uso

- scripts salvam aqui automaticamente em caso de falha.
- curadoria semanal decide:
  - arquivar,
  - promover para Graph,
  - descartar ruído.

## Convenção

- Conteúdo mantém ID `MEM::<TYPE>::<PROJECT>::<TOPIC>::<YYYYMMDD-HHMM>`.
- Em Windows, nome de arquivo fallback usa `MEM__<TYPE>__<PROJECT>__<TOPIC>__<YYYYMMDD-HHMM>.md`.
