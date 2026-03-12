# Parecer Arquitetural e Plano Inicial

- Status: `gerado-pela-ia`
- Data-base da analise: `2026-03-07`
- Contexto local lido: [`.agents/`](../../.agents/), [`../`](../), [`../../scripts/`](../../scripts/),
  [`../../tests/`](../../tests/), [`../../Taskfile.yml`](../../Taskfile.yml),
  [`../../AGENTS.md`](../../AGENTS.md) e contratos vivos da camada de IA
- Relacionados:
  - [`README.md`](README.md)
  - [`2026-03-07-blueprint-ai-product-owner-system.md`](2026-03-07-blueprint-ai-product-owner-system.md)
  - [`2026-03-07-melhores-praticas-mercado.md`](2026-03-07-melhores-praticas-mercado.md)
  - [`2026-03-07-operacao-agentes-jira-confluence.md`](2026-03-07-operacao-agentes-jira-confluence.md)

## Resumo executivo

A direcao de migrar a camada de IA para um modelo com `Jira` como fonte da
verdade de backlog e `Confluence` como fonte da verdade de documentacao e
viavel.

O ponto critico e a ordem da migracao:

- viavel como transicao faseada
- arriscado como `big bang`

Hoje, este repo possui uma camada operacional viva baseada em:

- [`.agents/`](../../.agents/)
- [`../AI-WIP-TRACKER.md`](../AI-WIP-TRACKER.md)
- [`../../ROADMAP.md`](../../ROADMAP.md)
- [`../ROADMAP-DECISIONS.md`](../ROADMAP-DECISIONS.md)
- [`../../LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md)
- [`../AI-REVIEW-LEDGER.md`](../AI-REVIEW-LEDGER.md)
- [`../AI-ORTHOGRAPHY-LEDGER.md`](../AI-ORTHOGRAPHY-LEDGER.md)

Esses artefatos nao sao apenas documentacao. Parte deles e backend de estado
operacional real, lido e escrito por:

- [`../../scripts/ai-worklog.py`](../../scripts/ai-worklog.py)
- [`../../scripts/ai-roadmap.py`](../../scripts/ai-roadmap.py)
- [`../../scripts/ai-lessons.py`](../../scripts/ai-lessons.py)
- [`../../scripts/ai-review.py`](../../scripts/ai-review.py)

Por isso, a primeira mudanca nao deve ser "criar mais agentes". A primeira
mudanca deve ser abstrair a persistencia e o backend de estado.

Atualizacao aprovada depois deste parecer:

- a fundacao dev-time da migracao deve nascer fora de [`../../df/`](../../app/df/)
  e desacoplada de [`../../bootstrap/`](../../app/bootstrap/)
- a control plane inicial passa a morar em [`../../config/ai/`](../../config/ai/)
- `Playwright` entra como capacidade opcional de evidencia, nao como
  dependencia do nucleo dos adapters
- a operacao Atlassian deve depender apenas de secrets e da control plane
  dev-time, nunca de runtime do bootstrap
- o plano desta trilha passa a ser documento vivo: toda definicao, regra,
  acordo ou expansao aprovada deve ser refletida aqui na mesma rodada
- `Atlassian Product Discovery` entra no roadmap como camada opcional de
  discovery e intake upstream do `Jira`, sem alterar a regra de que o backlog
  executavel continua canonico no `Jira`

Atualizacao tecnica validada durante a implementacao:

- tokens com escopo de `service account` exigem gateway
  `api.atlassian.com/ex/{product}/{cloud_id}` e nao o host
  `{site}.atlassian.net` para chamadas REST autenticadas
- `site_url` continua util para links navegaveis, URLs de UI e validacao por
  browser, mas o adapter REST principal deve priorizar o gateway oficial
- a regra canonica por produto fica:
  - `Jira` em `REST v3`
  - `Confluence` em `REST v2`
- o handshake real mostrou `Jira core` e `Confluence v2` operacionais; o unico
  gap residual confirmado neste momento e a API de board do `Jira Software`
  com `scope mismatch`
- a service account atual nao possui ainda `Jira Administrator`, entao
  `workflow`, `issue type scheme` e `custom fields` permanecem bloqueados ate a
  liberacao administrativa correta
- a linkagem bidirecional `Jira <-> Confluence` passa a ser contrato perene,
  governado pelo `AI Documentation Agent` e exigido no fechamento sempre que a
  demanda gerar trabalho nas duas plataformas
- referencias a documentos, arquivos e artefatos do repo publicadas em `Jira`
  ou `Confluence` devem usar URL oficial do `GitHub`; `path` local so pode
  aparecer como apoio textual quando o artefato nao for versionado
- o control plane deve promover para URL oficial apenas arquivos rastreados no
  `Git`, evitando gerar links falsos para caches, `storageState`, perfis de
  browser e outros artefatos efemeros
- para arquivos novos ou alterados nesta worktree, a validade externa do link
  depende de `commit checkpoint + push`; isso precisa ficar explicito nas
  evidencias ate a publicacao remota
- a operacao de cada papel em `Jira` e `Confluence` precisa nascer como
  contrato declarativo proprio, com passo a passo, transicoes, tipos de
  comentario e evidencia obrigatoria por atuacao
- schemas, endpoint maps, workflows, rotinas e payloads do control plane devem
  nascer primeiro como artefatos versionados no repo e so depois serem
  sincronizados para as tarefas do `Jira` e para as paginas do `Confluence`
- por ser um piloto da futura fabrica de software autonomo, a trilha de
  maturidade deve evoluir o nucleo para um `modular monolith` com pacotes
  importaveis por dominio, deixando microservicos como etapa posterior e
  seletiva
- a autenticacao visual via `Playwright` deve seguir bootstrap humano inicial
  com `storageState` local ignorado e reuso de sessao nas execucoes
  automatizadas, em vez de tentar automatizar `SSO` ou `MFA`

## O que manter do blueprint

- `Jira` como fonte oficial do backlog e do estado operacional.
- `Confluence` como fonte oficial da documentacao de processo e conhecimento.
- `Human in the loop` para decisoes estrategicas, aprovacoes e priorizacao.
- agentes especializados, mas coordenados por contratos declarativos.
- abstracao de plataforma para backlog e documentacao.
- registro de comentarios, evidencias e decisoes nas issues.
- comentarios soltos sem prova nao devem contar como entrega suficiente; a
  regra correta e comentario estruturado com evidencia ou `n/a` explicito.
- modelo puxado no Kanban, com cada agente puxando o item quando sua
  competencia for necessaria.
- separacao entre backlog bruto, refinamento e `Ready`, com `Definition of
  Ready` explicita antes de desenvolvimento.
- regra de que apenas o `AI Product Owner` cria e prioriza issues principais,
  enquanto outros agentes podem sugerir demanda e criar subtasks.

## O que eu mudaria no blueprint

### 1. Nao modelar o quadro por papel

As colunas nao devem representar agentes. Elas devem representar fases do
trabalho.

Sugestao mais robusta:

- `Backlog`
- `Refinement`
- `Ready`
- `In Progress`
- `Paused`
- `In Validation`
- `In Review`
- `Changes Requested`
- `Done`

`Blocked` deve ser flag, label ou campo, nao uma coluna primaria.

`Paused` deve existir como status proprio para separar trabalho interrompido de
trabalho ativamente em execucao.

### 2. Nao mover todo Markdown para Confluence

Ha dois tipos diferentes de Markdown no repo:

- docs acopladas ao codigo, bootstrap, testes e uso local
- docs de processo, conhecimento e governanca

Recomendacao:

- manter no repo o que e necessario para PR, CI, bootstrap e leitura tecnica local
- mover para Confluence apenas o que for conhecimento/processo/ADR/catalogo
- transformar artefatos vivos atuais em espelhos derivados ou camada de compatibilidade

### 3. Nao multiplicar papeis top-level sem especializacao real

`AI Developer` e `AI Reviewer` devem existir como guarda-chuva organizacional,
mas a execucao real precisa seguir familia de arquivo/capacidade.

Sugestao:

- governanca:
  - `AI Product Owner`
  - `AI Engineering Architect`
  - `AI Engineering Manager`
  - `AI Tech Lead`
  - `AI Documentation Agent`
- execucao:
  - `AI Developer Python`
  - `AI Developer PowerShell`
  - `AI Developer Automation`
  - `AI Developer Config Policy`
  - `AI QA`
  - `AI DevOps`
- revisao:
  - `AI Reviewer Python`
  - `AI Reviewer PowerShell`
  - `AI Reviewer Automation`
  - `AI Reviewer Docs Governance`

Para dominios de produto digital com frontend, design system ou aquisicao
organica, essa malha pode ganhar trilhas opcionais:

- `AI Designer`
- `AI UX / CRO Analyst`
- `AI SEO Specialist`

Esses papeis nao devem ser obrigatorios no fluxo-base do repo quando o dominio
nao pedir design, UX ou SEO. Eles entram por `capability flag`, `component`,
`label` ou tipo de issue.

### 4. Rovo MCP deve ser complementar

Como direcao tecnica atual, o backend principal deve usar as APIs oficiais de
`Jira` e `Confluence`.

`Rovo MCP` pode entrar como camada auxiliar de contexto, busca e assistencia,
mas nao como dependencia primaria da orquestracao neste primeiro corte.

### 5. O contrato principal precisa separar estado, conhecimento e codigo

Modelo alvo:

- Jira: execucao, backlog, comentarios, evidencias, bloqueios, transicoes
- Confluence: arquitetura, ADRs, RFCs, operating model, catalogos, runbooks
- repo: codigo, automacao, [`.agents/`](../../.agents/), testes e espelhos derivados

## Modelo sugerido de agentes

## Camada organizacional

- `AI Product Owner`: intake, escopo, priorizacao, criacao de issues, conexao
  com o stakeholder.
- `AI Engineering Architect`: arquitetura alvo, ADRs, fronteiras tecnicas,
  simplificacao estrutural.
- `AI Engineering Manager`: fluxo, capacidade, saude do sistema, riscos e
  bloqueios de delivery.
- `AI Tech Lead`: decomposicao tecnica e coordenacao do handoff entre
  implementacao, QA e review.
- `AI Documentation Agent`: manutencao do grafo Jira <-> Confluence e espelhos
  necessarios no repo.

Todos esses papeis devem operar por contrato nas ferramentas:

- o `Jira` recebe atividade estruturada, evidencias, handoffs e transicoes
- o `Confluence` recebe paginas oficiais, ADRs, runbooks e backlinks
- a fonte canonica do passo a passo por papel fica em
  [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)
  e no artefato
  [`artifacts/agent-operations.md`](artifacts/agent-operations.md)
- bloqueios que nenhum agente consiga destravar sozinho devem escalar o usuario
  por todos os canais disponiveis, com trilha obrigatoria em `Jira` e
  `Confluence`
- marcos relevantes da atuacao dos agentes tambem devem ser resumidos no chat
  em linguagem humana e curta, sem substituir a rastreabilidade oficial

## Camada especialista

- `AI Developer Python`
- `AI Developer PowerShell`
- `AI Developer Automation`
- `AI Developer Config Policy`
- `AI QA`
- `AI DevOps`

## Camada de aprovacao

- `AI Reviewer Python`
- `AI Reviewer PowerShell`
- `AI Reviewer Automation`
- `AI Reviewer Docs Governance`

Essa modelagem respeita o que o repo ja faz hoje com revisores por familia de
arquivo, em vez de introduzir um `reviewer` genericamente opaco.

## Estrutura sugerida para o Jira

## Tipos de issue

Sugestao inicial:

- `Epic`
- `Story`
- `Task`
- `Bug`
- `Sub-task`

Regra de uso recomendada:

- `Epic`
  - agrupar contexto pequeno ou medio, com progresso observavel e ownership claro
- `Story`
  - expressar regra de negocio, definicao global, fluxo funcional ou entrega com valor legivel
- `Task`
  - representar trabalho tecnico, operacional, documental ou de governanca
- `Bug`
  - registrar falha, regressao ou comportamento incorreto
- `Sub-task`
  - quebrar execucao dentro de um item pai quando isso melhorar fluxo ou handoff

Melhor pratica adotada:

- usar `Epic` e `Parent` como agrupamento principal
- evitar `Relates` em massa quando o objetivo for apenas agrupamento tematico
- reservar `issue links` para bloqueio, dependencia, duplicidade ou relacao tecnica real

Padrao de escrita adotado:

- titulos curtos, humanos e sem prefixo com `ID` local
- descricoes com `Contexto`, `Resultado esperado`, `Criterios de aceite` e `Referencias`
- `Story` preferindo `Card / Conversation / Confirmation`
- `Task` explicitando `Escopo tecnico` quando necessario
- `Bug` explicitando `Problema observado` e `Impacto`

Se houver fluxo de produto, design e aquisicao organica, pode valer adicionar:

- `Design`
- `UX Improvement`
- `SEO`

## Status e transicoes

Sugestao:

- `Backlog`
- `Refinement`
- `Ready`
- `Doing`
- `Paused`
- `Testing`
- `Review`
- `Changes Requested`
- `Done`

Transicoes principais:

```text
Backlog -> Refinement -> Ready -> Doing -> Testing -> Review -> Done
Doing -> Paused -> Doing
Testing -> Changes Requested -> Doing
Review -> Changes Requested -> Doing
```

Extensao opcional para escopos web e growth:

- `SEO Review` entre `In Review` e `Done`

Regra recomendada:

- usar `SEO Review` apenas quando a issue tocar pagina web, discoverability,
  metadados, performance de rendering, conteudo indexavel ou experimentos de CRO
- manter o fluxo-base sem essa coluna quando o dominio nao exigir SEO

## Campos recomendados

Preferir poucos campos customizados e muito uso de campos nativos. Campos
uteis:

- `Work Kind`
- `Workstream`
- `Affected Platforms`
- `Risk`
- `Confluence Source`
- `Evidence Links`
- `Branch / PR`
- `Current Agent Role`
- `Next Required Role`
- `Automation Mode`
- `Needs Design`
- `Needs UX Review`
- `Needs SEO Review`
- `Definition of Ready`
- `Subtask Creation Policy`

## Criterios de aceite

Todo item que possa entrar em `Refinement` ou `Ready` precisa ter criterios de
aceite iniciais.

Esses criterios devem ser:

- verificaveis
- observaveis
- ligados ao resultado esperado
- suficientes para `QA` e `Reviewer`

Evitar:

- `funcionar corretamente`
- repetir o titulo como criterio
- omitir forma de validacao

## Labels iniciais sugeridas

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

## Convencoes operacionais para comments

Cada comentario de agente deve ser estruturado e tipado. Campos minimos:

- `Agent`
- `Interaction Type`
- `Status`
- `Contexto`
- `Evidencias`
- `Proximo passo`

Cadencia minima obrigatoria:

- comentario ao iniciar a atuacao do papel na issue
- comentario em cada marco relevante, descoberta, decisao ou mudanca de estado
- comentario antes de handoff, pausa, aprovacao, reprovacao ou saida do fluxo
- atualizacao de status em tempo real, sempre coerente com o comentario mais
  recente e com o estado real da demanda

Tipos recomendados:

- `progress-update`
- `technical-decision`
- `unexpected-finding`
- `scope-change`
- `priority-change`
- `test-evidence`
- `test-failure`
- `test-success`
- `review-feedback`
- `approval`
- `blocker`

## Regras de backlog e subtasks

- apenas o `AI Product Owner` cria e prioriza issues principais do backlog
- qualquer agente pode criar subtasks dentro de uma issue existente
- sugestoes de novos trabalhos vindas de architect, QA, review, DevOps, UX,
  design ou SEO devem entrar como comentario estruturado ou subtask, e nao como
  issue principal criada fora do PO

## Camada opcional de Product Discovery

`Atlassian Product Discovery` pode entrar como sistema opcional de intake para:

- ideias novas do `AI Product Owner`
- oportunidades levantadas por outros agentes
- hipoteses ainda nao refinadas
- candidatos a roadmap que ainda nao sao issue executavel

Contrato recomendado:

- `Product Discovery` guarda discovery, oportunidade e hypothesis backlog
- `Jira` continua como backlog executavel oficial
- apenas o `AI Product Owner` promove uma ideia aprovada para issue principal
  em `Jira`
- a promocao deve preservar links cruzados entre a ideia de origem, a issue e,
  quando aplicavel, a documentacao em `Confluence`

## Capas opcionais de Figma, UX e SEO

Para produtos com interface e aquisicao organica, a trilha pode ser expandida:

- `Figma` como sistema de design, wireframes e prototipos
- `AI Designer` para artefatos visuais e handoff
- `AI UX / CRO Analyst` para usabilidade, experimentacao e conversao
- `AI SEO Specialist` para validacao final de discoverability e qualidade tecnica

No plano de implementacao, essas capacidades devem entrar como extensoes
opcionais por dominio, nao como dependencia obrigatoria do nucleo Jira +
Confluence + repo.

## Arquitetura alvo de integracao

Primeira camada a criar em [`Python`](https://www.python.org/):

```python
class DiscoveryPlatform:
    def create_idea(...)
    def update_idea(...)
    def add_comment(...)
    def search(...)
    def promote_to_issue(...)
    def link_delivery_issue(...)


class IssuePlatform:
    def create_issue(...)
    def update_issue(...)
    def transition_issue(...)
    def add_comment(...)
    def add_remote_link(...)
    def search(...)


class DocumentationPlatform:
    def create_page(...)
    def update_page(...)
    def search(...)
    def link_issue(...)
```

Implementacoes iniciais:

- `JiraAdapter`
- `ConfluenceAdapter`
- `MarkdownMirrorAdapter`

Expansao opcional planejada:

- `AtlassianProductDiscoveryAdapter`

Depois disso, os scripts atuais devem parar de falar diretamente com Markdown e
passar a usar adapters.

## Plano inicial de implementacao

### Fase 0. Modelo e contratos

- definir projeto Jira, space do Confluence, auth model e service accounts
- definir issue types, statuses, campos e convencoes
- classificar o que hoje permanece local e o que migrara para Confluence
- mapear artefato atual -> Jira, Confluence, repo ou espelho derivado
- decidir quais capacidades sao `core` e quais sao `opt-in` por dominio:
  design, UX/CRO, SEO e Figma
- definir se `Atlassian Product Discovery` entra neste tenant como fonte
  opcional de ideias e discovery, sem quebrar o contrato do `Jira`

### Fase 1. Abstracao de plataformas

- criar a control plane dev-time em [`../../config/ai/`](../../config/ai/) para
  plataformas, contratos e optionalidade dos agentes
- criar interfaces `IssuePlatform`, `DocumentationPlatform` e, quando ativado,
  `DiscoveryPlatform`
- implementar `JiraAdapter` e `ConfluenceAdapter`
- implementar `MarkdownMirrorAdapter` para transicao segura
- registrar e tratar diferencas reais de auth entre produtos Atlassian, sem
  assumir que `Jira` e `Confluence` respondem ao mesmo token/modo no tenant

### Fase 2. Compatibilidade e dual write

- refatorar [`../../scripts/ai-worklog.py`](../../scripts/ai-worklog.py)
- refatorar [`../../scripts/ai-roadmap.py`](../../scripts/ai-roadmap.py)
- refatorar [`../../scripts/ai-lessons.py`](../../scripts/ai-lessons.py)
- refatorar [`../../scripts/ai-review.py`](../../scripts/ai-review.py)
- manter espelho local temporario para nao quebrar a governanca existente

### Fase 3. Migracao da camada declarativa de IA

- expandir [`.agents/registry/`](../../.agents/registry/)
- expandir [`.agents/cards/`](../../.agents/cards/)
- ajustar [`.agents/orchestration/capability-matrix.yaml`](../../.agents/orchestration/capability-matrix.yaml)
- ajustar [`.agents/orchestration/routing-policy.yaml`](../../.agents/orchestration/routing-policy.yaml)
- introduzir contratos de handoff Jira/Confluence e politica de evidencias
- introduzir, quando aplicavel, papeis opcionais de `AI Designer`,
  `AI UX / CRO Analyst` e `AI SEO Specialist`
- modelar a regra de que apenas o `AI Product Owner` cria issues principais e
  que subtasks podem ser abertas por qualquer agente autorizado

### Fase 4. Governanca e testes

- atualizar [`../../Taskfile.yml`](../../Taskfile.yml)
- atualizar workflows em [`.github/workflows/`](../../.github/workflows/)
- trocar validacoes acopladas a Markdown por contratos de adapter
- adicionar testes de drift Jira <-> Confluence <-> repo
- adicionar validacoes de `Definition of Ready`, politica de subtasks e gates
  condicionais de design/SEO quando essas capacidades estiverem ativas
- apos estabilizacao da fase base, ativar `Playwright` como camada opcional de
  evidencia browser-level para `Jira` e `Confluence`, conforme
  [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66)

### Fase 5. Cutover controlado

- promover Jira e Confluence a fontes canonicas
- rebaixar ledgers Markdown vivos para mirrors derivados ou descontinuar
- realizar rollout por fases, evitando corte unico

### Fase 6. Discovery opcional com Atlassian Product Discovery

- introduzir `AtlassianProductDiscoveryAdapter` apenas depois do nucleo
  `Jira + Confluence` estar estabilizado
- permitir intake de ideias de agentes e do `AI Product Owner` em discovery
- implementar promocao controlada de ideia -> issue principal pelo
  `AI Product Owner`
- manter linkagem `Product Discovery <-> Jira <-> Confluence`

## Estado atual da implementacao

- [`../../config/ai/platforms.yaml`](../../config/ai/platforms.yaml) agora e
  contrato generico por ambiente
- o overlay local derivado de
  [`../../config/ai/platforms.local.yaml.tpl`](../../config/ai/platforms.local.yaml.tpl)
  concentra refs reais fora do Git
- o adapter REST ja suporta `service-account-api-token` no gateway oficial
- a resolucao de secrets do control plane ja opera com batch via `op run`,
  cache em memoria por processo e fallback por item, conforme
  [`2026-03-07-onepassword-batch-resolution.md`](2026-03-07-onepassword-batch-resolution.md)
- `Confluence` respondeu com sucesso no tenant atual e as paginas principais ja
  foram sincronizadas
- `Jira Platform` esta operacional no tenant atual para schema, issues,
  comentarios, transicoes, anexos e dashboards
- o schema alvo ja foi aplicado no projeto `DOT`
- a semeadura retroativa ja foi executada:
  - seed inicial com `64` issues reais confirmadas por API em `DOT`
  - total atual no tenant: `84` issues, agora com epicos tematicos, `DOT-75`
    para padronizacao do backlog, `DOT-76` para avaliar a fronteira `/app`,
    `DOT-77` para corrigir o falso negativo do browser validator e `DOT-78` /
    `DOT-79` para abrir a frente oficial de rastreabilidade `GitHub` + `Jira`
    + `Confluence`
  - o retroativo ja foi reescrito com titulos mais curtos e descricoes mais
    humanas
  - issue de migracao [`DOT-1`](https://pabloaugusto.atlassian.net/browse/DOT-1)
    com bundle auditavel anexado
- `29` paginas oficiais sincronizadas no `Confluence`, incluindo as paginas
  `DOT - Jira Writing Standards`, `DOT - GitHub Jira Confluence Traceability`
  e `DOT - GitHub Atlassian Runbook`
- o gap residual do board agora esta rastreado no backlog oficial em
  [`DOT-65`](https://pabloaugusto.atlassian.net/browse/DOT-65)
- a ativacao do browser validator via `Playwright` agora esta rastreada
  em [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66)
- o falso negativo de titulo generico no validator browser ja foi corrigido em
  [`DOT-77`](https://pabloaugusto.atlassian.net/browse/DOT-77)
- o bootstrap humano inicial do `Playwright` foi concluido com sucesso e a
  sessao autenticada agora e reutilizavel por `storageState`
- a primeira validacao browser positiva ja foi executada no board settings do
  `DOT`, com `PAUSED` visivel e sem warnings amarelos
- a heuristica do validator agora tambem aceita `title_match_mode =
  body-fallback` para paginas SPA do Atlassian cujo tab title seja generico
- [`DOT-76`](https://pabloaugusto.atlassian.net/browse/DOT-76) foi concluida em
  `Done`, com recomendacao final indicando que a fronteira `/app` faz sentido
  como direcao arquitetural, mas nao como migracao fisica imediata
- a frente de integracao `GitHub` + `Jira` + `Confluence` agora possui estudo
  oficial proprio em
  [`2026-03-08-github-jira-confluence-traceability.md`](2026-03-08-github-jira-confluence-traceability.md),
  e ja foi promovida para o backlog oficial em [`DOT-78`](https://pabloaugusto.atlassian.net/browse/DOT-78)
  e [`DOT-79`](https://pabloaugusto.atlassian.net/browse/DOT-79), com
  subtasks de execucao entre [`DOT-80`](https://pabloaugusto.atlassian.net/browse/DOT-80)
  e [`DOT-84`](https://pabloaugusto.atlassian.net/browse/DOT-84)
- o runbook operacional desta frente agora tambem existe como artefato
  versionado no repo em
  [`2026-03-08-github-for-atlassian-runbook.md`](2026-03-08-github-for-atlassian-runbook.md)
  e como pagina oficial no `Confluence`
- o repair retroativo agora tambem normaliza referencias a artefatos do repo em
  `Jira` e `Confluence` para links oficiais do `GitHub`
- o repair retroativo mais recente zerou residuos conhecidos de `paths` locais
  em descricoes e comentarios gerados pela automacao no `Jira`
- o linkificador central agora so promove para URL oficial arquivos rastreados
  no `Git`, deixando artefatos nao versionados apenas como contexto textual
- o unico gap residual confirmado nesta trilha continua sendo o board do
  `Jira Software`:
  - `GET /rest/agile/1.0/board` segue em `401 Unauthorized; scope does not match`
  - o layout visual do board ja foi alinhado por UI autenticada
- `project.target_board.layout_confirmed` agora pode permanecer `true` no
  modelo local, porque o bloqueio remanescente deixou de ser visual e passou a
  ser apenas de API

## Sequencia recomendada de branches

Se o trabalho for fatiado, a sequencia recomendada e:

- `feat/atlassian-platform-abstractions`
- `feat/jira-worklog-roadmap-adapter`
- `feat/confluence-doc-governance`
- `feat/ai-agent-registry-atlassian`

## Evolucao de maturidade aprovada para v2

- adicionar telemetria de esforco por agente e por etapa da demanda
- medir tempos de pesquisa, analise, arquitetura, desenvolvimento, revisao,
  testes e documentacao
- consolidar esses sinais no control plane, desacoplados de runtime de
  `dotfiles`
- refletir a telemetria em comentarios estruturados, artefatos de migracao e
  dashboards no `Jira` e no `Confluence`
- usar esses dados para eficiencia, throughput, gargalos, handoffs e custo
  operacional do time de IA

## Fontes oficiais validadas na analise

Validacao pontual conferida em 2026-03-07:

- [`Jira Cloud REST API - Issues`](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)
- [`Jira Cloud REST API - Issue comments`](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/)
- [`Confluence Cloud REST API v2 - Page`](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/)
- [`Jira Automation - Transition issue`](https://support.atlassian.com/cloud-automation/docs/jira-automation-actions/#Transition-issue)
- [`Jira Automation - Create Confluence page`](https://support.atlassian.com/cloud-automation/docs/use-confluence-with-jira-automation/)
- [`Atlassian - Set up Rovo MCP in IDEs and desktop clients`](https://support.atlassian.com/rovo/docs/set-up-rovo-mcp-in-ides-and-desktop-clients/)
- [`Atlassian - Atlassian Rovo MCP Server`](https://support.atlassian.com/rovo/docs/atlassian-rovo-mcp-server/)
- [`Atlassian Forge MCP Server`](https://developer.atlassian.com/platform/forge/mcp-server/)

## Conclusao

O blueprint e bom como direcao, mas precisa de um ajuste de ordem:

1. primeiro abstrair backend e persistencia
2. depois migrar worklog, roadmap, review e docs
3. so entao expandir o modelo multiagente em cima da nova plataforma

Sem isso, o risco e apenas trocar Markdown vivo por complexidade distribuida sem
fonte canonica realmente estavel.
