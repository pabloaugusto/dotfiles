# Prompt Pack Rules

## Objetivo

Definir a governanca dos packs formais versionados em [`.agents/prompts/`](../prompts/).

## Escopo

- namespace `prompt`
- owner issue
- catalogacao e pack formal

## Fonte canonica e precedencia

- [`../../.agents/prompts/README.md`](../../.agents/prompts/README.md)
- [`../../.agents/prompts/CATALOG.md`](../../.agents/prompts/CATALOG.md)
- [`../../docs/git-conventions.md`](../../docs/git-conventions.md)

## Regras obrigatorias

- pack versionado usa `task_id: prompt/<slug>`
- branch `prompt/<jira-key>-<slug>`
- `scope` `prompt` em commit e PR
- issue dona usa `PROMPT:` e label `prompt`

## Startup: o que precisa ser carregado

- catalogo de prompt packs
- pack formal aplicavel
- issue dona do pack

## Delegacao: o que o subagente precisa receber

- pack id
- owner issue
- preflight packs aplicaveis

## Fallback e Recuperacao

- pack sem issue dona e rejeitavel
- startup sem catalogo de prompt packs e incompleto

## Enforcement e validacoes

- `task ai:prompts:jira:check`
- `task docs:check`

## Artefatos relacionados

- [`../../.agents/prompts/formal/`](../../.agents/prompts/formal/)
- [`../../docs/TASKS.md`](../../docs/TASKS.md)

## Temas vizinhos

- [`git-rules.md`](git-rules.md)
- [`startup-and-resume-rules.md`](startup-and-resume-rules.md)
