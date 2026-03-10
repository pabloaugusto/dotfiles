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
- `Paused`
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
- `Paused`
- `Testing`
- `Review`
- `Changes Requested`
- `Done`
- `Cancelled`

## Tipos de issue alvo

- `Epic`
- `Story`
- `Task`
- `Bug`
- `Spike`
- `Sub-task`

## Hierarquia e uso recomendado

- `Epic`
  - agrupa um contexto pequeno ou medio, com progresso observavel
  - substitui a necessidade de criar dezenas de links `Relates` entre itens do mesmo assunto
- `Story`
  - expressa regra de negocio, definicao global, fluxo funcional ou entrega com valor legivel
- `Task`
  - representa trabalho tecnico, operacional, documental ou de governanca
- `Bug`
  - registra falha, regressao ou comportamento incorreto
- `Spike`
  - concentra pesquisa, discovery, benchmark, links e recomendacao antes da execucao
- `Sub-task`
  - quebra a execucao dentro de um item pai quando isso melhora fluxo, ownership ou handoff

## Padrao de escrita das issues

- titulos curtos, humanos e sem prefixo com `ID` local
- descricoes em Markdown orientadas a leitura humana
- secoes base obrigatorias:
  - `Contexto`
  - `Resultado esperado`
  - `Criterios de aceite`
  - `Referencias`
- `Story` deve preferir o padrao `Card / Conversation / Confirmation`
- `Task` deve explicitar `Escopo tecnico` quando o detalhe de execucao for importante
- `Bug` deve explicitar `Problema observado` e `Impacto`

## Regra de criterios de aceite

- nenhum item deve entrar em `Refinement` ou `Ready` sem criterios de aceite iniciais
- os criterios precisam ser verificaveis por humanos e pelos agentes de QA/review
- criterios genericos sem ligacao com o resultado esperado nao sao suficientes
- quando a demanda ainda estiver em descoberta, os criterios podem ser iniciais, mas nao podem ficar ausentes
- `Story` deve sair de `Refinement` com `Spike` concluida por padrao, salvo dispensa explicita
- `Spike` precisa documentar tambem `Evidencias`, `Viabilidade`, `Ganhos esperados`,
  `Custo operacional` e `Pendencias abertas`

## Politica de linkagem entre issues

- usar `Epic` e `Parent` como agrupamento principal de contexto
- reservar `issue links` para dependencia real, bloqueio real, duplicidade ou implementacao correlata
- evitar `Relates` em massa quando o objetivo for apenas agrupamento tematico

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
- `Doing -> Paused`
- `Paused -> Doing`
- `Doing -> Testing`
- `Testing -> Review`
- `Review -> Done`
- `Review -> Cancelled`
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
- `Doing` representa apenas execucao ativa; espera operacional vai para `Paused`
- `Current Agent Role` representa ownership ativo em tempo real e deve ficar visivel no card
- backlog, refinement e ready devem permanecer ordenados por prioridade real
- `Start date` e `Due date` devem ser mantidos pelo `AI Product Owner` em todo item acima de `Sub-task`
- schema deve ser aplicado antes do backfill retroativo
- todo item semeado deve carregar link para pagina relacionada do `Confluence`
  ou comentario explicito de `n/a`
- referencias a arquivos e artefatos do repo em descricoes, comentarios e
  evidencias devem usar o link do arquivo no `GitHub`
- toda atuacao de agente deve gerar comentario estruturado com evidencia,
  conforme [`agent-operations.md`](agent-operations.md)
- revisao profunda deve ser feita por revisores especialistas por familia de
  arquivo; `ai-reviewer` atua como gate transversal, nao como reviewer unico
