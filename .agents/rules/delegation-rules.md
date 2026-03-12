# Delegation Rules

## Objetivo

Garantir que nenhum subagente receba trabalho sem contexto suficiente.

## Escopo

- handoff
- pacote minimo de contexto
- bloqueio por papeis desabilitados

## Fonte canonica e precedencia

- [`../../docs/AI-DELEGATION-FLOW.md`](../../docs/AI-DELEGATION-FLOW.md)
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)
- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)

## Regras obrigatorias

- sem startup carregado, nao delegar
- sem issue dona, nao delegar
- sem `agent-enablement`, nao assumir que o papel esta habilitado
- agente `disabled` nao pode ser delegado por memoria de chat

## Startup: o que precisa ser carregado

- readiness artifact
- issue dona
- estado declarativo dos agentes

## Delegacao: o que o subagente precisa receber

- issue dona
- branch
- startup report
- regras aplicaveis
- confirmacao de enablement do papel

## Fallback e Recuperacao

- se faltar contexto minimo, bloquear delegacao
- se faltar enablement, tratar a delegacao como rejeitavel

## Enforcement e validacoes

- `task ai:delegate`
- `task ai:startup:enforce`

## Artefatos relacionados

- [`../../config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml)
- [`../../docs/AI-STARTUP-AND-RESTART.md`](../../docs/AI-STARTUP-AND-RESTART.md)

## Temas vizinhos

- [`startup-and-resume-rules.md`](startup-and-resume-rules.md)
- [`review-and-quality-rules.md`](review-and-quality-rules.md)
