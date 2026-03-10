# Agent Operations

- Status: `artifact-first`
- Data-base: `2026-03-07`
- Fonte canonica:
  [`../../../config/ai/agent-operations.yaml`](../../../config/ai/agent-operations.yaml)
- Sincronizacao alvo:
  - pagina operacional dedicada no `Confluence`
  - issue de governanca e comentarios tecnicos no `Jira`

## Regra central

Cada agente deve registrar sua atuacao de forma estruturada no `Jira` e, quando
houver documentacao correspondente, refletir isso tambem no `Confluence`.

Toda acao em demanda rastreada no `Jira` exige log do agente na propria issue,
inclusive atuacoes consultivas como `pascoalete`.

Esse log nao deve acontecer so no fim. A regra perene passa a ser:

- comentar ao iniciar a atuacao na issue
- comentar em cada marco relevante, descoberta, decisao ou mudanca de estado
  durante a execucao
- comentar antes de handoff, pausa, aprovacao, reprovacao ou encerramento da
  participacao do agente
- manter o status da issue em tempo real, sempre coerente com o comentario mais
  recente do agente e com o estado real da execucao

Comentario solto sem prova nao conta como trabalho concluido.

Quando um comentario, descricao ou evidencia citar artefato versionado deste
repo, a referencia precisa apontar para a URL oficial do arquivo no `GitHub`.
Esse contrato tambem vale para correcao retroativa do que ja foi semeado.

Toda issue ativa tambem deve manter descricao legivel, curta e humana, com
`Contexto`, `Resultado esperado`, `Criterios de aceite` e `Referencias`.

## Regra adicional de visibilidade no chat

Além de `Jira` e `Confluence`, cada marco relevante da atuacao dos agentes deve
ser espelhado no chat com uma mensagem curta, natural e humana.

Essa visibilidade em chat:

- nao substitui o log oficial em `Jira` e `Confluence`
- deve resumir marcos relevantes, nao microacoes ruidosas
- deve manter a pessoa usuaria ciente do estado real sem parecer template
  robotizado

## Campos obrigatorios em comentarios de atividade

- `Agent`
- `Interaction Type`
- `Status`
- `Contexto`
- `Evidencias`
- `Proximo passo`

## Evidencias aceitas

- attachment no `Jira`
- link para comentario anterior no `Jira`
- link de commit ou pull request
- link de pipeline ou job
- log de teste
- screenshot
- link da pagina do `Confluence`
- attachment do migration bundle

## Regras globais do Jira

- nenhuma transicao vale sem comentario estruturado
- todo agente que tocar uma issue rastreada deve registrar comentario no `Jira`
- todo papel atuante deve comentar no inicio da propria execucao na issue
- todo papel atuante deve comentar progresso relevante enquanto trabalha na issue
- todo papel atuante deve comentar antes de handoff, pausa ou saida do fluxo
- o status no `Jira` deve refletir o estado real da demanda no momento, sem
  atualizacao tardia ou em lote
- comentario e status precisam permanecer em paridade temporal e semantica
- todo papel que atuar deve atualizar `Current Agent Role` e `Next Required Role`
- todo papel que atuar deve anexar evidencia ou registrar `n/a` explicito
- `Doing` vale apenas para trabalho em execucao ativa
- item interrompido deve sair de `Doing` para `Paused` com motivo e criterio de retomada
- bloqueio que nenhum agente consiga destravar deve ser escalado ao usuario
- a escalacao de bloqueio deve usar todos os canais disponiveis no sistema
- cada tentativa de notificacao precisa ficar registrada no `Jira` e, quando
  houver pagina oficial, tambem no `Confluence`
- mudanca documental relevante deve aparecer tambem na issue correspondente
- review consultivo tambem precisa aparecer na issue quando o escopo estiver rastreado

## Regras globais do Confluence

- toda pagina gerada por trabalho deve linkar a issue correspondente no `Jira`
- atualizacao documental relevante deve ser mencionada na issue correspondente
- o `AI Documentation Agent` governa a arvore de paginas, backlinks e espelhos

## Semantica operacional de `Paused`

- `Paused` representa trabalho interrompido, aguardando dependencia, decisao,
  janela operacional ou retomada explicita
- `Doing` representa apenas trabalho sendo executado agora
- transicoes `Doing -> Paused` e `Paused -> Doing` exigem comentario estruturado
  com motivo, evidencia e criterio de retomada
- `Paused` nao substitui `Changes Requested`
  - `Paused`: espera operacional
  - `Changes Requested`: retrabalho exigido por validacao

## Passo a passo por papel

### `ai-product-owner`

- maximiza valor e mantem a voz unica de decisao sobre backlog e prioridade
- cria e prioriza issues principais no `Jira`
- registra objetivo, escopo, prioridade, criterio de aceite e evidencia de intake
- garante link para pagina relevante no `Confluence` ou `n/a`
- move `Backlog -> Refinement -> Ready`
- nao executa implementacao tecnica nem substitui `Scrum Master`, `Arquiteto` ou `Tech Lead`

### `ai-scrum-master`

- fiscaliza **board**, **WIP**, ownership, handoffs e comentarios no `Jira`
- garante aderencia ao processo agil, aos contratos e as **cerimonias**
- registra cada inconformidade relevante e cada **cerimonia** executada no
  [`docs/AI-SCRUM-MASTER-LEDGER.md`](../../AI-SCRUM-MASTER-LEDGER.md)
- abre ou exige bug de governanca quando a anomalia persistir
- registra evidencia objetiva e o papel responsavel por cada desvio

### `ai-engineering-architect`

- registra decisao arquitetural e riscos no `Jira`
- cria ou atualiza `ADR` no `Confluence` quando a decisao for perene
- linka issue e pagina nos dois sentidos
- pode reprovar em `Review -> Changes Requested`

### `ai-engineering-manager`

- registra bloqueios, riscos, capacidade e replanejamento no `Jira`
- coordena com o `ai-scrum-master` a saude do fluxo e das escalacoes
- atualiza runbooks/processo no `Confluence` quando a regra mudar
- move `Doing -> Paused` ou `Paused -> Doing` quando houver espera operacional real
- quando nenhum agente conseguir destravar a demanda, escala o bloqueio ao
  usuario por todos os canais disponiveis e registra a trilha completa

### `ai-tech-lead`

- decompõe trabalho em subtasks
- registra plano tecnico, handoff e dependencias no `Jira`
- referencia playbooks e runbooks no `Confluence`
- governa `Ready -> Doing` e retornos `Changes Requested -> Doing`
- governa tambem `Doing -> Paused` e `Paused -> Doing`
- revisa todo PR ou origem equivalente antes da aprovacao final
- aprova ou reprova em `Review` com base nos criterios de qualidade do repo e
  nos pareceres especializados

### `ai-developer-python`

- implementa codigo Python
- registra progresso, decisoes e achados no `Jira`
- anexa commit, diff, log ou teste como evidencia
- pede apoio documental quando a mudanca exigir pagina ou ADR

### `ai-developer-powershell`

- implementa codigo PowerShell
- registra progresso, compatibilidade e achados no `Jira`
- anexa dry-run, log ou saida de `Pester`
- referencia runbook operacional quando necessario

### `ai-developer-automation`

- implementa tasks, workflows e automacoes
- registra risco operacional, rollback e progresso no `Jira`
- anexa logs de CI, validacoes e diffs declarativos
- atualiza runbooks do `Confluence` quando o fluxo mudar

### `ai-developer-config-policy`

- ajusta schemas, contratos e politicas de configuracao
- registra impacto de schema e governanca no `Jira`
- anexa validacao YAML ou artefato declarativo
- atualiza a pagina de schema correspondente no `Confluence`

### `ai-qa`

- executa testes e validacoes
- registra cenarios cobertos, falhas ou sucesso no `Jira`
- anexa logs, screenshots, pipeline ou checklist
- move `Testing -> Review` ou `Testing -> Changes Requested`

### `ai-reviewer`

- consolida pareceres especializados e revisa risco transversal
- registra feedback ou aprovacao com evidencia no `Jira`
- exige links para `ADR` ou pagina relevante quando aplicavel
- move `Review -> Done` ou `Review -> Changes Requested`

### `ai-reviewer-python`

- revisa Python, tipagem, testes, manutencao e performance
- registra feedback ou aprovacao com evidencia objetiva no `Jira`
- aponta risco tecnico especifico da stack Python
- usa como base normativa o catalogo em [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- decide com base no modelo formal em [`reviewer-decision-model.md`](reviewer-decision-model.md)
- diferencia no comentario o que e quebra de especificacao, convencao ou tooling

### `ai-reviewer-powershell`

- revisa PowerShell, idempotencia, seguranca e compatibilidade do host
- registra feedback ou aprovacao com evidencia objetiva no `Jira`
- aponta risco tecnico especifico da stack PowerShell
- usa como base normativa o catalogo em [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- decide com base no modelo formal em [`reviewer-decision-model.md`](reviewer-decision-model.md)
- diferencia no comentario regra de linguagem, host e analyzer

### `ai-reviewer-automation`

- revisa shell, workflows, Taskfile, CI e automacao
- registra feedback ou aprovacao com evidencia objetiva no `Jira`
- aponta risco tecnico especifico de automacao e entrega
- usa como base normativa o catalogo em [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- decide com base no modelo formal em [`reviewer-decision-model.md`](reviewer-decision-model.md)
- explicita no comentario impacto em determinismo, rollback e seguranca operacional

### `ai-reviewer-config-policy`

- revisa YAML, JSON, TOML, schemas, contratos e politicas declarativas
- registra feedback ou aprovacao com evidencia objetiva no `Jira`
- aponta risco tecnico especifico da camada declarativa
- usa como base normativa o catalogo em [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- decide com base no modelo formal em [`reviewer-decision-model.md`](reviewer-decision-model.md)
- diferencia erro sintatico, quebra de schema e problema contratual

### `ai-devops`

- opera pipelines, infra e automacoes de entrega
- registra risco de ambiente, rollback e progresso no `Jira`
- anexa links de pipeline, ambiente ou runbook
- atualiza paginas operacionais do `Confluence` quando necessario

### `ai-documentation-agent`

- cria e atualiza paginas oficiais no `Confluence`
- garante backlinks `Jira <-> Confluence`
- registra comentario `documentation-link` com prova no `Jira`
- so libera `Done` quando a rastreabilidade estiver completa

### `pascoalete`

- registra parecer consultivo de ortografia tecnica no `Jira` quando o escopo
  estiver rastreado
- referencia o ledger local e a pendencia aberta no backlog quando houver
  reprovacao nao corrigida na rodada
- nao bloqueia `Done` tecnico, mas precisa deixar a trilha audivel na issue

### `ai-browser-validator`

- ativa a capacidade por config somente apos estabilizacao da fase base
- prioriza validacao browser-level de `Jira` e `Confluence` quando a rodada
  exigir evidencia visual objetiva
- executa `Playwright` quando a capacidade estiver ativa
- registra resultado no `Jira`
- anexa screenshot, video, trace ou relatorio
- publica evidencia permanente no `Confluence` quando fizer sentido

### `ai-designer`

- registra handoff visual e necessidade de design no `Jira`
- anexa link de `Figma`, wireframe ou guideline
- reflete guideline visual no `Confluence` quando necessario

### `ai-ux-cro-analyst`

- registra impacto de UX/CRO e recomendacoes no `Jira`
- anexa hipoteses, benchmarks ou analise de usabilidade
- reflete recomendacoes permanentes no `Confluence`

### `ai-seo-specialist`

- valida SEO quando a capacidade estiver ativa
- registra auditoria e evidencias no `Jira`
- anexa relatorio tecnico, screenshot ou metrica relevante
- atualiza guideline SEO no `Confluence` quando a regra mudar
