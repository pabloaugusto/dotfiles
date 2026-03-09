# AI Orthography Ledger

Atualizado em: 2026-03-07 16:07 UTC

Registro consultivo do agente Pascoalete para ortografia e higiene vocabular.

## Regras operacionais

- O parecer ortografico e consultivo: nao bloqueia PR, branch, commit, worktree,
  deploy, release ou `done` tecnico.
- Toda mudanca versionada pode receber parecer de Pascoalete; quando houver
  falha nao corrigida, o problema deve virar pendencia rastreavel no backlog
  vigente.
- O dicionario local em [`.cspell/project-words.txt`](../.cspell/project-words.txt)
  nao deve repetir palavras ja cobertas pelos dicionarios importados.
- A fonte de verdade da configuracao do `cspell` e [`.cspell.json`](../.cspell.json).

## Registros

<!-- ai-orthography:records:start -->
| Data/Hora UTC | Worklog ID | Revisor | Status | Arquivo | Achados | Evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | Taskfile.yml | PYTHONDONTWRITEBYTECODE, PYTHONPYCACHEPREFIX, venv, venv, disponiveis, worktree, alteracoes, alteracoes (+129) | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | README.md | Repositorio, multiambiente, seguranca, governanca, Normalizacao, canonicos, canonico, integracoes (+70) | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/README.md | documentacoes, Operacao, migracao, canonica, rotacao, canonicas, automacao, tecnico (+12) | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/TASKS.md | canonicas, repositorio, operacao, diaria, governanca, Operacao, diaria, sincronizacao (+73) | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/secrets-and-auth.md | tecnico, diretorio, gpgsign, worktree, worktree, signingkey, worktree, Rotacao (+4) | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/reference/secrets-rotation-architecture.md | Rotacao, canonica, rotacao, repositorio, unica, auditavel, rotacao, automacao (+30) | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | tests/python/secrets_rotation_test.py | gitlab, gitlab, gitlab, indisponivel, gitlab, gitlab | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/secrets-rotation.py | execucao, validacao, rotacao | task spell:check |
| 2026-03-09 10:02 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/secrets_rotation_lib.py | configuracao, rotacao, Sessao, editaveis, SSHKEY, glab, glab, possivel (+36) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | tests/python/ai_assets_validator_test.py | possivel, LICOES, Validacao, LICOES, Orquestracao, evals, Integracoes, guardiao (+2) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | tests/python/cspell_governance_test.py | Pascoalete, Pascoalete, Pascoalete, Pascoalete, pascoalete, ortograficas, Pascoalete, pascoalete (+1) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/validate_docs.py | LICOES, governanca, validacao, diretorios, disponivel, repoish, repoish, repoish (+3) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/validate-ai-assets.py | execucao, evals, LICOES, evals, evals, evals, evals, autolog (+44) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/cspell_governance_lib.py | Pascoalete, ortografico, worktree, tecnico, mudanca, Pascoalete, rastreavel, dicionarios (+9) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/cspell-governance.py | execucao, Governanca, ortografica, repositorio, Pascoalete, pascoalete | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/AI-SOURCE-AUDIT.md | governanca, catalogos, taskfiles, orquestracao, evals, relacoes, governanca, Repositorios (+160) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/WORKFLOWS.md | licoes, governanca, catalogos, integracao, unitaria, canonico, pytest, Observacao (+6) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/AI-GOVERNANCE-AND-REGRESSION.md | Principios, governanca, licoes, importacao, minimo, concluido, revisao, LICOES (+26) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/AI-DELEGATION-FLOW.md | canonico, LICOES, minimo, importacao, decomposicao, delegacao, rotacao, expiracao (+43) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/AI-SKILLS-CATALOG.md | usuario, canonicos, efemeros, organizacao, governanca, simplificacao, tecnico, mudanca (+20) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/AI-AGENTS-CATALOG.md | obrigatorios, obrigatorio, mudanca, obrigatorio, mudanca, rotacao, expiracao, revogacao (+40) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/skills/dotfiles-python-review/SKILL.md | mudancas, corretude, validacao, manutencao, tecnico, codigo, coesao, Pascoalete (+15) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/skills/dotfiles-powershell-review/SKILL.md | mudancas, idempotencia, seguranca, tecnico, codigo, possiveis, Pascoalete, comentarios (+15) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/skills/dotfiles-automation-review/SKILL.md | mudancas, automacao, resiliencia, tecnico, automacao, automacao, Pascoalete, comentarios (+17) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/skills/dotfiles-orthography-review/agents/openai.yaml | Pascoalete, tecnica, tecnica | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/skills/dotfiles-orthography-review/references/checklist.md | redundancias, estao, dicionarios | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/skills/dotfiles-orthography-review/SKILL.md | tecnica, comentarios, comentarios, configuracao, Pascoalete, redundancias, necessario, dicionarios (+8) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/cards/revisor-python.md | mudanca, corretude, regressao, mudancas, automacao, mudanca, validacoes, Saidas (+16) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/cards/revisor-powershell.md | mudancas, idempotencia, seguranca, mudancas, automacao, validacoes, Saidas, aprovacao (+19) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/cards/revisor-automacao.md | Automacao, mudancas, automacao, resiliencia, mudancas, automacao, validacoes, Saidas (+23) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | .agents/cards/pascoalete.md | Pascoalete, tecnica, worktree, comentarios, dicionarios, Saidas, ortografico, correcao (+17) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | AGENTS.md | Missao, confiavel, testavel, reproduzivel, precedencia, LICOES, instrucoes, usuario (+100) | task spell:check |
<!-- ai-orthography:records:end -->
