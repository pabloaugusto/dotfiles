# Prompt Para Codex - Unificar E Centralizar A Governanca Normativa Por Tema

## Missao

Implementar de ponta a ponta no repo
[`dotfiles`](../../../../README.md) a unificacao e centralizacao da governanca
normativa por tema em [`.agents/rules/`](../../../rules/), transformando essa
pasta na fonte canonica humana das regras por dominio, sem criar nova
duplicacao, sem quebrar startup, sem competir com hooks, tasks, scripts e
testes e sem perder aderencia aos contratos vivos do repo.

## Regra zero de intake e backlog

Antes de criar qualquer demanda nova:

1. verificar no `Jira` se ja existe **issue aberta** cobrindo total ou
   parcialmente esse escopo
2. verificar se ja existe **Epic aberto** aderente ao macro tema
3. reutilizar a issue existente quando o escopo ja estiver coberto
4. reutilizar o `Epic` aberto correto quando o tema ja existir
5. nao criar novo `Epic`
6. se o `Epic` aberto de governanca de IA ainda for
   [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71) e continuar
   aderente, usar `DOT-71`
7. so criar nova `Task` ou `Sub-task` se o preflight provar que ainda nao
   existe work item suficiente

Toda criacao, reuse ou bypass precisa ficar rastreada no `Jira` com comentario
estruturado.

## Preflight obrigatorio antes de qualquer edicao

Antes de editar:

1. reler a governanca obrigatoria do repo
2. rodar [`task ai:worklog:check`](../../../../docs/TASKS.md#aiworklogcheck)
   com `PENDING_ACTION=concluir_primeiro`
3. usar o startup oficial se houver qualquer risco de retomada sem continuidade
   confiavel
4. ler e respeitar:
   - [`AGENTS.md`](../../../../AGENTS.md)
   - [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md)
   - [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
   - [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
   - [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
   - [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
   - [`docs/git-conventions.md`](../../../../docs/git-conventions.md)
   - [`Taskfile.yml`](../../../../Taskfile.yml)
   - [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
   - [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
   - [`config/ai/jira-model.yaml`](../../../../config/ai/jira-model.yaml)

## Skills obrigatorias desta frente

Usar e seguir pelo menos estas skills locais:

- [`$dotfiles-repo-governance`](../../../skills/dotfiles-repo-governance/SKILL.md)
- [`$task-routing-and-decomposition`](../../../skills/task-routing-and-decomposition/SKILL.md)
- [`$dotfiles-architecture-modernization`](../../../skills/dotfiles-architecture-modernization/SKILL.md)

E acionar as skills e revisores obrigatorios por familia de arquivo alterada:

- Python ->
  [`$dotfiles-python-review`](../../../skills/dotfiles-python-review/SKILL.md)
- PowerShell ->
  [`$dotfiles-powershell-review`](../../../skills/dotfiles-powershell-review/SKILL.md)
- automacao, Taskfile, workflow ou shell ->
  [`$dotfiles-automation-review`](../../../skills/dotfiles-automation-review/SKILL.md)
- texto, doc ou config textual -> `pascoalete` com
  [`$dotfiles-orthography-review`](../../../skills/dotfiles-orthography-review/SKILL.md)

## Objetivo arquitetural

Implementar esta decisao arquitetural no repo:

- [`.agents/rules/`](../../../rules/) passa a ser a fonte canonica **normativa
  por tema**
- [`AGENTS.md`](../../../../AGENTS.md) continua como contrato global curto, com
  precedencia, leitura obrigatoria, guardrails transversais e ponte para os
  temas
- [`Taskfile.yml`](../../../../Taskfile.yml), [`.githooks/`](../../../../.githooks/),
  scripts e testes continuam como **enforcement executavel**
- [`docs/`](../../../../docs/) passa a conter guias, explicacoes, runbooks e
  material derivado, nao a fonte primaria das regras
- `fallback` nao deve nascer como arquivo tematico principal no primeiro corte;
  ele deve virar secao obrigatoria dentro de cada tema relevante

## Resultado alvo da pasta [`.agents/rules/`](../../../rules/)

Criar, ajustar ou consolidar a arvore abaixo:

- arquivo inicial da pasta de rules
- `CATALOG.md`
- `core-rules.md`
- `chat-and-identity-rules.md`
- `startup-and-resume-rules.md`
- `git-rules.md`
- `intake-and-backlog-rules.md`
- `jira-execution-rules.md`
- `documentation-and-confluence-rules.md`
- `delegation-rules.md`
- `review-and-quality-rules.md`
- `worklog-and-lessons-rules.md`
- `scrum-and-ceremonies-rules.md`
- `prompt-pack-rules.md`
- `auth-secrets-and-critical-integrations-rules.md`
- `sync-foundation-rules.md`
- `source-audit-and-cross-repo-rules.md`

Manter no primeiro corte os arquivos existentes:

- [`default.rules`](../../../rules/default.rules)
- [`ci.rules`](../../../rules/ci.rules)
- [`security.rules`](../../../rules/security.rules)

Esses arquivos atuais podem continuar temporariamente como camada declarativa
machine-readable ate a migracao posterior decidir se eles permanecem, sao
gerados ou sao consolidados de outra forma.

## Template obrigatorio de cada arquivo tematico

Cada arquivo `*-rules.md` deve ter obrigatoriamente estas secoes:

1. `Objetivo`
2. `Escopo`
3. `Fonte canonica e precedencia`
4. `Regras obrigatorias`
5. `Startup: o que precisa ser carregado`
6. `Delegacao: o que o subagente precisa receber`
7. `Fallback e Recuperacao`
8. `Enforcement e validacoes`
9. `Artefatos relacionados`
10. `Temas vizinhos`

Regra obrigatoria:

- o tema precisa ficar inteiro no seu arquivo
- o fallback daquele tema precisa aparecer dentro dele
- evitar criar arquivo transversal separado so porque existe um subtipo de
  excecao operacional

## Classificacao obrigatoria das regras atuais

Durante a migracao, classificar todo conteudo atual em uma destas categorias:

### 1. Normativa canonica

Vai para [`.agents/rules/`](../../../rules/)

### 2. Enforcement executavel

Permanece em:

- [`Taskfile.yml`](../../../../Taskfile.yml)
- [`.githooks/`](../../../../.githooks/)
- [`scripts/`](../../../../scripts/)
- [`tests/`](../../../../tests/)
- workflows

### 3. Documentacao derivada

Permanece ou e reescrita em:

- [`docs/`](../../../../docs/)

### 4. Contrato global

Permanece sintetizado em:

- [`AGENTS.md`](../../../../AGENTS.md)

## Ondas de implementacao

### Onda 1 - Arquitetura base e infraestrutura da pasta

Implementar:

- arquivo inicial da pasta de rules
- catalogo tematico `CATALOG.md` da pasta de rules
- template padrao de tema
- declaracao em [`AGENTS.md`](../../../../AGENTS.md) e
  [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md) de
  que [`.agents/rules/`](../../../rules/) e a fonte canonica normativa por
  tema
- explicitar que `fallback` sera secao por tema, nao arquivo tematico principal
  no primeiro corte

### Onda 2 - Piloto Git

Implementar `git-rules.md` com consolidacao do que hoje esta espalhado em:

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/git-conventions.md`](../../../../docs/git-conventions.md)
- [`Taskfile.yml`](../../../../Taskfile.yml)
- [`.githooks/`](../../../../.githooks/)

Aproveitar o antigo `git-rules.md` local do WSL apenas como insumo historico,
nao como fonte confiavel final, porque ele esta desatualizado.

### Onda 3 - Startup, resume, chat e identidade

Criar:

- `startup-and-resume-rules.md`
- `chat-and-identity-rules.md`

Migrar regras hoje espalhadas em:

- [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- camada `display_name`
- contratos de comunicacao no chat

### Onda 4 - Intake, backlog e execucao Jira

Criar:

- `intake-and-backlog-rules.md`
- `jira-execution-rules.md`

Migrar regras hoje espalhadas em:

- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/jira-model.yaml`](../../../../config/ai/jira-model.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)

### Onda 5 - Delegacao, review, worklog e cerimonias

Criar:

- `delegation-rules.md`
- `review-and-quality-rules.md`
- `worklog-and-lessons-rules.md`
- `scrum-and-ceremonies-rules.md`

Migrar regras hoje espalhadas em:

- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
- [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md)
- [`docs/AI-SCRUM-MASTER-LEDGER.md`](../../../../docs/AI-SCRUM-MASTER-LEDGER.md)
- [`.agents/cerimonias/`](../../../../.agents/cerimonias/)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)

### Onda 6 - Documentacao, prompts, auth e sync

Criar:

- `documentation-and-confluence-rules.md`
- `prompt-pack-rules.md`
- `auth-secrets-and-critical-integrations-rules.md`
- `sync-foundation-rules.md`

Migrar regras hoje espalhadas em:

- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`docs/secrets-and-auth.md`](../../../../docs/secrets-and-auth.md)
- [`docs/ai-sync-foundation.md`](../../../../docs/ai-sync-foundation.md)
- [`.agents/prompts/README.md`](../../README.md)
- [`.agents/prompts/CATALOG.md`](../../CATALOG.md)

### Onda 7 - Regras nucleares e auditoria cross-repo

Criar:

- `core-rules.md`
- `source-audit-and-cross-repo-rules.md`

Migrar o que hoje esta espalhado entre:

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`docs/AI-SOURCE-AUDIT.md`](../../../../docs/AI-SOURCE-AUDIT.md)

### Onda 8 - Paridade, validacao e limpeza final

Atualizar:

- startup para carregar a nova camada
- manifest para incluir [`.agents/rules/`](../../../rules/)
- validadores para exigir catalogacao e linkagem
- testes de startup e validacao
- docs derivadas para apontarem para a nova fonte
- reduzir duplicacao residual em [`AGENTS.md`](../../../../AGENTS.md) e
  [`docs/`](../../../../docs/)

## Mudancas obrigatorias em AGENTS, docs, startup e validadores

### AGENTS.md

Deve:

- ficar menor
- manter precedencia, leitura obrigatoria e guardrails transversais
- apontar para os temas em [`.agents/rules/`](../../../rules/)
- parar de concentrar detalhes tematicos que ja migraram

### [docs/](../../../../docs/)

Devem:

- virar guias, runbooks, explicacoes e consumo humano
- apontar explicitamente para a regra tematica canonica
- evitar repetir regra inteira quando nao houver necessidade

### startup

Deve:

- carregar a nova camada centralizada
- expor no report quais regras tematicas foram carregadas
- continuar distinguindo `startup`, `PEA` e `enforcement`

### validadores

Devem:

- falhar quando um tema critico nao estiver catalogado
- falhar quando docs e `AGENTS` apontarem para regra errada ou antiga
- falhar quando houver drift claro entre tema canonico e contratos derivados

## Regras especificas sobre fallback

Regra arquitetural obrigatoria:

- nao criar `fallback-rules.md` como tema principal neste primeiro corte

Em vez disso, cada tema relevante deve ter sua propria secao `Fallback e
Recuperacao`.

Exemplos:

- `git-rules.md` -> fallback de branch, worktree, checkpoint e higiene local
- `startup-and-resume-rules.md` -> fallback de contexto, auth GitHub/PAT e
  recuperacao Atlassian
- `jira-execution-rules.md` -> fallback entre Jira e trackers locais
- `sync-foundation-rules.md` -> retry, ack, dead-letter, recovery e compaction
- `auth-secrets-and-critical-integrations-rules.md` -> fallback de token,
  signer, `gh`, `op`, `sops` e `age`

So criar um artefato global de fallback no futuro se, apos a migracao, sobrar
um microcontrato transversal pequeno e claro o suficiente para justificar isso
sem repartir os temas novamente.

## Criterios de aceite

A entrega so estara correta se:

1. [`.agents/rules/`](../../../rules/) virar de fato a fonte canonica
   normativa
   por tema
2. todo tema relevante tiver um arquivo proprio ou uma justificativa explicita
   de por que ainda nao foi migrado
3. `fallback` estiver modelado como secao tematica, sem reespalhar a
   governanca
4. [`AGENTS.md`](../../../../AGENTS.md) ficar mais curto e mais claro
5. startup, agentes e subagentes passarem a carregar e consumir a nova camada
6. docs, contracts, startup, validadores e testes ficarem em paridade
7. hooks, tasks, scripts e testes continuarem como enforcement executavel, sem
   virar docs e sem perder backend real
8. o repo ganhar `README` e `CATALOG` para a pasta de regras
9. nao houver nova fonte concorrente de verdade fora dessa arquitetura
10. toda nova sessao ou restart continuar absorvendo essa camada centralizada
    como parte do startup oficial

## Validacoes minimas esperadas

Executar o que for cabivel em cada fatia:

- [`task ai:worklog:check`](../../../../docs/TASKS.md#aiworklogcheck)
- [`task ai:startup:session`](../../../../docs/TASKS.md#aistartupsession)
- [`task ai:validate`](../../../../docs/TASKS.md#aivalidate)
- [`task docs:check`](../../../../docs/TASKS.md#docscheck)
- [`task ai:eval:smoke`](../../../../docs/TASKS.md#aievalsmoke)
- `task type:check`
- [`task ai:lessons:check`](../../../../docs/TASKS.md#ailessonscheck)
- [`task ai:review:check`](../../../../docs/TASKS.md#aireviewcheck)
- [`task ai:worklog:close:gate`](../../../../docs/TASKS.md#aiworklogclosegate)
- testes Python dirigidos para startup e validadores de assets

## Regras de Git desta propria frente

- commits atomicos
- uma issue Jira real por commit
- branch coerente com uma unica trilha
- como a rodada toca [`.agents/prompts/`](../../README.md), seguir o namespace
  `prompt`
- podar branch e worktree apos merge
- manter `main` limpa ao final de cada fatia integrada

## Anti-padroes proibidos

- criar `fallback-rules.md` gordo e transversal logo de inicio
- mover tudo de uma vez sem ondas testaveis
- duplicar a mesma regra em [`.agents/rules/`](../../../rules/), `AGENTS` e
  `docs`
- transformar Markdown em enforcement
- deixar docs e validadores sem apontar para a nova fonte
- operar por memoria parcial ou sem startup quando a sessao tiver sido retomada
  do zero
- criar `Epic` novo sem preflight
- criar issue duplicada para esta frente

## Resultado esperado

Ao final, o repo `dotfiles` deve ter:

- governanca normativa centralizada por tema
- curadoria mais simples
- onboarding e startup mais confiaveis
- menos drift entre agentes, docs, startup e enforcement
- melhor discoverability das regras
- manutencao por dominio, nao por espalhamento
- base preparada para migrar os demais temas do repo de forma controlada

## Instrucao final

Execute esta frente de forma autonoma e completa.

- nao pare em analise
- nao entregue apenas proposta textual
- crie ou reutilize a issue certa no `Jira`
- implemente por ondas testaveis
- atualize contratos, docs, startup, validadores e testes
- abra PR, valide, integre, sincronize com `main`, limpe branches e worktrees e
  feche a trilha com evidencias completas

O sucesso desta frente nao e apenas criar arquivos novos.
O sucesso e fazer a governanca normativa do repo realmente passar a orbitar
[`.agents/rules/`](../../../rules/), com paridade, enforcement e startup
coerentes.
