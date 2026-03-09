# Artefatos Atlassian IA

Fonte canonica inicial dos artefatos de schema, endpoint catalog e contrato de
sincronizacao da trilha `Jira + Confluence + repo`.

## Regra desta pasta

- todo schema nasce primeiro aqui ou em [`../../../config/ai/`](../../../config/ai/)
  como artefato versionado no repo
- depois da aplicacao ou da semeadura, o mesmo artefato deve ser refletido em
  tarefa correspondente do `Jira` e/ou em pagina correspondente do `Confluence`
- nenhum workflow, rotina, payload, endpoint ou logica de sincronizacao pode
  existir apenas na memoria do chat

## Artefatos atuais

- [`jira-schema.md`](jira-schema.md): schema funcional alvo do projeto `DOT`
  no `Jira`, derivado de [`../../../config/ai/jira-model.yaml`](../../../config/ai/jira-model.yaml)
- [`confluence-schema.md`](confluence-schema.md): arquitetura de informacao e
  estrategia de publicacao do `Confluence`, derivada de
  [`../../../config/ai/confluence-model.yaml`](../../../config/ai/confluence-model.yaml)
- [`atlassian-endpoints.md`](atlassian-endpoints.md): catalogo dos endpoints
  oficiais usados para aplicar schema, semear backlog e sincronizar a
  documentacao
- [`agent-operations.md`](agent-operations.md): contrato do passo a passo
  operacional por papel em `Jira` e `Confluence`, com comentarios estruturados
  e evidencia obrigatoria
- [`migration-bundle.md`](migration-bundle.md): contrato do bundle auditavel
  que deve acompanhar cada lote de exportacao para `Jira` e `Confluence`
