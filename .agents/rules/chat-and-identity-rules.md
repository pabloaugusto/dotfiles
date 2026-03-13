# Chat And Identity Rules

## Objetivo

Centralizar a regra de comunicacao no chat e a camada de identidade humana dos
agentes.

## Escopo

- formato do chat
- ownership visivel do agente atuante (`acting-agent`)
- `display_name`
- `chat_alias`
- campos visiveis do `Jira`
- visibilidade de agentes `enabled` e `disabled`

## Fonte canonica e precedencia

- [`../../.agents/config/config.toml`](../../.agents/config/config.toml)
- [`../../.agents/config/agents.toml`](../../.agents/config/agents.toml)
- [`../../.agents/config/communication.toml`](../../.agents/config/communication.toml)
- [`../../.agents/config/startup.toml`](../../.agents/config/startup.toml)
- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml) como ponte legada
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml) como ponte legada
- [`../../config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml) como ponte legada
- [`../../config/ai/agent-runtime.yaml`](../../config/ai/agent-runtime.yaml) como ponte legada
- [`../../docs/AI-CHAT-CONTRACTS-REGISTER.md`](../../docs/AI-CHAT-CONTRACTS-REGISTER.md)
- [`../../.agents/registry/`](../../.agents/registry/)

Config canonica:

- manifesto raiz da IA: [`../../.agents/config/config.toml`](../../.agents/config/config.toml)
- identidade humana declarativa: [`../../.agents/config/agents.toml`](../../.agents/config/agents.toml)
- formato do chat e fallback alias-first:
  [`../../.agents/config/communication.toml`](../../.agents/config/communication.toml)
- ownership e handoff do startup:
  [`../../.agents/config/startup.toml`](../../.agents/config/startup.toml)
- quando um valor for configuravel, consultar a chave canonica nesses arquivos
  em vez de repetir o literal neste documento

## Regras obrigatorias

- o chat usa timestamp local real e o agente atuante deve ser o owner visivel da mensagem
- o `acting-agent` deve ser o owner visivel da mensagem que ele executa
- o nome visivel no chat e no `Jira` deve preferir `chat_alias`, depois `display_name` e so por ultimo o id tecnico
- a primeira saida operacional ate `ready_for_work` pertence ao
  `ai-startup-governor`
- `Current Agent Role` e `Next Required Role` no `Jira` usam valor visivel alias-first, nunca memoria manual
- `Assignee` no `Jira` so pode mudar por mapeamento explicito entre agente e principal real
- agente desabilitado por config nao pode ser reativado apenas por memoria de
  chat
- o chat espelha marcos relevantes, mas nao substitui `Jira` nem `Confluence`

## Startup: o que precisa ser carregado

- contrato de comunicacao no chat
- camada de `display_name`
- camada de `chat_alias` e runtime visivel dos agentes
- contratos pendentes do chat
- estado efetivo de enablement dos agentes

## Delegacao: o que o subagente precisa receber

- nome humano esperado para a superficie
- restricoes de comunicacao no chat
- enablement do papel delegado
- alias visivel e mapeamento de principal Jira quando houver

## Fallback e Recuperacao

- sem `chat_alias` e sem `display_name`, usar id tecnico como fallback visivel
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
