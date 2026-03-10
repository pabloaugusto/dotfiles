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
| 2026-03-10 12:53 UTC | DOT-127 | python-reviewer | aprovado | scripts/ai-worklog.py, scripts/ai_dispatch_lib.py, scripts/validate-ai-assets.py, tests/python/ai_worklog_test.py, tests/python/ai_dispatch_test.py, tests/python/ai_assets_validator_test.py | Scripts e testes Python aprovados para a nova semantica de concluir_primeiro com guidance explicito no preflight e intake. | task ai:validate; task ai:eval:smoke; task docs:check; python -m unittest tests.python.ai_worklog_test tests.python.ai_dispatch_test tests.python.ai_assets_validator_test |
| 2026-03-10 12:52 UTC | DOT-127 | automation-reviewer | aprovado | Taskfile.yml | Taskfile e trilha de automacao aprovados para refletir concluir_primeiro como concluir ou destravar o WIP ativo sem puxar demanda nova sem relacao. | task ai:validate; task docs:check; task ai:eval:smoke; task lint:yaml falhou apenas por baseline preexistente fora do escopo (.github/workflows/ai-governance.yml, config/ai/platforms.yaml, .agents/orchestration/routin... |
| 2026-03-09 23:59 UTC | DOT-114 | python-reviewer | aprovado | scripts/ai-atlassian-agent-comment-audit.py, scripts/ai-atlassian-backfill.py, scripts/ai_atlassian_agent_comment_audit_lib.py, scripts/ai_atlassian_board_ui_sync_lib.py, scripts/ai_atlassian_browser_auth_lib.py, scripts/ai_atlassian_browser_validate_lib.py, scripts/ai_atlassian_repair_lib.py, scripts/ai_control_plane_lib.py, scripts/ai_jira_apply_lib.py, scripts/atlassian_platform_lib.py, scripts/validate-ai-assets.py, scripts/validate_docs.py, tests/python/ai_atlassian_agent_comment_audit_test.py, tests/python/ai_atlassian_backfill_test.py, tests/python/ai_atlassian_board_ui_sync_test.py, tests/python/ai_atlassian_openapi_test.py, tests/python/ai_atlassian_seed_test.py, tests/python/ai_jira_apply_test.py, tests/python/atlassian_platform_test.py, tests/python/validate_docs_test.py | Cleanup tipado e de lint da trilha Atlassian aprovado com evidencias locais e regressao verde. | uv run --locked ruff check; uv run --locked ty check; uv run --locked python -m pytest; task ai:validate; task validate:actions; task test:integration:windows |
| 2026-03-08 04:21 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | powershell-reviewer | aprovado | scripts/run-ai-atlassian-docs-sync.ps1 | Wrapper PowerShell do docs sync aprovado para uso no Windows. | task ai:atlassian:docs:sync |
| 2026-03-08 04:21 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | python-reviewer | aprovado | scripts/ai-atlassian-docs-sync.py, scripts/ai_atlassian_seed_lib.py, scripts/atlassian_platform_lib.py, tests/python/ai_atlassian_seed_test.py, tests/python/atlassian_platform_test.py | Scripts e testes Atlassian aprovados para docs sync dedicado e diagnostico do board no check. | unittest, ruff, ty |
| 2026-03-08 04:21 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | automation-reviewer | aprovado | Taskfile.yml, docs/TASKS.md | Taskfile e tarefas de sync documental Atlassian aprovados para execucao deterministica. | task ai:atlassian:docs:sync, docs:check |
| 2026-03-07 16:04 UTC | WIP-20260307-SECRETS-ROTATION | automation-reviewer | aprovado | Taskfile.yml | Review de automacao aprovado para Taskfile e gates de revisao; os entrypoints canonicos e o fechamento do worklog permanecem coerentes com o fluxo do repo. | task ci:workflow:sync:check:windows; task docs:check:windows |
| 2026-03-07 16:04 UTC | WIP-20260307-SECRETS-ROTATION | python-reviewer | aprovado | scripts/ai-review.py, scripts/ai_review_lib.py, scripts/ai-worklog.py, scripts/validate-ai-assets.py, tests/python/ai_review_test.py, tests/python/ai_worklog_test.py, tests/python/ai_dispatch_test.py | Review Python aprovado para o ledger e gate especializado; a validacao cobre corretude, portabilidade Windows/WSL e regressao dos scripts Python de revisao/worklog. | task test:unit:python:windows; task ai:validate:windows; task ai:eval:smoke:windows |
<!-- ai-review:records:end -->
