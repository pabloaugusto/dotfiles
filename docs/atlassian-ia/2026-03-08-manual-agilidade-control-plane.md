# Manual de agilidade do control plane

- Status: `consolidado`
- Data-base: `2026-03-08`
- Epic Jira: [`DOT-91`](https://pabloaugusto.atlassian.net/browse/DOT-91)
- Task pai: [`DOT-92`](https://pabloaugusto.atlassian.net/browse/DOT-92)
- Spike Jira: [`DOT-93`](https://pabloaugusto.atlassian.net/browse/DOT-93)
- Base completa consultada:
  [`2026-03-08-atlassian-agile-hub-inventory.md`](2026-03-08-atlassian-agile-hub-inventory.md)

## Objetivo

Definir o modelo agil oficial deste projeto com base em fontes primarias da
Atlassian e nos guias classicos de `Agile`, `Scrum` e `Kanban`, traduzindo esse
material para um fluxo realista de operacao em:

- `Jira` como sistema de registro do trabalho
- `Confluence` como sistema de registro da documentacao
- repo como fonte de verdade do codigo e dos artefatos versionados

## Fontes oficiais mais relevantes para a operacao

### Fundacao

- [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- [The Scrum Guide](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf)
- [The Kanban Guide](https://kanbanguides.org/english/)

### Atlassian Agile Hub

- [Atlassian Agile](https://www.atlassian.com/br/agile)
- [Project management](https://www.atlassian.com/br/agile/project-management)
- [Kanban](https://www.atlassian.com/br/agile/kanban)
- [Scrum](https://www.atlassian.com/br/agile/scrum)
- [Scrumban](https://www.atlassian.com/br/agile/project-management/scrumban)
- [Definition of Ready](https://www.atlassian.com/br/agile/project-management/definition-of-ready)
- [Definition of Done](https://www.atlassian.com/br/agile/project-management/definition-of-done)
- [User stories](https://www.atlassian.com/br/agile/project-management/user-stories)
- [Acceptance criteria](https://www.atlassian.com/work-management/project-management/acceptance-criteria)
- [Backlog refinement](https://www.atlassian.com/br/agile/project-management/backlog-refinement-meeting)
- [Workflow management](https://www.atlassian.com/br/agile/project-management/workflow-management)
- [Kanban metrics](https://www.atlassian.com/br/agile/project-management/kanban-metrics)
- [Continuous improvement](https://www.atlassian.com/br/agile/project-management/continuous-improvement)
- [Standups](https://www.atlassian.com/br/agile/scrum/standups)
- [Retrospectives](https://www.atlassian.com/br/agile/scrum/retrospectives)
- [Scrum roles](https://www.atlassian.com/br/agile/scrum/roles)
- [Epics, stories, themes, and initiatives](https://www.atlassian.com/br/agile/project-management/epics-stories-themes)

## Sintese executiva

O modelo mais adequado para este projeto nao e `Scrum` puro. O repo opera com
fluxo continuo, backlog vivo, trabalho tecnico de infraestrutura, documentacao,
integracoes, automacao e discovery. Por isso, a estrategia correta e:

- `Kanban` como mecanismo de fluxo puxado
- praticas de `Scrum` usadas como cadencias de alinhamento
- `Scrumban` como linguagem de desenho operacional

## Principios que vamos adotar

### 1. Visualizar o trabalho inteiro

O board precisa mostrar o fluxo ponta a ponta, do intake ate a entrega, sem
esconder espera, retrabalho ou interrupcao.

### 2. Puxar, nao empurrar

Nenhum agente inicia trabalho fora de `Ready`. A demanda e puxada quando a fase
anterior foi concluida e a capacidade existe.

### 3. Limitar trabalho ativo

`Doing` representa apenas trabalho em execucao real. Item sem atuacao corrente
nao pode ficar em `Doing` por conveniencia.

### 4. Tornar politicas explicitas

`Definition of Ready`, `Definition of Done`, criterios de aceite, obrigacao de
`Spike`, regras de handoff e evidencia minima precisam estar documentados e
aplicados pelo workflow.

### 5. Usar feedback loops curtos

Refinement, review, QA, docs sync e retro precisam acontecer cedo e com
frequencia, nao apenas no fim da demanda.

### 6. Melhorar continuamente

Toda friccao estrutural do fluxo vira backlog de melhoria com rastreabilidade,
nao uma adaptacao informal perdida em comentario.

## Modelo operacional adotado

### Paradigma

- `Scrumban` com board `Kanban`
- backlog central no `Jira`
- docs oficiais no `Confluence`
- comentarios estruturados como log operacional do time de agentes

### Cadencias recomendadas

- refinement recorrente para converter `Backlog` em `Ready`
- checkpoint diario ou assincrono de saude do fluxo
- review ao fim de cada incremento relevante
- retrospectiva periodica de gargalos, drifts e desperdicios

### Enriquecimento proativo de backlog e refinement

Os papeis de engenharia nao devem ficar ociosos esperando apenas ativacao
explicita.

Contrato adotado:

- `ai-engineering-architect`, `ai-engineering-manager` e `ai-tech-lead`
  inspecionam proativamente itens em `Backlog` e `Refinement`
- esses papeis deixam insumos tecnicos, referencias, links, riscos, alternativas,
  benchmarks e recomendacoes antes de o `PO` promover o item para `Ready`
- isso reduz descoberta tardia durante `Doing` e melhora a solidez do backlog

### Ownership ativo

O status da issue representa a fase do fluxo. O campo `Current Agent Role`
representa quem esta atuando naquele momento.

Regras:

- quando alguem comeca a atuar, `Current Agent Role` deve ser preenchido
- quando o trabalho deixa de estar ativo, o campo deve ser limpo
- `Next Required Role` deve apontar o handoff esperado

### Priorizacao continua do backlog

Se existe uma lista ordenada, ela precisa refletir prioridade real.

Regras:

- toda demanda nova entra no ponto correto do backlog, e nao apenas no fim da lista
- `Backlog`, `Refinement` e `Ready` devem permanecer ordenados por prioridade
- o `AI Product Owner` e responsavel por recalcular a ordem sempre que surgir
  demanda nova, bloqueio, mudanca de risco ou ajuste humano
- o `AI Product Owner` tambem mantem `Start date` e `Due date` atualizados para
  todo item acima de `Sub-task`, para sustentar timeline, roadmap e releases

## Hierarquia de trabalho

### Epic

Agrupa contexto pequeno ou medio com progresso observavel.

### Story

Representa regra de negocio, definicao global, experiencia de uso, criterio de
governanca ou entrega com valor legivel por humanos.

### Task

Representa trabalho tecnico, operacional, documental ou de governanca.

### Bug

Representa defeito, regressao, falha de integracao ou comportamento incorreto.

### Spike

Subtarefa customizada de pesquisa, discovery, benchmark, levantamento
documental e reducao de incerteza.

### Sub-task

Quebra execucao dentro de um item pai quando isso melhora fluxo, ownership ou
handoff.

## Politica de Spike

Decisao adotada:

- `Story`: `Spike` obrigatoria por padrao antes de sair de `Refinement`
- `Task`: `Spike` condicional
- excecoes precisam ser explicitas e justificadas

Toda `Spike` deve concentrar:

- links oficiais pesquisados
- APIs, docs, RFCs ou guias consultados
- prints, evidencias e exemplos
- resumo do que foi encontrado
- viabilidade
- riscos e desafios
- complexidade
- custo operacional
- comparacao de alternativas

Sem isso, o item pai nao deve sair de `Refinement`.

## Workflow alvo

### Statuses

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

### Semantica de cada status

- `Backlog`: demanda registrada, mas ainda nao refinada
- `Refinement`: demanda em clarificacao, discovery, decomposicao ou pesquisa
- `Ready`: demanda pronta para ser puxada
- `Doing`: execucao ativa neste momento
- `Paused`: trabalho explicitamente estacionado fora do fluxo normal
- `Testing`: validacao funcional, tecnica ou operacional em curso
- `Review`: revisao tecnica ou de conformidade
- `Changes Requested`: retrabalho obrigatorio apos validacao negativa
- `Done`: entrega concluida e aceita
- `Cancelled`: item encerrado sem implementacao

### Regras centrais de transicao

- apenas `Ready` pode ser puxado para `Doing`
- `Doing` deve ter no maximo um item ativo por agente de cada vez
- item parado sai de `Doing`
- espera intencional e longa vai para `Paused`
- espera natural da fase pode permanecer em `Testing` ou `Review`, mas com
  `Current Agent Role` vazio
- item com retrabalho volta por `Changes Requested`

## WIP e fila

### Regra perene

Cada agente deve ter apenas um item realmente ativo em `Doing`.

Isso nao impede que existam varios itens em `Testing`, `Review` ou `Paused`,
desde que o status represente a fase real e nao uma execucao inexistente.

### Consequencia pratica

- excesso de `Doing` indica mentira operacional ou gargalo
- fila longa em `Review` indica falta de capacidade de review
- fila longa em `Testing` indica gargalo de QA

## Definition of Ready

Um item so entra em `Ready` quando tiver:

- contexto suficiente
- objetivo claro
- criterios de aceite observaveis
- referencias e links relevantes
- `Spike` concluida quando ela for obrigatoria
- proximo papel executor claramente identificado

## Definition of Done

Um item so entra em `Done` quando tiver:

- implementacao concluida
- evidencias minimas registradas
- validacao de QA ou n/a explicito
- review tecnico ou n/a explicito
- documentacao linkada ou n/a explicito
- comentario final de handoff/encerramento

## Modelo de review

Para manter alta qualidade sem transformar o `Tech Lead` em gargalo, o modelo
adotado passa a ser:

- revisores especialistas por familia de arquivo fazem a revisao tecnica profunda
- `ai-reviewer` atua como gate transversal, consolidando pareceres quando houver
  multiplas linguagens, risco sistemico ou necessidade de aprovacao cruzada
- `ai-tech-lead` continua dono de coerencia tecnica, decomposicao e excecoes,
  mas nao funciona como reviewer universal de toda mudanca

Especializacoes minimas:

- `ai-reviewer-python`
- `ai-reviewer-powershell`
- `ai-reviewer-automation`
- `ai-reviewer-config-policy`

## Padrao de escrita das issues

### Titulo

- curto
- humano
- sem prefixo com `ID` local
- focado no resultado, nao no historico

### Corpo

Escrever em linguagem natural, como time humano real, com Markdown legivel.

Secoes base:

- `Contexto`
- `Resultado esperado`
- `Criterios de aceite`
- `Referencias`

Secoes por tipo:

- `Story`: adicionar `Historia`
- `Task`: adicionar `Escopo tecnico`
- `Bug`: adicionar `Problema observado`, `Impacto` e `Evidencias`
- `Spike`: adicionar `Perguntas de pesquisa`, `Achados`, `Riscos`,
  `Alternativas` e `Recomendacao`

## Comentarios e evidencias

Cada agente que tocar a issue deve comentar:

- quando inicia
- em marcos relevantes
- antes de pausar
- antes de handoff
- antes de encerrar

Comentario sem evidencia nao conta como trabalho concluido.

Evidencias aceitas:

- link de commit
- link de PR
- log de teste
- screenshot
- link de pipeline
- link de pagina do Confluence
- attachment do Jira

## Cerimonias e checkpoints recomendados

Mesmo em fluxo continuo, vale institucionalizar:

- refinement recorrente
- checkpoint de WIP e bloqueios
- review do incremento entregue
- retro de fluxo e gargalos

O board nao substitui essas conversas; ele da visibilidade para que elas sejam
objetivas.

## Metricas recomendadas

- WIP por coluna
- aging em `Doing`, `Testing` e `Review`
- cycle time
- throughput
- retrabalho por `Changes Requested`
- bloqueios por causa

## Como isso se traduz no Jira deste projeto

- `Epic` passa a ser o agrupador principal por contexto
- `Story` e `Task` viram o eixo do fluxo
- `Spike` vira subtarefa oficial de refinamento
- `Current Agent Role` fica visivel no card
- `Next Required Role` orienta o handoff
- o board mostra a fase real, nao apenas o desejo do momento

## Ordem recomendada de implementacao

1. consolidar o manual e o inventario pesquisado
2. refletir isso no `Confluence`
3. ajustar o schema oficial do `Jira`
4. aplicar workflow, screens e layout do board
5. sanear itens hoje em `Doing` que nao estao em execucao real
6. endurecer automacoes e validacoes para impedir regressao

## Resultado esperado

Quando esse manual estiver aplicado, o projeto deve operar como um time agil
real:

- backlog claro
- WIP confiavel
- ownership visivel
- handoff explicito
- refinamento rastreavel
- documentacao e execucao em paridade
- menos drift entre comentario, status e realidade
