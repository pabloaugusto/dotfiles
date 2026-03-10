from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ai_atlassian_repair_lib import (
    canonicalize_generated_comment_text,
    canonicalize_generated_text,
    issue_is_ai_generated,
    prune_redundant_migration_links,
)


class AtlassianRepairTests(unittest.TestCase):
    def test_prune_redundant_migration_links_removes_relates_to_migration_issue(self) -> None:
        class FakeJira:
            def __init__(self) -> None:
                self.deleted: list[str] = []

            def list_issue_links(self, issue_key: str) -> list[dict[str, object]]:
                self.issue_key = issue_key
                return [
                    {
                        "id": "1001",
                        "type": {"name": "Relates"},
                        "outwardIssue": {"key": "DOT-1"},
                    },
                    {
                        "id": "1002",
                        "type": {"name": "Blocks"},
                        "outwardIssue": {"key": "DOT-65"},
                    },
                ]

            def delete_issue_link(self, link_id: str) -> None:
                self.deleted.append(link_id)

        fake = FakeJira()
        deleted = prune_redundant_migration_links(
            fake,  # type: ignore[arg-type]
            "DOT-75",
            migration_issue_key="DOT-1",
        )

        self.assertEqual(deleted, 1)
        self.assertEqual(fake.deleted, ["1001"])

    def test_issue_is_ai_generated_by_reporter(self) -> None:
        issue = {
            "fields": {
                "reporter": {"accountId": "bot-account"},
                "labels": [],
                "summary": "Qualquer tarefa",
            }
        }
        self.assertTrue(issue_is_ai_generated(issue, author_account_id="bot-account"))

    def test_issue_is_ai_generated_by_label_hint(self) -> None:
        issue = {
            "fields": {
                "reporter": {"accountId": "humano"},
                "labels": ["retro-sync"],
                "summary": "Qualquer tarefa",
            }
        }
        self.assertTrue(issue_is_ai_generated(issue, author_account_id="bot-account"))

    def test_issue_is_ai_generated_by_migration_summary(self) -> None:
        issue = {
            "fields": {
                "reporter": {"accountId": "humano"},
                "labels": [],
                "summary": "[MIGRATION] Bootstrap retro-sync Atlassian AI control plane",
            }
        }
        self.assertTrue(issue_is_ai_generated(issue, author_account_id="bot-account"))

    def test_issue_is_ai_generated_rejects_manual_issue(self) -> None:
        issue = {
            "fields": {
                "reporter": {"accountId": "humano"},
                "labels": ["manual"],
                "summary": "Tarefa manual",
            }
        }
        self.assertFalse(issue_is_ai_generated(issue, author_account_id="bot-account"))

    def test_canonicalize_generated_text_promotes_space_alias(self) -> None:
        self.assertEqual(
            canonicalize_generated_text(
                "https://pabloaugusto.atlassian.net/wiki/spaces/DO/pages/123",
                repo_root=Path.cwd(),
                legacy_space_key="DO",
                canonical_space_key="DOT",
            ),
            "https://pabloaugusto.atlassian.net/wiki/spaces/DOT/pages/123",
        )

    def test_canonicalize_generated_comment_text_rerenders_structured_comment(self) -> None:
        rendered = canonicalize_generated_comment_text(
            "\n".join(
                [
                    "Agent: ai-qa",
                    "Interaction Type: test-success",
                    "Status: Testing",
                    "Contexto:",
                    "- Suite executada",
                    "Evidencias:",
                    "- https://example.invalid/pipeline/123",
                    "Proximo passo: Encaminhar para Review.",
                ]
            ),
            repo_root=Path.cwd(),
            legacy_space_key="DO",
            canonical_space_key="DOT",
        )
        self.assertIn("Agente: ai-qa", rendered)
        self.assertIn("## Evidencias", rendered)

    def test_canonicalize_generated_text_linkifies_repo_paths(self) -> None:
        rendered = canonicalize_generated_text(
            "Artefato: docs/AI-WIP-TRACKER.md",
            repo_root=Path.cwd(),
            legacy_space_key="DO",
            canonical_space_key="DOT",
        )
        self.assertIn(
            "[docs/AI-WIP-TRACKER.md](https://github.com/pabloaugusto/dotfiles/blob/main/docs/AI-WIP-TRACKER.md)",
            rendered,
        )

    def test_canonicalize_generated_text_removes_playwright_storage_state_path(self) -> None:
        rendered = canonicalize_generated_text(
            "StorageState pronto em .cache/playwright/atlassian/storage-state.json.",
            repo_root=Path.cwd(),
            legacy_space_key="DO",
            canonical_space_key="DOT",
        )
        self.assertNotIn(".cache/playwright/atlassian/storage-state.json", rendered)
        self.assertIn("storageState local do Playwright (nao versionado)", rendered)


if __name__ == "__main__":
    unittest.main()
