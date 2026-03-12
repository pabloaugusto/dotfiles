from __future__ import annotations

import pathlib
import tempfile
import textwrap
import unittest

from scripts.ai_atlassian_browser_auth_lib import (
    bootstrap_config,
    browser_auth_status,
    default_target_url,
    needs_reauthentication,
)


def write_control_plane(repo_root: pathlib.Path) -> None:
    config_dir = repo_root / "config" / "ai"
    config_dir.mkdir(parents=True)
    (config_dir / "agents.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            roles:
              ai-product-owner:
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
            defaults:
              registry_agents_enabled_by_default: true
            roles:
              ai-product-owner:
                enabled: true
            registry_agents: {}
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
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "agent-runtime.yaml").write_text(
        textwrap.dedent(
            """\
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
                runtime_artifacts:
                  - config/ai/agents.yaml
            registry_agents: {}
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
                - Doing
                - Done
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "platforms.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            platforms:
              atlassian:
                enabled: true
                provider: atlassian-cloud
                auth:
                  mode: basic-api-token
                  site_url: "https://example.atlassian.net"
                  email: "bot@example.com"
                  token: "token-123"
                  service_account: "svc"
                  cloud_id: "cloud-123"
                jira:
                  enabled: true
                  project_key: "DOT"
                confluence:
                  enabled: true
                  space_key: "DOT"
            """
        ),
        encoding="utf-8",
    )


class AtlassianBrowserAuthTests(unittest.TestCase):
    def test_default_target_url_uses_confluence_space(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            self.assertEqual(
                default_target_url(repo_root),
                "https://example.atlassian.net/wiki/home",
            )

    def test_bootstrap_config_uses_repo_cache_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            config = bootstrap_config(repo_root=repo_root)

        self.assertTrue(str(config.storage_state_path).endswith("storage-state.json"))
        self.assertIn(".cache", str(config.evidence_dir))
        self.assertEqual(config.browser_name, "chromium")

    def test_needs_reauthentication_detects_login_flow(self) -> None:
        self.assertTrue(needs_reauthentication("https://id.atlassian.com/login"))
        self.assertTrue(needs_reauthentication("https://id.atlassian.com/login/two-step"))
        self.assertTrue(
            needs_reauthentication(
                "https://id.atlassian.com/join/user-access?resource=ari%3Acloud%3Aconfluence"
            )
        )
        self.assertFalse(
            needs_reauthentication("https://example.atlassian.net/wiki/spaces/DOT/pages/123")
        )

    def test_browser_auth_status_reports_missing_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_control_plane(repo_root)
            payload = browser_auth_status(repo_root=repo_root)

        self.assertFalse(payload["storage_state_exists"])
        self.assertIn("storage-state.json", payload["storage_state_path"])


if __name__ == "__main__":
    unittest.main()
