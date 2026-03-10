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
- [`jira-writing-standards.md`](jira-writing-standards.md): padrao de escrita
  de epics, stories, tasks, bugs e subtasks, com criterios de aceite e
  hierarquia recomendada
- [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md): base
  normativa dos reviewers especializados, com especificacoes oficiais,
  convencoes secundarias e tooling de enforcement
- [`reviewer-decision-model.md`](reviewer-decision-model.md): modelo formal de
  decisao tecnica dos reviewers especializados, com severidade, decisoes e
  contrato de saida estruturada
- [`reviewer-severity-policy.md`](reviewer-severity-policy.md): politica
  canonica de severidade para separar blockers, majors, minors, debt e nit
- [`reviewer-jira-workflow-policy.md`](reviewer-jira-workflow-policy.md):
  politica operacional de comentarios, evidencias e transicoes do reviewer no Jira
- [`python-quality-review-agent.md`](python-quality-review-agent.md): blueprint
  canonico do reviewer Python como gate absoluto de qualidade
- [`universal-engineering-standards-stack.md`](universal-engineering-standards-stack.md):
  stack universal de governanca tecnica com standards, style guides, lint,
  format, seguranca, Git, CI/CD, containers e AI
- [`onepassword-runtime-read-inventory.md`](onepassword-runtime-read-inventory.md):
  inventario versionado das leituras `op` no runtime para orientar cache,
  invalidacao e reducao de rate limit
- [`onepassword-runtime-cache-contract.md`](onepassword-runtime-cache-contract.md):
  contrato canonico de classes de material, TTL, invalidacao e locais
  permitidos para o cache de runtime do `1Password`
- [`migration-bundle.md`](migration-bundle.md): contrato do bundle auditavel
  que deve acompanhar cada lote de exportacao para `Jira` e `Confluence`
