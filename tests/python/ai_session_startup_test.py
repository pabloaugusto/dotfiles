from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ai_session_startup_lib import (
    DEFAULT_READINESS_PATH,
    agent_enablement_payload,
    agent_identity_payload,
    git_governance_payload,
    load_active_worklog_items,
    load_pending_chat_contracts,
    manifest_evidence_payload,
    render_startup_session_markdown,
    resolve_startup_manifest_paths,
    rules_projections_payload,
    startup_drift_payload,
    startup_governor_status_payload,
    startup_session_payload,
    write_startup_session_report,
)


class AiSessionStartupTests(unittest.TestCase):
    @staticmethod
    def _fake_git_inventory() -> dict[str, object]:
        return {
            "status": "ok",
            "current_branch": "feat/DOT-177-startup-preflight-memory",
            "dirty_entries": [" M docs/AI-STARTUP-AND-RESTART.md"],
            "local_branch_count": 2,
            "merged_local_branches": [],
            "worktrees": [
                {
                    "path": "C:/Users/pablo/dotfiles",
                    "head": "abc123",
                    "branch": "feat/DOT-177-startup-preflight-memory",
                }
            ],
            "branch_lifecycle": {
                "branch": "feat/DOT-177-startup-preflight-memory",
                "upstream": "origin/feat/DOT-177-startup-preflight-memory",
                "ahead_count": 1,
                "behind_count": 0,
                "has_upstream": True,
                "absorbed_in_origin_main": False,
                "origin_main_probe": "ok",
                "prune_candidate": False,
            },
            "open_prs_for_current_branch": [
                {
                    "number": 99,
                    "state": "OPEN",
                    "title": "DOT-177 startup memory",
                    "url": "https://github.com/pabloaugusto/dotfiles/pull/99",
                }
            ],
            "pr_probe_status": "ok",
            "pr_probe_note": "",
        }

    @staticmethod
    def _fake_active_execution() -> dict[str, object]:
        return {
            "status": "ok",
            "issue_key": "DOT-177",
            "issue_summary": "Endurecer startup/restart com absorcao integral de contexto, fallback e delegacao segura",
            "issue_url": "https://pabloaugusto.atlassian.net/browse/DOT-177",
            "agent": "ai-developer-config-policy",
            "agent_display_name": "Engenheiro Agentes IA",
            "workflow_status": "doing",
            "branch": "feat/DOT-177-startup-preflight-memory",
            "worktree_root": "C:/Users/pablo/dotfiles",
            "started_at": "2026-03-11T10:23:00-03:00",
            "updated_at": "2026-03-11T10:23:00-03:00",
        }

    @staticmethod
    def _fake_fallback_status() -> dict[str, object]:
        return {
            "mode": "primary",
            "jira_available": True,
            "jira_reason": "probe-ok",
            "active_fallback_count": 0,
            "resolved_fallback_count": 0,
            "tracker_doing_count": 1,
            "active_records": [],
            "guidance": "Fluxo primario ativo.",
            "ledger_path": "docs/AI-FALLBACK-LEDGER.md",
            "tracker_path": "docs/AI-WIP-TRACKER.md",
        }

    @staticmethod
    def _fake_github_auth() -> dict[str, object]:
        return {
            "status": "ok",
            "fallback_chain": [
                "reaproveitar sessao existente do gh",
                "GH_TOKEN",
                "GITHUB_TOKEN",
                "op://secrets/dotfiles/github/token",
                "op://secrets/github/api/token",
                "op://Personal/github/token-full-access",
            ],
            "active_sources_current_shell": ["GH_TOKEN"],
            "active_sources_without_env_tokens": ["keyring"],
            "ssh_signing_keys_probe": "ok",
            "user_installations_probe": "resource_not_accessible_by_pat",
            "graphql_probe": {"status": "ok", "note": "viewer=pabloaugusto"},
            "recommendations": [
                "Se o GraphQL falhar, comparar o gh com e sem GH_TOKEN/GITHUB_TOKEN antes de concluir bloqueio estrutural."
            ],
        }

    @staticmethod
    def _fake_atlassian() -> dict[str, object]:
        return {
            "status": "ok",
            "overall_ok": True,
            "auth_mode": "service-account-api-token",
            "site_url": "https://pabloaugusto.atlassian.net",
            "cloud_id": "cloud-123",
            "jira_project_key": "DOT",
            "confluence_space_key": "DOT",
            "jira_status": "ok",
            "jira_project": {"key": "DOT"},
            "confluence_status": "ok",
            "confluence_space": {"key": "DOT"},
            "recovery_hints": [
                "rodar task ai:atlassian:check antes de assumir bloqueio estrutural",
                "lembrar que service-account-api-token usa api.atlassian.com com cloud_id",
            ],
        }

    @staticmethod
    def _fake_pea_status() -> dict[str, object]:
        return {
            "status": "ok",
            "catalog_path": ".agents/prompts/CATALOG.md",
            "pack_root": ".agents/prompts/formal/startup-alignment",
            "required_paths": [
                ".agents/prompts/CATALOG.md",
                ".agents/prompts/formal/startup-alignment/prompt.md",
            ],
            "missing_paths": [],
            "startup_loads_pack": True,
            "execution_modes": [
                "fast_lane",
                "alinhamento_resumido_e_execucao",
                "aguardando_confirmacao_humana",
                "bloqueado_por_pre_condicao",
            ],
            "separation_note": "startup rele a camada e expoe pea_status; PEA alinha entendimento; enforcement real permanece nos gates oficiais",
        }

    @staticmethod
    def _fake_agent_enablement() -> dict[str, object]:
        return {
            "status": "ok",
            "agents_path": "config/ai/agents.yaml",
            "overlay_path": "config/ai/agent-enablement.yaml",
            "overlay_local_path": "config/ai/agent-enablement.local.yaml",
            "overlay_local_active": False,
            "declared_roles": [
                "ai-developer-config-policy",
                "ai-linguistic-reviewer",
                "ai-startup-governor",
            ],
            "overridden_roles": ["ai-linguistic-reviewer"],
            "enabled_roles": ["ai-developer-config-policy", "ai-startup-governor"],
            "disabled_roles": ["ai-linguistic-reviewer"],
            "required_roles_disabled": [],
            "enabled_registry_agents": ["repo-governance-authority"],
            "disabled_registry_agents": ["pascoalete"],
        }

    @staticmethod
    def _fake_rules_projections() -> dict[str, object]:
        return {
            "status": "ok",
            "catalog_path": ".agents/rules/projections.yaml",
            "declared_projection_ids": ["chat", "git", "security", "startup"],
            "required_for_startup": ["chat", "git", "security", "startup"],
            "loaded_for_startup": ["chat", "git", "security", "startup"],
            "missing_required": [],
            "projection_count": 4,
            "loaded_required_count": 4,
            "projections": {
                "chat": {
                    "status": "ok",
                    "human_source": ".agents/rules/chat-and-identity-rules.md",
                    "machine_projection": ".agents/rules/chat.rules",
                    "must": ["usar display_name oficial", "carregar o contrato de chat"],
                },
                "git": {
                    "status": "ok",
                    "human_source": ".agents/rules/git-rules.md",
                    "machine_projection": ".agents/rules/git.rules",
                    "must": ["manter commit atomico", "podar branch e worktree residuais"],
                },
                "startup": {
                    "status": "ok",
                    "human_source": ".agents/rules/startup-and-resume-rules.md",
                    "machine_projection": ".agents/rules/startup.rules",
                    "must": ["reler integralmente o manifest resolvido"],
                },
                "security": {
                    "status": "ok",
                    "human_source": ".agents/rules/auth-secrets-and-critical-integrations-rules.md",
                    "machine_projection": ".agents/rules/security.rules",
                    "must": ["proteger gh, op, sops, age, ssh-agent, signing e checkEnv"],
                },
            },
        }

    def test_resolve_startup_manifest_paths_collects_explicit_and_recursive_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            cards_dir = repo_root / ".agents" / "cards"
            docs_dir.mkdir(parents=True)
            cards_dir.mkdir(parents=True)
            (docs_dir / "AI-STARTUP-GOVERNANCE-MANIFEST.md").write_text(
                textwrap.dedent(
                    """\
                    # Manifest

                    - [`AGENTS.md`](../AGENTS.md)
                    - todos os arquivos `AI-*` em [`docs/`](./)
                    - todos os arquivos em [`.agents/cards/`](../.agents/cards/)
                    - [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml)
                    """
                ),
                encoding="utf-8",
            )
            (repo_root / "AGENTS.md").write_text("# contrato\n", encoding="utf-8")
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                "# register\n", encoding="utf-8"
            )
            (docs_dir / "AI-STARTUP-AND-RESTART.md").write_text("# runbook\n", encoding="utf-8")
            (cards_dir / "ai-product-owner.md").write_text("# card\n", encoding="utf-8")
            secrets_dir = repo_root / "df" / "secrets"
            secrets_dir.mkdir(parents=True)
            (secrets_dir / "secrets-ref.yaml").write_text("---\n", encoding="utf-8")

            resolved = resolve_startup_manifest_paths(repo_root)

        self.assertIn("AGENTS.md", resolved)
        self.assertIn("docs/AI-CHAT-CONTRACTS-REGISTER.md", resolved)
        self.assertIn("docs/AI-STARTUP-AND-RESTART.md", resolved)
        self.assertIn(".agents/cards/ai-product-owner.md", resolved)
        self.assertIn("df/secrets/secrets-ref.yaml", resolved)

    def test_load_pending_chat_contracts_reads_markdown_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            docs_dir.mkdir(parents=True)
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                textwrap.dedent(
                    """\
                    # Register

                    <!-- ai-chat-contracts:pending:start -->
                    | ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
                    | --- | --- | --- | --- | --- | --- |
                    | CHAT-001 | Exemplo | Busca | DOT-999 | cards | pendente |
                    <!-- ai-chat-contracts:pending:end -->
                    """
                ),
                encoding="utf-8",
            )

            entries = load_pending_chat_contracts(repo_root)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].contract_id, "CHAT-001")
        self.assertEqual(entries[0].status, "pendente")

    def test_load_active_worklog_items_reads_doing_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            docs_dir.mkdir(parents=True)
            (docs_dir / "AI-WIP-TRACKER.md").write_text(
                textwrap.dedent(
                    """\
                    # Tracker

                    <!-- ai-worklog:doing:start -->
                    | ID | Tarefa | Branch | Responsavel | Inicio UTC | Ultima atualizacao UTC | Proximo passo | Bloqueios |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | WIP-DOT-177 | Startup | feat/DOT-177-startup-preflight-memory | ai-developer-config-policy | 2026-03-11 13:23 UTC | 2026-03-11 13:23 UTC | Ajustar startup | - |
                    <!-- ai-worklog:doing:end -->
                    """
                ),
                encoding="utf-8",
            )

            entries = load_active_worklog_items(repo_root)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["ID"], "WIP-DOT-177")
        self.assertEqual(entries[0]["Branch"], "feat/DOT-177-startup-preflight-memory")

    def test_agent_identity_payload_uses_display_name_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            registry_dir = repo_root / ".agents" / "registry"
            registry_dir.mkdir(parents=True)
            (registry_dir / "ai-developer-config-policy.toml").write_text(
                textwrap.dedent(
                    """\
                    id = "ai-developer-config-policy"
                    display_name = "Engenheiro Agentes IA"
                    """
                ),
                encoding="utf-8",
            )

            payload = agent_identity_payload(
                repo_root,
                {"agent": "ai-developer-config-policy"},
            )

        self.assertEqual(payload["active_display_name"], "Engenheiro Agentes IA")
        self.assertEqual(payload["fallback_display"], "technical-id")

    def test_agent_enablement_payload_reads_effective_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            config_dir = repo_root / "config" / "ai"
            registry_dir = repo_root / ".agents" / "registry"
            config_dir.mkdir(parents=True)
            registry_dir.mkdir(parents=True)
            (registry_dir / "pascoalete.toml").write_text(
                'id = "pascoalete"\ndisplay_name = "Pascoalete"\n',
                encoding="utf-8",
            )
            (config_dir / "agents.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    defaults:
                      registry_agents_enabled_by_default: true
                    roles:
                      ai-startup-governor:
                        enabled: true
                        required: true
                      ai-linguistic-reviewer:
                        enabled: true
                        required: true
                    """
                ),
                encoding="utf-8",
            )
            (config_dir / "agent-enablement.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    roles:
                      ai-startup-governor:
                        enabled: true
                      ai-linguistic-reviewer:
                        enabled: false
                    registry_agents:
                      pascoalete:
                        enabled: false
                    """
                ),
                encoding="utf-8",
            )
            (config_dir / "agent-operations.yaml").write_text(
                "version: 1\nroles: {}\n",
                encoding="utf-8",
            )
            (config_dir / "contracts.yaml").write_text(
                "version: 1\nworkflow:\n  always_enabled_columns:\n    - Backlog\n",
                encoding="utf-8",
            )
            (config_dir / "platforms.yaml").write_text(
                'version: 1\nplatforms:\n  atlassian:\n    enabled: false\n    provider: none\n    auth:\n      mode: disabled\n      site_url: ""\n      email: ""\n      token: ""\n      service_account: ""\n      cloud_id: ""\n    jira:\n      enabled: false\n      project_key: ""\n    confluence:\n      enabled: false\n      space_key: ""\n',
                encoding="utf-8",
            )

            payload = agent_enablement_payload(repo_root)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["overlay_path"], "config/ai/agent-enablement.yaml")
        self.assertEqual(payload["enabled_roles"], ["ai-startup-governor"])
        self.assertEqual(payload["disabled_roles"], ["ai-linguistic-reviewer"])
        self.assertEqual(payload["required_roles_disabled"], ["ai-linguistic-reviewer"])
        self.assertEqual(payload["disabled_registry_agents"], ["pascoalete"])

    def test_rules_projections_payload_reads_catalog_and_required_layers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            rules_dir = repo_root / ".agents" / "rules"
            rules_dir.mkdir(parents=True)
            (repo_root / ".agents" / "config.toml").write_text(
                textwrap.dedent(
                    """\
                    version = 1

                    [skills]
                    required = []
                    mandatory_parallel = []

                    [agents]
                    required = []
                    mandatory_global = []
                    mandatory_platform = []

                    [orchestration]
                    capability_matrix = ".agents/orchestration/capability-matrix.yaml"
                    routing_policy = ".agents/orchestration/routing-policy.yaml"
                    task_card_schema = ".agents/orchestration/task-card.schema.json"
                    delegation_plan_schema = ".agents/orchestration/delegation-plan.schema.json"

                    [rules]
                    default = ".agents/rules/default.rules"
                    ci = ".agents/rules/ci.rules"
                    security = ".agents/rules/security.rules"
                    startup = ".agents/rules/startup.rules"
                    chat = ".agents/rules/chat.rules"
                    git = ".agents/rules/git.rules"
                    projections = ".agents/rules/projections.yaml"

                    [evals]
                    smoke = ".agents/evals/scenarios/smoke.md"
                    regression = ".agents/evals/scenarios/regression.md"
                    security = ".agents/evals/scenarios/security.md"
                    routing_dataset = ".agents/evals/datasets/routing.jsonl"
                    governance_dataset = ".agents/evals/datasets/governance.jsonl"

                    [ceremonies]
                    root = ".agents/cerimonias"
                    schema = ".agents/cerimonias/ceremony.schema.json"
                    default_log_root = ".agents/cerimonias/logs"

                    [identity]
                    registry_root = ".agents/registry"
                    display_name_field = "display_name"
                    card_title_mirror_required = true
                    fallback_display = "technical-id"
                    """
                ),
                encoding="utf-8",
            )
            (rules_dir / "chat-and-identity-rules.md").write_text(
                "display_name\nenablement\nai-startup-governor\n",
                encoding="utf-8",
            )
            (rules_dir / "git-rules.md").write_text("branch\nissue\nworktree\n", encoding="utf-8")
            (rules_dir / "startup-and-resume-rules.md").write_text(
                "manifest\nready_for_work\nai-startup-governor\n",
                encoding="utf-8",
            )
            (rules_dir / "auth-secrets-and-critical-integrations-rules.md").write_text(
                "gh\nsigning\nsecrets\n",
                encoding="utf-8",
            )
            (rules_dir / "chat.rules").write_text(
                "rule AI-CHAT-001\nwhen: startup-chat\nmust:\n- usar display_name oficial\n",
                encoding="utf-8",
            )
            (rules_dir / "git.rules").write_text(
                "rule AI-GIT-001\nwhen: startup-git\nmust:\n- manter commit atomico\n",
                encoding="utf-8",
            )
            (rules_dir / "startup.rules").write_text(
                "rule AI-STARTUP-001\nwhen: startup\nmust:\n- reler integralmente o manifest resolvido\n",
                encoding="utf-8",
            )
            (rules_dir / "security.rules").write_text(
                "rule AI-SEC-001\nwhen: startup-critical-integrations\nmust:\n- proteger gh, signing e secrets\n",
                encoding="utf-8",
            )
            (rules_dir / "projections.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    projections:
                      startup:
                        human_source: .agents/rules/startup-and-resume-rules.md
                        machine_projection: .agents/rules/startup.rules
                        required_for_startup: true
                        parity_terms:
                          - manifest
                          - ready_for_work
                          - ai-startup-governor
                      chat:
                        human_source: .agents/rules/chat-and-identity-rules.md
                        machine_projection: .agents/rules/chat.rules
                        required_for_startup: true
                        parity_terms:
                          - display_name
                          - ai-startup-governor
                          - enablement
                      git:
                        human_source: .agents/rules/git-rules.md
                        machine_projection: .agents/rules/git.rules
                        required_for_startup: true
                        parity_terms:
                          - branch
                          - issue
                          - worktree
                      security:
                        human_source: .agents/rules/auth-secrets-and-critical-integrations-rules.md
                        machine_projection: .agents/rules/security.rules
                        required_for_startup: true
                        parity_terms:
                          - gh
                          - signing
                          - secrets
                    """
                ),
                encoding="utf-8",
            )

            payload = rules_projections_payload(repo_root)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["catalog_path"], ".agents/rules/projections.yaml")
        self.assertEqual(payload["loaded_required_count"], 4)
        self.assertEqual(payload["missing_required"], [])
        self.assertEqual(
            payload["projections"]["chat"]["machine_projection"],
            ".agents/rules/chat.rules",
        )

    def test_git_governance_payload_exposes_sources_without_claiming_enforcement(self) -> None:
        payload = git_governance_payload(Path.cwd(), self._fake_rules_projections())

        self.assertEqual(payload["status"], "ok")
        self.assertIn("docs/git-conventions.md", payload["sources"])
        self.assertTrue(any("commit atomico" in item for item in payload["rules"]))
        self.assertEqual(payload["machine_projection"], ".agents/rules/git.rules")
        self.assertIn("enforcement real", payload["enforcement_note"])

    def test_startup_drift_payload_detects_branch_mismatch(self) -> None:
        payload = startup_drift_payload(
            {
                "status": "ok",
                "issue_key": "DOT-177",
                "branch": "feat/DOT-177-startup-preflight-memory",
            },
            [
                {
                    "ID": "WIP-DOT-176",
                    "Tarefa": "Startup antigo",
                    "Branch": "feat/DOT-176-startup-auth-fallback-preflight",
                }
            ],
            self._fake_git_inventory(),
        )

        self.assertEqual(payload["status"], "drift")
        self.assertTrue(any("worklog ativo aponta" in item for item in payload["findings"]))

    def test_startup_governor_status_blocks_without_pending_action_for_active_worklog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            registry_dir = repo_root / ".agents" / "registry"
            docs_dir.mkdir(parents=True)
            registry_dir.mkdir(parents=True)
            (registry_dir / "ai-startup-governor.toml").write_text(
                'id = "ai-startup-governor"\ndisplay_name = "Guardiao de Startup"\n',
                encoding="utf-8",
            )
            manifest_evidence = manifest_evidence_payload(repo_root, [])
            status = startup_governor_status_payload(
                repo_root,
                manifest_evidence=manifest_evidence,
                pending_contracts=[],
                git_inventory=self._fake_git_inventory(),
                active_worklog_items=[
                    {
                        "ID": "WIP-DOT-177",
                        "Tarefa": "Startup",
                        "Branch": "feat/DOT-177-startup-preflight-memory",
                    }
                ],
                active_execution=self._fake_active_execution(),
                agent_identity={
                    "status": "ok",
                    "registry_count": 1,
                    "active_agent": "ai-developer-config-policy",
                    "active_display_name": "Engenheiro Agentes IA",
                    "fallback_display": "technical-id",
                },
                agent_enablement=self._fake_agent_enablement(),
                rules_projections=self._fake_rules_projections(),
                chat_communication={"status": "ok", "rules": ["usar portugues"]},
                git_governance={"status": "ok", "sources": [], "rules": [], "enforcement_note": ""},
                pea_status=self._fake_pea_status(),
                startup_drift={"status": "clean", "findings": []},
                fallback_status=self._fake_fallback_status(),
                github_auth=self._fake_github_auth(),
                atlassian_connectivity=self._fake_atlassian(),
                prioritized_work_item={
                    "source": "active-execution",
                    "identifier": "DOT-177",
                    "summary": "Startup",
                },
            )

        self.assertEqual(status["state"], "wip_decision_pending")
        self.assertFalse(status["clearance_granted"])
        self.assertTrue(
            any(
                "concluir_primeiro" in item or "roadmap_pendente" in item
                for item in status["blocking_findings"]
            )
        )

    def test_write_startup_session_report_persists_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            registry_dir = repo_root / ".agents" / "registry"
            docs_dir.mkdir(parents=True)
            registry_dir.mkdir(parents=True)
            secrets_dir = repo_root / "df" / "secrets"
            secrets_dir.mkdir(parents=True)
            (repo_root / "AGENTS.md").write_text("# contrato\n", encoding="utf-8")
            (docs_dir / "AI-STARTUP-GOVERNANCE-MANIFEST.md").write_text(
                textwrap.dedent(
                    """\
                    # Manifest

                    - [`AGENTS.md`](../AGENTS.md)
                    - todos os arquivos `AI-*` em [`docs/`](./)
                    - todos os arquivos em [`.agents/registry/`](../.agents/registry/)
                    - [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml)
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                textwrap.dedent(
                    """\
                    # Register

                    <!-- ai-chat-contracts:pending:start -->
                    | ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
                    | --- | --- | --- | --- | --- | --- |
                    | CHAT-001 | Exemplo | Busca | DOT-999 | cards | pendente |
                    <!-- ai-chat-contracts:pending:end -->
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-STARTUP-AND-RESTART.md").write_text("# runbook\n", encoding="utf-8")
            (docs_dir / "AI-WIP-TRACKER.md").write_text(
                textwrap.dedent(
                    """\
                    # Tracker

                    <!-- ai-worklog:doing:start -->
                    | ID | Tarefa | Branch | Responsavel | Inicio UTC | Ultima atualizacao UTC | Proximo passo | Bloqueios |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | WIP-DOT-177 | Startup | feat/DOT-177-startup-preflight-memory | ai-developer-config-policy | 2026-03-11 13:23 UTC | 2026-03-11 13:23 UTC | Ajustar startup | - |
                    <!-- ai-worklog:doing:end -->
                    """
                ),
                encoding="utf-8",
            )
            (registry_dir / "ai-developer-config-policy.toml").write_text(
                'id = "ai-developer-config-policy"\ndisplay_name = "Engenheiro Agentes IA"\n',
                encoding="utf-8",
            )
            (secrets_dir / "secrets-ref.yaml").write_text("---\n", encoding="utf-8")

            with (
                patch(
                    "scripts.ai_session_startup_lib.git_inventory_payload",
                    return_value=self._fake_git_inventory(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.active_execution_payload",
                    return_value=self._fake_active_execution(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.fallback_status_payload",
                    return_value=self._fake_fallback_status(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.github_auth_summary",
                    return_value=self._fake_github_auth(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.agent_enablement_payload",
                    return_value=self._fake_agent_enablement(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.rules_projections_payload",
                    return_value=self._fake_rules_projections(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.atlassian_connectivity_summary",
                    return_value=self._fake_atlassian(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.pea_status_payload",
                    return_value=self._fake_pea_status(),
                ),
            ):
                payload = write_startup_session_report(
                    repo_root,
                    pending_action="concluir_primeiro",
                )

            report_path = repo_root / payload["report_path"]
            readiness_path = repo_root / payload["readiness_artifact_path"]
            report_exists = report_path.exists()
            readiness_exists = readiness_path.exists()
            report_text = report_path.read_text(encoding="utf-8")
            readiness_text = readiness_path.read_text(encoding="utf-8")

        self.assertTrue(report_exists)
        self.assertTrue(readiness_exists)
        self.assertIn("AI Startup Session Report", report_text)
        self.assertIn("## Comunicacao no chat e identidade", report_text)
        self.assertIn("Engenheiro Agentes IA", report_text)
        self.assertIn("## Drift operacional detectado", report_text)
        self.assertIn("## PEA carregado no startup", report_text)
        self.assertIn("## Enablement efetivo de agentes", report_text)
        self.assertIn("## Delegacao e subagentes", report_text)
        self.assertIn("## startup_governor_status", report_text)
        self.assertIn("cloud_id", report_text)
        self.assertIn('"state": "ready_for_work"', readiness_text)
        self.assertIn(DEFAULT_READINESS_PATH.as_posix(), payload["default_readiness_path"])

    def test_render_startup_session_markdown_lists_new_sections(self) -> None:
        payload = {
            "generated_at": "2026-03-11 13:30:00",
            "manifest_path": "docs/AI-STARTUP-GOVERNANCE-MANIFEST.md",
            "chat_contracts_register_path": "docs/AI-CHAT-CONTRACTS-REGISTER.md",
            "resolved_paths": ["AGENTS.md", "docs/AI-CHAT-CONTRACTS-REGISTER.md"],
            "resolved_count": 2,
            "manifest_evidence": {
                "status": "ok",
                "resolved_count": 2,
                "textual_line_count": 10,
                "textual_bytes": 120,
                "sha256": "abc123",
                "missing_paths": [],
            },
            "pending_chat_contracts": [
                {
                    "contract_id": "CHAT-001",
                    "summary": "Exemplo",
                    "evidence": "Busca",
                    "owner": "DOT-999",
                    "destination": "cards",
                    "status": "pendente",
                }
            ],
            "pending_chat_contract_count": 1,
            "default_report_path": ".cache/ai/startup-session.md",
            "default_readiness_path": ".cache/ai/startup-ready.json",
            "pending_action": "concluir_primeiro",
            "active_worklog_count": 1,
            "git_inventory": self._fake_git_inventory(),
            "active_worklog_items": [
                {
                    "ID": "WIP-DOT-177",
                    "Tarefa": "Startup",
                    "Branch": "feat/DOT-177-startup-preflight-memory",
                    "Proximo passo": "Ajustar startup",
                }
            ],
            "active_execution": self._fake_active_execution(),
            "agent_identity": {
                "status": "ok",
                "registry_count": 1,
                "active_agent": "ai-developer-config-policy",
                "active_display_name": "Engenheiro Agentes IA",
                "fallback_display": "technical-id",
            },
            "agent_enablement": self._fake_agent_enablement(),
            "rules_projections": self._fake_rules_projections(),
            "chat_communication": {
                "status": "ok",
                "rules": ["usar portugues", "preferir display_name oficial"],
            },
            "git_governance": {
                "status": "ok",
                "sources": ["AGENTS.md", "docs/git-conventions.md"],
                "rules": ["commits devem ser atomicos, ligados a uma unica issue"],
                "enforcement_note": "o startup relembra a governanca Git, mas o enforcement real continua nos hooks, tasks e gates oficiais do repo",
            },
            "pea_status": self._fake_pea_status(),
            "delegation_context": {
                "status": "ok",
                "owner_issue": "DOT-177",
                "current_branch": "feat/DOT-177-startup-preflight-memory",
                "required_paths": ["AGENTS.md", "docs/AI-DELEGATION-FLOW.md"],
                "rules": ["nao delegar sem startup"],
            },
            "startup_drift": {
                "status": "drift",
                "findings": ["worklog ativo aponta para outra branch"],
            },
            "fallback_status": self._fake_fallback_status(),
            "github_auth": self._fake_github_auth(),
            "atlassian_connectivity": self._fake_atlassian(),
            "prioritized_work_item": {
                "source": "active-execution",
                "identifier": "DOT-177",
                "summary": "Startup",
            },
            "startup_governor_status": {
                "owner_role": "ai-startup-governor",
                "owner_display_name": "Guardiao de Startup",
                "audit_owner_role": "ai-scrum-master",
                "state": "ready_for_work",
                "clearance": "granted",
                "clearance_granted": True,
                "pending_action": "concluir_primeiro",
                "progression": [
                    "not_started",
                    "reading_manifest",
                    "rules_projections_loaded",
                    "ready_for_work",
                ],
                "blocking_findings": [],
                "warnings": ["existem contratos pendentes"],
                "blocked_actions": [],
                "harness": {
                    "report_path": ".cache/ai/startup-session.md",
                    "readiness_artifact": ".cache/ai/startup-ready.json",
                },
                "handoff": {
                    "allowed": True,
                    "current_chat_owner_role": "ai-startup-governor",
                    "current_chat_owner_display_name": "Guardiao de Startup",
                    "next_owner_role": "ai-developer-config-policy",
                    "next_owner_display_name": "Engenheiro Agentes IA",
                },
                "context_snapshot": {"current_branch": "feat/DOT-177-startup-preflight-memory"},
                "context_fingerprint": "fingerprint-123",
            },
            "readiness_artifact_path": ".cache/ai/startup-ready.json",
        }

        markdown = render_startup_session_markdown(payload)

        self.assertIn("## Comunicacao no chat e identidade", markdown)
        self.assertIn("## Projecoes .rules criticas", markdown)
        self.assertIn("## Enablement efetivo de agentes", markdown)
        self.assertIn("## Governanca Git carregada no startup", markdown)
        self.assertIn("## PEA carregado no startup", markdown)
        self.assertIn("config/ai/agent-enablement.yaml", markdown)
        self.assertIn(".agents/rules/projections.yaml", markdown)
        self.assertIn("pascoalete", markdown)
        self.assertIn("docs/git-conventions.md", markdown)
        self.assertIn("startup-alignment", markdown)
        self.assertIn("enforcement", markdown)
        self.assertIn("## Inventario Git e worktree", markdown)
        self.assertIn("## Drift operacional detectado", markdown)
        self.assertIn("## GitHub auth e fallback", markdown)
        self.assertIn("## Atlassian", markdown)
        self.assertIn("## Delegacao e subagentes", markdown)
        self.assertIn("## startup_governor_status", markdown)
        self.assertIn("startup-ready.json", markdown)
        self.assertIn("fingerprint-123", markdown)
        self.assertIn("op://Personal/github/token-full-access", markdown)

    def test_startup_session_payload_counts_pending_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            registry_dir = repo_root / ".agents" / "registry"
            secrets_dir = repo_root / "df" / "secrets"
            docs_dir.mkdir(parents=True)
            registry_dir.mkdir(parents=True)
            secrets_dir.mkdir(parents=True)
            (repo_root / "AGENTS.md").write_text("# contrato\n", encoding="utf-8")
            (docs_dir / "AI-STARTUP-GOVERNANCE-MANIFEST.md").write_text(
                textwrap.dedent(
                    """\
                    # Manifest

                    - [`AGENTS.md`](../AGENTS.md)
                    - todos os arquivos `AI-*` em [`docs/`](./)
                    - todos os arquivos em [`.agents/registry/`](../.agents/registry/)
                    - [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml)
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                textwrap.dedent(
                    """\
                    # Register

                    <!-- ai-chat-contracts:pending:start -->
                    | ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
                    | --- | --- | --- | --- | --- | --- |
                    | CHAT-001 | Exemplo | Busca | DOT-999 | cards | pendente |
                    | CHAT-002 | Exemplo 2 | Busca | DOT-998 | docs | pendente |
                    <!-- ai-chat-contracts:pending:end -->
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-STARTUP-AND-RESTART.md").write_text("# runbook\n", encoding="utf-8")
            (docs_dir / "AI-WIP-TRACKER.md").write_text(
                textwrap.dedent(
                    """\
                    # Tracker

                    <!-- ai-worklog:doing:start -->
                    | ID | Tarefa | Branch | Responsavel | Inicio UTC | Ultima atualizacao UTC | Proximo passo | Bloqueios |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | WIP-DOT-177 | Startup | feat/DOT-177-startup-preflight-memory | ai-developer-config-policy | 2026-03-11 13:23 UTC | 2026-03-11 13:23 UTC | Ajustar startup | - |
                    <!-- ai-worklog:doing:end -->
                    """
                ),
                encoding="utf-8",
            )
            (registry_dir / "ai-developer-config-policy.toml").write_text(
                'id = "ai-developer-config-policy"\ndisplay_name = "Engenheiro Agentes IA"\n',
                encoding="utf-8",
            )
            (secrets_dir / "secrets-ref.yaml").write_text("---\n", encoding="utf-8")

            with (
                patch(
                    "scripts.ai_session_startup_lib.git_inventory_payload",
                    return_value=self._fake_git_inventory(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.active_execution_payload",
                    return_value=self._fake_active_execution(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.fallback_status_payload",
                    return_value=self._fake_fallback_status(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.github_auth_summary",
                    return_value=self._fake_github_auth(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.agent_enablement_payload",
                    return_value=self._fake_agent_enablement(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.rules_projections_payload",
                    return_value=self._fake_rules_projections(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.atlassian_connectivity_summary",
                    return_value=self._fake_atlassian(),
                ),
                patch(
                    "scripts.ai_session_startup_lib.pea_status_payload",
                    return_value=self._fake_pea_status(),
                ),
            ):
                payload = startup_session_payload(repo_root, pending_action="concluir_primeiro")

        self.assertEqual(payload["pending_chat_contract_count"], 2)
        self.assertEqual(payload["agent_identity"]["active_display_name"], "Engenheiro Agentes IA")
        self.assertEqual(
            payload["agent_enablement"]["overlay_path"], "config/ai/agent-enablement.yaml"
        )
        self.assertEqual(
            payload["rules_projections"]["catalog_path"], ".agents/rules/projections.yaml"
        )
        self.assertEqual(payload["pea_status"]["status"], "ok")
        self.assertEqual(payload["prioritized_work_item"]["identifier"], "DOT-177")
        self.assertEqual(payload["startup_drift"]["status"], "clean")
        self.assertEqual(payload["startup_governor_status"]["state"], "ready_for_work")
        self.assertTrue(payload["startup_governor_status"]["clearance_granted"])


if __name__ == "__main__":
    unittest.main()
