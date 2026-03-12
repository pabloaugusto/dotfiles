# Startup And Resume Rules

## Objetivo

Definir o startup do zero, o restart confiavel e a liberacao de
`ready_for_work`.

## Escopo

- leitura do manifest
- `startup-ready.json`
- handoff do `ai-startup-governor`
- carga de rules e enablement

## Fonte canonica e precedencia

- [`../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
- [`../../docs/AI-STARTUP-AND-RESTART.md`](../../docs/AI-STARTUP-AND-RESTART.md)
- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../scripts/ai_session_startup_lib.py`](../../scripts/ai_session_startup_lib.py)

## Regras obrigatorias

- toda retomada sem continuidade confiavel exige releitura integral do manifest
- startup precisa carregar [`.agents/rules/`](./) e o enablement declarativo
  dos agentes
- `ai-startup-governor` bloqueia saida operacional prematura
- handoff operacional so existe com `ready_for_work`

## Startup: o que precisa ser carregado

- manifest resolvido
- [`README.md`](README.md) e [`CATALOG.md`](CATALOG.md)
- regras tematicas aplicaveis
- [`../../config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml)
- contrato de chat e `display_name`

## Delegacao: o que o subagente precisa receber

- startup report
- readiness artifact
- issue dona, branch e regra aplicavel
- status de enablement do papel delegado

## Fallback e Recuperacao

- drift de startup invalida clearance
- fallback local so com ledger e reconciliacao dirigida
- startup incompleto torna o trabalho rejeitavel

## Enforcement e validacoes

- [`../../docs/TASKS.md#aistartupsession`](../../docs/TASKS.md#aistartupsession)
- [`../../docs/TASKS.md#aistartupenforce`](../../docs/TASKS.md#aistartupenforce)
- [`../../tests/python/ai_session_startup_test.py`](../../tests/python/ai_session_startup_test.py)

## Artefatos relacionados

- [`startup.rules`](startup.rules)
- [`../../.agents/cards/ai-startup-governor.md`](../../.agents/cards/ai-startup-governor.md)
- [`../../docs/TASKS.md#aistartupenforce`](../../docs/TASKS.md#aistartupenforce)
- [`../../docs/AI-CHAT-CONTRACTS-REGISTER.md`](../../docs/AI-CHAT-CONTRACTS-REGISTER.md)

## Temas vizinhos

- [`chat-and-identity-rules.md`](chat-and-identity-rules.md)
- [`git-rules.md`](git-rules.md)
- [`delegation-rules.md`](delegation-rules.md)
