from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate-ai-assets.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_ai_assets", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("Nao foi possivel carregar validate-ai-assets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateAiAssetsTests(unittest.TestCase):
    def test_validator_exports_new_governance_contracts(self) -> None:
        module = load_validator_module()
        self.assertIn("LICOES-APRENDIDAS.md", module.REQUIRED_FILES)
        self.assertIn(".agents/README.md", module.REQUIRED_FILES)
        self.assertIn(".agents/prompts/README.md", module.REQUIRED_FILES)
        self.assertIn(".agents/prompts/CATALOG.md", module.REQUIRED_FILES)
        self.assertIn(
            ".agents/prompts/formal/startup-alignment/prompt.md",
            module.REQUIRED_FILES,
        )
        self.assertIn(
            ".agents/prompts/formal/sync-outbox-foundation/prompt.md",
            module.REQUIRED_FILES,
        )
        self.assertIn(
            ".agents/prompts/formal/documentation-layer-governance/prompt.md",
            module.REQUIRED_FILES,
        )
        self.assertIn(".agents/config.toml", module.REQUIRED_FILES)
        self.assertIn(".agents/cards/ai-startup-governor.md", module.REQUIRED_FILES)
        self.assertIn(".agents/cerimonias/README.md", module.REQUIRED_FILES)
        self.assertIn(".agents/cerimonias/ceremony.schema.json", module.REQUIRED_FILES)
        self.assertIn(".agents/cerimonias/retrospectiva.yaml", module.REQUIRED_FILES)
        self.assertIn(".codex/README.md", module.REQUIRED_FILES)
        self.assertIn(".agents/registry/ai-startup-governor.toml", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/README.md", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/CATALOG.md", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/projections.yaml", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/core-rules.md", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/chat-and-identity-rules.md", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/startup-and-resume-rules.md", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/startup.rules", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/chat.rules", module.REQUIRED_FILES)
        self.assertIn(".agents/rules/git.rules", module.REQUIRED_FILES)
        self.assertIn("docs/AI-AGENTS-CATALOG.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-CHAT-CONTRACTS-REGISTER.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-FALLBACK-LEDGER.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-FALLBACK-OPERATIONS.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-ORTHOGRAPHY-LEDGER.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-SCRUM-MASTER-LEDGER.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-SOURCE-AUDIT.md", module.REQUIRED_FILES)
        self.assertIn("docs/ai-sync-foundation.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-STARTUP-AND-RESTART.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-STARTUP-GOVERNANCE-MANIFEST.md", module.REQUIRED_FILES)
        self.assertIn("docs/TASKS.md", module.REQUIRED_FILES)
        self.assertIn("docs/WORKFLOWS.md", module.REQUIRED_FILES)
        self.assertIn("docs/secrets-and-auth.md", module.REQUIRED_FILES)
        self.assertIn("config/ai/platforms.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/platforms.local.yaml.tpl", module.REQUIRED_FILES)
        self.assertIn("config/ai/agents.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/agent-enablement.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/agent-operations.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/contracts.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/sync-targets.yaml", module.REQUIRED_FILES)
        self.assertIn("df/secrets/secrets-ref.yaml", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-prompt-governance.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-route.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-control-plane.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai_sync_foundation_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-fallback.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-session-startup.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai_control_plane_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai_rules_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai_fallback_governance_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai_session_startup_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/atlassian_platform_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/git-governance-check.py", module.REQUIRED_FILES)
        self.assertIn("scripts/run-ai-startup-session.ps1", module.REQUIRED_FILES)
        self.assertIn("scripts/cspell-governance.py", module.REQUIRED_FILES)
        self.assertIn("scripts/validate_workflow_task_sync.py", module.REQUIRED_FILES)
        self.assertIn("## Validacao recomendada", module.REQUIRED_AGENT_HEADINGS)
        self.assertIn("## Regras", module.REQUIRED_SKILL_HEADINGS)
        self.assertIn("## Entregas esperadas", module.REQUIRED_SKILL_HEADINGS)
        self.assertIn(
            "## Startup: o que precisa ser carregado", module.REQUIRED_THEME_RULE_HEADINGS
        )
        self.assertIn(".agents/rules/delegation-rules.md", module.THEMATIC_RULE_FILES)
        self.assertIn("Nunca operar por amostragem", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn("docs/AI-STARTUP-GOVERNANCE-MANIFEST.md", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn("docs/AI-FALLBACK-LEDGER.md", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn("`Jira` e a fonte primaria do fluxo vivo", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn(
            "Antes de criar qualquer demanda que nao seja `Epic`, verificar se ja existe `Epic` aberto aderente ao macro tema",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "concluir_primeiro passa a significar concluir ou puxar apenas o work item minimo que o destrava diretamente",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "carregar o contrato de comunicacao no chat e",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "governanca Git canonica do",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "nenhuma delegacao para subagente e valida sem issue dona",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "Nenhum `done` e valido sem revisar `LICOES-APRENDIDAS.md`",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "Quando a rodada tocar [`.agents/prompts/`](.agents/prompts/), o namespace",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn("titulo com prefixo", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn("label `prompt`", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn(
            "### 1.2. Contratos nascidos no chat precisam de registrador vivo",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### 3.1. Terminar antes de comecar inclui destravar o WIP ativo",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### 3.3. Intake nao pode duplicar issue nem Epic",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### 4.4. Higiene Git obrigatoria e rastreabilidade Jira",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### 4.5. Fallback local exige modo explicito e reconciliacao dirigida",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "task ai:fallback:capture",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "task ai:fallback:resolve",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "docs/git-conventions.md",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### Camada 2.2. Orquestracao, rules e evals",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "cadeia minima de evidencia para cada execucao obrigatoria",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "## Politica de leitura do board",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "## Camada de identidade humana dos agentes",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "task_id: prompt/<slug>",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn("PROMPT: ...", module.OPERATING_MODEL_REQUIRED_SNIPPETS)
        self.assertIn("label `prompt`", module.OPERATING_MODEL_REQUIRED_SNIPPETS)
        self.assertIn(
            "### Fronteira entre `.agents/` e adaptadores de assistente",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(".agents/config.toml", module.AGENT_IDENTITY_REQUIRED_SNIPPETS)
        self.assertIn(
            "display_name: Guardiao de Startup",
            module.AGENT_IDENTITY_REQUIRED_SNIPPETS["config/ai/agents.yaml"],
        )
        self.assertIn(
            "| Guardiao de Startup |",
            module.AGENT_IDENTITY_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            'display_name = "Guardiao de Startup"',
            module.AGENT_IDENTITY_REQUIRED_SNIPPETS[".agents/registry/ai-startup-governor.toml"],
        )
        self.assertIn(
            'display_name = "PO"',
            module.AGENT_IDENTITY_REQUIRED_SNIPPETS[".agents/registry/ai-product-owner.toml"],
        )
        self.assertIn(".agents/config.toml", module.RULES_LAYER_REQUIRED_SNIPPETS)
        self.assertIn(
            'projections = ".agents/rules/projections.yaml"',
            module.RULES_LAYER_REQUIRED_SNIPPETS[".agents/config.toml"],
        )
        self.assertIn(
            "## Projecoes executaveis",
            module.RULES_LAYER_REQUIRED_SNIPPETS[".agents/rules/CATALOG.md"],
        )
        self.assertIn("config/ai/contracts.yaml", module.BOARD_OPERATION_REQUIRED_SNIPPETS)
        self.assertIn(
            "reading_order: right-to-left",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "verify-existing-open-issue-before-any-new-issue",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "verify-existing-open-epic-before-any-non-epic-demand",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "verify-existing-open-epic-before-any-new-epic-for-the-same-theme",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "verify-existing-open-issue-before-creating-any-new-issue",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/jira-model.yaml"],
        )
        self.assertIn(
            "verify-existing-open-epic-before-creating-any-non-epic-demand",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/jira-model.yaml"],
        )
        self.assertIn(
            "new-epic-creation-requires-proof-of-no-open-epic-match",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/jira-model.yaml"],
        )
        self.assertIn(
            "verificar se a demanda ja nao existe antes de criar issue",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "assegurar que nao existe epic aberto cobrindo o tema antes de criar novo epic",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "auditar se toda criacao de issue ou epic passou pelo preflight de deduplicacao e reuse de epic",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "verificar se a issue ja existe",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS[".agents/cards/ai-product-owner.md"],
        )
        self.assertIn(
            "Reusar o `Epic` aberto correto",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS[".agents/cards/ai-product-owner.md"],
        )
        self.assertIn(
            "sem resposta por 3 minutos",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS[".agents/cards/ai-product-owner.md"],
        )
        self.assertIn(
            "preflight de deduplicacao",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS[".agents/cards/ai-scrum-master.md"],
        )
        self.assertIn(
            "issue ou `Epic` criado sem preflight",
            module.BOARD_OPERATION_REQUIRED_SNIPPETS[".agents/cards/ai-scrum-master.md"],
        )
        self.assertIn("docs/git-conventions.md", module.GIT_GOVERNANCE_REQUIRED_SNIPPETS)
        self.assertIn(
            "branch_pattern: <type>/<jira-key>-<slug>",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "branch_pattern: prompt/<jira-key>-<slug>",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "changes-touching-agents-prompts-must-use-prompt-branch-type",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            'jira_summary_prefix: "PROMPT:"',
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "prompt-related-jira-issues-must-carry-prompt-label",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "versioned-prompt-pack-work-must-use-prompt-branch-type",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "versioned-prompt-pack-owner-issues-must-carry-prompt-label",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "recovery_ledger: docs/AI-FALLBACK-LEDGER.md",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "ledger_entry_required: true",
            module.CEREMONY_REQUIRED_SNIPPETS[".agents/cerimonias/retrospectiva.yaml"],
        )
        self.assertIn(
            "Entrada no ledger",
            module.CEREMONY_REQUIRED_SNIPPETS[".agents/cerimonias/logs/retrospectiva-template.md"],
        )
        self.assertIn("ceremonies", module.REQUIRED_AI_CONFIG_SECTIONS)
        self.assertIn(
            "## LA-007 - Integracoes criticas exigem guardiao proprio",
            module.LESSONS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "$task-routing-and-decomposition",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-SKILLS-CATALOG.md"],
        )
        self.assertIn(
            "$dotfiles-orthography-review",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-SKILLS-CATALOG.md"],
        )
        self.assertIn(
            "pascoalete",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            "ai-startup-governor",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            "ai-startup-governor",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-DELEGATION-FLOW.md"],
        )
        self.assertIn(
            "### `ai:fallback:status`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "### `ai:fallback:capture`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "### `ai:fallback:resolve`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "AI-FALLBACK-LEDGER.md",
            module.GIT_GOVERNANCE_REQUIRED_SNIPPETS["docs/README.md"],
        )
        self.assertIn(
            "### `ai:atlassian:check`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "### `git:governance:check`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "### `ai:startup:session`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "### `ai:startup:enforce`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "gh auth status",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "probe GraphQL",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "display_name",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "Guardiao de Startup",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "pea_status",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "startup_governor_status",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "startup-ready.json",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "ai:startup:enforce",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "subagentes",
            module.STARTUP_AND_RESTART_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "validate-gh-auth-and-graphql-before-github-pr-or-merge-operations",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "version: 1",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-enablement.yaml"],
        )
        self.assertIn(
            "registry_agents:",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-enablement.yaml"],
        )
        self.assertIn(
            "ai-startup-governor:",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-enablement.yaml"],
        )
        self.assertIn(
            "ai-linguistic-reviewer:",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-enablement.yaml"],
        )
        self.assertIn(
            "pascoalete:",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-enablement.yaml"],
        )
        self.assertIn(
            "load-chat-communication-contract-before-first-user-facing-message",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "startup_readiness:",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "owner_role: ai-startup-governor",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "readiness_artifact: .cache/ai/startup-ready.json",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "capture-current-branch-lifecycle-upstream-and-main-absorption-state",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "startup-governor-must-own-the-first-user-facing-message-until-ready-for-work",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "startup-governor-must-block-operational-output-when-clearance-is-not-ready",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "startup-report-must-expose-pea-status",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "startup_governor_status",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "startup-ready.json",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "ai:startup:enforce",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "Guardiao de Startup",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/ai-operating-model.md"],
        )
        self.assertIn(
            "first-operational-chat-message-belongs-to-ai-startup-governor-until-ready-for-work",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "startup-governor-must-materialize-startup-ready-artifact-before-handoff",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "startup-governor-must-block-operational-output-when-clearance-is-not-ready",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "startup-ready.json",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/AI-DELEGATION-FLOW.md"],
        )
        self.assertIn(
            "ai-startup-governor",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/AI-DELEGATION-FLOW.md"],
        )
        self.assertIn(
            "fallback GitHub/PAT",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "pea_status",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "zero-context-startup-must-load-chat-contract-before-first-user-message",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            ".agents/prompts/CATALOG.md",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/AI-STARTUP-GOVERNANCE-MANIFEST.md"],
        )
        self.assertIn(
            ".agents/prompts/README.md",
            module.PROMPT_PACK_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            'summary_prefix: "PROMPT:"',
            module.PROMPT_PACK_REQUIRED_SNIPPETS[".agents/prompts/README.md"],
        )
        self.assertIn(
            "task_id: prompt/startup-alignment",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/startup-alignment/meta.yaml"
            ],
        )
        self.assertIn(
            'summary_prefix: "PROMPT:"',
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/startup-alignment/meta.yaml"
            ],
        )
        self.assertIn(
            "task_id: prompt/sync-outbox-foundation",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/sync-outbox-foundation/meta.yaml"
            ],
        )
        self.assertIn(
            'summary_prefix: "PROMPT:"',
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/sync-outbox-foundation/meta.yaml"
            ],
        )
        self.assertIn(
            "task_id: prompt/documentation-layer-governance",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/documentation-layer-governance/meta.yaml"
            ],
        )
        self.assertIn(
            "owner_issue: DOT-181",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/documentation-layer-governance/meta.yaml"
            ],
        )
        self.assertIn("docs/ai-sync-foundation.md", module.SYNC_FOUNDATION_REQUIRED_SNIPPETS)
        self.assertIn(
            "workspace_id",
            module.SYNC_FOUNDATION_REQUIRED_SNIPPETS["docs/ai-sync-foundation.md"],
        )
        self.assertIn(
            "runtime_environment_id",
            module.SYNC_FOUNDATION_REQUIRED_SNIPPETS["docs/ai-sync-foundation.md"],
        )
        self.assertIn(
            "### `ai:control-plane:sync:check`",
            module.SYNC_FOUNDATION_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "sync_foundation:",
            module.SYNC_FOUNDATION_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "DEPENDENCIAS DE PACKS E ORDEM SEGURA DE EXECUCAO",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[
                ".agents/prompts/formal/documentation-layer-governance/prompt.md"
            ],
        )
        self.assertIn(
            "prompt/documentation-layer-governance",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[".agents/prompts/CATALOG.md"],
        )
        self.assertIn(
            "DOT-181",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[".agents/prompts/CATALOG.md"],
        )
        self.assertIn(
            "prompt/sync-outbox-foundation",
            module.PROMPT_PACK_REQUIRED_SNIPPETS[".agents/prompts/CATALOG.md"],
        )
        self.assertIn(
            "documentation_links",
            module.SYNC_FOUNDATION_REQUIRED_SNIPPETS["docs/ai-sync-foundation.md"],
        )
        self.assertIn(
            "### `ai:prompts:jira:check`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "### `ai:prompts:jira:sync`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )
        self.assertIn(
            "df/secrets/secrets-ref.yaml",
            module.STARTUP_GOVERNANCE_REQUIRED_SNIPPETS["docs/AI-STARTUP-GOVERNANCE-MANIFEST.md"],
        )
        self.assertIn(
            "| Escrivao |",
            module.AGENT_IDENTITY_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            "| Revisor Documental |",
            module.AGENT_IDENTITY_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            "ai-documentation-manager",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            "ai-documentation-sync",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-DELEGATION-FLOW.md"],
        )
        self.assertIn(
            "ai-documentation-reviewer",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-GOVERNANCE-AND-REGRESSION.md"],
        )
        self.assertIn(
            "config/ai/contracts.yaml",
            module.DOCUMENTATION_LAYER_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "ownership_by_surface:",
            module.DOCUMENTATION_LAYER_REQUIRED_SNIPPETS["config/ai/contracts.yaml"],
        )
        self.assertIn(
            "documentation: repo-first-then-confluence",
            module.DOCUMENTATION_LAYER_REQUIRED_SNIPPETS["config/ai/jira-model.yaml"],
        )
        self.assertIn(
            "delivery_role: ai-documentation-sync",
            module.DOCUMENTATION_LAYER_REQUIRED_SNIPPETS["config/ai/confluence-model.yaml"],
        )
        self.assertIn(
            "ai-documentation-writer:",
            module.DOCUMENTATION_LAYER_REQUIRED_SNIPPETS["config/ai/agent-operations.yaml"],
        )
        self.assertIn(
            "Camada documental opera por competencia dominante",
            module.DOCUMENTATION_LAYER_REQUIRED_SNIPPETS["docs/ai-operating-model.md"],
        )

    def test_validator_passes_on_current_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("AI assets OK.", completed.stdout)


if __name__ == "__main__":
    unittest.main()
