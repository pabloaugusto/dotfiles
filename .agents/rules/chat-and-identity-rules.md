# Chat And Identity Rules

## Objetivo

Centralizar a regra de comunicacao no chat e a camada de identidade humana dos
agentes.

## Escopo

- formato do chat
- `display_name`
- visibilidade de agentes `enabled` e `disabled`

## Fonte canonica e precedencia

- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)
- [`../../config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml)
- [`../../docs/AI-CHAT-CONTRACTS-REGISTER.md`](../../docs/AI-CHAT-CONTRACTS-REGISTER.md)
- [`../../.agents/registry/`](../../.agents/registry/)

## Regras obrigatorias

- o chat usa timestamp local real e `display_name` oficial
- a primeira saida operacional ate `ready_for_work` pertence ao
  `ai-startup-governor`
- agente desabilitado por config nao pode ser reativado apenas por memoria de
  chat
- o chat espelha marcos relevantes, mas nao substitui `Jira` nem `Confluence`

## Startup: o que precisa ser carregado

- contrato de comunicacao no chat
- camada de `display_name`
- contratos pendentes do chat
- estado efetivo de enablement dos agentes

## Delegacao: o que o subagente precisa receber

- nome humano esperado para a superficie
- restricoes de comunicacao no chat
- enablement do papel delegado

## Fallback e Recuperacao

- sem `display_name`, usar id tecnico como fallback visivel
- se o contrato de chat nao estiver carregado, bloquear saida operacional

## Enforcement e validacoes

- [`../../scripts/ai_session_startup_lib.py`](../../scripts/ai_session_startup_lib.py)
- [`../../tests/python/ai_session_startup_test.py`](../../tests/python/ai_session_startup_test.py)
- [`../../scripts/validate-ai-assets.py`](../../scripts/validate-ai-assets.py)

## Artefatos relacionados

- [`chat.rules`](chat.rules)
- [`../../docs/AI-STARTUP-AND-RESTART.md`](../../docs/AI-STARTUP-AND-RESTART.md)
- [`../../docs/AI-AGENTS-CATALOG.md`](../../docs/AI-AGENTS-CATALOG.md)
- [`../../docs/AI-DELEGATION-FLOW.md`](../../docs/AI-DELEGATION-FLOW.md)

## Temas vizinhos

- [`startup-and-resume-rules.md`](startup-and-resume-rules.md)
- [`delegation-rules.md`](delegation-rules.md)
- [`scrum-and-ceremonies-rules.md`](scrum-and-ceremonies-rules.md)
