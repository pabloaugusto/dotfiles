# AI Review Ledger

Atualizado em: 2026-03-07 15:46 UTC

Registro operacional dos pareceres de revisao especializada por `worklog`.

## Regras operacionais

- Toda mudanca de codigo ou automacao que toque Python, PowerShell, shell,
  workflows, [`Taskfile.yml`](../Taskfile.yml) ou Docker exige parecer explicito
  do revisor especializado correspondente antes de fechar o `worklog`.
- O parecer vale por `worklog` + `revisor`.
- Apenas o registro mais recente de cada `worklog` + `revisor` conta como fonte
  de verdade.
- `reprovado` bloqueia o `done` ate existir um novo parecer `aprovado`.
- Se nao houver familia de arquivo coberta pelo gate especializado, o ledger nao
  bloqueia o fechamento.

## Status validos

- `aprovado`
- `reprovado`

## Artefatos relacionados

- [`AGENTS.md`](../AGENTS.md)
- [`LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md)
- [`docs/AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md)
- [`ROADMAP.md`](../ROADMAP.md)
- [`scripts/ai-review.py`](../scripts/ai-review.py)
- [`scripts/ai_review_lib.py`](../scripts/ai_review_lib.py)

## Registros

<!-- ai-review:records:start -->
| Data/Hora UTC | Worklog ID | Revisor | Status | Arquivos | Resumo | Evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-03-08 04:21 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | powershell-reviewer | aprovado | scripts/run-ai-atlassian-docs-sync.ps1 | Wrapper PowerShell do docs sync aprovado para uso no Windows. | task ai:atlassian:docs:sync |
| 2026-03-08 04:21 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | python-reviewer | aprovado | scripts/ai-atlassian-docs-sync.py, scripts/ai_atlassian_seed_lib.py, scripts/atlassian_platform_lib.py, tests/python/ai_atlassian_seed_test.py, tests/python/atlassian_platform_test.py | Scripts e testes Atlassian aprovados para docs sync dedicado e diagnostico do board no check. | unittest, ruff, ty |
| 2026-03-08 04:21 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | automation-reviewer | aprovado | Taskfile.yml, docs/TASKS.md | Taskfile e tarefas de sync documental Atlassian aprovados para execucao deterministica. | task ai:atlassian:docs:sync, docs:check |
| 2026-03-07 16:04 UTC | WIP-20260307-SECRETS-ROTATION | automation-reviewer | aprovado | Taskfile.yml | Review de automacao aprovado para Taskfile e gates de revisao; os entrypoints canonicos e o fechamento do worklog permanecem coerentes com o fluxo do repo. | task ci:workflow:sync:check:windows; task docs:check:windows |
| 2026-03-07 16:04 UTC | WIP-20260307-SECRETS-ROTATION | python-reviewer | aprovado | scripts/ai-review.py, scripts/ai_review_lib.py, scripts/ai-worklog.py, scripts/validate-ai-assets.py, tests/python/ai_review_test.py, tests/python/ai_worklog_test.py, tests/python/ai_dispatch_test.py | Review Python aprovado para o ledger e gate especializado; a validacao cobre corretude, portabilidade Windows/WSL e regressao dos scripts Python de revisao/worklog. | task test:unit:python:windows; task ai:validate:windows; task ai:eval:smoke:windows |
<!-- ai-review:records:end -->
