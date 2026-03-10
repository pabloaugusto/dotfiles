# Spike: operacao agil e workflow do DOT

- Status: `em_andamento`
- Data-base: `2026-03-08`
- Epic Jira: [`DOT-91`](https://pabloaugusto.atlassian.net/browse/DOT-91)
- Task pai: [`DOT-92`](https://pabloaugusto.atlassian.net/browse/DOT-92)
- Spike Jira: [`DOT-93`](https://pabloaugusto.atlassian.net/browse/DOT-93)
- Follow-up de implementacao: [`DOT-94`](https://pabloaugusto.atlassian.net/browse/DOT-94)

## Objetivo

Consolidar, com base em fontes oficiais, um modelo de operacao agil robusto
para o projeto `DOT`, cobrindo:

- metodologia e principios base
- workflow e politicas de WIP
- hierarquia de itens no `Jira`
- escrita de epics, stories, tasks, spikes e subtasks
- regra de ownership ativo em tempo real
- criterios para mover um item de `Refinement` para `Ready`

## Fontes oficiais pesquisadas

### Fundacao agil

- [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- [The Scrum Guide 2020](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf)
- [The Kanban Guide](https://kanbanguides.org/english/)

### Atlassian: fluxo, WIP e visualizacao

- [Atlassian Agile](https://www.atlassian.com/agile)
- [Kanban | Atlassian](https://www.atlassian.com/agile/kanban/)
- [Kanban cards | Atlassian](https://www.atlassian.com/agile/kanban/cards)
- [Scrumban | Atlassian](https://www.atlassian.com/agile/project-management/scrumban)
- [Kanban vs Scrum | Atlassian](https://www.atlassian.com/agile/teams/scrum-kanban-agile)
- [Jira Kanban board template](https://www.atlassian.com/software/jira/templates/kanban)
- [Cumulative flow diagram | Atlassian Support](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-team-managed-cumulative-flow-diagram/)

### Atlassian: refinamento, escrita e criterios

- [Definition of Ready | Atlassian](https://www.atlassian.com/agile/project-management/definition-of-ready)
- [Definition of Done | Atlassian](https://www.atlassian.com/agile/project-management/definition-of-done)
- [User stories with examples and a template | Atlassian](https://www.atlassian.com/agile/project-management/user-stories)
- [Acceptance criteria explained | Atlassian](https://www.atlassian.com/work-management/project-management/acceptance-criteria)
- [Epics, stories, themes, and initiatives | Atlassian](https://www.atlassian.com/agile/project-management/epics-stories-themes)
- [What are issue types? | Atlassian Support](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/)

### Crawl oficial ampliado do hub Atlassian Agile

- [`2026-03-08-atlassian-agile-hub-inventory.md`](2026-03-08-atlassian-agile-hub-inventory.md)
  registra a leitura ampla do diretorio
  [`https://www.atlassian.com/br/agile`](https://www.atlassian.com/br/agile)
  com `217` paginas validas encontradas no crawl recursivo do hub oficial.
- a partir desse inventario, o modelo operacional consolidado foi promovido
  para [`2026-03-08-manual-agilidade-control-plane.md`](2026-03-08-manual-agilidade-control-plane.md),
  que passa a ser o guia pragmatico desta frente.

## Achados principais

### 1. O fluxo-base do projeto deve ser puxado e visual

As fontes oficiais convergem em tres ideias:

- visualizar o trabalho de ponta a ponta
- limitar trabalho em progresso
- explicitar as politicas do fluxo

Isso reforca que o `DOT` deve operar com board `Kanban` puxado, sem usar
`Doing` como deposito de tudo que esta apenas "aberto".

### 2. O projeto combina melhor com Kanban do que com Scrum puro

O repo trabalha com:

- fluxo continuo
- backlog vivo
- muita governanca tecnica e operacional
- trabalho de infraestrutura, documentacao, integracao e automacao

Por isso, o modelo mais coerente e:

- `Kanban` como engine de fluxo
- praticas de `Scrum` usadas como cadencias de alinhamento
  - refinement
  - planejamento
  - review
  - retrospectiva

Em outras palavras, a operacao recomendada aqui e mais `Scrumban` do que
`Scrum` puro.

### 3. Status deve representar fase; ownership ativo deve representar execucao real

Um dos problemas observados no tenant foi usar `Doing` para qualquer item
aberto, mesmo sem atuacao real naquele momento.

Pela pratica de Kanban e pela necessidade de rastreabilidade deste projeto:

- `status` deve mostrar a fase do fluxo
- `Current Agent Role` deve mostrar quem esta atuando agora
- quando ninguem estiver atuando ativamente, `Current Agent Role` deve ficar vazio

Isso permite distinguir:

- item em `Testing`, mas sem QA atuando naquele minuto
- item em `Review`, aguardando disponibilidade do reviewer
- item em `Doing`, com developer realmente executando

### 4. `Paused` e util, mas nao deve substituir toda espera do sistema

`Paused` continua valido para trabalho intencionalmente estacionado fora do
fluxo normal. Mas ele nao deve virar um curinga para qualquer espera.

Decisao:

- `Paused` = trabalho explicitamente estacionado
- `blocked` = impedimento sinalizado por label/flag
- `Testing` e `Review` podem continuar refletindo a fase mesmo quando o agente
  ativo sair temporariamente, desde que `Current Agent Role` seja limpo

### 5. Falta um encerramento terminal para trabalho abandonado

Sem um status terminal de cancelamento, o sistema fica forçado a:

- manter item em backlog indefinidamente
- usar `Done` para algo que nao foi entregue
- ou esconder a decisao em comentario

Decisao:

- adicionar `Cancelled` como status terminal na categoria `Done`
- mapear `Cancelled` junto da coluna final do board

### 6. Historias precisam nascer mais refinadas e mais humanas

As referencias da Atlassian reforcam:

- historias legiveis por pessoas
- criterios de aceite observaveis
- `DoR` claro antes de puxar execucao
- `DoD` compartilhado pelo time

Isso confirma a necessidade de:

- titulos curtos
- descricoes em seções
- criterios de aceite claros
- referencias e contexto no proprio item

### 7. Spike faz sentido, mas nao deve ser obrigatoria para tudo

O uso de `Spike` como pesquisa timeboxed faz sentido para este piloto, mas
transformar toda demanda em `Spike` obrigatoria geraria desperdicio.

Decisao adotada:

- `Story`: `Spike` obrigatoria por padrao antes de sair de `Refinement`
- `Task`: `Spike` condicional
- excecao: pode haver dispensa explicita quando a investigacao for
  desnecessaria, mas isso deve ficar registrado

### 8. A leitura ampliada da Atlassian reforca que board e so uma parte do sistema

Ao consolidar o hub `/br/agile`, a Atlassian reforca repetidamente que
operacao agil robusta depende de um conjunto integrado de elementos:

- backlog refinement recorrente
- workflow explicito
- ownership claro
- criterios de aceite
- visibilidade de bloqueios e dependencias
- loops de melhoria continua

Isso valida a necessidade de tratar `Jira`, `Confluence`, comentarios
estruturados, `Current Agent Role`, `Next Required Role`, `Spike`, `DoR` e
`DoD` como partes do mesmo sistema operacional, e nao como detalhes isolados.

## Decisoes arquiteturais para o DOT

### Modelo de operacao

- `Kanban` puxado como fluxo oficial
- `Scrumban` como referencia metodologica
- `Refinement` e `Ready` como gates explicitos
- `Current Agent Role` como ownership ativo em tempo real
- `Next Required Role` como handoff esperado

### Status alvo

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

### Politica de WIP

- cada agente deve ter no maximo um item realmente ativo por fase executora
- `Doing` nao pode acumular demandas sem atuacao real
- itens parados devem:
  - limpar `Current Agent Role`
  - ficar no status que represente a fase real
  - ou ir para `Paused` quando forem explicitamente estacionados

### Politica de hierarquia

- `Epic`: contexto pequeno ou medio, com progresso observavel
- `Story`: regra de negocio, comportamento esperado, definicao global ou fluxo
  com valor legivel
- `Task`: trabalho tecnico, operacional, documental ou de governanca
- `Bug`: defeito, regressao ou incidente
- `Spike`: subtarefa customizada para pesquisa, discovery, benchmarking e
  definicao de refinamento
- `Sub-task`: decomposicao de execucao sem carater investigativo

### Politica de spikes

- toda `Story` deve sair de `Refinement` com `Spike` concluida por padrao
- `Task` ganha `Spike` quando houver incerteza tecnica, operacional, documental
  ou de integracao
- a `Spike` precisa concentrar:
  - links e referencias
  - apis consultadas
  - prints e evidencias
  - resumo do que foi encontrado
  - viabilidade
  - desafios e riscos
  - complexidade estimada
  - custo operacional
  - benchmark e alternativas
- sem isso, a task pai nao sai de `Refinement`

## Implementacao recomendada

### Fase 1

- formalizar `Spike` no schema do `Jira`
- endurecer contratos de `DoR`, `DoD` e WIP
- expor `Current Agent Role` no card do board
- revisar os `Doing` ativos e limpar o drift atual

### Fase 2

- ajustar screens para permitir `Current Agent Role` e `Next Required Role`
- automatizar validacoes minimas de transicao
- melhorar dashboards de fluxo e gargalo

### Fase 3

- medir `cycle time`, aging e acumulacao por coluna
- usar `spikes` e subtasks como base objetiva de refinamento e previsibilidade

## Riscos e ressalvas

- a API do board do `Jira Software` continua com gap administrativo no tenant,
  entao parte do ajuste visual ainda depende de UI autenticada
- os campos `Current Agent Role` e `Next Required Role` existem, mas ainda
  precisam entrar corretamente nas screens e no card layout para cumprir o
  papel esperado
- adicionar `Spike` como subtarefa melhora o refinamento, mas nao substitui
  escrita humana boa nem criterios de aceite verificaveis

## Proxima decisao desta frente

Transformar estas conclusoes em:

- contrato versionado
- schema oficial do `Jira`
- layout do board
- saneamento do WIP atual no tenant
