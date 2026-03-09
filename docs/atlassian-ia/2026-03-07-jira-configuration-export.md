# Export de Configuracao do Jira

- Status: `schema-e-seed-aplicados-com-gap-em-board`
- Data-base: `2026-03-07`
- Relacionados:
  - [`../../config/ai/jira-model.yaml`](../../config/ai/jira-model.yaml)
  - [`2026-03-07-diagnostico-auth-e-acesso-atlassian.md`](2026-03-07-diagnostico-auth-e-acesso-atlassian.md)
  - [`2026-03-07-atlassian-auth-scopes-and-permissions.md`](2026-03-07-atlassian-auth-scopes-and-permissions.md)

## Alvo declarado

- projeto: `DOT`
- board alvo: `DOT - Autonomous Engineering`
- fluxo alvo:
  - `Backlog`
  - `Refinement`
  - `Ready`
  - `Doing`
  - `Testing`
  - `Review`
  - `Changes Requested`
  - `Done`
- issue types alvo:
  - `Epic`
  - `Story`
  - `Task`
  - `Bug`
  - `Sub-task`
- custom fields alvo:
  - `Work Kind`
  - `Workstream`
  - `Affected Platforms`
  - `Risk`
  - `Current Agent Role`
  - `Next Required Role`
  - `Confluence Source`
  - `Evidence Links`
  - `Automation Mode`
  - `Needs Design`
  - `Needs UX Review`
  - `Needs SEO Review`

## Estado atual validado

- `issue types`: aderentes
- `components`: aplicados por API em `2026-03-07`
- `statuses` oficiais do workflow: aplicados por API em `2026-03-08`
  - `Backlog`
  - `Refinement`
  - `Ready`
  - `Doing`
  - `Paused`
  - `Testing`
  - `Review`
  - `Changes Requested`
  - `Done`
- `custom fields`: aplicados por API em `2026-03-08`
- `workflow` e `workflow scheme`: aplicados por API em `2026-03-08`
- `dashboards`: criados por API em `2026-03-08`
- `semeadura retroativa`: executada por API em `2026-03-08`
  - migration issue criada: [`DOT-1`](https://pabloaugusto.atlassian.net/browse/DOT-1)
  - bundle auditavel anexado em `DOT-1`
  - issues criadas no seed inicial e verificadas por API: `64`
- total atual confirmado no tenant apos `DOT-84`: `84`
- intervalo atual confirmado: `DOT-1` -> `DOT-84`
  - status atuais no tenant:
    - `Backlog`: `42`
    - `Done`: `32`
    - `DOING`: `6`
    - `Refinement`: `1`
    - `PAUSED`: `2`
    - `TESTING`: `1`
- nova frente oficial de rastreabilidade aberta:
  - [`DOT-78`](https://pabloaugusto.atlassian.net/browse/DOT-78): epic
    `Rastreabilidade GitHub no fluxo Atlassian`
  - [`DOT-79`](https://pabloaugusto.atlassian.net/browse/DOT-79): story
    `Integrar GitHub, Jira Dev e Confluence`
  - [`DOT-80`](https://pabloaugusto.atlassian.net/browse/DOT-80) ->
    [`DOT-84`](https://pabloaugusto.atlassian.net/browse/DOT-84): subtasks de
    conexao, naming, workflows/deployments, runbook e validacao ponta a ponta
- `board`: segue com um gap residual:
  - API oficial em `401 Unauthorized; scope does not match`
  - o layout visual ja foi alinhado na UI autenticada e nao e mais o bloqueio principal

## Delta restante

### Board e dashboards pendentes

- alinhar o board `DOT board` ou substitui-lo pelo board alvo
  `DOT - Autonomous Engineering`
- manter por API o mesmo mapeamento de colunas ja validado visualmente na UI:
  - `Backlog`
  - `Refinement`
  - `Ready`
  - `Doing`
  - `Paused`
  - `Testing`
  - `Review`
  - `Changes Requested`
  - `Done`
- os dashboards alvo ja existem:
  - `DOT - Autonomous Engineering Overview`
  - `DOT - AI Delivery Ops`

### Pos-seed e operacao continua

- manter a governanca pos-seed em paralelo no repo, `Jira` e `Confluence`
- preservar o bundle auditavel por lote em `DOT-1` ou na issue de migracao
  correspondente
- manter como contrato perene que referencias ao repo em descricoes,
  comentarios e paginas sincronizadas usem URL oficial do `GitHub`, nunca
  `path` local
- permitir promocao automatica para URL oficial apenas quando o arquivo estiver
  rastreado no `Git`; caches, sessoes de browser e outros artefatos efemeros
  ficam como texto descritivo e nao como link
- tratar como ressalva operacional que arquivos novos desta worktree exigem
  `commit checkpoint + push` antes de terem URL valida no `GitHub`
- tratar o gap visual/API do board sob backlog explicito em
  [`DOT-65`](https://pabloaugusto.atlassian.net/browse/DOT-65)
- tratar a validacao visual browser-level sob backlog explicito em
  [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66)
- usar `ai:atlassian:docs:sync` para manter o `Confluence` atualizado mesmo
  quando a semeadura completa de `Jira` nao puder ser rerrodada
- nao liberar nova rodada de seed enquanto `project.target_board.layout_confirmed`
  permanecer `false`, salvo excecao humana explicita

## Bloqueios reais confirmados por API

- `GET /rest/agile/1.0/board`:
  - `401`
  - mensagem: `Unauthorized; scope does not match`
- causa mais provavel no token atual:
  - ausencia de `read:project:jira` no snapshot anterior

## Estado atualizado apos o token amplo

Validado em `2026-03-08`:

- `GET /rest/api/3/workflow/search`: `ok`
- `GET /rest/api/3/issuetypescheme/project`: `ok`
- `GET /rest/api/3/field/search`: `ok`
- apply de workflow, workflow scheme, custom fields e dashboards: `ok`
- `GET /rest/agile/1.0/board`: continua `401 Unauthorized; scope does not match`
- board UI atual: alinhada ao workflow oficial; o gap remanescente e apenas de
  automacao pela API

## Ordem de aplicacao assim que o acesso subir

1. liberar ou corrigir o acesso efetivo da `Jira Software board API`
2. alinhar o layout do board ao workflow oficial
3. validar colunas finais com probe API e evidencia visual
4. como a semeadura em massa ja foi executada nesta rodada por excecao aprovada,
   usar as proximas iteracoes para governanca pos-seed, drift control e
   normalizacao do board
