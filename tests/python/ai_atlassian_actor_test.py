from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.ai_atlassian_actor_lib import (
    ResolvedAtlassianActor,
    actor_runtime_state,
    clear_actor_resolution_caches,
    resolve_atlassian_actor,
    resolve_global_atlassian_actor,
    with_jira_actor,
)
from scripts.atlassian_platform_lib import AtlassianPlatformError


def write_actor_runtime(
    repo_root: Path,
    *,
    include_account_id_secret: bool = True,
) -> None:
    config_dir = repo_root / "config" / "ai"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "agents.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            roles:
              ai-product-owner:
                enabled: true
                required: true
                display_name: Product Owner
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
              ai-product-owner: {}
            """
        ),
        encoding="utf-8",
    )
    (config_dir / "contracts.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            workflow:
              always_enabled_columns: [Backlog, Doing, Done]
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
                  mode: service-account-api-token
                  site_url: https://example.atlassian.net
                  email: global@example.com
                  token: token-global
                  service_account: dotfiles-ai-atlassian
                  cloud_id: cloud-123
                jira:
                  enabled: true
                  project_key: DOT
                confluence:
                  enabled: true
                  space_key: DOT
            """
        ),
        encoding="utf-8",
    )
    account_id_block = ""
    if include_account_id_secret:
        account_id_block = "                  account_id_secret_ref: account-po\n"
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
                runtime_artifacts:
                  - config/ai/agent-runtime.yaml
                atlassian_actor:
                  enabled: true
                  fallback_to_global_on_error: true
                  email_secret_ref: ia-product-owner@example.com
                  token_secret_ref: token-po
{account_id_block}                  search_fallback:
                    enabled: true
                    prefer_email_lookup: true
                    query: ia-product-owner
                    expected_display_name: ia-product-owner
                    expected_account_type: app
                    require_active: true
                  surfaces:
                    jira-comment:
                      enabled: true
                    jira-assignee:
                      enabled: true
                    confluence-comment:
                      enabled: false
                    confluence-page:
                      enabled: false
            registry_agents: {{}}
            """
        ),
        encoding="utf-8",
    )
    startup_dir = repo_root / ".cache" / "ai"
    startup_dir.mkdir(parents=True, exist_ok=True)
    (startup_dir / "startup-ready.json").write_text(
        '{"startup_governor_status":{"context_fingerprint":"fp-actor-test"}}\n',
        encoding="utf-8",
    )


class DummyJiraAdapter:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def add_comment(self, issue_key: str, body_text: str) -> dict[str, str]:
        if self.fail:
            raise AtlassianPlatformError("forbidden")
        return {"id": "9001", "issue_key": issue_key, "body_text": body_text}


class AiAtlassianActorTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_actor_resolution_caches()

    def tearDown(self) -> None:
        clear_actor_resolution_caches()

    def test_resolve_comment_surface_uses_role_service_account(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_actor_runtime(repo_root)

            actor = resolve_atlassian_actor(repo_root, "ai-product-owner", "jira-comment")

        self.assertEqual(actor.actor_mode, "role-service-account")
        self.assertEqual(actor.role_visible_name, "PO")
        self.assertEqual(actor.email, "ia-product-owner@example.com")
        self.assertFalse(actor.search_fallback_used)

    def test_resolve_assignee_surface_uses_search_fallback_when_secret_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_actor_runtime(repo_root, include_account_id_secret=False)
            with patch(
                "scripts.ai_atlassian_actor_lib._resolve_user_account_id",
                return_value={
                    "account_id": "account-po",
                    "source": "search-email",
                    "search_type": "search-email",
                    "resolved_from_secret": False,
                },
            ), patch("scripts.ai_atlassian_actor_lib._notify_fallback_issue_if_needed"):
                actor = resolve_atlassian_actor(repo_root, "ai-product-owner", "jira-assignee")

        self.assertEqual(actor.account_id, "account-po")
        self.assertTrue(actor.search_fallback_used)
        self.assertEqual(actor.account_id_source, "search-email")

    def test_resolve_global_actor_is_best_effort_when_account_lookup_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_actor_runtime(repo_root)
            with patch(
                "scripts.ai_atlassian_actor_lib._resolve_user_account_id",
                side_effect=AtlassianPlatformError("lookup failed"),
            ):
                actor = resolve_global_atlassian_actor(repo_root, "ai-product-owner", "jira-comment")

            state = actor_runtime_state(repo_root)

        self.assertEqual(actor.actor_mode, "global-service-account")
        self.assertEqual(actor.account_id, "")
        self.assertEqual(actor.account_id_source, "global-unresolved")
        self.assertIn("global::ai-product-owner::jira-comment", state["resolutions"])
        self.assertNotIn("ai-product-owner::jira-comment", state["resolutions"])

    def test_with_jira_actor_records_global_fallback_after_write_error(self) -> None:
        role_actor = ResolvedAtlassianActor(
            role_id="ai-product-owner",
            role_visible_name="PO",
            surface="jira-comment",
            actor_mode="role-service-account",
            resolution_reason="role-service-account",
            search_fallback_used=False,
            search_fallback_type="",
            account_id_source="secret",
            email="ia-product-owner@example.com",
            token="token-po",
            account_id="account-po",
            service_account="ia-product-owner",
            site_url="https://example.atlassian.net",
            cloud_id="cloud-123",
            auth_mode="service-account-api-token",
            jira_project_key="DOT",
            confluence_space_key="DOT",
            fallback_issue_required=False,
            fallback_issue_reason="",
            fallback_issue_type="",
            global_fallback_allowed=True,
        )
        fallback_actor = ResolvedAtlassianActor(
            role_id="ai-product-owner",
            role_visible_name="PO",
            surface="jira-comment",
            actor_mode="global-service-account",
            resolution_reason="global-default",
            search_fallback_used=False,
            search_fallback_type="",
            account_id_source="search-email",
            email="global@example.com",
            token="token-global",
            account_id="account-global",
            service_account="dotfiles-ai-atlassian",
            site_url="https://example.atlassian.net",
            cloud_id="cloud-123",
            auth_mode="service-account-api-token",
            jira_project_key="DOT",
            confluence_space_key="DOT",
            fallback_issue_required=True,
            fallback_issue_reason="surface-write-failure",
            fallback_issue_type="global-fallback-after-write-error",
            global_fallback_allowed=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_actor_runtime(repo_root)
            with patch(
                "scripts.ai_atlassian_actor_lib.jira_adapter_for_role",
                return_value=(DummyJiraAdapter(fail=True), role_actor),
            ), patch(
                "scripts.ai_atlassian_actor_lib._global_actor",
                return_value=fallback_actor,
            ), patch(
                "scripts.ai_atlassian_actor_lib._resolve_global_platform",
                return_value=fallback_actor.as_platform(),
            ), patch(
                "scripts.ai_atlassian_actor_lib.AtlassianHttpClient",
                return_value=SimpleNamespace(),
            ), patch(
                "scripts.ai_atlassian_actor_lib.JiraAdapter",
                return_value=DummyJiraAdapter(fail=False),
            ), patch("scripts.ai_atlassian_actor_lib._notify_fallback_issue_if_needed"):
                payload, used_actor = with_jira_actor(
                    repo_root,
                    "ai-product-owner",
                    "jira-comment",
                    lambda jira, _actor: jira.add_comment("DOT-1", "body"),
                    context_issue_key="DOT-1",
                )

            state = actor_runtime_state(repo_root)

        self.assertEqual(payload["id"], "9001")
        self.assertEqual(used_actor.actor_mode, "global-service-account")
        self.assertEqual(
            state["resolutions"]["ai-product-owner::jira-comment"]["actor_mode"],
            "global-service-account",
        )
        self.assertNotIn("token", state["resolutions"]["ai-product-owner::jira-comment"])
        self.assertTrue(state["resolutions"]["ai-product-owner::jira-comment"]["has_token"])

    def test_runtime_state_redacts_secret_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_actor_runtime(repo_root)

            actor = resolve_atlassian_actor(repo_root, "ai-product-owner", "jira-comment")
            state = actor_runtime_state(repo_root)

        self.assertEqual(actor.actor_mode, "role-service-account")
        self.assertNotIn("token", state["resolutions"]["ai-product-owner::jira-comment"])
        self.assertTrue(state["resolutions"]["ai-product-owner::jira-comment"]["has_token"])

    def test_runtime_state_sanitizes_legacy_token_from_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            cache_dir = repo_root / ".cache" / "ai"
            cache_dir.mkdir(parents=True, exist_ok=True)
            state_path = cache_dir / "atlassian-actor-resolution.json"
            state_path.write_text(
                '{\n'
                '  "resolutions": {\n'
                '    "ai-product-owner::jira-comment": {\n'
                '      "role_id": "ai-product-owner",\n'
                '      "surface": "jira-comment",\n'
                '      "token": "secret-token"\n'
                "    }\n"
                "  },\n"
                '  "notified_fallbacks": {}\n'
                '}\n',
                encoding="utf-8",
            )

            state = actor_runtime_state(repo_root)
            persisted = state_path.read_text(encoding="utf-8")

        self.assertNotIn("token", state["resolutions"]["ai-product-owner::jira-comment"])
        self.assertTrue(state["resolutions"]["ai-product-owner::jira-comment"]["has_token"])
        self.assertNotIn("secret-token", persisted)


if __name__ == "__main__":
    unittest.main()
