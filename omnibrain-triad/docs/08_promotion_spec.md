# 08 Promotion Spec

## Política anti-poluição

Nem toda nota vira nó do Graph.

Sobe para `02_GRAPH` apenas o que for:

- reproduzível;
- validado em caso real;
- reutilizável em mais de um contexto;
- claro e curto.

## Pipeline de promoção

1. Origem:
   - ByteRover ou INBOX bruto.
2. Curadoria:
   - remover contexto irrelevante;
   - manter checklist e validação objetiva.
3. Destino:
   - nó atômico no Graph.
4. Atualização de links:
   - incluir no `index.md` da disciplina.

## Critérios mínimos de promoção

- snippet mínimo funcional (quando aplicável);
- quando usar;
- objetivo;
- checklist;
- validação objetiva;
- armadilhas;
- links relacionados.

## Quando não promover

- tentativa não validada;
- solução específica demais de um único incidente;
- conteúdo redundante com nó existente.

Use `tools/promote_to_obsidian.py` para listar e mover candidatos.

