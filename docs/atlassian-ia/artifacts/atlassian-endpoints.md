# Endpoint Catalog

- Status: `artifact-first`
- Data-base: `2026-03-07`
- Swagger base fornecida pelo usuario:
  - [`Jira Cloud Swagger v3`](https://dac-static.atlassian.com/cloud/jira/platform/swagger-v3.v3.json?_v=1.8409.0)
  - [`Jira Cloud Postman`](https://developer.atlassian.com/cloud/jira/platform/jiracloud.3.postman.json)
  - [`Jira REST API v3`](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#about)
  - [`Confluence REST API v2`](https://developer.atlassian.com/cloud/confluence/rest/v2/)

## Task map de aplicacao do schema

### Task: aplicar statuses

- `GET /rest/api/3/project/{projectKey}/statuses`
  - snapshot do estado efetivo do projeto
- `POST /rest/api/3/statuses`
  - criar statuses faltantes quando a estrategia escolhida for create-before-workflow
- `GET /rest/api/3/status`
  - listar statuses existentes reutilizaveis

### Task: aplicar workflow

- `POST /rest/api/3/workflows/create/validation`
  - validar payload do workflow antes da escrita
  - request schema oficial: `WorkflowCreateValidateRequest`
  - contrato obrigatorio: enviar envelope `payload` com `WorkflowCreateRequest`
    e, quando desejado, `validationOptions.levels`
- `POST /rest/api/3/workflows/create`
  - criar workflow e, quando aplicavel, statuses associados
  - request schema oficial: `WorkflowCreateRequest`
  - contrato obrigatorio: enviar apenas o corpo de criacao, sem envelope de
    validacao
- `GET /rest/api/3/workflow/search`
  - verificar existencia e lookup de workflow alvo

### Task: aplicar workflow scheme

- `GET /rest/api/3/workflowscheme/project`
  - descobrir o scheme atual do projeto
- `POST /rest/api/3/workflowscheme`
  - criar o workflow scheme alvo
- `PUT /rest/api/3/workflowscheme/project`
  - associar scheme quando o projeto ainda nao tiver issues
- `POST /rest/api/3/workflowscheme/project/switch`
  - trocar scheme quando houver issues e for necessario mapear statuses

### Task: aplicar custom fields

- `GET /rest/api/3/field/search`
  - inventario dos fields atuais
- `POST /rest/api/3/field`
  - criar custom field
- `GET /rest/api/3/field/{fieldId}/context`
  - localizar ou validar contextos
- `POST /rest/api/3/field/{fieldId}/context`
  - criar contexto quando necessario
- `POST /rest/api/3/field/{fieldId}/context/{contextId}/option`
  - criar opcoes para fields `select`, `multiselect` e `checkbox`

### Task: aplicar dashboards

- `GET /rest/api/3/dashboard/search`
  - verificar dashboards existentes
- `POST /rest/api/3/dashboard`
  - criar dashboard
- `GET /rest/api/3/dashboard/gadgets`
  - catalogar gadgets disponiveis no tenant
- `POST /rest/api/3/dashboard/{dashboardId}/gadget`
  - adicionar gadgets quando o tenant expuser `moduleKey` ou `uri` valido

### Task: aplicar board

- `GET /rest/agile/1.0/board`
  - estado atual do acesso a `Jira Software board API`
- `GET /rest/agile/1.0/board/{boardId}/configuration`
  - leitura oficial do mapeamento atual de colunas quando o scope efetivo
    estiver verde
- `POST /rest/agile/1.0/board`
  - criar board quando o gap de scope efetivo for resolvido
- observacao:
  - a API oficial publica do `Jira Software` exposta hoje no repo cobre leitura
    de configuracao, mas nao expoe um endpoint publico equivalente para mutar o
    layout de colunas; o ajuste fino do board permanece dependente de UI
    autenticada ou de capacidade oficial futura
  - probes reais executados no tenant em `2026-03-08`:
    - `gateway + Bearer`: `401 Unauthorized; scope does not match`
    - `gateway + Basic`: `401 Unauthorized`
    - `site + Basic`: `401 Client must be authenticated to access this resource`
    - `site + Bearer`: `403 Failed to parse Connect Session Auth Token`
  - conclusao operacional atual:
    - `gateway + Bearer` continua sendo o modo canonico mais proximo do alvo
    - o gap residual parece estar em scope/entitlement/acesso efetivo do
      produto, nao apenas em base path

## Task map de semeadura

### Task: semear backlog no Jira

- `GET /rest/api/3/search/jql`
  - detectar duplicacao e buscar itens existentes
- `POST /rest/api/3/issue`
  - criar epics, tasks, stories, bugs e subtasks
- `PUT /rest/api/3/issue/{issueKey}`
  - ajustar fields apos a criacao quando a semeadura precisar enriquecer o item
- `POST /rest/api/3/issue/{issueKey}/attachments`
  - anexar bundle de migracao ou evidencias binarias
- `POST /rest/api/3/issue/{issueKey}/comment`
  - registrar evidencia, justificativa, link de artefato, backfill retroativo
    e atividade estruturada dos agentes
- `POST /rest/api/3/issue/{issueKey}/transitions`
  - posicionar o item no status correto do backfill

### Task: semear documentacao no Confluence

- `GET /wiki/api/v2/spaces`
  - resolver `space` por key ou alias
- `GET /wiki/api/v2/pages`
  - localizar pagina por titulo
- `POST /wiki/api/v2/pages`
  - criar pagina oficial
- `GET /wiki/api/v2/pages/{id}`
  - obter versao atual antes de atualizar storage
- `PUT /wiki/api/v2/pages/{id}`
  - atualizar pagina oficial ja existente

## Observacoes operacionais

- `Jira` usa `REST API v3`
- `Confluence` usa `REST API v2`
- payloads de `apply` e `seed` devem nascer da documentacao oficial
  vendorizada em [`../../../vendor/atlassian/`](../../../vendor/atlassian/)
  e dos artefatos desta pasta, nao de probes ad hoc
- a API `Jira Software board` segue bloqueada no tenant atual com
  `401 Unauthorized; scope does not match`
- cada endpoint usado no apply e na semeadura deve ser citado tambem nos
  comentarios tecnicos das issues correspondentes no `Jira`
- comentarios dos agentes devem sempre carregar evidencia ou `n/a` explicito;
  comentario sem prova nao encerra trabalho nem valida handoff
