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
| 2026-03-09 12:04 UTC | WIP-20260307-SECRETS-ROTATION | automation-reviewer | aprovado | Taskfile.yml, df/bash/.inc/check-env.sh, bootstrap/README.md, docs/checkenv.md, docs/secrets-and-auth.md | Taskfile, shell e fluxo de automacao aprovados para o modo GitHub SSH sem prompt humano | task docs:check; task env:check SIGN_MODE=automation; git ls-remote origin |
| 2026-03-09 12:03 UTC | WIP-20260307-SECRETS-ROTATION | powershell-reviewer | aprovado | df/powershell/_functions.ps1, bootstrap/README.md, docs/checkenv.md, docs/secrets-and-auth.md | Ajustes PowerShell do checkEnv aprovados com paridade real para o signer tecnico da worktree | task test:unit:powershell; task env:check SIGN_MODE=automation |
| 2026-03-09 12:02 UTC | WIP-20260307-SECRETS-ROTATION | python-reviewer | aprovado | scripts/git_signing_lib.py, scripts/secrets_rotation_lib.py, tests/python/git_signing_mode_test.py, tests/python/secrets_rotation_test.py | Scripts Python de signing e rotation aprovados sem regressao funcional nem de integracao | uv run --active python -m unittest tests.python.git_signing_mode_test tests.python.secrets_rotation_test; task type:check |
<!-- ai-review:records:end -->
