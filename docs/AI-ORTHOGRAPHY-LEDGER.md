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
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | scripts/validate-ai-assets.py | execucao, evals, LICOES, evals, evals, evals, evals, atlassian (+47) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/evals/datasets/routing.jsonl | governanca, tecnico, agil | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | docs/atlassian-ia/artifacts/agent-operations.md | canonica, Sincronizacao, governanca, comentarios, tecnicos, atuacao, documentacao, tambem (+56) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | docs/config-reference.md | worktree, generica, materializacao, atlassian, atlassian, precedencia, atlassian, atlassian (+42) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | docs/ai-operating-model.md | reutilizavel, testavel, worktree, Principios, Instrucoes, instrucoes, estaveis, Especializacao (+126) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | docs/AI-GOVERNANCE-AND-REGRESSION.md | Principios, governanca, licoes, importacao, minimo, concluido, revisao, LICOES (+25) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | docs/AI-DELEGATION-FLOW.md | canonico, LICOES, minimo, importacao, comunicacao, decomposicao, delegacao, rotacao (+47) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | docs/AI-AGENTS-CATALOG.md | obrigatorios, comunicacao, obrigatorio, mudanca, obrigatorio, mudanca, rotacao, expiracao (+58) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | config/ai/jira-model.yaml | atlassian, tecnica, governanca, regressao, decomposicao, canonico, autonomo, Workstream (+4) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | config/ai/contracts.yaml | descricao, tecnico, criterios, aceitacao, documentacao | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | config/ai/agent-operations.yaml | atlassian, decisao, documentacao, linkar, mudanca, atualizacao, necessario, linkar (+110) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | config/ai/agents.yaml | figma | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/orchestration/routing-policy.yaml | LICOES, LICOES, pascoalete, mypy, pytest, governanca, pascoalete, pascoalete (+3) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/orchestration/capability-matrix.yaml | pascoalete | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/config.toml | pascoalete, evals, evals, evals, evals, evals | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/registry/ai-engineering-manager.toml | escalacoes | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/registry/ai-scrum-master.toml | comunicacao | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/cards/ai-engineering-manager.md | escalacoes, colaboracao, saturacao, escalacao, usuario, Saidas, necessario, escalacoes (+16) | task spell:check |
| 2026-03-09 21:21 UTC | DOT-115 | pascoalete | reprovado | .agents/cards/ai-scrum-master.md | agil, aderencia, comunicacao, fiscalizacao, comunicacao, escalacao, governanca, worktrees (+38) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | tests/powershell/BootstrapConfig.Tests.ps1 | pablo, pablo, pabloaugusto, AAAATESTLOCAL | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | docs/secrets-and-auth.md | tecnico, migracao, comentarios, documentacao, canonica, permissoes, rotacao, atlassian (+25) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | docs/checkenv.md | gpgsign, signingkey, identityagent, identityfile, worktree, worktree, worktree, signingkey (+3) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | df/secrets/secrets-ref.yaml | repositorio | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | df/powershell/_functions.ps1 | SFTA, winget, winget, winget, winget, Winget, winget, acceptlicense (+166) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | df/bash/.inc/check-env.sh | Disponivel, Disponivel, Disponivel, decriptografia, acessivel, acessivel, permissoes, toplevel (+64) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | config/secrets-rotation.yaml | onepassword, onepassword, gitlab, gitlab, glab, gitlab, gitlab, gitlab | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | bootstrap/user-config.yaml.tpl | Configuracao, configuracao, canonicos, implicita, varios, variaveis, expansao, resolucao (+23) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | bootstrap/bootstrap-ubuntu-wsl.sh | gsub, gsub, gsub, gsub, gsub, sofware, procps, fontconfig (+37) | task spell:check |
| 2026-03-10 14:17 UTC | DOT-128 | pascoalete | reprovado | bootstrap/bootstrap-config.ps1 | onepassword, variaveis, padrao, canonicos, implicita, varios, variaveis, expansao (+35) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | tests/python/ai_worklog_test.py | gpgsign, worktree, LICOES, obrigatorio, worktree, LICOES, licao, licao (+11) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | tests/python/ai_dispatch_test.py | tecnico, governanca | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | tests/python/ai_assets_validator_test.py | possivel, LICOES, atlassian, Validacao, minimo, LICOES, comecar, Orquestracao (+6) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | scripts/validate-ai-assets.py | execucao, evals, LICOES, evals, evals, evals, evals, atlassian (+50) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | scripts/ai_dispatch_lib.py | execucao, minimo, Secao, condicoes, Acao, Semantica, acao | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | scripts/ai-worklog.py | execucao, Responsavel, atualizacao, Responsavel, Concluido, Descricao, Atualizacao, minimo (+42) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | .agents/skills/wip-continuity-governance/SKILL.md | obrigatorio, LICOES, execucao, decisao, minimo, execucao, LICOES, licao (+10) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | .agents/skills/task-routing-and-decomposition/SKILL.md | decomposicao, delegacao, delegacao, tecnico, distribuicao, verificacao, obrigatorios, implementacao (+14) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | .agents/cards/orquestrador-delegacao.md | Delegacao, decomposicao, delegacao, decomposicao, verificacao, obrigatorios, reconciliacao, execucao (+19) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | .agents/cards/governador-continuidade-wip.md | mudanca, implementacao, acionavel, usuario, LICOES, Saidas, decisao, minimo (+12) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | docs/ai-operating-model.md | reutilizavel, testavel, worktree, Principios, Instrucoes, instrucoes, estaveis, governanca (+144) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | docs/TASKS.md | canonicas, repositorio, operacao, diaria, governanca, Operacao, diaria, sincronizacao (+106) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | docs/AI-WIP-TRACKER.md | solicitacao, acionavel, minimo, execucao, execucao, obrigatorio, Responsavel, atualizacao (+253) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | docs/AI-STARTUP-AND-RESTART.md | sessao, confiavel, sessao, sessoes, worktree, worktree, alteracoes, sessao (+24) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | docs/AI-CHAT-CONTRACTS-REGISTER.md | definicoes, governanca, obrigatoria, sessao, usuario, promocao, promocao, governanca (+35) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | config/ai/jira-model.yaml | atlassian, tecnica, governanca, regressao, reducao, decomposicao, Recomendacao, Criterios (+19) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | config/ai/contracts.yaml | worktrees, worktree, minimo, descricao, tecnico, criterios, aceitacao, documentacao | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | config/ai/agent-operations.yaml | atlassian, comentario, atuacao, comentario, decisao, comentario, transicao, decisao (+138) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | Taskfile.yml | PYTHONDONTWRITEBYTECODE, PYTHONPYCACHEPREFIX, venv, venv, disponiveis, worktree, alteracoes, alteracoes (+152) | task spell:check |
| 2026-03-10 12:40 UTC | DOT-127 | pascoalete | reprovado | AGENTS.md | Missao, confiavel, testavel, reproduzivel, precedencia, LICOES, instrucoes, usuario (+116) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | aprovado | tests/python/ai_tech_lead_review_contract_test.py | sem achados | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | tests/python/ai_reviewer_policies_test.py | comentario, omissao, decisao | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | docs/atlassian-ia/artifacts/jira-writing-standards.md | Decisao, padrao, medio, definicao, legivel, tecnico, governanca, regressao (+61) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | docs/atlassian-ia/artifacts/agent-operations.md | canonica, Sincronizacao, governanca, comentarios, tecnicos, atuacao, documentacao, tambem (+112) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | docs/atlassian-ia/2026-03-08-spike-cobertura-agentes-e-review-especializado.md | priorizacao, generico, unico, revisao, tecnica, revisao, codigo, autonomo (+78) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | docs/atlassian-ia/2026-03-08-manual-agilidade-control-plane.md | atlassian, agil, classicos, operacao, documentacao, codigo, operacao, Fundacao (+125) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | config/ai/jira-model.yaml | atlassian, tecnica, governanca, regressao, reducao, decomposicao, Recomendacao, Criterios (+19) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | config/ai/reviewer-policies.yaml | atlassian, decisao, tecnica, opiniao, decisao, corretude, seguranca, eficiencia (+61) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | config/ai/agent-operations.yaml | atlassian, comentario, atuacao, comentario, decisao, comentario, transicao, decisao (+136) | task spell:check |
| 2026-03-10 03:33 UTC | DOT-117 | pascoalete | reprovado | config/ai/agents.yaml | figma | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/validate_docs_test.py | repoish | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/atlassian_platform_test.py | atlassian, atlassian, atlassian, atlassian, linkifies, linkify, regressao, interacao (+12) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/ai_jira_apply_test.py | canonico, canonico, canonico, atlassian, atlassian | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/ai_atlassian_seed_test.py | atlassian, atlassian, atlassian, atlassian, atlassian, linkify, Conteudo, Conteudo (+7) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/ai_atlassian_openapi_test.py | atlassian, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/ai_atlassian_board_ui_sync_test.py | atlassian | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/ai_atlassian_backfill_test.py | atlassian, Criterios, tecnico, Criterios, LICOES, LICOES, LICOES | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | tests/python/ai_atlassian_agent_comment_audit_test.py | atlassian, atlassian, interacao, interacao, pascoalete | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/validate_docs.py | LICOES, governanca, validacao, diretorios, disponivel, repoish, repoish, repoish (+3) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/validate-ai-assets.py | execucao, evals, LICOES, evals, evals, evals, evals, atlassian (+47) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/atlassian_platform_lib.py | atlassian, interacao, concluido, concluida, dedup, dedup, dedup, atlassian (+13) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_jira_apply_lib.py | atlassian, atlassian, atlassian, customfieldtypes, atlassian, customfieldtypes, multiselectsearcher, atlassian (+19) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_control_plane_lib.py | atlassian, atlassian, atlassian, atlassian, atlassian, repositorio, linkify, obrigatorio (+2) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_atlassian_repair_lib.py | atlassian, atlassian, linkify, atlassian, atlassian, dedup, atlassian, interacao (+6) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_atlassian_browser_validate_lib.py | atlassian, reauthentication, atlassian, atlassian, disponivel, domcontentloaded, networkidle, reauthentication (+4) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_atlassian_browser_auth_lib.py | atlassian, atlassian, atlassian, timespec, atlassian, atlassian, reauthentication, reauthentication (+13) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_atlassian_board_ui_sync_lib.py | atlassian, reauthentication, atlassian, testid, testid, testid, testid, testid (+16) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai_atlassian_agent_comment_audit_lib.py | atlassian, atlassian, interacao, pascoalete, comentarios, comentario, comentario, comentario (+11) | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai-atlassian-backfill.py | execucao, atlassian | task spell:check |
| 2026-03-09 23:54 UTC | DOT-114 | pascoalete | reprovado | scripts/ai-atlassian-agent-comment-audit.py | execucao, atlassian | task spell:check |
| 2026-03-08 04:38 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-parecer-e-plano-inicial.md | operacao, direcao, documentacao, viavel, migracao, viavel, transicao, LICOES (+196) | task spell:check |
| 2026-03-08 04:38 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-jira-configuration-export.md | Configuracao, atlassian, atlassian, Workstream, auditavel, substituidos, operacao, governanca (+14) | task spell:check |
| 2026-03-08 04:38 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-diagnostico-auth-e-acesso-atlassian.md | concluido, atlassian, atlassian, estao, visivel, migracao, auditavel, comentarios (+32) | task spell:check |
| 2026-03-08 04:38 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/agent-operations.md | canonica, Sincronizacao, governanca, comentarios, tecnicos, atuacao, documentacao, tambem (+50) | task spell:check |
| 2026-03-08 04:38 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/TASKS.md | canonicas, repositorio, operacao, diaria, governanca, Operacao, diaria, sincronizacao (+96) | task spell:check |
| 2026-03-08 03:56 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/AI-WIP-TRACKER.md | solicitacao, acionavel, usuario, execucao, execucao, obrigatorio, Responsavel, atualizacao (+224) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | config/ai/jira-model.yaml | atlassian, tecnica, governanca, regressao, decomposicao, canonico, autonomo, Workstream (+4) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | config/ai/confluence-model.yaml | atlassian, navegacao, atlassian, atlassian, atlassian, atlassian, Operacao, Governanca | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/jira-board-layout.md | canonica, automacao, documentacao, expone, mutar, correcao, governanca, validacao (+2) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/atlassian-endpoints.md | usuario, aplicacao, reutilizaveis, obrigatorio, aplicavel, obrigatorio, criacao, validacao (+23) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md | Permissoes, canonico, rotacao, atlassian, canonica, especificos, necessario, usuario (+44) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | Taskfile.yml | PYTHONDONTWRITEBYTECODE, PYTHONPYCACHEPREFIX, venv, venv, disponiveis, worktree, alteracoes, alteracoes (+142) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/ai_atlassian_migration_bundle_test.py | atlassian | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/atlassian_platform_test.py | atlassian, atlassian, atlassian, atlassian, regressao, atlassian | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/ai_atlassian_seed_test.py | atlassian | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai_atlassian_migration_bundle_lib.py | atlassian, atlassian, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/atlassian_platform_lib.py | atlassian, obrigatorio, atlassian, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai_atlassian_seed_lib.py | atlassian, atlassian, atlassian, atlassian, atlassian, repositorio, sincronizacao, Conteudo (+11) | task spell:check |
| 2026-03-08 03:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai-atlassian-seed.py | execucao, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-08 02:36 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/migration-bundle.md | atlassian, atlassian, atlassian, unico, auditavel, Conteudo, minimo, vendorizadas (+4) | task spell:check |
| 2026-03-08 02:36 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/jira-schema.md | canonica, Sincronizacao, comentario, tecnico, atlassian, estao, entao, Workstream (+7) | task spell:check |
| 2026-03-08 02:36 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/config-reference.md | worktree, generica, materializacao, atlassian, atlassian, precedencia, atlassian, atlassian (+41) | task spell:check |
| 2026-03-08 02:36 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/secrets-and-auth.md | tecnico, migracao, comentarios, documentacao, canonica, permissoes, rotacao, atlassian (+20) | task spell:check |
| 2026-03-08 02:36 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/ai_control_plane_test.py | atlassian, atlassian, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-08 02:36 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai_control_plane_lib.py | atlassian, atlassian, atlassian, atlassian, atlassian, obrigatorio, Variavel, obrigatoria | task spell:check |
| 2026-03-08 02:29 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/ai_atlassian_openapi_test.py | atlassian, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-08 02:29 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | aprovado | tests/python/ai_jira_apply_test.py | sem achados | task spell:check |
| 2026-03-08 02:29 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai_jira_apply_lib.py | atlassian, atlassian, atlassian, customfieldtypes, atlassian, customfieldtypes, multiselectsearcher, atlassian (+15) | task spell:check |
| 2026-03-08 02:07 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/ROADMAP-DECISIONS.md | Decisoes, decisoes, governanca, sugestoes, Sugestoes, Descricao, Atualizacao, esforco (+283) | task spell:check |
| 2026-03-08 02:07 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | ROADMAP.md | Repositorio, governanca, sugestao, Priorizacao, automatica, decisao, Governanca, Priorizacao (+175) | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/ai_atlassian_backfill_test.py | atlassian | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai_atlassian_backfill_lib.py | Responsavel, atualizacao, Responsavel, Concluido, tecnicas, normalizacao, exibicao, atlassian (+21) | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-python-modular-architecture-research.md | recomendacao, modularizacao, dominios, importaveis, possivel, evolucao, microservicos, monolito (+37) | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/confluence-schema.md | canonica, Sincronizacao, operacao, Operacao, Governanca, publicacao, comentario | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/artifacts/README.md | canonica, sincronizacao, aplicacao, sincronizacao, informacao, publicacao, atlassian, documentacao (+4) | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/README.md | migracao, governanca, usuario, implicita, cutover, proprio, decisoes, tambem (+38) | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/README.md | documentacoes, Operacao, migracao, canonicas, automacao, tecnico, manutencao, Governanca (+19) | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | config/ai/contracts.yaml | descricao, tecnico, criterios, aceitacao, documentacao | task spell:check |
| 2026-03-08 02:00 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | config/ai/agent-operations.yaml | atlassian, decisao, documentacao, linkar, mudanca, atualizacao, necessario, linkar (+92) | task spell:check |
| 2026-03-07 23:02 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | tests/python/ai_jira_model_test.py | atlassian | task spell:check |
| 2026-03-07 23:02 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai-jira-model.py | execucao | task spell:check |
| 2026-03-07 23:02 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | scripts/ai_jira_model_lib.py | atlassian, atlassian, atlassian, atlassian | task spell:check |
| 2026-03-07 23:02 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | config/ai/agents.yaml | figma | task spell:check |
| 2026-03-07 21:35 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-atlassian-product-discovery.md | Decisao, hipoteses, proprio, canonica, executavel, executavel, avaliacao, consolidacao (+20) | task spell:check |
| 2026-03-07 18:19 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-parecer-e-plano-inicial.md | operacao, direcao, documentacao, viavel, migracao, viavel, transicao, LICOES (+122) | task spell:check |
| 2026-03-07 18:19 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-modelo-operacional-completo-figma-seo.md | usuario, rastreavel, atlassian, atlassian, agil, execucao, documentacao, repositorio (+52) | task spell:check |
| 2026-03-07 18:19 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/atlassian-ia/README.md | migracao, governanca, usuario, implicita, cutover, proprio, decisoes, tambem (+11) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-operacao-agentes-jira-confluence.md | Operacao, usuario, agil, operacao, agil, governanca, execucao, documentacao (+47) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-melhores-praticas-mercado.md | Autonomo, usuario, Observacao, usuario, validacao, repositorios, codigo, agil (+38) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/atlassian-ia/2026-03-07-blueprint-ai-product-owner-system.md | usuario, rastreavel, agil, documentacao, sincronizacao, repositorio, tecnico, automatico (+58) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/ai-operating-model.md | reutilizavel, testavel, worktree, Principios, Instrucoes, instrucoes, estaveis, Especializacao (+122) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | docs/README.md | documentacoes, Operacao, migracao, canonicas, automacao, tecnico, manutencao, Governanca (+12) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | LICOES-APRENDIDAS.md | Licoes, Historico, obrigatoria, usuario, LICOES, licao, Criterio, licoes (+232) | task spell:check |
| 2026-03-07 18:16 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | pascoalete | reprovado | .agents/cards/guardiao-rotacao-secrets.md | Guardiao, Rotacao, rotacao, validacao, rotacao, criacao, rotacao, revogacao (+44) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | tests/python/ai_assets_validator_test.py | possivel, LICOES, Validacao, LICOES, Orquestracao, evals, Integracoes, guardiao (+2) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | tests/python/cspell_governance_test.py | Pascoalete, Pascoalete, Pascoalete, Pascoalete, pascoalete, ortograficas, Pascoalete, pascoalete (+1) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/validate_docs.py | LICOES, governanca, validacao, diretorios, disponivel, repoish, repoish, repoish (+3) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/validate-ai-assets.py | execucao, evals, LICOES, evals, evals, evals, evals, autolog (+44) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/cspell_governance_lib.py | Pascoalete, ortografico, worktree, tecnico, mudanca, Pascoalete, rastreavel, dicionarios (+9) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | scripts/cspell-governance.py | execucao, Governanca, ortografica, repositorio, Pascoalete, pascoalete | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/AI-SOURCE-AUDIT.md | governanca, catalogos, taskfiles, orquestracao, evals, relacoes, governanca, Repositorios (+160) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/WORKFLOWS.md | licoes, governanca, catalogos, integracao, unitaria, canonico, pytest, Observacao (+6) | task spell:check |
| 2026-03-07 16:37 UTC | WIP-20260307-SECRETS-ROTATION | pascoalete | reprovado | docs/TASKS.md | canonicas, repositorio, operacao, diaria, governanca, Operacao, diaria, sincronizacao (+68) | task spell:check |
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
