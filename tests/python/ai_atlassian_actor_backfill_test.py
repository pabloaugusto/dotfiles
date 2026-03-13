from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from scripts.ai_atlassian_actor_backfill_lib import (
    apply_actor_comment_backfill,
    audit_actor_comment_backfill,
)
from scripts.ai_atlassian_actor_lib import ResolvedAtlassianActor, clear_actor_resolution_caches
from scripts.atlassian_platform_lib import AtlassianPlatformError, adf_text_document


def write_control_plane(repo_root: Path) -> None:
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
        "version: 1\nroles:\n  ai-product-owner: {}\n",
        encoding="utf-8",
    )
    (config_dir / "contracts.yaml").write_text(
        "version: 1\nworkflow:\n  always_enabled_columns: [Backlog, Doing, Done]\n",
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
                  - config/ai/agent-runtime.yaml
            registry_agents: {}
            """
        ),
        encoding="utf-8",
    )


def structured_comment(text: str, *, author_id: str, author_name: str, comment_id: str) -> dict[str, Any]:
    return {
        "id": comment_id,
        "author": {
            "accountId": author_id,
            "displayName": author_name,
        },
        "body": adf_text_document(text),
    }


class FakeJira:
    def __init__(self) -> None:
        self.client = type(
            "Client",
            (),
            {
                "resolved": type(
                    "Resolved",
                    (),
                    {
                        "jira_project_key": "DOT",
                    },
                )()
            },
        )()
        self.issues = [
            {
                "key": "DOT-1",
                "fields": {
                    "summary": "Issue piloto",
                    "status": {"name": "Doing"},
                },
            }
        ]
        self.comments_by_issue: dict[str, list[dict[str, Any]]] = {
            "DOT-1": [
                structured_comment(
                    "\n".join(
                        [
                            "Agente: PO",
                            "Tipo de interacao: progress-update",
                            "Status atual: doing",
                            "",
                            "## Contexto",
                            "- backlog refinado",
                        ]
                    ),
                    author_id="account-global",
                    author_name="dotfiles-ai-atlassian",
                    comment_id="1",
                )
            ]
        }
        self.deleted_comments: list[tuple[str, str]] = []

    def search_issues(
        self,
        jql: str,
        *,
        fields: list[str] | None = None,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        del jql, fields, max_results
        return list(self.issues)

    def get_issue(self, issue_key: str, *, fields: list[str] | None = None) -> dict[str, Any]:
        del fields
        return next(issue for issue in self.issues if issue["key"] == issue_key)

    def list_comments(self, issue_key: str, *, max_results: int = 200) -> list[dict[str, Any]]:
        del max_results
        return list(self.comments_by_issue.get(issue_key, []))

    def delete_comment(self, issue_key: str, comment_id: str) -> dict[str, Any]:
        entries = self.comments_by_issue.get(issue_key, [])
        self.comments_by_issue[issue_key] = [
            entry for entry in entries if str(entry.get("id", "")).strip() != comment_id
        ]
        self.deleted_comments.append((issue_key, comment_id))
        return {}


class FlakyCommentsJira(FakeJira):
    def __init__(self) -> None:
        super().__init__()
        self.failures_remaining = 1

    def list_comments(self, issue_key: str, *, max_results: int = 200) -> list[dict[str, Any]]:
        del max_results
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise AtlassianPlatformError(
                "Falha de conectividade com Atlassian em /rest/api/3/issue/DOT-1/comment: [WinError 10054]"
            )
        return list(self.comments_by_issue.get(issue_key, []))


def role_actor() -> ResolvedAtlassianActor:
    return ResolvedAtlassianActor(
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


def global_actor() -> ResolvedAtlassianActor:
    return ResolvedAtlassianActor(
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
        fallback_issue_required=False,
        fallback_issue_reason="",
        fallback_issue_type="",
        global_fallback_allowed=False,
    )


class AiAtlassianActorBackfillTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_actor_resolution_caches()

    def tearDown(self) -> None:
        clear_actor_resolution_caches()

    def test_audit_detects_legacy_global_comment_for_role(self) -> None:
        fake_jira = FakeJira()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_control_plane(repo_root)
            with patch(
                "scripts.ai_atlassian_actor_backfill_lib.resolve_atlassian_actor",
                return_value=role_actor(),
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.resolve_global_atlassian_actor",
                return_value=global_actor(),
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.global_jira_adapter",
                return_value=fake_jira,
            ):
                payload = audit_actor_comment_backfill(repo_root, role_id="ai-product-owner")

        self.assertEqual(payload["counts"]["candidate_comments"], 1)
        self.assertEqual(payload["candidates"][0]["issue_key"], "DOT-1")
        self.assertIn("Agente: PO", payload["candidates"][0]["desired_body"])

    def test_apply_creates_role_comment_and_removes_legacy_comment(self) -> None:
        fake_jira = FakeJira()

        def fake_with_jira_actor(repo_root, role_id, surface, operation, *, context_issue_key=""):
            del repo_root, role_id, surface, context_issue_key
            comment = {
                "id": "2",
                "author": {"accountId": "account-po", "displayName": "ia-product-owner"},
                "body": adf_text_document("Agent: PO"),
            }
            fake_jira.comments_by_issue["DOT-1"].append(comment)
            return operation(
                type(
                    "RoleJira",
                    (),
                    {
                        "add_comment": lambda self, issue_key, body_text: {
                            "id": "2",
                            "issue_key": issue_key,
                            "body_text": body_text,
                        }
                    },
                )(),
                role_actor(),
            ), role_actor()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_control_plane(repo_root)
            with patch(
                "scripts.ai_atlassian_actor_backfill_lib.resolve_atlassian_actor",
                return_value=role_actor(),
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.resolve_global_atlassian_actor",
                return_value=global_actor(),
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.global_jira_adapter",
                return_value=fake_jira,
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.with_jira_actor",
                side_effect=fake_with_jira_actor,
            ):
                payload = apply_actor_comment_backfill(repo_root, role_id="ai-product-owner")

        self.assertEqual(payload["apply_status"], "applied")
        self.assertEqual(payload["apply_counts"]["created_comments"], 1)
        self.assertEqual(payload["apply_counts"]["deleted_legacy_comments"], 1)
        self.assertEqual(fake_jira.deleted_comments, [("DOT-1", "1")])

    def test_audit_retries_transient_comment_read_error(self) -> None:
        flaky_jira = FlakyCommentsJira()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write_control_plane(repo_root)
            with patch(
                "scripts.ai_atlassian_actor_backfill_lib.resolve_atlassian_actor",
                return_value=role_actor(),
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.resolve_global_atlassian_actor",
                return_value=global_actor(),
            ), patch(
                "scripts.ai_atlassian_actor_backfill_lib.global_jira_adapter",
                return_value=flaky_jira,
            ):
                payload = audit_actor_comment_backfill(repo_root, role_id="ai-product-owner")

        self.assertEqual(payload["counts"]["candidate_comments"], 1)
        self.assertEqual(flaky_jira.failures_remaining, 0)


if __name__ == "__main__":
    unittest.main()
