## Clearance E Gates

- modelar `startup-ready.json` como artefato de prontidao executavel
- bloquear primeira resposta operacional sem `ready_for_work`
- invalidar `clearance` em drift de branch, worktree, auth, `WIP`, contexto ou
  contratos carregados
- impedir delegacao sem contexto de startup valido
- falhar cedo quando o startup estiver apenas parcialmente absorvido
- manter o relatorio humano de startup, mas nao trata-lo como prova suficiente
