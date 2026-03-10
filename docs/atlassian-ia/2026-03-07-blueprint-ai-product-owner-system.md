# Blueprint AI Product Owner System

- Status: `input-do-usuario`
- Origem: blueprint inicial enviado em 2026-03-07
- Curadoria: texto consolidado em formato Markdown rastreavel
- Relacionados:
  - [`README.md`](README.md)
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)

## Objetivo do sistema

Definir uma arquitetura para um `AI Product Owner System` capaz de governar:

- backlog
- roadmap
- fluxo agil
- documentacao
- sincronizacao entre repositorio, backlog e conhecimento

O blueprint assume um arranjo de agentes de IA operando como um time real dentro
de um fluxo DevOps.

## Resultados esperados

- backlog governado por IA
- roadmap tecnico automatico
- criacao e atualizacao automatica de issues
- priorizacao baseada em criticidade e estrategia
- agentes operando o fluxo Kanban
- comentarios, evidencias e decisoes registrados nas issues
- sincronizacao entre repositorio, backlog e documentacao
- Jira como fonte da verdade do backlog
- Confluence como fonte da verdade da documentacao
- arquivos Markdown no repo como artefatos derivados sincronizados

## Principios arquiteturais

### Jira como fonte da verdade do backlog

O backlog oficial passa a existir em [`Jira`](https://www.atlassian.com/software/jira),
incluindo:

- criacao e consolidacao de issues
- estado oficial do trabalho
- fluxo Kanban
- priorizacao
- comentarios operacionais
- evidencias de testes, revisoes e decisoes

### Confluence como fonte da verdade da documentacao

A documentacao oficial passa a existir em
[`Confluence`](https://www.atlassian.com/software/confluence), cobrindo:

- arquitetura
- decisoes tecnicas
- RFCs
- documentacao operacional
- documentacao dos agentes
- automacoes
- roadmap narrativo
- processos

### Independencia de plataforma

O blueprint pede camadas de abstracao para permitir:

- migrar no futuro para GitHub Projects
- usar Jira e GitHub Projects em paralelo
- trocar ou complementar o Confluence por outra plataforma

### Incrementalidade

Mudancas devem preservar historico e sincronismo consistente, evitando recriar
estado a cada rodada.

## Visao de alto nivel

Arquitetura resumida:

1. repositorio
2. `Repository Intelligence Layer`
3. `AI Product Owner`
4. camada de abstracao de backlog
5. adapters de plataforma

Para documentacao:

1. `AI Documentation Agent`
2. camada de abstracao de documentacao
3. adapters como Confluence e espelhos locais

Para entrega:

1. agentes de entrega
2. workflow engine
3. issue platform via abstracao

## Repository Intelligence Layer

Itens a analisar continuamente:

- estrutura de diretorios
- scripts PowerShell
- scripts Bash
- automacoes
- pipelines CI/CD
- `TODO`, `FIXME` e `HACK`
- backlog legado em Markdown
- roadmap legado
- notas WIP
- documentacao existente
- inconsistencias arquiteturais

Resultados esperados da analise:

- funcionalidades existentes
- funcionalidades ausentes
- bugs potenciais
- divida tecnica
- refactors recomendados
- gaps de documentacao
- oportunidades de automacao
- iniciativas candidatas a epico

## Papeis propostos no blueprint

- `AI Product Owner`
- `AI Engineering Manager`
- `AI Tech Lead`
- `AI Developer`
- `AI QA`
- `AI Reviewer`
- `AI Architect`
- `AI DevOps`
- `AI Documentation Agent`

Todos devem atuar via Jira, movendo cards, comentando, registrando decisoes,
evidencias, resultados de testes, bloqueios e revisoes.

## Priorizacao inicial sugerida

Formula conceitual do blueprint:

```text
PriorityScore =
  Impact * 4
+ Risk * 3
+ TechDebt * 2
+ Effort * -1
```

O equilibrio deve considerar:

- interesse do repositorio
- diretrizes do stakeholder

## Workflow Kanban sugerido no blueprint

Colunas iniciais:

- `Backlog`
- `Ready`
- `Doing`
- `Testing`
- `Review`
- `Changes Requested`
- `Done`

Fluxo principal:

```text
Backlog -> Ready -> Doing -> Testing -> Review -> Done
```

Fluxo de falha:

```text
Testing -> Changes Requested -> Doing
Review -> Changes Requested -> Doing
```

## Modelo inicial de issues no Jira

Projeto inicial proposto: `DOT`

Tipos:

- `Epic`
- `Feature`
- `Task`
- `Bug`
- `Tech Debt`
- `Research`
- `Automation`

Labels iniciais:

- `bootstrap`
- `powershell`
- `bash`
- `windows`
- `linux`
- `wsl`
- `ci`
- `testing`
- `security`
- `refactor`
- `automation`

Componentes iniciais:

- `bootstrap`
- `environment`
- `secrets`
- `ci`
- `developer-experience`
- `cross-platform`

## Camadas de abstracao previstas

### Backlog platform

Interface conceitual:

```python
class IssuePlatform:
    def create_issue()
    def update_issue()
    def move_issue()
    def comment()
    def search()
    def link_issue()
```

Implementacoes previstas:

- `JiraAdapter`
- `GitHubProjectsAdapter`

### Documentation platform

Interface conceitual:

```python
class DocumentationPlatform:
    def create_page()
    def update_page()
    def search()
    def link_issue()
```

Implementacoes previstas:

- `ConfluenceAdapter`
- `RepoDocsAdapter`

## Sincronizacao prevista

Fontes oficiais desenhadas pelo blueprint:

- Jira para backlog
- Confluence para documentacao
- repositorio para codigo

Sincronismos propostos:

- repo -> Jira para detectar backlog tecnico e funcional
- Jira -> repo para gerar espelhos locais de backlog e roadmap

## Frequencia operacional sugerida

- repo scan: a cada `push`
- backlog grooming: diariamente
- roadmap update: semanalmente

## Ciclo de vida de issue proposto

1. `Repository Intelligence` detecta problema.
2. `AI Product Owner` cria a issue.
3. item entra em `Backlog`.
4. item vai para `Ready`.
5. `AI Developer` move para `Doing`.
6. `AI QA` move para `Testing`.
7. `AI Reviewer` move para `Review`.
8. se falhar, volta para `Changes Requested`.
9. retorna para `Doing`.
10. apos aprovacao, vai para `Done`.

## Tecnologia base sugerida

O blueprint recomenda [`Python`](https://www.python.org/) para:

- integracao com APIs
- orquestracao de agentes
- automacao
- ecossistema LLM

## Proxima evolucao natural proposta

- arquitetura interna do sistema
- modelo de dados
- estrutura detalhada dos agentes
- eventos de sincronizacao
- estrutura dos arquivos Markdown
- design de adapters
- desenho operacional dos servicos
