# Rules Catalog

## Temas

| Tema | Arquivo | Foco principal |
| --- | --- | --- |
| Core | [`core-rules.md`](core-rules.md) | precedencia, fronteira e contratos transversais |
| Chat e identidade | [`chat-and-identity-rules.md`](chat-and-identity-rules.md) | contrato de chat, `display_name` e visibilidade humana |
| Startup e resume | [`startup-and-resume-rules.md`](startup-and-resume-rules.md) | startup do zero, restart, readiness e handoff |
| Git | [`git-rules.md`](git-rules.md) | branch, commit, PR, merge e higiene de worktree |
| Intake e backlog | [`intake-and-backlog-rules.md`](intake-and-backlog-rules.md) | dedupe, reuse de `Epic` e leitura do board |
| Execucao Jira | [`jira-execution-rules.md`](jira-execution-rules.md) | comments, ownership, transicoes e evidencias |
| Documentacao e Confluence | [`documentation-and-confluence-rules.md`](documentation-and-confluence-rules.md) | source of truth, placement, sync e backlinks |
| Delegacao | [`delegation-rules.md`](delegation-rules.md) | pacote minimo de contexto e regras de subagentes |
| Review e qualidade | [`review-and-quality-rules.md`](review-and-quality-rules.md) | revisores, testes e gates especializados |
| Worklog e licoes | [`worklog-and-lessons-rules.md`](worklog-and-lessons-rules.md) | `Doing`, `Done`, lessons e closeout |
| Scrum e cerimonias | [`scrum-and-ceremonies-rules.md`](scrum-and-ceremonies-rules.md) | board, WIP, retrospectiva e ledger |
| Prompt packs | [`prompt-pack-rules.md`](prompt-pack-rules.md) | namespace `prompt`, Jira dona e catalogacao |
| Auth, secrets e integracoes | [`auth-secrets-and-critical-integrations-rules.md`](auth-secrets-and-critical-integrations-rules.md) | `gh`, `op`, signing, secrets e integracoes criticas |
| Sync foundation | [`sync-foundation-rules.md`](sync-foundation-rules.md) | outbox duravel, ack, retry e fonte perene |
| Source audit e cross-repo | [`source-audit-and-cross-repo-rules.md`](source-audit-and-cross-repo-rules.md) | auditoria estrutural exaustiva e imports |

## Regra de navegacao

- leia primeiro o tema dono do trabalho atual
- use [`core-rules.md`](core-rules.md) para contratos compartilhados
- quando um tema tocar startup ou delegacao, leia tambem os temas vizinhos

## Projecoes executaveis

| Tema | Fonte humana | Projecao `.rules` | Obrigatoria no startup |
| --- | --- | --- | --- |
| Startup | [`startup-and-resume-rules.md`](startup-and-resume-rules.md) | [`startup.rules`](startup.rules) | sim |
| Chat | [`chat-and-identity-rules.md`](chat-and-identity-rules.md) | [`chat.rules`](chat.rules) | sim |
| Git | [`git-rules.md`](git-rules.md) | [`git.rules`](git.rules) | sim |
| Security | [`auth-secrets-and-critical-integrations-rules.md`](auth-secrets-and-critical-integrations-rules.md) | [`security.rules`](security.rules) | sim |

- o vinculo declarativo oficial entre essas camadas vive em
  [`projections.yaml`](projections.yaml)
- novas projecoes `.rules` so devem nascer quando houver consumidor real no
  runtime, no startup ou em gates automatizados
