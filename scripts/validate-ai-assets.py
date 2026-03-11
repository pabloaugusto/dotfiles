#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import cast

import yaml

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_contract_paths import (
    cards_root,
    config_path,
    evals_root,
    legacy_codex_readme,
    legacy_codex_root,
    orchestration_root,
    registry_root,
    rules_root,
    skills_root,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for Python < 3.11
    tomllib = None  # type: ignore[assignment]


REQUIRED_FILES = [
    "AGENTS.md",
    "LICOES-APRENDIDAS.md",
    "docs/AI-AGENTS-CATALOG.md",
    "docs/AI-CHAT-CONTRACTS-REGISTER.md",
    "docs/AI-DELEGATION-FLOW.md",
    "docs/AI-FALLBACK-LEDGER.md",
    "docs/AI-FALLBACK-OPERATIONS.md",
    "docs/AI-GOVERNANCE-AND-REGRESSION.md",
    "docs/AI-ORTHOGRAPHY-LEDGER.md",
    "docs/AI-REVIEW-LEDGER.md",
    "docs/AI-SCRUM-MASTER-LEDGER.md",
    "docs/AI-SKILLS-CATALOG.md",
    "docs/AI-STARTUP-AND-RESTART.md",
    "docs/AI-STARTUP-GOVERNANCE-MANIFEST.md",
    "docs/AI-SOURCE-AUDIT.md",
    "docs/ai-operating-model.md",
    "docs/ai-sync-foundation.md",
    "docs/secrets-and-auth.md",
    "docs/AI-WIP-TRACKER.md",
    "ROADMAP.md",
    "docs/ROADMAP-DECISIONS.md",
    "docs/TASKS.md",
    "docs/WORKFLOWS.md",
    "config/ai/platforms.yaml",
    "config/ai/platforms.local.yaml.tpl",
    "config/ai/agents.yaml",
    "config/ai/agent-operations.yaml",
    "config/ai/contracts.yaml",
    "config/ai/sync-targets.yaml",
    "df/secrets/secrets-ref.yaml",
    ".agents/README.md",
    ".agents/prompts/README.md",
    ".agents/prompts/CATALOG.md",
    ".agents/prompts/formal/startup-alignment/prompt.md",
    ".agents/prompts/formal/startup-alignment/context.md",
    ".agents/prompts/formal/startup-alignment/meta.yaml",
    ".agents/prompts/formal/startup-alignment/fragments/modes.md",
    ".agents/prompts/formal/startup-alignment/fragments/bypass.md",
    ".agents/prompts/formal/startup-alignment/fragments/startup-extension.md",
    ".agents/prompts/formal/sync-outbox-foundation/prompt.md",
    ".agents/prompts/formal/sync-outbox-foundation/context.md",
    ".agents/prompts/formal/sync-outbox-foundation/meta.yaml",
    ".agents/prompts/formal/sync-outbox-foundation/fragments/identity-model.md",
    ".agents/prompts/formal/sync-outbox-foundation/fragments/sync-contract.md",
    ".agents/prompts/formal/sync-outbox-foundation/fragments/artifact-classification.md",
    ".agents/prompts/formal/documentation-layer-governance/prompt.md",
    ".agents/prompts/formal/documentation-layer-governance/context.md",
    ".agents/prompts/formal/documentation-layer-governance/meta.yaml",
    ".agents/prompts/formal/documentation-layer-governance/fragments/composition.md",
    ".agents/config.toml",
    ".agents/cerimonias/README.md",
    ".agents/cerimonias/ceremony.schema.json",
    ".agents/cerimonias/retrospectiva.yaml",
    ".agents/cerimonias/logs/retrospectiva-template.md",
    ".agents/cerimonias/logs/retrospectiva/README.md",
    ".codex/README.md",
    ".agents/orchestration/capability-matrix.yaml",
    ".agents/orchestration/routing-policy.yaml",
    ".agents/orchestration/task-card.schema.json",
    ".agents/orchestration/delegation-plan.schema.json",
    ".agents/rules/default.rules",
    ".agents/rules/ci.rules",
    ".agents/rules/security.rules",
    ".agents/evals/scenarios/smoke.md",
    ".agents/evals/scenarios/regression.md",
    ".agents/evals/scenarios/security.md",
    ".agents/evals/datasets/routing.jsonl",
    ".agents/evals/datasets/governance.jsonl",
    "scripts/ai-lessons.py",
    "scripts/ai_lessons_lib.py",
    "scripts/ai-worklog.py",
    "scripts/ai-chat-intake.py",
    "scripts/ai-route.py",
    "scripts/ai-delegate.py",
    "scripts/ai-eval-smoke.py",
    "scripts/ai-review.py",
    "scripts/ai_review_lib.py",
    "scripts/ai-control-plane.py",
    "scripts/ai-fallback.py",
    "scripts/ai-session-startup.py",
    "scripts/ai_control_plane_lib.py",
    "scripts/ai_sync_foundation_lib.py",
    "scripts/ai_fallback_governance_lib.py",
    "scripts/ai_session_startup_lib.py",
    "scripts/atlassian_platform_lib.py",
    "scripts/git-governance-check.py",
    "scripts/run-ai-atlassian-check.ps1",
    "scripts/run-ai-startup-session.ps1",
    "scripts/cspell-governance.py",
    "scripts/cspell_governance_lib.py",
    "scripts/ai-prompt-governance.py",
    "scripts/validate_workflow_task_sync.py",
    "scripts/validate-ai-assets.ps1",
]

TRACKER_MARKERS = [
    "<!-- ai-worklog:doing:start -->",
    "<!-- ai-worklog:doing:end -->",
    "<!-- ai-worklog:done:start -->",
    "<!-- ai-worklog:done:end -->",
    "<!-- ai-worklog:log:start -->",
    "<!-- ai-worklog:log:end -->",
]

CHAT_CONTRACTS_MARKERS = [
    "<!-- ai-chat-contracts:pending:start -->",
    "<!-- ai-chat-contracts:pending:end -->",
    "<!-- ai-chat-contracts:promoted:start -->",
    "<!-- ai-chat-contracts:promoted:end -->",
]

DECISIONS_MARKERS = [
    "<!-- roadmap:suggestions:start -->",
    "<!-- roadmap:suggestions:end -->",
    "<!-- roadmap:cycles:start -->",
    "<!-- roadmap:cycles:end -->",
    "<!-- roadmap:autolog:start -->",
    "<!-- roadmap:autolog:end -->",
]

ROADMAP_MARKERS = [
    "<!-- roadmap:backlog:start -->",
    "<!-- roadmap:backlog:end -->",
    "<!-- roadmap:priority:start -->",
    "<!-- roadmap:priority:end -->",
    "<!-- roadmap:now:start -->",
    "<!-- roadmap:now:end -->",
    "<!-- roadmap:next:start -->",
    "<!-- roadmap:next:end -->",
    "<!-- roadmap:later:start -->",
    "<!-- roadmap:later:end -->",
    "<!-- roadmap:pending:start -->",
    "<!-- roadmap:pending:end -->",
]

LESSONS_MARKERS = [
    "<!-- ai-lessons:catalog:start -->",
    "<!-- ai-lessons:catalog:end -->",
    "<!-- ai-lessons:reviews:start -->",
    "<!-- ai-lessons:reviews:end -->",
]

SCRUM_MASTER_MARKERS = [
    "<!-- ai-scrum-master:inconformities:start -->",
    "<!-- ai-scrum-master:inconformities:end -->",
    "<!-- ai-scrum-master:ceremonies:start -->",
    "<!-- ai-scrum-master:ceremonies:end -->",
]

FALLBACK_LEDGER_MARKERS = [
    "<!-- ai-fallback:active:start -->",
    "<!-- ai-fallback:active:end -->",
    "<!-- ai-fallback:resolved:start -->",
    "<!-- ai-fallback:resolved:end -->",
]

REQUIRED_AGENT_HEADINGS = [
    "## Objetivo",
    "## Quando usar",
    "## Skill principal",
    "## Entradas",
    "## Saidas",
    "## Fluxo",
    "## Guardrails",
    "## Validacao recomendada",
    "## Criterios de conclusao",
]

REQUIRED_SKILL_HEADINGS = [
    "## Objetivo",
    "## Fluxo",
    "## Regras",
    "## Entregas esperadas",
    "## Validacao",
    "## Referencias",
]

AGENTS_REQUIRED_SNIPPETS = [
    "Nunca operar por amostragem",
    "docs/AI-SOURCE-AUDIT.md",
    "docs/AI-STARTUP-GOVERNANCE-MANIFEST.md",
    "docs/AI-CHAT-CONTRACTS-REGISTER.md",
    "docs/AI-FALLBACK-LEDGER.md",
    "`Jira` e a fonte primaria do fluxo vivo",
    "Antes de criar qualquer demanda que nao seja `Epic`, verificar se ja existe `Epic` aberto aderente ao macro tema",
    "concluir_primeiro passa a significar concluir ou puxar apenas o work item minimo que o destrava diretamente",
    "carregar o contrato de comunicacao no chat e",
    "governanca Git canonica do",
    "nenhuma delegacao para subagente e valida sem issue dona",
    "**REJEITADO**",
    "Manter o item ativo em `Doing` durante toda a execucao relevante",
    "Nenhum `done` e valido sem revisar `LICOES-APRENDIDAS.md`",
    "Acionar os gates paralelos obrigatorios de arquitetura/modernizacao",
    "Quando a rodada tocar [`.agents/prompts/`](.agents/prompts/), o namespace",
    "titulo com prefixo",
    "label `prompt`",
]

OPERATING_MODEL_REQUIRED_SNIPPETS = [
    "### 1.1. Retomada do zero exige releitura integral de governanca",
    "### 1.2. Contratos nascidos no chat precisam de registrador vivo",
    "### 3.1. Terminar antes de comecar inclui destravar o WIP ativo",
    "### 3.3. Intake nao pode duplicar issue nem Epic",
    "### 4.4. Higiene Git obrigatoria e rastreabilidade Jira",
    "### 4.5. Fallback local exige modo explicito e reconciliacao dirigida",
    "### 5. Auditoria exaustiva antes de reuso cross-repo",
    "### Fronteira entre `.agents/` e adaptadores de assistente",
    "### Camada 2.1. Registry declarativo do repo",
    "### Camada 2.2. Orquestracao, rules e evals",
    "cadeia minima de evidencia para cada execucao obrigatoria",
    "task_id: prompt/<slug>",
    "PROMPT: ...",
    "label `prompt`",
    "## Politica de leitura do board",
    "## Camada de identidade humana dos agentes",
]

LESSONS_REQUIRED_SNIPPETS = [
    "## LA-001 - Auditoria exaustiva antes de importacao cross-repo",
    "## LA-004 - Toda finalizacao de worklog exige revisao explicita de licoes",
    "## LA-006 - Arquitetura e modernizacao precisam de um gate paralelo permanente",
    "## LA-007 - Integracoes criticas exigem guardiao proprio",
]

SOURCE_AUDIT_REQUIRED_SNIPPETS = [
    "## Escopo da auditoria",
    "## Repositorios auditados",
    "## Inventario consolidado por dominio",
    "## Gaps no repo atual",
    "## Decisoes de importacao",
    "## Fronteira entre",
    "## Regra operacional permanente",
]

STARTUP_AND_RESTART_REQUIRED_SNIPPETS = [
    "task ai:worklog:check",
    "fallback local, nunca como substituto do quadro vivo do Jira",
    "task ai:fallback:status",
    "task ai:fallback:capture",
    "task ai:fallback:resolve",
    "Jira como fonte primaria do backlog",
    "gh auth status",
    "probe GraphQL",
    "task ai:atlassian:check",
    "Cadeia de fallback GitHub/PAT",
    "display_name",
    "pea_status",
    ".agents/prompts/CATALOG.md",
    "docs/git-conventions.md",
    "subagentes",
    "REJEITADO",
]

STARTUP_GOVERNANCE_REQUIRED_SNIPPETS = {
    "config/ai/contracts.yaml": [
        "load-chat-communication-contract-before-first-user-facing-message",
        "load-display-name-layer-before-chat-jira-or-confluence-visible-communication",
        "load-git-governance-contracts-before-changing-worktree-state",
        "validate-gh-auth-and-graphql-before-github-pr-or-merge-operations",
        "remember-and-apply-the-documented-github-pat-fallback-chain",
        "snapshot-current-branch-worktree-and-open-pr-state-at-startup",
        "capture-current-branch-lifecycle-upstream-and-main-absorption-state",
        "detect-drift-between-active-execution-worklog-branch-and-dirty-tree",
        "capture-minimum-operational-health-of-jira-and-confluence-at-startup",
        "remember-atlassian-auth-mode-cloud-id-and-recovery-path",
        "no-subagent-delegation-before-startup-context-is-loaded-and-scoped",
        "subagent-context-pack-must-carry-owner-issue-startup-artifacts-and-applicable-rules",
        "startup-must-load-prompts-catalog-and-applicable-formal-pea-pack",
        "startup-report-must-expose-pea-status",
        "subagent-context-pack-must-carry-pea-classification-when-applicable",
        "work-started-without-full-startup-context-is-rejectable",
    ],
    "docs/TASKS.md": [
        "contrato de comunicacao com o",
        "`display_name`",
        "governanca Git canonica",
        "enforcement de commit atomico",
        "probe GraphQL",
        "fallback GitHub/PAT",
        "pea_status",
        "PRs` abertos para a branch atual",
        "subagentes",
    ],
    "docs/ai-operating-model.md": [
        "carregar o contrato de comunicacao com o usuario",
        "camada de `display_name`",
        "governanca Git canonica da sessao",
        "enforcement de commit atomico",
        "validar `gh auth status`",
        "probe GraphQL cedo",
        "cadeia documentada de fallback GitHub/PAT",
        "Pre-Execution Alignment reduz drift antes da execucao",
        "saude minima de `Jira` e `Confluence`",
        "pacote minimo de contexto antes de delegar para subagentes",
        "rejeitavel ate a remediacao do contexto",
    ],
    "config/ai/agent-operations.yaml": [
        "zero-context-startup-must-load-chat-contract-before-first-user-message",
        "no-subagent-delegation-before-startup-context-is-loaded-or-linked",
        "subagent-handoff-must-carry-owner-issue-startup-context-and-applicable-rules",
        "subagent-handoff-must-carry-pea-classification-when-applicable",
        "work-executed-without-required-startup-context-is-rejectable",
    ],
    "docs/AI-STARTUP-GOVERNANCE-MANIFEST.md": [
        "### Secrets, auth e runtime operacional",
        "df/secrets/secrets-ref.yaml",
        "### Prompt packs formais e contexto executavel",
        ".agents/prompts/CATALOG.md",
    ],
    "docs/AI-DELEGATION-FLOW.md": [
        "startup report",
        "pacote minimo de contexto",
        "subagente",
        "classificacao do `PEA`",
    ],
}

PROMPT_PACK_REQUIRED_SNIPPETS = {
    ".agents/prompts/README.md": [
        "## Estrutura canonica",
        "legacy/",
        "formal/",
        "prompt.md",
        "context.md",
        "meta.yaml",
        "fragments/",
        "task_id",
        "prompt/<slug>",
        "dependencies",
        "prerequisite_packs",
        "preflight_packs",
        'summary_prefix: "PROMPT:"',
        "required_labels",
        "`scope` obrigatorio `prompt`",
    ],
    ".agents/prompts/CATALOG.md": [
        "## Formais",
        "prompt/startup-alignment",
        "prompt/sync-outbox-foundation",
        "prompt/documentation-layer-governance",
        "checar `startup-alignment`",
        "validar `sync-outbox-foundation` antes",
        "## Legados",
        "DOT-178",
        "DOT-179",
    ],
    ".agents/prompts/formal/startup-alignment/prompt.md": [
        "Pre-Execution Alignment",
        "startup/restart",
        "enforcement",
        "pea_status",
        "fast_lane",
        "aguardando_confirmacao_humana",
    ],
    ".agents/prompts/formal/startup-alignment/context.md": [
        "Jira",
        "DOT-71",
        "DOT-178",
        "pea_status",
        "Dependencias e ordem segura",
    ],
    ".agents/prompts/formal/startup-alignment/meta.yaml": [
        "id: startup-alignment",
        "task_id: prompt/startup-alignment",
        "owner_issue: DOT-178",
        'summary_prefix: "PROMPT:"',
        "required_labels:",
        "report_key: pea_status",
        "dependencies:",
        "prerequisite_packs: []",
        "preflight_packs: []",
    ],
    ".agents/prompts/formal/sync-outbox-foundation/meta.yaml": [
        "id: sync-outbox-foundation",
        "task_id: prompt/sync-outbox-foundation",
        "owner_issue: DOT-179",
        'summary_prefix: "PROMPT:"',
        "required_labels:",
        "state_root: ~/.ai-control-plane",
        "dependencies:",
        "preflight_packs:",
        "- startup-alignment",
    ],
    ".agents/prompts/formal/documentation-layer-governance/meta.yaml": [
        "id: documentation-layer-governance",
        "task_id: prompt/documentation-layer-governance",
        'summary_prefix: "PROMPT:"',
        "required_labels:",
        "dependencies:",
        "prerequisite_packs:",
        "- sync-outbox-foundation",
        "preflight_packs:",
        "- startup-alignment",
    ],
    ".agents/prompts/formal/documentation-layer-governance/context.md": [
        "Dependencias e ordem segura",
        "startup-alignment",
        "sync-outbox-foundation",
        "nao redefine `workspace_id`",
    ],
    ".agents/prompts/formal/documentation-layer-governance/prompt.md": [
        "DEPENDENCIAS DE PACKS E ORDEM SEGURA DE EXECUCAO",
        "ai-documentation-sync",
        "documentation-layer-governance",
        "Curador Repo",
    ],
}

SYNC_FOUNDATION_REQUIRED_SNIPPETS = {
    "docs/ai-sync-foundation.md": [
        "# AI Sync Foundation",
        "repo declarativo -> outbox local duravel -> fonte perene remota",
        "workspace_id",
        "runtime_environment_id",
        "~/.ai-control-plane/workspaces/<workspace_id>/",
        "config/ai/sync-targets.yaml",
        "ack",
        "dead-letter",
        "runtime ledger candidate",
        "documentation-layer-governance",
    ],
    "docs/TASKS.md": [
        "### `ai:control-plane:sync:check`",
        "### `ai:control-plane:sync:status`",
        "### `ai:control-plane:sync:drain`",
        "docs/ai-sync-foundation.md",
    ],
    "docs/README.md": [
        "config/ai/sync-targets.yaml",
        "docs/ai-sync-foundation.md",
    ],
    "config/ai/contracts.yaml": [
        "sync_foundation:",
        "manifest: config/ai/sync-targets.yaml",
        "no-domain-may-create-a-parallel-outbox-contract",
    ],
}

CEREMONY_REQUIRED_SNIPPETS = {
    ".agents/cerimonias/README.md": [
        "ceremony.schema.json",
        "retrospectiva.yaml",
        "Toda execucao real de **cerimonia** deve gerar log Markdown proprio.",
        "Toda branch finalizada que exigir **Retrospectiva** precisa gerar log",
    ],
    ".agents/cerimonias/retrospectiva.yaml": [
        "id: retrospectiva",
        "title: Retrospectiva",
        "mode: every-branch-finished",
        "- plano_de_acao",
        "- responsavel",
        "- proximo_passo",
        "ledger_entry_required: true",
        "confluence_page_required: true",
        "jira_bug_required_when_unresolved: true",
        "- cerimonia",
        "- retrospectiva",
        "title_template: Retrospectiva - {yyyy-MM-dd HH:mm}",
    ],
    ".agents/cerimonias/logs/retrospectiva-template.md": [
        "# Retrospectiva - {{data_hora_utc}} - {{branch}}",
        "## Problemas catalogados",
        "Entrada no ledger",
        "Plano de acao: {{plano_de_acao}}",
        "## Encaminhamento",
    ],
}

AGENT_IDENTITY_REQUIRED_SNIPPETS = {
    ".agents/config.toml": [
        "[identity]",
        'display_name_field = "display_name"',
        'fallback_display = "technical-id"',
    ],
    "config/ai/contracts.yaml": [
        "agent_identity:",
        "source_of_truth: .agents/registry/*.toml::display_name",
        "startup-and-restart-must-load-display-name-layer",
        "jira-must-prefer-display-name-when-surface-allows",
    ],
    "config/ai/agents.yaml": [
        "display_name: PO",
        "display_name: Scrum Master",
        "display_name: Engenheiro Agentes IA",
    ],
    "docs/AI-AGENTS-CATALOG.md": [
        "| PO |",
        "| Scrum Master |",
        "| Engenheiro Agentes IA |",
        "| Escrivão |",
    ],
    ".agents/cards/ai-developer-config-policy.md": [
        "# Engenheiro Agentes IA",
    ],
    ".agents/registry/ai-product-owner.toml": [
        'display_name = "PO"',
    ],
    ".agents/registry/ai-scrum-master.toml": [
        'display_name = "Scrum Master"',
    ],
    ".agents/registry/ai-developer-config-policy.toml": [
        'display_name = "Engenheiro Agentes IA"',
    ],
    ".agents/registry/pascoalete.toml": [
        'display_name = "Pascoalete"',
    ],
}

BOARD_OPERATION_REQUIRED_SNIPPETS = {
    "config/ai/contracts.yaml": [
        "board-must-be-read-right-to-left",
        "finish-before-start-is-mandatory",
        "reading_order: right-to-left",
        "pull_strategy: finish-before-start",
        "delegate-idle-agents-to-finishable-work",
        "verify-existing-open-issue-before-any-new-issue",
        "verify-existing-open-epic-before-any-non-epic-demand",
        "verify-existing-open-epic-before-any-new-epic-for-the-same-theme",
    ],
    "config/ai/jira-model.yaml": [
        "reading_order: right-to-left",
        "dispatch_owner_role: ai-scrum-master",
        "idle_agent_policy: assign-rightmost-finishable-item-first",
        "verify-existing-open-issue-before-creating-any-new-issue",
        "verify-existing-open-epic-before-creating-any-non-epic-demand",
        "new-epic-creation-requires-proof-of-no-open-epic-match",
    ],
    "config/ai/agent-operations.yaml": [
        "ler o board da direita para a esquerda",
        "priorizar agentes ociosos para o item mais a direita com avanco real possivel",
        "tentar fazer a equipe comecar a terminar antes de autorizar nova puxada",
        "verificar se a demanda ja nao existe antes de criar issue",
        "assegurar que nao existe epic aberto cobrindo o tema antes de criar novo epic",
        "auditar se toda criacao de issue ou epic passou pelo preflight de deduplicacao e reuse de epic",
        "branch-closure-must-trigger-required-ceremony-chain",
        "required-ceremony-chain-must-produce-log-ledger-confluence-and-jira-when-applicable",
    ],
    ".agents/cards/ai-product-owner.md": [
        "verificar se a issue ja existe",
        "Reusar o `Epic` aberto correto",
        "sem resposta por 3 minutos",
    ],
    ".agents/cards/ai-scrum-master.md": [
        "Ler o **board** da direita para a esquerda",
        "**comecar a terminar**",
        "agente ocioso puxar trabalho novo",
        "preflight de deduplicacao",
        "issue ou `Epic` criado sem preflight",
    ],
    ".agents/cards/ai-engineering-manager.md": [
        "agentes ociosos ajudem a mover o item",
        "da direita para a esquerda",
        "Nao deixar agente ocioso puxar trabalho novo",
    ],
}

GIT_GOVERNANCE_REQUIRED_SNIPPETS = {
    "docs/git-conventions.md": [
        "<type>/<jira-key>-<slug>",
        "scope` passa a ser obrigatorio e deve ser `prompt`",
        "titulo `PROMPT: ...` com label `prompt`",
        "cada commit deve representar uma unica **issue** Jira real",
        "quando possivel, cada commit deve ser auto-testavel",
        "retomada nova deve nascer de `main` no padrao canonico",
        "`task git:governance:check`",
    ],
    "docs/README.md": [
        "fallback contingencial local; o `Jira` e a fonte primaria do fluxo vivo.",
        "AI-FALLBACK-OPERATIONS.md",
        "AI-FALLBACK-LEDGER.md",
    ],
    "scripts/ai-worklog.py": [
        "Fallback local de continuidade. O Jira e a fonte primaria do fluxo vivo.",
        "docs/AI-FALLBACK-LEDGER.md",
        "Commit de fechamento obrigatorio antes de nova rodada",
    ],
    "config/ai/agent-operations.yaml": [
        "versioned-prompt-pack-work-must-declare-task-id-as-prompt-slug",
        "versioned-prompt-pack-work-must-use-prompt-branch-type",
        "versioned-prompt-pack-work-must-use-prompt-scope-in-commit-and-pr-title",
        "versioned-prompt-pack-owner-issues-must-use-prompt-summary-prefix",
        "versioned-prompt-pack-owner-issues-must-carry-prompt-label",
    ],
    "config/ai/contracts.yaml": [
        "git_governance:",
        "source_of_truth: jira",
        "fallback_operation:",
        "recovery_ledger: docs/AI-FALLBACK-LEDGER.md",
        "branch_pattern: <type>/<jira-key>-<slug>",
        "branch_pattern: prompt/<jira-key>-<slug>",
        "task_id_pattern: prompt/<slug>",
        'jira_summary_prefix: "PROMPT:"',
        "jira_required_labels:",
        "changes-touching-agents-prompts-must-use-prompt-branch-type",
        "changes-touching-agents-prompts-must-use-prompt-scope-in-commit-title",
        "changes-touching-agents-prompts-must-use-prompt-scope-in-pr-title",
        "prompt-related-jira-issues-must-use-summary-prefix-prompt",
        "prompt-related-jira-issues-must-carry-prompt-label",
        "commits-must-be-atomic-contextualized-and-preferably-self-testable",
        "resume-old-work-on-a-new-branch-from-main-unless-evidence-keeps-the-existing-branch-valid",
        "prune-unneeded-local-branches-and-worktrees-after-merge",
        "fail-when-local-merged-branches-or-worktrees-remain-without-purpose",
    ],
}

CATALOG_REQUIRED_SNIPPETS = {
    "docs/AI-AGENTS-CATALOG.md": [
        "architecture-modernization-authority",
        "critical-integrations-guardian",
        "lessons-governance-curator",
        "pascoalete",
        "python-reviewer",
        "powershell-reviewer",
        "automation-reviewer",
        "ai-scrum-master",
    ],
    "docs/AI-SKILLS-CATALOG.md": [
        "$dotfiles-architecture-modernization",
        "$dotfiles-critical-integrations",
        "$dotfiles-lessons-governance",
        "$dotfiles-orthography-review",
        "$task-routing-and-decomposition",
        "$dotfiles-python-review",
        "$dotfiles-powershell-review",
        "$dotfiles-automation-review",
    ],
    "docs/AI-DELEGATION-FLOW.md": [
        "architecture-modernization-authority",
        "critical-integrations-guardian",
        "lessons-governance-curator",
        "pascoalete",
        "orchestrator",
        "python-reviewer",
        "powershell-reviewer",
        "automation-reviewer",
        "ai-scrum-master",
    ],
    "docs/AI-GOVERNANCE-AND-REGRESSION.md": [
        "task ai:lessons:check",
        "task ai:review:check",
        "task spell:review",
        "architecture-modernization-authority",
        "ai-scrum-master",
        "critical-integrations-guardian",
        "task ai:eval:smoke",
        "task ci:workflow:sync:check",
        "pascoalete",
        "python-reviewer",
        "powershell-reviewer",
        "automation-reviewer",
    ],
    "docs/TASKS.md": [
        "### `ai:fallback:status`",
        "### `ai:fallback:capture`",
        "### `ai:fallback:resolve`",
        "### `git:governance:check`",
        "### `ai:chat:intake`",
        "### `ai:route`",
        "### `ai:delegate`",
        "### `ai:review:record`",
        "### `ai:review:check`",
        "### `ai:control-plane:show`",
        "### `ai:startup:session`",
        "### `ai:atlassian:check`",
        "### `ai:prompts:jira:check`",
        "### `ai:prompts:jira:sync`",
        "### `spell:review:windows`",
        "### `spell:dictionary:audit:windows`",
        "### `ci:workflow:sync:check`",
    ],
    "docs/WORKFLOWS.md": [
        "### `ai-governance.yml`",
        "### `bootstrap-integration.yml`",
        "### `pr-validate.yml`",
        "spell:review",
    ],
}

REQUIRED_REGISTRY_AGENT_KEYS = [
    "id",
    "tier",
    "purpose",
    "default_skills",
    "triggers",
    "output_contract",
    "handoff_to",
]

REQUIRED_AI_CONFIG_SECTIONS = [
    "skills",
    "agents",
    "orchestration",
    "rules",
    "evals",
    "ceremonies",
    "identity",
]


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
    if not match:
        return None
    return match.group(1).strip().strip("'\"")


def normalize_contract_text(value: str) -> str:
    normalized = value or ""
    normalized = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", normalized)
    normalized = normalized.replace("`", "")
    return " ".join(normalized.split())


def require_markers(content: str, markers: list[str], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in content:
            failures.append(f"Marcador obrigatorio ausente em {label}: {marker}")


def require_snippets(content: str, snippets: list[str], label: str, failures: list[str]) -> None:
    normalized_content = normalize_contract_text(content)
    for snippet in snippets:
        if normalize_contract_text(snippet) not in normalized_content:
            failures.append(f"Trecho obrigatorio ausente em {label}: {snippet}")


def validate_skill_dir(skill_dir: Path, failures: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    agent_yaml = skill_dir / "agents" / "openai.yaml"
    references_dir = skill_dir / "references"

    if not skill_md.is_file():
        failures.append(f"SKILL.md ausente em {skill_dir.name}")
        return
    if not agent_yaml.is_file():
        failures.append(f"agents/openai.yaml ausente em {skill_dir.name}")
    if not references_dir.is_dir():
        failures.append(f"references/ ausente em {skill_dir.name}")

    skill_content = skill_md.read_text(encoding="utf-8")
    if "TODO" in skill_content:
        failures.append(f"Placeholder TODO encontrado em {skill_dir.name}/SKILL.md")

    frontmatter_match = re.match(r"(?s)\A---\r?\n(?P<front>.*?)\r?\n---", skill_content)
    if not frontmatter_match:
        failures.append(f"Frontmatter invalido em {skill_dir.name}/SKILL.md")
        return

    frontmatter = frontmatter_match.group("front")
    skill_name = frontmatter_value(frontmatter, "name")
    description = frontmatter_value(frontmatter, "description")

    if not skill_name:
        failures.append(f"name ausente em {skill_dir.name}/SKILL.md")
    elif skill_name != skill_dir.name:
        failures.append(f"name '{skill_name}' difere da pasta '{skill_dir.name}'")
    elif not re.match(r"^[a-z0-9-]+$", skill_name):
        failures.append(f"name invalido em {skill_dir.name}/SKILL.md")

    if not description:
        failures.append(f"description ausente em {skill_dir.name}/SKILL.md")

    for heading in REQUIRED_SKILL_HEADINGS:
        if heading not in skill_content:
            failures.append(f"Heading obrigatorio ausente em {skill_dir.name}/SKILL.md: {heading}")

    if agent_yaml.is_file():
        agent_content = agent_yaml.read_text(encoding="utf-8")
        if not re.search(r"(?m)^interface:\s*$", agent_content):
            failures.append(f"interface ausente em {skill_dir.name}/agents/openai.yaml")
        expected_skill_ref = f"${skill_dir.name}"
        default_prompt_re = rf'(?m)^\s*default_prompt:\s*".*{re.escape(expected_skill_ref)}.*"\s*$'
        if not re.search(default_prompt_re, agent_content):
            failures.append(
                f"default_prompt precisa mencionar {expected_skill_ref} em {skill_dir.name}/agents/openai.yaml"
            )
        short_match = re.search(r'(?m)^\s*short_description:\s*"(?P<value>.+)"\s*$', agent_content)
        if not short_match:
            failures.append(f"short_description ausente em {skill_dir.name}/agents/openai.yaml")
        else:
            short_len = len(short_match.group("value"))
            if short_len < 25 or short_len > 64:
                failures.append(
                    f"short_description fora do intervalo 25-64 em {skill_dir.name}/agents/openai.yaml"
                )


def validate_registry_agent(agent_file: Path, skill_names: set[str], failures: list[str]) -> None:
    try:
        payload = parse_toml_text(agent_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        failures.append(f"TOML invalido em {agent_file.as_posix()}: {exc}")
        return
    for key in REQUIRED_REGISTRY_AGENT_KEYS:
        if key not in payload:
            failures.append(f"Chave obrigatoria ausente em {agent_file.as_posix()}: {key}")
    for list_key in ("default_skills", "triggers", "handoff_to"):
        value = payload.get(list_key)
        if value is not None and not isinstance(value, list):
            failures.append(f"{list_key} deve ser lista em {agent_file.as_posix()}")
    default_skills = payload.get("default_skills", [])
    if isinstance(default_skills, list):
        for skill_name in default_skills:
            if isinstance(skill_name, str) and skill_name not in skill_names:
                failures.append(
                    f"default_skill inexistente em {agent_file.as_posix()}: {skill_name}"
                )


def validate_ai_config(repo_root: Path, failures: list[str]) -> None:
    config_file = config_path(repo_root)
    try:
        payload = parse_toml_text(config_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        failures.append(f"TOML invalido em .agents/config.toml: {exc}")
        return
    for section in REQUIRED_AI_CONFIG_SECTIONS:
        if section not in payload:
            failures.append(f"Secao obrigatoria ausente em .agents/config.toml: [{section}]")
    for section_name in ("orchestration", "rules", "evals"):
        section = payload.get(section_name, {})
        if not isinstance(section, dict):
            continue
        for value in section.values():
            if isinstance(value, str) and not (repo_root / value).exists():
                failures.append(f"Referencia ausente em .agents/config.toml: {value}")
    skills_section = payload.get("skills", {})
    if isinstance(skills_section, dict):
        for skill_name in string_list_setting(skills_section, "required"):
            if (
                isinstance(skill_name, str)
                and not (skills_root(repo_root) / skill_name / "SKILL.md").exists()
            ):
                failures.append(f"Skill requerida ausente em .agents/config.toml: {skill_name}")
        for skill_name in string_list_setting(skills_section, "mandatory_parallel"):
            if (
                isinstance(skill_name, str)
                and not (skills_root(repo_root) / skill_name / "SKILL.md").exists()
            ):
                failures.append(
                    f"Skill de gate paralelo ausente em .agents/config.toml: {skill_name}"
                )
    agents_section = payload.get("agents", {})
    if isinstance(agents_section, dict):
        for agent_name in string_list_setting(agents_section, "required"):
            if (
                isinstance(agent_name, str)
                and not (registry_root(repo_root) / f"{agent_name}.toml").exists()
            ):
                failures.append(f"Agente requerido ausente em .agents/config.toml: {agent_name}")
        for agent_name in string_list_setting(agents_section, "mandatory_global"):
            if (
                isinstance(agent_name, str)
                and not (registry_root(repo_root) / f"{agent_name}.toml").exists()
            ):
                failures.append(
                    f"Agente mandatory_global ausente em .agents/config.toml: {agent_name}"
                )
        for agent_name in string_list_setting(agents_section, "mandatory_platform"):
            if (
                isinstance(agent_name, str)
                and not (registry_root(repo_root) / f"{agent_name}.toml").exists()
            ):
                failures.append(
                    f"Agente mandatory_platform ausente em .agents/config.toml: {agent_name}"
                )


def validate_prompt_packs(repo_root: Path, failures: list[str]) -> None:
    prompts_root = repo_root / ".agents" / "prompts"
    legacy_root = prompts_root / "legacy"
    formal_root = prompts_root / "formal"

    if not prompts_root.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/prompts")
        return
    if not legacy_root.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/prompts/legacy")
    if not formal_root.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/prompts/formal")
        return

    formal_packs = sorted(
        [item for item in formal_root.iterdir() if item.is_dir()],
        key=lambda item: item.name,
    )
    formal_pack_names = {item.name for item in formal_packs}
    if not formal_packs:
        failures.append("Nenhum prompt pack formal encontrado em .agents/prompts/formal")

    for pack_root in formal_packs:
        for file_name in ("prompt.md", "context.md", "meta.yaml"):
            if not (pack_root / file_name).is_file():
                failures.append(
                    f"Arquivo obrigatorio ausente em .agents/prompts/formal/{pack_root.name}: {file_name}"
                )
        fragments_root = pack_root / "fragments"
        if not fragments_root.is_dir():
            failures.append(
                f"Pasta obrigatoria ausente: .agents/prompts/formal/{pack_root.name}/fragments"
            )

        meta_path = pack_root / "meta.yaml"
        if meta_path.is_file():
            meta_content = meta_path.read_text(encoding="utf-8")
            meta_payload = yaml.safe_load(meta_content) or {}
            if not isinstance(meta_payload, dict):
                failures.append(f"meta.yaml invalido em {meta_path.as_posix()}")
                continue
            id_match = re.search(r"(?m)^id:\s*(?P<value>[a-z0-9-]+)\s*$", meta_content)
            if not id_match:
                failures.append(f"id ausente ou invalido em {meta_path.as_posix()}")
            elif id_match.group("value") != pack_root.name:
                failures.append(
                    f"id em {meta_path.as_posix()} deve ser igual ao slug da pasta ({pack_root.name})"
                )
            task_match = re.search(
                r"(?m)^task_id:\s*(?P<value>prompt/[a-z0-9-]+)\s*$", meta_content
            )
            expected_task_id = f"prompt/{pack_root.name}"
            if not task_match:
                failures.append(f"task_id ausente ou invalido em {meta_path.as_posix()}")
            elif task_match.group("value") != expected_task_id:
                failures.append(f"task_id em {meta_path.as_posix()} deve ser {expected_task_id}")
            dependencies_payload = meta_payload.get("dependencies")
            if not isinstance(dependencies_payload, dict):
                failures.append(f"bloco dependencies obrigatorio ausente em {meta_path.as_posix()}")
            else:
                for field_name in ("prerequisite_packs", "preflight_packs"):
                    field_value = dependencies_payload.get(field_name)
                    if not isinstance(field_value, list):
                        failures.append(
                            f"dependencies.{field_name} em {meta_path.as_posix()} deve ser lista"
                        )
                        continue
                    for pack_name in field_value:
                        if not isinstance(pack_name, str) or not re.fullmatch(
                            r"[a-z0-9-]+", pack_name
                        ):
                            failures.append(
                                f"dependencies.{field_name} em {meta_path.as_posix()} deve conter apenas slugs validos"
                            )
                            break
                        if pack_name == pack_root.name:
                            failures.append(
                                f"dependencies.{field_name} em {meta_path.as_posix()} nao pode apontar para o proprio pack"
                            )
                        elif pack_name not in formal_pack_names:
                            failures.append(
                                f"dependencies.{field_name} em {meta_path.as_posix()} referencia pack inexistente: {pack_name}"
                            )
            owner_issue = str(meta_payload.get("owner_issue", "") or "").strip()
            if owner_issue:
                jira_payload = meta_payload.get("jira")
                if not isinstance(jira_payload, dict):
                    failures.append(
                        f"bloco jira obrigatorio ausente em {meta_path.as_posix()} para owner_issue"
                    )
                else:
                    summary_prefix = str(jira_payload.get("summary_prefix", "") or "").strip()
                    if summary_prefix != "PROMPT:":
                        failures.append(
                            f"jira.summary_prefix em {meta_path.as_posix()} deve ser PROMPT:"
                        )
                    required_labels = jira_payload.get("required_labels") or []
                    normalized_labels = {
                        str(label).strip() for label in required_labels if str(label).strip()
                    }
                    if "prompt" not in normalized_labels:
                        failures.append(
                            f"jira.required_labels em {meta_path.as_posix()} deve conter prompt"
                        )

    for relative, snippets in PROMPT_PACK_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    for relative, snippets in SYNC_FOUNDATION_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)


def validate_legacy_codex_stub(repo_root: Path, failures: list[str]) -> None:
    legacy_root = legacy_codex_root(repo_root)
    readme_path = legacy_codex_readme(repo_root)

    if not readme_path.is_file():
        failures.append("Arquivo obrigatorio ausente: .codex/README.md")
        return

    unexpected = []
    if legacy_root.exists():
        for child in legacy_root.iterdir():
            if child.name == "README.md":
                continue
            if child.is_dir() and not any(child.iterdir()):
                continue
            unexpected.append(child.name)
    if unexpected:
        failures.append(
            ".codex deve conter apenas README.md de compatibilidade; entradas extras encontradas: "
            + ", ".join(sorted(unexpected))
        )


def validate_json_schema(path: Path, failures: list[str]) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"JSON invalido em {path.as_posix()}: {exc}")


def validate_jsonl(path: Path, failures: list[str]) -> None:
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            json.loads(stripped)
        except json.JSONDecodeError as exc:
            failures.append(f"JSONL invalido em {path.as_posix()} linha {index}: {exc}")


def parse_basic_toml_value(raw: str) -> object:
    stripped = raw.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
    if stripped.startswith('"') and stripped.endswith('"'):
        return stripped[1:-1]
    if stripped.startswith("'") and stripped.endswith("'"):
        return stripped[1:-1]
    if stripped.isdigit():
        return int(stripped)
    return stripped


def parse_basic_toml(text: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current: dict[str, object] = data
    pending_key = ""
    pending_value_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if pending_key:
            pending_value_lines.append(line)
            if "]" in line:
                current[pending_key] = parse_basic_toml_value(" ".join(pending_value_lines))
                pending_key = ""
                pending_value_lines = []
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            if not section_name:
                raise ValueError("Secao TOML vazia")
            section = data.setdefault(section_name, {})
            if not isinstance(section, dict):
                raise ValueError(f"Secao duplicada com tipo invalido: {section_name}")
            current = cast(dict[str, object], section)
            continue
        if "=" not in line:
            raise ValueError(f"Linha TOML invalida: {raw_line}")
        key, value = line.split("=", 1)
        normalized_key = key.strip()
        normalized_value = value.strip()
        if normalized_value.startswith("[") and not normalized_value.endswith("]"):
            pending_key = normalized_key
            pending_value_lines = [normalized_value]
            continue
        current[normalized_key] = parse_basic_toml_value(normalized_value)
    if pending_key:
        raise ValueError(f"Array TOML nao finalizado para a chave: {pending_key}")
    return data


def parse_toml_text(text: str) -> dict[str, object]:
    if tomllib is not None:
        try:
            return tomllib.loads(text)
        except Exception as exc:  # pragma: no cover - delegated to stdlib parser
            raise ValueError(str(exc)) from exc
    return parse_basic_toml(text)


def string_list_setting(section: object, key: str) -> list[str]:
    if not isinstance(section, dict):
        return []
    mapping = cast(dict[str, object], section)
    raw_value = mapping.get(key)
    if not isinstance(raw_value, list):
        return []
    return [item for item in raw_value if isinstance(item, str)]


def validate_agent_card(card: Path, skill_names: set[str], failures: list[str]) -> None:
    content = card.read_text(encoding="utf-8")
    for heading in REQUIRED_AGENT_HEADINGS:
        if heading not in content:
            failures.append(f"Heading obrigatorio ausente em .agents/cards/{card.name}: {heading}")

    skill_refs = re.findall(r"(?m)^-\s+`\$(.+?)`", content)
    if not skill_refs:
        failures.append(f"Skill principal ausente ou invalida em .agents/cards/{card.name}")
        return
    for skill_ref in skill_refs:
        if skill_ref not in skill_names:
            failures.append(
                f"Skill referenciada e inexistente em .agents/cards/{card.name}: {skill_ref}"
            )


def main(argv: list[str]) -> int:
    repo_root = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        path = repo_root / relative
        if not path.is_file():
            failures.append(f"Arquivo obrigatorio ausente: {relative}")

    tracker_path = repo_root / "docs" / "AI-WIP-TRACKER.md"
    if tracker_path.is_file():
        require_markers(
            tracker_path.read_text(encoding="utf-8"),
            TRACKER_MARKERS,
            "docs/AI-WIP-TRACKER.md",
            failures,
        )

    fallback_ledger_path = repo_root / "docs" / "AI-FALLBACK-LEDGER.md"
    if fallback_ledger_path.is_file():
        require_markers(
            fallback_ledger_path.read_text(encoding="utf-8"),
            FALLBACK_LEDGER_MARKERS,
            "docs/AI-FALLBACK-LEDGER.md",
            failures,
        )

    chat_contracts_path = repo_root / "docs" / "AI-CHAT-CONTRACTS-REGISTER.md"
    if chat_contracts_path.is_file():
        require_markers(
            chat_contracts_path.read_text(encoding="utf-8"),
            CHAT_CONTRACTS_MARKERS,
            "docs/AI-CHAT-CONTRACTS-REGISTER.md",
            failures,
        )

    roadmap_path = repo_root / "ROADMAP.md"
    if roadmap_path.is_file():
        require_markers(
            roadmap_path.read_text(encoding="utf-8"), ROADMAP_MARKERS, "ROADMAP.md", failures
        )

    decisions_path = repo_root / "docs" / "ROADMAP-DECISIONS.md"
    if decisions_path.is_file():
        require_markers(
            decisions_path.read_text(encoding="utf-8"),
            DECISIONS_MARKERS,
            "docs/ROADMAP-DECISIONS.md",
            failures,
        )

    scrum_master_ledger_path = repo_root / "docs" / "AI-SCRUM-MASTER-LEDGER.md"
    if scrum_master_ledger_path.is_file():
        require_markers(
            scrum_master_ledger_path.read_text(encoding="utf-8"),
            SCRUM_MASTER_MARKERS,
            "docs/AI-SCRUM-MASTER-LEDGER.md",
            failures,
        )

    lessons_path = repo_root / "LICOES-APRENDIDAS.md"
    if lessons_path.is_file():
        lessons_content = lessons_path.read_text(encoding="utf-8")
        require_markers(lessons_content, LESSONS_MARKERS, "LICOES-APRENDIDAS.md", failures)
        require_snippets(
            lessons_content, LESSONS_REQUIRED_SNIPPETS, "LICOES-APRENDIDAS.md", failures
        )

    agents_contract_path = repo_root / "AGENTS.md"
    if agents_contract_path.is_file():
        require_snippets(
            agents_contract_path.read_text(encoding="utf-8"),
            AGENTS_REQUIRED_SNIPPETS,
            "AGENTS.md",
            failures,
        )

    operating_model_path = repo_root / "docs" / "ai-operating-model.md"
    if operating_model_path.is_file():
        require_snippets(
            operating_model_path.read_text(encoding="utf-8"),
            OPERATING_MODEL_REQUIRED_SNIPPETS,
            "docs/ai-operating-model.md",
            failures,
        )

    source_audit_path = repo_root / "docs" / "AI-SOURCE-AUDIT.md"
    if source_audit_path.is_file():
        require_snippets(
            source_audit_path.read_text(encoding="utf-8"),
            SOURCE_AUDIT_REQUIRED_SNIPPETS,
            "docs/AI-SOURCE-AUDIT.md",
            failures,
        )

    startup_path = repo_root / "docs" / "AI-STARTUP-AND-RESTART.md"
    if startup_path.is_file():
        require_snippets(
            startup_path.read_text(encoding="utf-8"),
            STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
            "docs/AI-STARTUP-AND-RESTART.md",
            failures,
        )

    for relative, snippets in CEREMONY_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    for relative, snippets in AGENT_IDENTITY_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    for relative, snippets in BOARD_OPERATION_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    for relative, snippets in GIT_GOVERNANCE_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    for relative, snippets in CATALOG_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    for relative, snippets in STARTUP_GOVERNANCE_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    skills_dir = skills_root(repo_root)
    if not skills_dir.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/skills")
    else:
        skill_dirs = sorted(
            [item for item in skills_dir.iterdir() if item.is_dir()], key=lambda item: item.name
        )
        if not skill_dirs:
            failures.append("Nenhuma skill encontrada em .agents/skills")
        skill_names = {item.name for item in skill_dirs}
        for skill_dir in skill_dirs:
            validate_skill_dir(skill_dir, failures)
    skill_names = locals().get("skill_names", set())

    registry_dir = registry_root(repo_root)
    if not registry_dir.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/registry")
    else:
        agent_files = sorted(registry_dir.glob("*.toml"))
        if not agent_files:
            failures.append("Nenhum agente declarativo encontrado em .agents/registry")
        for agent_file in agent_files:
            validate_registry_agent(agent_file, skill_names, failures)

    validate_ai_config(repo_root, failures)
    validate_prompt_packs(repo_root, failures)
    validate_legacy_codex_stub(repo_root, failures)

    for schema_path in (
        orchestration_root(repo_root) / "task-card.schema.json",
        orchestration_root(repo_root) / "delegation-plan.schema.json",
        repo_root / ".agents" / "cerimonias" / "ceremony.schema.json",
    ):
        if schema_path.is_file():
            validate_json_schema(schema_path, failures)

    for dataset_path in (
        evals_root(repo_root) / "datasets" / "routing.jsonl",
        evals_root(repo_root) / "datasets" / "governance.jsonl",
    ):
        if dataset_path.is_file():
            validate_jsonl(dataset_path, failures)

    for rule_path in (
        rules_root(repo_root) / "default.rules",
        rules_root(repo_root) / "ci.rules",
        rules_root(repo_root) / "security.rules",
    ):
        if rule_path.is_file():
            content = rule_path.read_text(encoding="utf-8")
            if "rule " not in content or "must:" not in content:
                failures.append(f"Formato minimo ausente em {rule_path.as_posix()}")

    cards_dir = cards_root(repo_root)
    if not cards_dir.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/cards")
    else:
        cards = sorted(cards_dir.glob("*.md"))
        if not cards:
            failures.append("Nenhum cartao de agente encontrado em .agents/cards")
        for card in cards:
            validate_agent_card(card, skill_names, failures)

    if failures:
        print("Falhas encontradas na camada de IA:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1

    print("AI assets OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
