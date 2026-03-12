# Prompt Para Codex - Endurecer O Startup Obrigatorio Com Guardiao Dedicado

## Missao

Implementar no repo [`dotfiles`](../../../../README.md) uma camada formal e
executavel de `startup gatekeeping`, adicionando um agente especializado para
rodar o startup obrigatorio, garantir seu enforcement e verificar aderencia
real antes da primeira resposta operacional ao usuario em `nova_sessao` ou
`restart`, sem criar startup paralelo, sem enfraquecer o `Scrum Master` e sem
substituir hooks, tasks, validadores ou workflow real do projeto.

## Por que este pack existe

Este pack existe porque o repo ja possui regras fortes para `startup/restart`,
contrato de chat e `display_name`, mas ainda deixa uma lacuna entre:

- o que a governanca exige em
  [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml),
  [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
  e [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- e o que efetivamente impede a primeira resposta operacional fora de
  conformidade

O problema alvo nao e falta de regra escrita. O problema alvo e falta de
`gatekeeper` especializado, `clearance` verificavel e bloqueio tecnico antes da
primeira saida concreta ao usuario.

## Origem imediata e origem normativa

### Origem imediata

Falhas reais recentes de aderencia em sessao nova ou retomada mostraram que a
disciplina manual do agente ainda nao e barreira suficiente para impedir:

- resposta operacional antes do startup integral
- resposta fora do contrato de chat carregado
- alegacao prematura de aderencia sem prova executavel

### Origem normativa

As regras ja existem e sao claras:

- `startup/restart` precisa reler o manifest integral e carregar o contrato de
  chat antes da primeira resposta operacional
- `display_name` precisa ser carregado no startup
- trabalho iniciado sem startup completo e rejeitavel
- delegacao sem contexto de startup e invalida

Esse pack nasce para fechar a lacuna entre regra declarada e enforcement real.

## Regra zero de intake e ownership

Antes de abrir demanda nova:

1. verificar se ja existe `Task` aberta no `Jira` cobrindo este escopo
2. verificar se o `Epic` aberto aderente continua sendo
   [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71)
3. reutilizar item existente quando ele cobrir o pack ou a execucao real
4. nao abrir `Epic` novo
5. so abrir `Task` nova se o preflight provar ausencia de item suficiente

## Evidencias versionadas obrigatorias

Use como evidencias minimas:

- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
  ja exige `zero-context-startup-must-load-chat-contract-before-first-user-message`
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml) ja declara
  que trabalho sem startup completo e rejeitavel
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
  ja gera report, carrega `display_name` e expande `pea_status`, mas ainda nao
  modela `startup clearance` como artefato bloqueante
- [`config/ai/agents.yaml`](../../../../config/ai/agents.yaml) e
  [`docs/AI-AGENTS-CATALOG.md`](../../../../docs/AI-AGENTS-CATALOG.md) ainda
  nao expoem papel dedicado de `startup gatekeeper`
- [`docs/AI-CHAT-CONTRACTS-REGISTER.md`](../../../../docs/AI-CHAT-CONTRACTS-REGISTER.md)
  e [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
  comprovam que a obrigatoriedade ja foi consolidada, mas o bypass ainda pode
  acontecer sem bloqueio duro suficiente

## Fronteiras obrigatorias

- este pack nao autoriza criar `startup` paralelo fora do fluxo oficial
- este pack nao rebaixa o `Scrum Master`; ele continua auditando visibilidade,
  conformidade de chat, `WIP` e cerimonias
- este pack nao transforma Markdown em enforcement; o enforcement real continua
  em tasks, scripts, validadores, testes e adaptadores
- este pack nao mistura `startup`, `PEA` e `enforcement`; ele endurece a
  fronteira entre essas camadas

## Objetivo arquitetural

Implementar esta arquitetura alvo:

- existir um agente dedicado `ai-startup-governor`
- esse agente ser o unico autorizado a emitir a primeira resposta concreta ao
  usuario durante `nova_sessao` e `restart`
- o startup produzir um artefato verificavel, como
  `.cache/ai/startup-ready.json`
- nenhum outro agente emitir resposta operacional sem `startup clearance`
- mudanca de branch, worktree, auth, `WIP`, contexto ou contratos invalidar a
  `clearance`
- o handoff do `Guardiao de Startup` para o agente dono do trabalho ser
  explicito, rastreavel e auditavel

## Modelo de ownership do chat

Definir e implementar a seguinte regra:

- antes de `ready_for_work`, quem fala no chat e o `Guardiao de Startup`
- durante `startup_in_progress`, `startup_blocked` ou `wip_decision_pending`,
  nenhum agente operacional assume a conversa
- depois de `ready_for_work`, o agente dono da rodada assume a comunicacao
  operacional
- o `Scrum Master` continua owner da auditoria de conformidade do chat
- o `Guardiao de Startup` nao substitui o dono da entrega; ele libera ou
  bloqueia a sessao

## State machine obrigatoria

Modelar o startup pelo menos com estes estados:

- `not_started`
- `reading_manifest`
- `chat_contract_loaded`
- `identity_loaded`
- `git_context_loaded`
- `probes_passed`
- `wip_decision_pending`
- `startup_failed`
- `ready_for_work`

Regras:

- `ready_for_work` so existe com prova material e valida
- `wip_decision_pending` bloqueia a sessao para qualquer saida operacional
- `startup_failed` so autoriza mensagem de erro, bloqueio ou pedido de decisao
- qualquer drift de contexto derruba a sessao de volta para `not_ready`

## Artefatos obrigatorios

Criar, endurecer ou alinhar:

- [`config/ai/agents.yaml`](../../../../config/ai/agents.yaml)
- [`docs/AI-AGENTS-CATALOG.md`](../../../../docs/AI-AGENTS-CATALOG.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)
- [`tests/python/ai_session_startup_test.py`](../../../../tests/python/ai_session_startup_test.py)
- [`tests/python/ai_assets_validator_test.py`](../../../../tests/python/ai_assets_validator_test.py)

Criar tambem os artefatos novos quando fizer sentido:

- `startup-ready.json`
- compilador do contrato de chat
- verificador de `first-response clearance`
- auditoria de drift de sessao

## Criterios de aceite

Esta frente so esta correta se:

1. o repo ganhar um papel dedicado de `startup gatekeeper`
2. a primeira resposta operacional ao usuario ficar bloqueada sem `startup clearance`
3. o startup gerar prova executavel de prontidao, nao apenas relatorio humano
4. o `display_name`, o contrato de chat e os contratos pendentes continuarem
   obrigatorios antes da primeira saida operacional
5. o `Scrum Master` continuar auditando a conformidade do chat sem perder
   ownership
6. drift de branch, worktree, auth, `WIP` ou contexto invalidar a `clearance`
7. delegacao continuar proibida sem contexto de startup valido
8. docs, contracts, scripts, validadores e testes ficarem em paridade
9. o repo passar a detectar objetivamente resposta fora do fluxo de startup
10. o bypass passar a depender apenas de ordem humana explicita

## Validacoes minimas esperadas

- [`task ai:worklog:check`](../../../../docs/TASKS.md#aiworklogcheck)
- [`task ai:startup:session`](../../../../docs/TASKS.md#aistartupsession)
- [`task ai:validate`](../../../../docs/TASKS.md#aivalidate)
- [`task docs:check`](../../../../docs/TASKS.md#docscheck)
- [`task ai:eval:smoke`](../../../../docs/TASKS.md#aievalsmoke)
- `python -m unittest tests.python.ai_session_startup_test`
- `python -m unittest tests.python.ai_assets_validator_test`

## Anti-padroes proibidos

- tratar esse tema como mera orientacao textual
- criar agente novo sem `clearance` ou sem veto real
- deixar o primeiro output concreto ao usuario sem gate tecnico
- fingir que o startup esta completo sem prova material
- descarregar a responsabilidade toda no `Scrum Master`
- implementar bloqueio que so vale para um adaptador e deixa os outros livres
- duplicar a mesma regra em muitas superficies sem fonte canonica clara

## Instrucao final

Execute esta frente como endurecimento estrutural do startup obrigatorio.

- nao pare em analise
- nao entregue so texto aspiracional
- modele ownership, handoff, `clearance`, drift e invalidacao
- preserve a separacao entre `startup`, `PEA`, `enforcement` e auditoria
- deixe as evidencias e os racionais explicitamente rastreaveis no repo
