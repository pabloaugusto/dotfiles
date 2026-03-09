# Jira Schema

- Status: `artifact-first`
- Data-base: `2026-03-07`
- Fonte canonica:
  [`../../../config/ai/jira-model.yaml`](../../../config/ai/jira-model.yaml)
- Sincronizacao alvo:
  - comentario tecnico e/ou attachment na issue de schema do `Jira`
  - pagina `DOT - Jira Schema` no `Confluence`

## Identidade estrutural

- projeto: `DOT`
- nome atual: `dotfiles`
- estilo: `company-managed-software`
- workflow alvo: `DOT - Autonomous Delivery Workflow`
- workflow scheme alvo: `DOT - Autonomous Delivery Workflow Scheme`
- board alvo quando a API `Jira Software` destravar:
  `DOT - Autonomous Engineering`

## Colunas ativas do fluxo-base

- `Backlog`
- `Refinement`
- `Ready`
- `Doing`
- `Testing`
- `Review`
- `Changes Requested`
- `Done`

## Colunas condicionais por capability flag

- `SEO Review`
  - habilitar apenas quando o papel `ai-seo-specialist` estiver ativo em
    [`../../../config/ai/agents.yaml`](../../../config/ai/agents.yaml)

## Statuses alvo

- `Backlog`
- `Refinement`
- `Ready`
- `Doing`
- `Testing`
- `Review`
- `Changes Requested`
- `Done`

## Tipos de issue alvo

- `Epic`
- `Story`
- `Task`
- `Bug`
- `Sub-task`

## Components baseline

- `ai-control-plane`
- `jira-confluence-integration`
- `documentation-governance`
- `bootstrap`
- `environment`
- `secrets`
- `ci`
- `developer-experience`
- `cross-platform`

## Labels baseline

- `atlassian-ia`
- `bootstrap`
- `powershell`
- `python`
- `automation`
- `windows`
- `linux`
- `wsl`
- `ci`
- `security`
- `docs`
- `governance`

## Custom fields ativos no tenant atual

Os papeis opcionais `ai-designer`, `ai-ux-cro-analyst` e
`ai-seo-specialist` estao desabilitados hoje, entao os campos abaixo ficam
fora do apply inicial.

Campos ativos:

- `Work Kind`
- `Workstream`
- `Affected Platforms`
- `Risk`
- `Current Agent Role`
- `Next Required Role`
- `Confluence Source`
- `Evidence Links`
- `Automation Mode`

Campos condicionais:

- `Needs Design`
  - habilitar quando `ai-designer` estiver ativo
- `Needs UX Review`
  - habilitar quando `ai-ux-cro-analyst` estiver ativo
- `Needs SEO Review`
  - habilitar quando `ai-seo-specialist` estiver ativo

## Transicoes alvo

- `Backlog -> Refinement`
- `Refinement -> Ready`
- `Ready -> Doing`
- `Doing -> Testing`
- `Testing -> Review`
- `Review -> Done`
- `Testing -> Changes Requested`
- `Review -> Changes Requested`
- `Changes Requested -> Doing`

## Contrato oficial de apply

- o schema do projeto deve ser aplicado apenas com base na spec oficial
  vendorizada em [`../../../vendor/atlassian/jira-openapi.json`](../../../vendor/atlassian/jira-openapi.json)
- `POST /rest/api/3/workflows/create/validation` usa
  `WorkflowCreateValidateRequest`
- `POST /rest/api/3/workflows/create` usa `WorkflowCreateRequest`
- o endpoint legado `POST /rest/api/3/search` nao entra mais no fluxo; a busca
  de issues no apply usa `GET /rest/api/3/search/jql`

## Dashboards alvo

- `DOT - Autonomous Engineering Overview`
- `DOT - AI Delivery Ops`

## Regras de semeadura

- nenhuma issue entra em execucao sem existir no `Jira`
- schema deve ser aplicado antes do backfill retroativo
- todo item semeado deve carregar link para pagina relacionada do `Confluence`
  ou comentario explicito de `n/a`
- toda atuacao de agente deve gerar comentario estruturado com evidencia,
  conforme [`agent-operations.md`](agent-operations.md)
