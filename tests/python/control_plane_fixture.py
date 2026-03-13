from __future__ import annotations

import textwrap
from collections.abc import Mapping
from pathlib import Path


def _normalized_text(content: str) -> str:
    stripped = textwrap.dedent(content).strip()
    return f"{stripped}\n" if stripped else ""


def write_test_control_plane(
    repo_root: Path,
    *,
    agents_toml: str,
    platforms_yaml: str,
    registry_display_names: Mapping[str, str] | None = None,
    startup_toml: str | None = None,
    orchestration_toml: str | None = None,
    communication_toml: str | None = None,
    operation_manifest_toml: str | None = None,
    reviews_toml: str | None = None,
) -> None:
    root_config_dir = repo_root / "config"
    app_config_dir = repo_root / "app" / "config"
    agents_config_dir = repo_root / ".agents" / "config"
    registry_dir = repo_root / ".agents" / "registry"
    docs_dir = repo_root / "docs"

    root_config_dir.mkdir(parents=True, exist_ok=True)
    app_config_dir.mkdir(parents=True, exist_ok=True)
    agents_config_dir.mkdir(parents=True, exist_ok=True)
    registry_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    (root_config_dir / "config.toml").write_text(
        _normalized_text(
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
    (root_config_dir / "dev.toml").write_text("version = 1\n", encoding="utf-8")
    (root_config_dir / "integrations.toml").write_text(
        _normalized_text(
            """\
            version = 1

            [atlassian]
            platforms = "config/platforms.yaml"
            """
        ),
        encoding="utf-8",
    )
    (root_config_dir / "quality.toml").write_text(
        _normalized_text(
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
    (root_config_dir / "schema.json").write_text("{}\n", encoding="utf-8")
    (root_config_dir / "time-surfaces.yaml").write_text(
        "version: 1\nsurfaces: {}\n", encoding="utf-8"
    )
    (root_config_dir / "platforms.yaml").write_text(
        _normalized_text(platforms_yaml), encoding="utf-8"
    )

    (app_config_dir / "config.toml").write_text(
        _normalized_text(
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
            """
        ),
        encoding="utf-8",
    )
    (app_config_dir / "runtime.toml").write_text(
        _normalized_text(
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
    (app_config_dir / "schema.json").write_text("{}\n", encoding="utf-8")

    (agents_config_dir / "config.toml").write_text(
        _normalized_text(
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
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "agents.toml").write_text(
        _normalized_text(agents_toml), encoding="utf-8"
    )
    (agents_config_dir / "communication.toml").write_text(
        _normalized_text(
            communication_toml
            or """\
            version = 1

            [chat]
            timestamp_surface = "chat"
            timestamp_source = "local_system_clock"
            body_starts_on_next_line = true
            visible_name_fallback_order = ["chat_alias", "display_name", "technical_id"]
            display_name_source = ".agents/config/agents.toml::source_of_truth.display_name_registry"

            [jira.fields]
            current_agent_role = "Current Agent Role"
            next_required_role = "Next Required Role"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "startup.toml").write_text(
        _normalized_text(
            startup_toml
            or """\
            version = 1

            [startup]
            owner_role = "ai-startup-governor"
            readiness_artifact = ".cache/ai/startup-ready.json"

            [handoff]
            chat_contract_ref = ".agents/config/communication.toml::chat"

            [workflow]
            always_enabled_columns = ["Backlog", "Doing", "Review", "Done"]
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "orchestration.toml").write_text(
        _normalized_text(
            orchestration_toml
            or """\
            version = 1

            [paths]
            capability_matrix = ".agents/orchestration/capability-matrix.yaml"
            routing_policy = ".agents/orchestration/routing-policy.yaml"
            task_card_schema = ".agents/orchestration/task-card.schema.json"
            delegation_plan_schema = ".agents/orchestration/delegation-plan.schema.json"

            [delegation]
            require_owner_issue = true
            require_startup_artifact = true
            require_applicable_rules = true
            config_ref_convention = "arquivo::chave"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "reviews.toml").write_text(
        _normalized_text(
            reviews_toml
            or """\
            version = 1

            [paths]
            review_output_schema = ".agents/config/review-output.schema.json"
            review_ledger = "docs/AI-REVIEW-LEDGER.md"
            orthography_ledger = "docs/AI-ORTHOGRAPHY-LEDGER.md"
            """
        ),
        encoding="utf-8",
    )
    (agents_config_dir / "prompts.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "migration-matrix.yaml").write_text(
        "version: 1\nentries: []\n", encoding="utf-8"
    )
    (agents_config_dir / "schema.json").write_text("{}\n", encoding="utf-8")
    (agents_config_dir / "review-output.schema.json").write_text("{}\n", encoding="utf-8")

    (repo_root / ".agents" / "config.toml").write_text(
        _normalized_text(
            operation_manifest_toml
            or """\
            version = 1

            [config_context]
            manifest = ".agents/config/config.toml"
            mode = "repo-canonical"

            [identity]
            registry_root = ".agents/registry"
            display_name_field = "display_name"
            card_title_mirror_required = true
            fallback_display = "technical-id"
            """
        ),
        encoding="utf-8",
    )

    for agent_id, display_name in (registry_display_names or {}).items():
        (registry_dir / f"{agent_id}.toml").write_text(
            _normalized_text(
                f"""\
                id = "{agent_id}"
                display_name = "{display_name}"
                """
            ),
            encoding="utf-8",
        )
