# Jira Writing Standards

- Status: `artifact-first`
- Data-base: `2026-03-08`
- Fontes oficiais principais:
  - [`Atlassian - What are epics, stories, tasks, and subtasks?`](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/)
  - [`Atlassian - User stories with examples and a template`](https://www.atlassian.com/agile/project-management/user-stories)
  - [`Atlassian - Acceptance criteria explained`](https://www.atlassian.com/work-management/project-management/acceptance-criteria)
  - [`Atlassian - Epics, stories, themes, and initiatives`](https://www.atlassian.com/agile/project-management/epics-stories-themes)
  - [`Atlassian - What are code reviews and how do they save time?`](https://www.atlassian.com/br/agile/software-development/code-reviews)
  - [`Atlassian - Working with specialists`](https://www.atlassian.com/br/agile/teams/working-with-specialists)
  - [`GitHub Docs - About pull request reviews`](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
  - [`GitHub Docs - About code owners`](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

## Decisao adotada

Para este piloto, o padrao recomendado e:

- `Epic` para agrupar contexto pequeno ou medio
- `Story` para regra de negocio, definicao global, fluxo funcional ou entrega com valor legivel
- `Task` para trabalho tecnico, operacional, documental ou de governanca
- `Bug` para falha, regressao ou comportamento incorreto
- `Spike` para pesquisa timeboxed, benchmark, levantamento documental e reducao de incerteza
- `Sub-task` apenas para decomposicao de execucao

Essa hierarquia substitui o uso excessivo de `Relates` para agrupamento.

## Principios de escrita

- escrever para pessoas leitoras, nao para o chat
- manter o titulo curto, direto e sem `ID` local no inicio
- deixar o corpo suficiente para uma pessoa entender o trabalho sem contexto externo
- registrar referencias, evidencias e dependencias no proprio item
- quebrar em `Sub-task` somente quando isso melhorar fluxo, ownership ou handoff
- manter backlog e listas ordenadas por prioridade real
- manter `Start date` e `Due date` atualizados para todo item acima de `Sub-task`

## Padrao por tipo de issue

### Epic

- objetivo: agrupar um contexto claro e acompanhar progresso agregado
- deve conter:
  - `Contexto`
  - `Resultado esperado`
  - `Criterios de aceite`
  - `Referencias`
- deve evitar detalhe tecnico excessivo

### Story

- objetivo: expressar uma entrega ou decisao com valor legivel
- deve preferir o padrao `Card / Conversation / Confirmation`
- corpo recomendado:
  - `Historia`
  - `Contexto`
  - `Resultado esperado`
  - `Criterios de aceite`
  - `Referencias`

### Task

- objetivo: orientar execucao tecnica, operacional ou documental
- corpo recomendado:
  - `Contexto`
  - `Resultado esperado`
  - `Escopo tecnico`
  - `Criterios de aceite`
  - `Referencias`

### Bug

- objetivo: explicar a falha e como validar a correcao
- corpo recomendado:
  - `Problema observado`
  - `Impacto`
  - `Resultado esperado`
  - `Criterios de aceite`
  - `Evidencias`

### Sub-task

- objetivo: separar uma fatia executavel de um item pai
- deve ser curta e concreta
- deve conter:
  - `Contexto da execucao`
  - `Entrega esperada`
  - `Evidencias`
  - `Dependencias`

### Spike

- objetivo: consolidar pesquisa e reduzir incerteza antes da execucao
- corpo recomendado:
  - `Perguntas de pesquisa`
  - `Achados`
  - `Evidencias`
  - `Viabilidade`
  - `Riscos`
  - `Alternativas`
  - `Ganhos esperados`
  - `Custo operacional`
  - `Pendencias abertas`
  - `Recomendacao`
  - `Referencias`
- regra:
  - `Story` deve ter `Spike` concluida por padrao antes de sair de `Refinement`
  - `Task` recebe `Spike` quando houver incerteza relevante

## Regra de revisao

- `ai-tech-lead` e reviewer obrigatorio e aprovador oficial de todo PR ou
  origem equivalente
- revisao profunda de codigo e contratos continua sendo feita por revisores
  especialistas da familia afetada
- `ai-reviewer` fica como gate transversal para risco cross-cutting, multiplas
  linguagens ou consolidacao final de pareceres
- quando o escopo tocar mais de uma familia relevante, as revisoes especializadas
  podem acontecer em paralelo antes do fechamento final do `ai-tech-lead`

Especializacoes minimas do piloto:

- `ai-reviewer-python`
- `ai-reviewer-powershell`
- `ai-reviewer-automation`
- `ai-reviewer-config-policy`

## Regra de criterios de aceite

Os criterios de aceite precisam ser:

- verificaveis
- observaveis
- ligados ao resultado esperado
- suficientes para `QA` e `Reviewer`

Evitar:

- criterios vagos como `funcionar corretamente`
- criterios que so repetem o titulo
- ausencia de prova ou de forma de validacao

## Linkagem e rastreabilidade

- usar `Epic` e `Parent` para agrupamento principal
- usar `issue links` so para bloqueio, dependencia, duplicidade ou relacao tecnica real
- linkar `Confluence` sempre que houver contexto, decisao ou documento oficial relevante
- quando a issue ou comentario citar artefato do repo, usar o link do arquivo no
  `GitHub`, nao apenas path local
- essa regra vale tambem para reparo retroativo de backlog, comentarios e
  descricoes gerados pela automacao
- registrar em comentario estruturado o trabalho de cada agente que tocar a issue
- registrar quem revisou o item, com evidencia objetiva do que foi checado

## Aplicacao neste piloto

- backlog retroativo deve ser reescrito com titulos mais curtos
- descricoes retroativas devem seguir o schema acima
- epics devem ser pequenos ou medios, orientados por contexto
- `Story` e `Task` devem virar o eixo principal do fluxo
- `Spike` deve sustentar o refinamento sempre que a demanda depender de pesquisa
- `Sub-task` deve ser a quebra de execucao, nao o mecanismo de agrupamento
