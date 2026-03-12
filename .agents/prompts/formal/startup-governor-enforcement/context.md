# Contexto Do Pack

Este pack existe para transformar uma exigencia normativa ja consolidada em
barreira operacional verificavel: o startup obrigatorio precisa deixar de
depender apenas da obediencia do agente e passar a bloquear a primeira resposta
operacional quando o contexto ainda nao estiver integralmente carregado.

## Origem

### Origem imediata

Uma sessao recente expos, de forma pratica, um gap importante:

- o repo ja exigia `startup` integral
- o chat ja exigia contrato de comunicacao e `display_name`
- mas a primeira resposta operacional ainda podia escapar sem `clearance`
  tecnicamente endurecida

Essa evidencia imediata nasceu no uso real do repo e ainda nao esta promovida
como artefato versionado especifico. Por isso, este pack ancora sua
justificativa sobretudo nas evidencias versionadas abaixo.

### Origem normativa

O repositorio ja consolidou esses contratos em varias superficies:

- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-CHAT-CONTRACTS-REGISTER.md`](../../../../docs/AI-CHAT-CONTRACTS-REGISTER.md)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)

O problema, portanto, nao e ausencia de regra. O problema e ausencia de
`gatekeeper` especializado e de `startup clearance` executavel.

## Evidencias versionadas

- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
  ja obriga o carregamento do contrato de chat antes da primeira mensagem ao
  usuario em retomadas sem contexto confiavel.
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml) ja marca
  trabalho sem startup completo como rejeitavel e mantem o `Scrum Master` como
  owner da visibilidade/auditoria do chat.
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
  ja produz o relatorio oficial de startup, carrega `display_name`, relembra a
  governanca Git e integra o pack `startup-alignment`.
- [`config/ai/agents.yaml`](../../../../config/ai/agents.yaml) e
  [`docs/AI-AGENTS-CATALOG.md`](../../../../docs/AI-AGENTS-CATALOG.md) nao
  declaram hoje um papel especializado em `startup gatekeeping`.
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
  e [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
  deixam claro que o startup deve acontecer antes de operar, mas ainda nao
  estabelecem `clearance` formal como artefato obrigatorio de primeira resposta.

## Racional

- regra sem gate tecnico ainda deixa espaco para drift operacional
- um papel dedicado reduz a dependencia de disciplina manual do agente
- `Guardiao de Startup` e complementar ao `Scrum Master`, nao concorrente
- `clearance` invalida por drift torna o startup continuamente verificavel
- a primeira resposta operacional vira consequencia do estado da sessao, nao da
  boa vontade do modelo

## Fronteiras

- este pack nao autoriza `startup` paralelo
- este pack nao retira do `Scrum Master` o ownership de auditoria do chat
- este pack nao transforma relatorio em prova suficiente; o relatorio humano
  continua util, mas a prova precisa ser executavel
- este pack nao substitui `Jira`, `worklog`, reviews, lessons, closeout ou
  demais gates reais do repo

## Dependencias e ordem segura

- prerequisite packs: nenhum
- preflight packs:
  - [`startup-alignment`](../startup-alignment/prompt.md)
  - [`agents-rules-centralization`](../agents-rules-centralization/prompt.md)
- este pack depende da separacao correta entre `startup`, `PEA`,
  `enforcement`, ownership de chat e fonte canonica em [`.agents/rules/`](../../../rules/)

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-CHAT-CONTRACTS-REGISTER.md`](../../../../docs/AI-CHAT-CONTRACTS-REGISTER.md)
- [`docs/AI-AGENTS-CATALOG.md`](../../../../docs/AI-AGENTS-CATALOG.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`config/ai/agents.yaml`](../../../../config/ai/agents.yaml)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)

## Resultado esperado

- o catalogo de prompts passa a ter um pack formal dedicado ao hardening do
  startup
- a governanca ganha um papel especializado de `startup gatekeeper`
- a primeira resposta operacional ao usuario passa a depender de `clearance`
  verificavel
- o repo reduz drasticamente a chance de responder fora do contrato de startup
  em `nova_sessao` e `restart`
