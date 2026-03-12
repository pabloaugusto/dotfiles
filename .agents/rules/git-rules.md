# Git Rules

## Objetivo

Consolidar branch, commit, PR, merge e higiene de worktree.

## Escopo

- naming
- commit atomico
- branch/worktree lifecycle
- publish e cleanup

## Fonte canonica e precedencia

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../docs/git-conventions.md`](../../docs/git-conventions.md)
- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../Taskfile.yml`](../../Taskfile.yml)

## Regras obrigatorias

- uma branch, um contexto coerente
- commit e PR ligados a uma unica issue real
- trabalho em [`.agents/prompts/`](../prompts/) usa namespace `prompt`
- apos merge seguro, branch e worktree residuais devem ser podadas

## Startup: o que precisa ser carregado

- branch atual, upstream e ahead/behind
- `PR` atual da branch
- merged branches e worktrees absorvidas em `main`

## Delegacao: o que o subagente precisa receber

- branch correta da rodada
- issue dona
- regra de naming e escopo

## Fallback e Recuperacao

- worktree suja sem `Doing` bloqueia nova rodada
- local fallback nunca substitui `Jira` como fluxo vivo

## Enforcement e validacoes

- [`../../docs/TASKS.md#aigovernancecheck`](../../docs/TASKS.md)
- [`../../docs/TASKS.md#aiworklogcheck`](../../docs/TASKS.md#aiworklogcheck)
- [`.githooks/`](../../.githooks/)

## Artefatos relacionados

- [`git.rules`](git.rules)
- [`../../docs/TASKS.md`](../../docs/TASKS.md)
- [`../../docs/AI-WIP-TRACKER.md`](../../docs/AI-WIP-TRACKER.md)
- [`../../.github/pull_request_template.md`](../../.github/pull_request_template.md)

## Temas vizinhos

- [`worklog-and-lessons-rules.md`](worklog-and-lessons-rules.md)
- [`prompt-pack-rules.md`](prompt-pack-rules.md)
- [`startup-and-resume-rules.md`](startup-and-resume-rules.md)
