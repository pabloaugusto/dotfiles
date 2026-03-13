from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import textwrap
import unittest
from unittest.mock import patch

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    clear_secret_resolver_cache,
    github_blob_url,
    linkify_repo_relative_paths,
    load_ai_control_plane,
    normalize_github_remote_url,
    resolve_atlassian_platform,
    resolve_repo_web_context,
    resolve_value_spec,
    service_account_ratelimit_payload,
    summary_payload,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]


def write_control_plane(
    repo_root: pathlib.Path,
    *,
    enable_seo: bool = False,
    site_url_spec: str = "env://ATLASSIAN_SITE_URL",
    token_spec: str = "env://ATLASSIAN_API_TOKEN",
    enable_po_actor: bool = False,
    include_po_jira_assignee: bool = True,
) -> None:
    config_dir = repo_root / "config" / "ai"
    root_config_dir = repo_root / "config"
    app_config_dir = repo_root / "app" / "config"
    agents_config_dir = repo_root / ".agents" / "config"
    registry_dir = repo_root / ".agents" / "registry"
    config_dir.mkdir(parents=True)
    root_config_dir.mkdir(parents=True, exist_ok=True)
    app_config_dir.mkdir(parents=True, exist_ok=True)
    agents_config_dir.mkdir(parents=True, exist_ok=True)
    registry_dir.mkdir(parents=True)
    (root_config_dir / "config.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [project]
            id = "dotfiles"
            source_of_truth = "config/config.toml"
            default_config_ref_convention = "arquivo::chave"

            [contexts]
            dev_root = "config"
            dev_manifest = "config/config.toml"
            runtime_root = "app/config"
            runtime_manifest = "app/config/config.toml"
            ai_root = ".agents/config"
            ai_manifest = ".agents/config/config.toml"

            [resolution]
            precedence = ["defaults", "context_config", "domain_files", "local_overlay", "environment", "cli"]
            literal_lint_enabled = true
            generated_tables_enabled = true
            single_resolution_library_required = true

            [regionalization]
            timezone_name = "America/Sao_Paulo"
            locale = "pt-BR"
            language = "pt-BR"
            currency = "BRL"
            calendar_system = "gregorian"

            [domains]
            dev = "config/dev.toml"
            integrations = "config/integrations.toml"
            quality = "config/quality.toml"
            time_surfaces = "config/time-surfaces.yaml"
            schema = "config/schema.json"
            """
        ),
        encoding="utf-8",
    )
    (root_config_dir / "dev.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [context]
            kind = "dev"
            """
        ),
        encoding="utf-8",
    )
    (root_config_dir / "integrations.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [context]
            kind = "dev-integrations"
            """
        ),
        encoding="utf-8",
    )
    (root_config_dir / "quality.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [literal_lint]
            enabled = true
            scope = ["docs", "scripts", ".agents", "config"]
            allowlist = []
            """
        ),
        encoding="utf-8",
    )
    (root_config_dir / "schema.json").write_text("{}", encoding="utf-8")
    (root_config_dir / "time-surfaces.yaml").write_text(
        "version: 1\nsurfaces: {}\n", encoding="utf-8"
    )
    (app_config_dir / "config.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [context]
            kind = "runtime"
            source_of_truth = "app/config/config.toml"
            inherits_regionalization = "config/config.toml::regionalization"

            [domains]
            runtime = "app/config/runtime.toml"
            bootstrap = "app/config/bootstrap.toml"
            links = "app/config/links.toml"
            schema = "app/config/schema.json"

            [compatibility]
            legacy_df_root = "app/df"
            legacy_bootstrap_root = "app/bootstrap"
            """
        ),
        encoding="utf-8",
    )
    (app_config_dir / "runtime.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [regionalization]
            defaults = "config/config.toml::regionalization"
            surfaces = "config/time-surfaces.yaml::surfaces"
            """
        ),
        encoding="utf-8",
    )
    (app_config_dir / "bootstrap.toml").write_text("version = 1\n", encoding="utf-8")
    (app_config_dir / "links.toml").write_text("version = 1\n", encoding="utf-8")
    (app_config_dir / "schema.json").write_text("{}", encoding="utf-8")
    (agents_config_dir / "config.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [context]
            kind = "ai"
            source_of_truth = ".agents/config/config.toml"
            inherits_regionalization = "config/config.toml::regionalization"

            [domains]
            agents = ".agents/config/agents.toml"
            communication = ".agents/config/communication.toml"
            startup = ".agents/config/startup.toml"
            orchestration = ".agents/config/orchestration.toml"
            reviews = ".agents/config/reviews.toml"
            prompts = ".agents/config/prompts.toml"
            migration_matrix = ".agents/config/migration-matrix.yaml"
            schema = ".agents/config/schema.json"

            [compatibility]
            bridge_manifest = ".agents/config.toml"
            legacy_control_plane_root = "config/ai"
            legacy_agents = "config/ai/agents.yaml"
            legacy_agent_enablement = "config/ai/agent-enablement.yaml"
            legacy_agent_runtime = "config/ai/agent-runtime.yaml"
            legacy_agent_operations = "config/ai/agent-operations.yaml"
            legacy_contracts = "config/ai/contracts.yaml"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "agents.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [source_of_truth]
            display_name_registry = ".agents/registry/*.toml::display_name"

            [identity]
            display_name_source = ".agents/registry/*.toml::display_name"
            chat_alias_source = "config/ai/agent-runtime.yaml::roles"
            enablement_source = "config/ai/agent-enablement.yaml::roles"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "communication.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [chat]
            prefix_template = "[{timestamp}] **{visible_name}**"
            timestamp_display_pattern = "dd-mm hh:mm"
            timestamp_surface = "chat"
            timestamp_source = "local_system_clock"
            body_starts_on_next_line = true
            visible_name_fallback_order = ["chat_alias", "display_name", "technical_id"]
            display_name_source = ".agents/config/agents.toml::source_of_truth.display_name_registry"

            [jira.fields]
            current_agent_role = "Current Agent Role"
            next_required_role = "Next Required Role"

            [literal_lint]
            managed_literals = ["[{timestamp}] **{visible_name}**", "dd-mm hh:mm"]
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "startup.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [startup]
            owner_role = "ai-startup-governor"
            audit_owner_role = "ai-scrum-master"
            report_path = ".cache/ai/startup-session.md"
            readiness_artifact = ".cache/ai/startup-ready.json"
            clearance_required = true
            report_key = "startup_governor_status"

            [handoff]
            current_chat_owner_role = "ai-startup-governor"
            blocked_before_ready = true
            next_owner_resolution = "active_execution_agent"
            chat_contract_ref = ".agents/config/communication.toml::chat"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "orchestration.toml").write_text(
        textwrap.dedent(
            """\
            version = 1

            [paths]
            capability_matrix = ".agents/orchestration/capability-matrix.yaml"
            routing_policy = ".agents/orchestration/routing-policy.yaml"
            task_card_schema = ".agents/orchestration/task-card.schema.json"
            delegation_plan_schema = ".agents/orchestration/delegation-plan.schema.json"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "reviews.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "prompts.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "migration-matrix.yaml").write_text(
        "version: 1\nentries: []\n", encoding="utf-8"
    )
    (agents_config_dir / "schema.json").write_text("{}", encoding="utf-8")
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
    (registry_dir / "pascoalete.toml").write_text(
        'id = "pascoalete"\ndisplay_name = "Pascoalete"\n',
        encoding="utf-8",
    )
    (config_dir / "agents.yaml").write_text(
        textwrap.dedent(
            f"""\
            version: 1
            roles:
              ai-product-owner:
                enabled: true
                required: true
              ai-browser-validator:
                enabled: false
                required: false
              ai-seo-specialist:
                enabled: {"true" if enable_seo else "false"}
                required: false
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "agent-enablement.yaml").write_text(
        textwrap.dedent(
            f"""\
            version: 1
            defaults:
              registry_agents_enabled_by_default: true
            roles:
              ai-product-owner:
                enabled: true
              ai-browser-validator:
                enabled: false
              ai-seo-specialist:
                enabled: {"true" if enable_seo else "false"}
            registry_agents:
              pascoalete:
                enabled: true
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "agent-operations.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            roles:
              ai-product-owner:
                jira:
                  primary_issue_actions:
                    - create-top-level-issue
              ai-browser-validator:
                jira:
                  primary_issue_actions:
                    - browser-validation
              ai-seo-specialist:
                jira:
                  primary_issue_actions:
                    - seo-review
            """
        ),
        encoding="utf-8",
    )
    po_actor_block = ""
    if enable_po_actor:
        po_actor_block = (
            "                atlassian_actor:\n"
            "                  enabled: true\n"
            "                  fallback_to_global_on_error: true\n"
            "                  email_secret_ref: op://secrets/dotfiles/atlassian-service-accounts/ai-product-owner-email\n"
            "                  token_secret_ref: op://secrets/dotfiles/atlassian-service-accounts/ai-product-owner-api-token\n"
            "                  account_id_secret_ref: op://secrets/dotfiles/atlassian-service-accounts/ai-product-owner-id\n"
            "                  search_fallback:\n"
            "                    enabled: true\n"
            "                    query: ia-product-owner\n"
            "                    expected_display_name: ia-product-owner\n"
            "                  surfaces:\n"
            "                    jira-comment:\n"
            "                      enabled: true\n"
            "                    jira-assignee:\n"
            "                      enabled: true\n"
            "                    confluence-comment:\n"
            "                      enabled: false\n"
            "                    confluence-page:\n"
            "                      enabled: false\n"
        )

    po_jira_assignee_block = ""
    if include_po_jira_assignee:
        po_jira_assignee_block = (
            "                jira_assignee:\n                  account_id: account-po\n"
        )

    (config_dir / "agent-runtime.yaml").write_text(
        textwrap.dedent(
            f"""\
            version: 1
            policies:
              enabled_role_statuses: [operational, consultive]
              required_role_statuses: [operational, consultive]
              enabled_registry_statuses: [operational, consultive]
              chat_owner_statuses: [operational, consultive]
              chat_name_fallback_order: [chat_alias, display_name, technical_id]
            roles:
              ai-product-owner:
                status: operational
                chat_alias: PO
                chat_owner_supported: true
                owner_mode: primary
                surfaces: [jira, chat]
                process_scopes: [backlog]
{po_jira_assignee_block}{po_actor_block}                runtime_artifacts:
                  - config/ai/agents.yaml
              ai-browser-validator:
                status: disabled_stub
                chat_alias: Browser Validator
                chat_owner_supported: false
                owner_mode: optional
                surfaces: [browser]
                process_scopes: [browser-validation]
                runtime_artifacts:
                  - config/ai/agents.yaml
              ai-seo-specialist:
                status: {"operational" if enable_seo else "disabled_stub"}
                chat_alias: SEO Specialist
                chat_owner_supported: {"true" if enable_seo else "false"}
                owner_mode: optional
                surfaces: [jira, chat]
                process_scopes: [seo-review]
                jira_assignee:
                  account_id: {"account-seo" if enable_seo else '""'}
                runtime_artifacts:
                  - config/ai/agents.yaml
            registry_agents:
              pascoalete:
                status: operational
                chat_alias: Pascoalete
                chat_owner_supported: true
                owner_mode: consultive
                surfaces: [chat, docs]
                process_scopes: [linguistic-review]
                runtime_artifacts:
                  - .agents/registry/pascoalete.toml
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "contracts.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            workflow:
              always_enabled_columns:
                - Backlog
                - Ready
              optional_columns:
                - name: SEO Review
                  enabled_when_role: ai-seo-specialist
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "platforms.yaml").write_text(
        textwrap.dedent(
            f"""\
            version: 1
            platforms:
              atlassian:
                enabled: true
                provider: atlassian-cloud
                auth:
                  mode: service-account-api-token
                  site_url: "{site_url_spec}"
                  email: "env://ATLASSIAN_EMAIL"
                  token: "{token_spec}"
                  service_account: "env://ATLASSIAN_SERVICE_ACCOUNT"
                  cloud_id: "env://ATLASSIAN_CLOUD_ID"
                jira:
                  enabled: true
                  project_key: "env://ATLASSIAN_PROJECT_KEY"
                confluence:
                  enabled: true
                  space_key: "env://ATLASSIAN_SPACE_KEY"
            """
        ),
        encoding="utf-8",
    )


class AiControlPlaneTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_secret_resolver_cache()

    def tearDown(self) -> None:
        clear_secret_resolver_cache()

    def test_summary_payload_uses_temp_control_plane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            payload = summary_payload(repo_root)
        self.assertIn("ai-product-owner", payload["enabled_roles"])
        self.assertIn("ai-browser-validator", payload["disabled_roles"])
        self.assertNotIn("SEO Review", payload["workflow_columns"])
        self.assertTrue(payload["platforms"]["atlassian"]["uses_env_site_url"])
        self.assertFalse(payload["local_overrides"]["platforms"])
        self.assertEqual(
            payload["role_enablement"]["declared_roles"],
            ["ai-browser-validator", "ai-product-owner", "ai-seo-specialist"],
        )
        self.assertIn("pascoalete", payload["enabled_registry_agents"])
        self.assertEqual(payload["role_operation_coverage"]["missing_roles"], [])
        self.assertEqual(payload["role_runtime_coverage"]["missing_roles"], [])
        self.assertEqual(payload["registry_runtime_coverage"]["missing_registry_agents"], [])
        self.assertEqual(
            payload["runtime_operability"]["enabled_roles_without_operational_runtime"],
            [],
        )
        self.assertEqual(
            payload["chat_identity_runtime"]["enabled_role_visible_names_by_id"][
                "ai-product-owner"
            ],
            "PO",
        )

    def test_optional_workflow_column_is_enabled_by_role_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(
                repo_root, enable_seo=True, site_url_spec="https://example.atlassian.net"
            )
            control_plane = load_ai_control_plane(repo_root)
            self.assertIn("SEO Review", control_plane.effective_workflow_columns())

    def test_visible_name_for_reference_prefers_alias_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            control_plane = load_ai_control_plane(repo_root)
            self.assertEqual(control_plane.visible_name_for_reference("ai-product-owner"), "PO")
            self.assertEqual(control_plane.visible_name_for_reference("PO"), "PO")

    def test_communication_manifest_drives_chat_order_and_jira_field_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / ".agents" / "config" / "communication.toml").write_text(
                textwrap.dedent(
                    """\
                    version = 1

                    [chat]
                    prefix_template = "[{timestamp}] **{visible_name}**"
                    timestamp_display_pattern = "dd-mm hh:mm"
                    timestamp_surface = "chat"
                    timestamp_source = "local_system_clock"
                    body_starts_on_next_line = true
                    visible_name_fallback_order = ["display_name", "technical_id"]
                    display_name_source = ".agents/config/agents.toml::source_of_truth.display_name_registry"

                    [jira.fields]
                    current_agent_role = "Agente Atual"
                    next_required_role = "Proximo Papel"

                    [literal_lint]
                    managed_literals = ["[{timestamp}] **{visible_name}**", "dd-mm hh:mm"]
                    """
                ),
                encoding="utf-8",
            )
            control_plane = load_ai_control_plane(repo_root)
            self.assertEqual(
                control_plane.chat_name_fallback_order(),
                ["display_name", "technical_id"],
            )
            self.assertEqual(control_plane.jira_field_name("current_agent_role"), "Agente Atual")
            self.assertEqual(control_plane.jira_field_name("next_required_role"), "Proximo Papel")

    def test_summary_payload_reports_roles_with_own_atlassian_actor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root, enable_po_actor=True)
            payload = summary_payload(repo_root)

        self.assertEqual(
            payload["runtime_operability"]["enabled_roles_with_atlassian_actor"],
            ["ai-product-owner"],
        )
        self.assertEqual(
            payload["runtime_operability"]["atlassian_actor_surface_matrix"]["ai-product-owner"],
            ["jira-assignee", "jira-comment"],
        )

    def test_actor_assignee_surface_counts_as_mapping_without_legacy_account_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(
                repo_root,
                enable_po_actor=True,
                include_po_jira_assignee=False,
            )
            control_plane = load_ai_control_plane(repo_root)

        self.assertTrue(control_plane.role_has_jira_assignee_mapping("ai-product-owner"))
        self.assertIn("ai-product-owner", control_plane.jira_assignable_roles())
        self.assertNotIn(
            "ai-product-owner",
            control_plane.enabled_roles_missing_jira_assignee_mapping(),
        )

    def test_local_overlay_overrides_base_specs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / "config" / "ai" / "platforms.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    platforms:
                      atlassian:
                        auth:
                          site_url: "op://vault/item/section/site-url"
                          token: "op://vault/item/section/api-token"
                    """
                ),
                encoding="utf-8",
            )
            (repo_root / "config" / "ai" / "agent-enablement.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    roles:
                      ai-browser-validator:
                        enabled: true
                    """
                ),
                encoding="utf-8",
            )
            payload = summary_payload(repo_root)
            control_plane = load_ai_control_plane(repo_root)
            definition = control_plane.atlassian_definition()
            self.assertTrue(payload["local_overrides"]["platforms"])
            self.assertTrue(payload["local_overrides"]["agent_enablement"])
            self.assertFalse(payload["platforms"]["atlassian"]["uses_env_site_url"])
            self.assertEqual(definition.site_url_spec, "op://vault/item/section/site-url")
            self.assertEqual(definition.token_spec, "op://vault/item/section/api-token")
            self.assertIn("ai-browser-validator", payload["enabled_roles"])
            self.assertIn("ai-browser-validator", payload["role_enablement"]["overridden_roles"])

    def test_summary_payload_reports_disabled_registry_agent_from_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / "config" / "ai" / "agent-enablement.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    registry_agents:
                      pascoalete:
                        enabled: false
                    """
                ),
                encoding="utf-8",
            )

            payload = summary_payload(repo_root)

        self.assertIn("pascoalete", payload["disabled_registry_agents"])

    def test_summary_payload_reports_missing_role_operation_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / "config" / "ai" / "agent-operations.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    roles:
                      ai-product-owner:
                        jira:
                          primary_issue_actions:
                            - create-top-level-issue
                    """
                ),
                encoding="utf-8",
            )
            payload = summary_payload(repo_root)

        self.assertIn("ai-browser-validator", payload["role_operation_coverage"]["missing_roles"])
        self.assertIn("ai-seo-specialist", payload["role_operation_coverage"]["missing_roles"])

    def test_summary_payload_reports_required_roles_disabled_by_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / "config" / "ai" / "agent-enablement.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    roles:
                      ai-product-owner:
                        enabled: false
                    """
                ),
                encoding="utf-8",
            )

            payload = summary_payload(repo_root)

        self.assertIn("ai-product-owner", payload["disabled_roles"])
        self.assertEqual(
            payload["role_enablement"]["required_roles_disabled"], ["ai-product-owner"]
        )

    def test_load_ai_control_plane_rejects_unknown_enablement_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / "config" / "ai" / "agent-enablement.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    roles:
                      ai-agente-fantasma:
                        enabled: false
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(AiControlPlaneError) as ctx:
                load_ai_control_plane(repo_root).enabled_roles()

        self.assertIn("roles desconhecidos", str(ctx.exception))

    def test_load_ai_control_plane_rejects_unknown_registry_agent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            (repo_root / "config" / "ai" / "agent-enablement.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    registry_agents:
                      agente-fantasma:
                        enabled: false
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(AiControlPlaneError) as ctx:
                load_ai_control_plane(repo_root).disabled_registry_agents()

        self.assertIn("agentes declarativos desconhecidos", str(ctx.exception))

    def test_resolve_value_spec_reads_env_values(self) -> None:
        old_value = os.environ.get("ATLASSIAN_SITE_URL")
        self.addCleanup(self._restore_env, "ATLASSIAN_SITE_URL", old_value)
        os.environ["ATLASSIAN_SITE_URL"] = "https://env.atlassian.net"
        self.assertEqual(
            resolve_value_spec("env://ATLASSIAN_SITE_URL", repo_root=ROOT),
            "https://env.atlassian.net",
        )

    def test_normalize_github_remote_url_supports_ssh_origin(self) -> None:
        self.assertEqual(
            normalize_github_remote_url("git@github.com:pabloaugusto/dotfiles.git"),
            "https://github.com/pabloaugusto/dotfiles",
        )

    def test_resolve_repo_web_context_reads_origin_and_default_branch(self) -> None:
        def fake_run_command(
            args: list[str],
            *,
            cwd: pathlib.Path | None = None,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            if args == ["git", "remote", "get-url", "origin"]:
                return subprocess.CompletedProcess(
                    args=args,
                    returncode=0,
                    stdout="git@github.com:pabloaugusto/dotfiles.git\n",
                    stderr="",
                )
            if args == ["git", "symbolic-ref", "refs/remotes/origin/HEAD"]:
                return subprocess.CompletedProcess(
                    args=args,
                    returncode=0,
                    stdout="refs/remotes/origin/main\n",
                    stderr="",
                )
            raise AssertionError(args)

        with patch("scripts.ai_control_plane_lib.run_command", side_effect=fake_run_command):
            context = resolve_repo_web_context(ROOT)

        self.assertEqual(context.github_base_url, "https://github.com/pabloaugusto/dotfiles")
        self.assertEqual(context.default_branch, "main")

    def test_github_blob_url_uses_default_branch(self) -> None:
        with patch(
            "scripts.ai_control_plane_lib.resolve_repo_web_context",
            return_value=type(
                "RepoWebContextStub",
                (),
                {
                    "github_base_url": "https://github.com/pabloaugusto/dotfiles",
                    "default_branch": "main",
                },
            )(),
        ):
            url = github_blob_url(ROOT, "docs/AI-WIP-TRACKER.md")

        self.assertEqual(
            url,
            "https://github.com/pabloaugusto/dotfiles/blob/main/docs/AI-WIP-TRACKER.md",
        )

    def test_linkify_repo_relative_paths_converts_tracked_file_references(self) -> None:
        text = "Evidencias:\n- docs/AI-WIP-TRACKER.md\n- ROADMAP.md"
        linked = linkify_repo_relative_paths(text, repo_root=ROOT)

        self.assertIn(
            "[docs/AI-WIP-TRACKER.md](https://github.com/pabloaugusto/dotfiles/blob/main/docs/AI-WIP-TRACKER.md)",
            linked,
        )
        self.assertIn(
            "[ROADMAP.md](https://github.com/pabloaugusto/dotfiles/blob/main/ROADMAP.md)",
            linked,
        )

    def test_linkify_repo_relative_paths_ignores_untracked_runtime_paths(self) -> None:
        with patch(
            "scripts.ai_control_plane_lib.resolve_repo_web_context",
            return_value=type(
                "RepoWebContextStub",
                (),
                {
                    "github_base_url": "https://github.com/pabloaugusto/dotfiles",
                    "default_branch": "main",
                },
            )(),
        ):
            with patch(
                "scripts.ai_control_plane_lib.resolve_tracked_repo_files",
                return_value={"docs/AI-WIP-TRACKER.md"},
            ):
                linked = linkify_repo_relative_paths(
                    "Evidencia: .cache/playwright/atlassian/storage-state.json",
                    repo_root=ROOT,
                )

        self.assertEqual(linked, "Evidencia: .cache/playwright/atlassian/storage-state.json")

    def test_github_blob_url_preserves_dot_prefixed_paths(self) -> None:
        with patch(
            "scripts.ai_control_plane_lib.resolve_repo_web_context",
            return_value=type(
                "RepoWebContextStub",
                (),
                {
                    "github_base_url": "https://github.com/pabloaugusto/dotfiles",
                    "default_branch": "main",
                },
            )(),
        ):
            url = github_blob_url(ROOT, ".github/pull_request_template.md")

        self.assertEqual(
            url,
            "https://github.com/pabloaugusto/dotfiles/blob/main/.github/pull_request_template.md",
        )

    def test_resolve_value_spec_reads_op_item_once_for_multiple_fields(self) -> None:
        item_payload = {
            "fields": [
                {"id": "site-url", "label": "site-url", "value": "https://example.atlassian.net"},
                {"id": "api-token", "label": "api-token", "value": "token-123"},
            ]
        }
        ratelimit_completed = subprocess.CompletedProcess(
            args=["op", "service-account", "ratelimit", "--format", "json"],
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "type": "account",
                        "action": "read_write",
                        "limit": 1000,
                        "used": 10,
                        "remaining": 990,
                        "reset": 1800,
                    }
                ]
            )
            + "\n",
            stderr="",
        )
        item_completed = subprocess.CompletedProcess(
            args=["op", "item", "get", "dotfiles", "--vault", "secrets", "--format", "json"],
            returncode=0,
            stdout=f"{json.dumps(item_payload)}\n",
            stderr="",
        )

        def fake_run_command(
            args: list[str],
            *,
            cwd: pathlib.Path | None = None,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            if args == ["op", "service-account", "ratelimit", "--format", "json"]:
                return ratelimit_completed
            raise AssertionError(args)

        with patch(
            "scripts.ai_control_plane_lib.run_command", side_effect=fake_run_command
        ) as mocked:
            with patch(
                "scripts.ai_control_plane_lib.run_op_command",
                return_value=item_completed,
            ) as mocked_op:
                site_url = resolve_value_spec("op://secrets/dotfiles/site-url", repo_root=ROOT)
                token = resolve_value_spec("op://secrets/dotfiles/api-token", repo_root=ROOT)

        self.assertEqual(site_url, "https://example.atlassian.net")
        self.assertEqual(token, "token-123")
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(
            mocked_op.call_args.args[0],
            ["op", "item", "get", "dotfiles", "--vault", "secrets", "--format", "json"],
        )

    def test_resolve_atlassian_platform_batches_op_refs_with_op_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(
                repo_root,
                site_url_spec="op://secrets/dotfiles/site-url",
                token_spec="op://secrets/dotfiles/api-token",
            )
            (repo_root / "config" / "ai" / "platforms.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    platforms:
                      atlassian:
                        auth:
                          email: "op://secrets/dotfiles/email"
                          service_account: "op://secrets/dotfiles/service-account"
                          cloud_id: "op://secrets/dotfiles/cloud-id"
                        jira:
                          project_key: "op://secrets/dotfiles/project-key"
                        confluence:
                          space_key: "op://secrets/dotfiles/space-key"
                    """
                ),
                encoding="utf-8",
            )
            control_plane = load_ai_control_plane(repo_root)

            ratelimit_completed = subprocess.CompletedProcess(
                args=["op", "service-account", "ratelimit", "--format", "json"],
                returncode=0,
                stdout=json.dumps(
                    [
                        {
                            "type": "account",
                            "action": "read_write",
                            "limit": 1000,
                            "used": 10,
                            "remaining": 990,
                            "reset": 1800,
                        }
                    ]
                )
                + "\n",
                stderr="",
            )

            def fake_run_command(
                args: list[str],
                *,
                cwd: pathlib.Path | None = None,
                check: bool = True,
            ) -> subprocess.CompletedProcess[str]:
                self.assertEqual(cwd, repo_root)
                if args == ["op", "service-account", "ratelimit", "--format", "json"]:
                    return ratelimit_completed
                raise AssertionError(args)

            def fake_run_op_command(
                args: list[str],
                *,
                cwd: pathlib.Path | None = None,
                max_attempts: int = 3,
                initial_delay_seconds: int = 5,
            ) -> subprocess.CompletedProcess[str]:
                self.assertEqual(cwd, repo_root)
                self.assertEqual(args[:4], ["op", "run", "--env-file", args[3]])
                env_file = pathlib.Path(args[3])
                env_map: dict[str, str] = {}
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    name, ref = line.split("=", 1)
                    field = ref.rsplit("/", 1)[-1]
                    match field:
                        case "site-url":
                            env_map[name] = "https://batch.atlassian.net"
                        case "email":
                            env_map[name] = "bot@example.com"
                        case "api-token":
                            env_map[name] = "token-xyz"
                        case "service-account":
                            env_map[name] = "dotfiles-ai-atlassian"
                        case "cloud-id":
                            env_map[name] = "cloud-123"
                        case "project-key":
                            env_map[name] = "DOT"
                        case "space-key":
                            env_map[name] = "DOT"
                        case _:
                            env_map[name] = field
                return subprocess.CompletedProcess(
                    args=args,
                    returncode=0,
                    stdout=f"{json.dumps(env_map)}\n",
                    stderr="",
                )

            with patch(
                "scripts.ai_control_plane_lib.run_command", side_effect=fake_run_command
            ) as mocked:
                with patch(
                    "scripts.ai_control_plane_lib.run_op_command", side_effect=fake_run_op_command
                ):
                    resolved = resolve_atlassian_platform(
                        control_plane.atlassian_definition(),
                        repo_root=repo_root,
                    )

        self.assertEqual(resolved.site_url, "https://batch.atlassian.net")
        self.assertEqual(resolved.email, "bot@example.com")
        self.assertEqual(resolved.token, "token-xyz")
        self.assertEqual(resolved.service_account, "dotfiles-ai-atlassian")
        self.assertEqual(resolved.cloud_id, "cloud-123")
        self.assertEqual(resolved.jira_project_key, "DOT")
        self.assertEqual(resolved.confluence_space_key, "DOT")
        self.assertEqual(mocked.call_count, 1)

    def test_service_account_ratelimit_payload_detects_exhausted_account_limit(self) -> None:
        ratelimit_rows = [
            {
                "type": "token",
                "action": "read",
                "limit": 1000,
                "used": 42,
                "remaining": 958,
                "reset": 2198,
            },
            {
                "type": "account",
                "action": "read_write",
                "limit": 1000,
                "used": 1000,
                "remaining": 0,
                "reset": 65309,
            },
        ]
        completed = subprocess.CompletedProcess(
            args=["op", "service-account", "ratelimit", "--format", "json"],
            returncode=0,
            stdout=f"{json.dumps(ratelimit_rows)}\n",
            stderr="",
        )
        with patch("scripts.ai_control_plane_lib.run_command", return_value=completed) as mocked:
            payload = service_account_ratelimit_payload(ROOT, force_refresh=True)

        self.assertTrue(payload["account_read_write_exhausted"])
        self.assertEqual(payload["account_read_write"]["remaining"], 0)
        self.assertEqual(payload["account_read_write"]["reset_human"], "18:08:29")
        self.assertEqual(
            mocked.call_args.args[0],
            ["op", "service-account", "ratelimit", "--format", "json"],
        )

    def test_resolve_atlassian_platform_fails_fast_when_account_limit_is_exhausted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(
                repo_root,
                site_url_spec="op://secrets/dotfiles/site-url",
                token_spec="op://secrets/dotfiles/api-token",
            )
            (repo_root / "config" / "ai" / "platforms.local.yaml").write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    platforms:
                      atlassian:
                        auth:
                          email: "op://secrets/dotfiles/email"
                          service_account: "op://secrets/dotfiles/service-account"
                          cloud_id: "op://secrets/dotfiles/cloud-id"
                        jira:
                          project_key: "op://secrets/dotfiles/project-key"
                        confluence:
                          space_key: "op://secrets/dotfiles/space-key"
                    """
                ),
                encoding="utf-8",
            )
            control_plane = load_ai_control_plane(repo_root)
            ratelimit_rows = [
                {
                    "type": "account",
                    "action": "read_write",
                    "limit": 1000,
                    "used": 1000,
                    "remaining": 0,
                    "reset": 65309,
                }
            ]
            completed = subprocess.CompletedProcess(
                args=["op", "service-account", "ratelimit", "--format", "json"],
                returncode=0,
                stdout=f"{json.dumps(ratelimit_rows)}\n",
                stderr="",
            )
            with patch("scripts.ai_control_plane_lib.run_command", return_value=completed):
                with self.assertRaises(AiControlPlaneError) as ctx:
                    resolve_atlassian_platform(
                        control_plane.atlassian_definition(),
                        repo_root=repo_root,
                    )

        self.assertIn("rate limit esgotado", str(ctx.exception))

    def test_resolve_atlassian_platform_requires_env_site_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            control_plane = load_ai_control_plane(repo_root)
            old_value = os.environ.pop("ATLASSIAN_SITE_URL", None)
            self.addCleanup(self._restore_env, "ATLASSIAN_SITE_URL", old_value)
            with self.assertRaises(AiControlPlaneError):
                resolve_atlassian_platform(
                    control_plane.atlassian_definition(),
                    repo_root=repo_root,
                )

    @staticmethod
    def _restore_env(name: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(name, None)
            return
        os.environ[name] = value


if __name__ == "__main__":
    unittest.main()
