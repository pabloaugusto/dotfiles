# Scrum And Ceremonies Rules

## Objetivo

Consolidar board, WIP, Scrum Master e cerimonias obrigatorias.

## Escopo

- leitura do board
- ownership
- cerimonias

## Fonte canonica e precedencia

- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../docs/AI-SCRUM-MASTER-LEDGER.md`](../../docs/AI-SCRUM-MASTER-LEDGER.md)
- [`../../.agents/cerimonias/`](../../.agents/cerimonias/)

## Regras obrigatorias

- board e lido da direita para a esquerda
- priorizar terminar ou destravar o item mais a direita
- `ai-scrum-master` fiscaliza ownership, chat e cerimonias
- branch fechada exige cadeia de retrospectiva quando aplicavel

## Startup: o que precisa ser carregado

- item mais a direita destravavel
- ownership atual
- backlog vivo e WIP

## Delegacao: o que o subagente precisa receber

- contexto do board
- papel atual e proximo papel
- backlog residual relevante

## Fallback e Recuperacao

- se board remoto degradar, usar tracker local como contingencia explicita
- cerimonia incompleta gera bug ou pendencia rastreavel

## Enforcement e validacoes

- `task ai:worklog:check`
- ledger do Scrum Master
- logs de cerimonias

## Artefatos relacionados

- [`../../docs/AI-AGENTS-CATALOG.md`](../../docs/AI-AGENTS-CATALOG.md)
- [`../../docs/AI-DELEGATION-FLOW.md`](../../docs/AI-DELEGATION-FLOW.md)

## Temas vizinhos

- [`intake-and-backlog-rules.md`](intake-and-backlog-rules.md)
- [`worklog-and-lessons-rules.md`](worklog-and-lessons-rules.md)
