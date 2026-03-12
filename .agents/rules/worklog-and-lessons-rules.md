# Worklog And Lessons Rules

## Objetivo

Definir continuidade operacional, fechamento e revisao de licoes.

## Escopo

- `Doing` e `Done`
- closeout
- lessons review

## Fonte canonica e precedencia

- [`../../docs/AI-WIP-TRACKER.md`](../../docs/AI-WIP-TRACKER.md)
- [`../../LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md)
- [`../../Taskfile.yml`](../../Taskfile.yml)

## Regras obrigatorias

- toda rodada relevante precisa de `Doing`
- o item ativo fica em `Doing` durante a execucao
- `Done` so no ultimo passo tecnico
- toda finalizacao revisa licoes com `capturada` ou `sem_nova_licao`

## Startup: o que precisa ser carregado

- item ativo
- branch atual
- dirty tree e contexto local

## Delegacao: o que o subagente precisa receber

- worklog id aplicavel
- proximo passo
- bloqueios

## Fallback e Recuperacao

- tracker local e fallback contingencial do Jira
- worktree suja sem `Doing` bloqueia nova rodada

## Enforcement e validacoes

- `task ai:worklog:check`
- `task ai:lessons:check`
- `task ai:worklog:close:gate`

## Artefatos relacionados

- [`../../docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
- [`../../docs/ROADMAP-DECISIONS.md`](../../docs/ROADMAP-DECISIONS.md)

## Temas vizinhos

- [`jira-execution-rules.md`](jira-execution-rules.md)
- [`scrum-and-ceremonies-rules.md`](scrum-and-ceremonies-rules.md)
