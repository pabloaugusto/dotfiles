from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast
from unittest.mock import patch

from scripts.ai_atlassian_seed_lib import (
    build_migration_issue_description,
    build_seed_plan,
    build_storage_snapshot,
    confluence_expand_macro,
    ensure_issue_reaches_status,
    extract_external_id,
    flatten_page_tree,
    jira_board_layout_confirmed,
    logical_status_from_name,
    markdown_to_storage_html,
    normalize_status_label,
    state_hint_to_logical_status,
    workflow_transition_path,
)
from scripts.ai_control_plane_lib import load_yaml_map


class AtlassianSeedPlanTests(unittest.TestCase):
    def test_build_seed_plan_reports_records_and_pages(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ATLASSIAN_SITE_URL": "https://example.atlassian.net",
                "ATLASSIAN_EMAIL": "bot@example.com",
                "ATLASSIAN_API_TOKEN": "token",
                "ATLASSIAN_SERVICE_ACCOUNT": "dotfiles-ai-atlassian",
                "ATLASSIAN_CLOUD_ID": "cloud-id",
                "ATLASSIAN_PROJECT_KEY": "DOT",
                "ATLASSIAN_SPACE_KEY": "DOT",
            },
            clear=False,
        ):
            payload = build_seed_plan()

        self.assertEqual(payload["metadata"]["project_key"], "DOT")
        self.assertEqual(payload["metadata"]["space_key"], "DOT")
        self.assertGreater(payload["jira"]["total_records"], 0)
        self.assertGreater(payload["confluence"]["total_pages"], 0)
        self.assertTrue(payload["preconditions"]["board_layout_confirmed"])
        self.assertEqual(payload["preconditions"]["board_layout_status"], "confirmed")

    def test_flatten_page_tree_keeps_declared_titles(self) -> None:
        model = load_yaml_map(Path("config/ai/confluence-model.yaml"))
        titles = [entry["title"] for entry in flatten_page_tree(model)]

        self.assertIn("DOT - AI Control Plane Hub", titles)
        self.assertIn("DOT - Jira Schema", titles)
        self.assertIn("DOT - Migration Plan", titles)
        self.assertIn("DOT - Agent Operations Contract", titles)
        self.assertIn("DOT - Atlassian OpenAPI Strategy", titles)
        self.assertIn("DOT - Optional Capabilities Figma UX SEO", titles)

    def test_state_hint_mapping_is_stable(self) -> None:
        self.assertEqual(state_hint_to_logical_status("done"), "done")
        self.assertEqual(state_hint_to_logical_status("Doing"), "doing")
        self.assertEqual(state_hint_to_logical_status("Paused"), "paused")
        self.assertEqual(state_hint_to_logical_status("pendente"), "backlog")
        self.assertEqual(normalize_status_label(" Changes   Requested "), "changes requested")
        self.assertEqual(logical_status_from_name("DOING"), "doing")
        self.assertEqual(logical_status_from_name("PAUSED"), "paused")

    def test_board_layout_confirmation_reflects_model(self) -> None:
        model = load_yaml_map(Path("config/ai/jira-model.yaml"))
        self.assertTrue(jira_board_layout_confirmed(model))

    def test_markdown_to_storage_html_renders_markdown(self) -> None:
        payload = markdown_to_storage_html("# Titulo\n\n- item")
        self.assertIn("<h1>Titulo</h1>", payload)
        self.assertIn("<li>item</li>", payload)

    def test_confluence_expand_macro_wraps_rich_text_body(self) -> None:
        payload = confluence_expand_macro("Expandir", "<p>Corpo</p>")
        self.assertIn('ac:name="expand"', payload)
        self.assertIn("<ac:rich-text-body><p>Corpo</p></ac:rich-text-body>", payload)

    def test_build_storage_snapshot_renders_markdown_and_keeps_source_in_expand(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "docs" / "sample.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("# Titulo\n\n- item", encoding="utf-8")
            with patch(
                "scripts.ai_atlassian_seed_lib.github_blob_url",
                return_value="https://github.com/pabloaugusto/dotfiles/blob/main/docs/sample.md",
            ), patch(
                "scripts.ai_atlassian_seed_lib.resolve_tracked_repo_files",
                return_value={"docs/sample.md"},
            ), patch(
                "scripts.ai_atlassian_seed_lib.linkify_repo_relative_paths",
                side_effect=lambda text, repo_root: text,
            ):
                payload = build_storage_snapshot(
                    title="Pagina",
                    repo_root=root,
                    repo_artifact="docs/sample.md",
                    related_issues=[("DOT-1", "https://example.invalid/browse/DOT-1")],
                    extra_notes=["Sincronizada"],
                )

        self.assertIn("<h2>Conteudo sincronizado</h2>", payload)
        self.assertIn("<h2>Conteudo de origem</h2>", payload)
        self.assertIn('ac:name="expand"', payload)
        self.assertIn("Expandir documento de origem", payload)
        self.assertNotIn('ac:name="code"', payload)
        self.assertIn(
            'href="https://github.com/pabloaugusto/dotfiles/blob/main/docs/sample.md"',
            payload,
        )
        self.assertIn("<h1>Titulo</h1>", payload)
        self.assertIn("<li>item</li>", payload)

    def test_build_storage_snapshot_rewrites_relative_markdown_links_to_github(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "docs" / "sample.md"
            reference = root / "docs" / "ref.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(
                "[Runbook](ref.md)\n\nVeja docs/ref.md para mais detalhes.",
                encoding="utf-8",
            )
            reference.write_text("# Referencia", encoding="utf-8")

            def fake_blob_url(_repo_root: Path, repo_path: str) -> str:
                return f"https://github.com/pabloaugusto/dotfiles/blob/main/{repo_path}"

            with patch(
                "scripts.ai_atlassian_seed_lib.github_blob_url",
                side_effect=fake_blob_url,
            ), patch(
                "scripts.ai_atlassian_seed_lib.resolve_tracked_repo_files",
                return_value={"docs/sample.md", "docs/ref.md"},
            ), patch(
                "scripts.ai_atlassian_seed_lib.linkify_repo_relative_paths",
                side_effect=lambda text, repo_root: text,
            ):
                payload = build_storage_snapshot(
                    title="Pagina",
                    repo_root=root,
                    repo_artifact="docs/sample.md",
                    related_issues=[("DOT-83", "https://example.invalid/browse/DOT-83")],
                )

        self.assertIn(
            'href="https://github.com/pabloaugusto/dotfiles/blob/main/docs/ref.md"',
            payload,
        )
        self.assertNotIn('href="ref.md"', payload)

    def test_build_migration_issue_description_prefers_github_refs_and_attachment(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs" / "atlassian-ia" / "artifacts").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "atlassian-ia").mkdir(parents=True, exist_ok=True)
            for relative in (
                "docs/atlassian-ia/2026-03-07-parecer-e-plano-inicial.md",
                "docs/atlassian-ia/artifacts/migration-bundle.md",
                "docs/atlassian-ia/artifacts/jira-writing-standards.md",
                "docs/atlassian-ia/2026-03-08-github-jira-confluence-traceability.md",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# placeholder", encoding="utf-8")
            with patch(
                "scripts.ai_atlassian_seed_lib.github_blob_url",
                side_effect=lambda _repo_root, repo_path: (
                    f"https://github.com/pabloaugusto/dotfiles/blob/main/{repo_path}"
                ),
            ):
                payload = build_migration_issue_description(
                    root,
                    bundle_attachment_name="bundle-auditavel.zip",
                )

        self.assertIn(
            "[Plano vivo da migracao](https://github.com/pabloaugusto/dotfiles/blob/main/docs/atlassian-ia/2026-03-07-parecer-e-plano-inicial.md)",
            payload,
        )
        self.assertIn("Bundle auditavel anexado nesta issue: bundle-auditavel.zip", payload)
        self.assertNotIn("Bundle local:", payload)
        self.assertNotIn("Manifesto local:", payload)

    def test_extract_external_id_supports_bullet_rastreabilidade(self) -> None:
        issue: dict[str, object] = {
            "fields": {
                "summary": "Harness Linux para bootstrap e relink",
                "description": markdown_to_storage_html(""),
            }
        }
        fields = issue["fields"]
        self.assertIsInstance(fields, dict)
        fields = cast(dict[str, Any], fields)
        fields["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "ID local: RM-001"}],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        self.assertEqual(extract_external_id(issue), "RM-001")

    def test_workflow_transition_path_ignores_paused_when_target_is_testing(self) -> None:
        self.assertEqual(
            workflow_transition_path("doing", "testing"),
            ["doing", "testing"],
        )

    def test_workflow_transition_path_resumes_from_paused_before_following_main_flow(self) -> None:
        self.assertEqual(
            workflow_transition_path("paused", "review"),
            ["paused", "doing", "testing", "review"],
        )

    def test_ensure_issue_reaches_status_does_not_route_doing_through_paused(self) -> None:
        class FakeJira:
            def __init__(self) -> None:
                self.status = "DOING"
                self.transitioned_to: list[str] = []
                self.transitions_by_status = {
                    "DOING": [
                        {"id": "51", "to": {"name": "PAUSED"}},
                        {"id": "61", "to": {"name": "TESTING"}},
                    ],
                    "TESTING": [{"id": "71", "to": {"name": "Review"}}],
                    "REVIEW": [{"id": "81", "to": {"name": "Done"}}],
                }

            def get_issue(self, issue_key: str, *, fields: list[str] | None = None) -> dict[str, Any]:
                self.last_issue_key = issue_key
                return {"fields": {"status": {"name": self.status}}}

            def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
                self.last_issue_key = issue_key
                return list(self.transitions_by_status.get(self.status, []))

            def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, Any]:
                self.last_issue_key = issue_key
                for transition in self.transitions_by_status.get(self.status, []):
                    if str(transition.get("id")) == str(transition_id):
                        next_status = str(((transition.get("to") or {}).get("name")) or "").strip()
                        self.status = next_status
                        self.transitioned_to.append(next_status)
                        return {}
                raise AssertionError(f"Transicao inesperada: {transition_id}")

        fake_jira = FakeJira()
        ensure_issue_reaches_status(
            jira=cast(Any, fake_jira),
            issue_key="DOT-87",
            target_logical_status="testing",
        )
        self.assertEqual(fake_jira.transitioned_to, ["TESTING"])

    def test_ensure_issue_reaches_status_resumes_paused_before_review(self) -> None:
        class FakeJira:
            def __init__(self) -> None:
                self.status = "PAUSED"
                self.transitioned_to: list[str] = []
                self.transitions_by_status = {
                    "PAUSED": [{"id": "51", "to": {"name": "DOING"}}],
                    "DOING": [{"id": "61", "to": {"name": "TESTING"}}],
                    "TESTING": [{"id": "71", "to": {"name": "Review"}}],
                }

            def get_issue(self, issue_key: str, *, fields: list[str] | None = None) -> dict[str, Any]:
                self.last_issue_key = issue_key
                return {"fields": {"status": {"name": self.status}}}

            def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
                self.last_issue_key = issue_key
                return list(self.transitions_by_status.get(self.status, []))

            def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, Any]:
                self.last_issue_key = issue_key
                for transition in self.transitions_by_status.get(self.status, []):
                    if str(transition.get("id")) == str(transition_id):
                        next_status = str(((transition.get("to") or {}).get("name")) or "").strip()
                        self.status = next_status
                        self.transitioned_to.append(next_status)
                        return {}
                raise AssertionError(f"Transicao inesperada: {transition_id}")

        fake_jira = FakeJira()
        ensure_issue_reaches_status(
            jira=cast(Any, fake_jira),
            issue_key="DOT-87",
            target_logical_status="review",
        )
        self.assertEqual(fake_jira.transitioned_to, ["DOING", "TESTING", "Review"])


if __name__ == "__main__":
    unittest.main()
