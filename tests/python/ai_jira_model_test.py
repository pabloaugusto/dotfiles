from __future__ import annotations

import pathlib
import tempfile
import textwrap
import unittest
from unittest import mock

from scripts.atlassian_platform_lib import AtlassianPlatformError
from scripts.ai_jira_model_lib import (
    active_custom_field_names,
    current_custom_field_option_gaps,
    current_fields_by_name,
    live_delta_payload,
    load_jira_model,
    model_summary_payload,
)
from scripts.ai_control_plane_lib import load_yaml_map


def write_jira_model(repo_root: pathlib.Path) -> None:
    config_dir = repo_root / "config" / "ai"
    config_dir.mkdir(parents=True)
    (config_dir / "jira-model.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            project:
              key: DOT
              name: dotfiles
              style: company-managed-software
              target_board:
                name: DOT - Autonomous Engineering
                type: kanban
                board_api_scopes:
                  - read:board-scope:jira-software
                columns:
                  - name: Backlog
                    statuses: [Backlog]
                  - name: Ready
                    statuses: [Ready]
                optional_columns:
                  - name: SEO Review
                    enabled_when_role: ai-seo-specialist
                    statuses: [SEO Review]
            issue_types:
              standard:
                - Epic
                - Task
            workflow:
              statuses:
                - name: Backlog
                  category: To Do
                - name: Ready
                  category: To Do
            fields:
              custom_fields:
                - name: Work Kind
                  type: single_select
                - name: Current Agent Role
                  type: single_select
            components:
              - ai-control-plane
              - documentation-governance
            labels:
              baseline:
                - atlassian-ia
                - docs
            dashboards:
              - name: DOT - Autonomous Engineering Overview
            """
        ),
        encoding="utf-8",
    )


class AiJiraModelTests(unittest.TestCase):
    def test_load_jira_model_reads_repo_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_jira_model(repo_root)
            model_path, model = load_jira_model(repo_root)
        self.assertTrue(str(model_path).endswith("config\\ai\\jira-model.yaml"))
        self.assertEqual(model["project"]["key"], "DOT")

    def test_model_summary_payload_extracts_core_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_jira_model(repo_root)
            payload = model_summary_payload(repo_root)
        self.assertEqual(payload["project"]["key"], "DOT")
        self.assertEqual(payload["board"]["columns"], ["Backlog", "Ready"])
        self.assertEqual(payload["custom_fields"], ["Work Kind", "Current Agent Role"])
        self.assertEqual(payload["components"], ["ai-control-plane", "documentation-governance"])

    def test_active_custom_field_names_respects_enabled_roles(self) -> None:
        model = {
            "fields": {
                "custom_fields": [
                    {"name": "Current Agent Role", "type": "single_select"},
                    {
                        "name": "Needs SEO Review",
                        "type": "checkbox",
                        "enabled_when_role": "ai-seo-specialist",
                    },
                ]
            }
        }

        field_names = active_custom_field_names(model, role_ids={"ai-product-owner"})

        self.assertEqual(field_names, ["Current Agent Role"])

    def test_current_fields_by_name_paginates_field_search(self) -> None:
        client = mock.Mock()
        client.request_json.side_effect = [
            {
                "values": [{"name": "Current Agent Role", "id": "customfield_10223"}],
                "isLast": False,
                "maxResults": 1,
            },
            {
                "values": [{"name": "Next Required Role", "id": "customfield_10224"}],
                "isLast": True,
                "maxResults": 1,
            },
        ]

        catalog = current_fields_by_name(client)

        self.assertEqual(
            catalog,
            {
                "Current Agent Role": {"name": "Current Agent Role", "id": "customfield_10223"},
                "Next Required Role": {"name": "Next Required Role", "id": "customfield_10224"},
            },
        )

    def test_current_custom_field_option_gaps_reports_missing_enabled_role(self) -> None:
        client = mock.Mock()
        client.request_json.side_effect = [
            {
                "values": [{"name": "Current Agent Role", "id": "customfield_10223"}],
                "isLast": True,
                "maxResults": 100,
            },
            {
                "values": [
                    {
                        "id": "20001",
                        "name": "Outro projeto",
                        "isGlobalContext": False,
                        "projectIds": ["20000"],
                    },
                    {
                        "id": "10333",
                        "name": "DOT Roles",
                        "isGlobalContext": False,
                        "projectIds": ["10005"],
                    },
                ],
            },
            {
                "values": [
                    {"value": "ai-product-owner"},
                    {"value": "ai-legacy-role"},
                ],
                "isLast": True,
                "maxResults": 100,
            },
        ]
        model = {
            "fields": {
                "custom_fields": [
                    {
                        "name": "Current Agent Role",
                        "type": "single_select",
                        "options_source": "enabled_roles",
                    }
                ]
            }
        }

        gaps = current_custom_field_option_gaps(
            client,
            model,
            role_ids={"ai-product-owner", "ai-scrum-master"},
            project_id="10005",
        )

        self.assertEqual(
            gaps,
            [
                {
                    "field": "Current Agent Role",
                    "field_id": "customfield_10223",
                    "context_id": "10333",
                    "context_name": "DOT Roles",
                    "context_status": "applicable",
                    "is_global_context": False,
                    "missing_options": ["ai-scrum-master"],
                    "unexpected_options": ["ai-legacy-role"],
                    "desired_option_count": 2,
                    "current_option_count": 2,
                }
            ],
        )

    def test_current_custom_field_option_gaps_supports_visible_role_labels(self) -> None:
        client = mock.Mock()
        client.request_json.side_effect = [
            {
                "values": [{"name": "Current Agent Role", "id": "customfield_10223"}],
                "isLast": True,
                "maxResults": 100,
            },
            {
                "values": [
                    {
                        "id": "10333",
                        "name": "DOT Roles",
                        "isGlobalContext": False,
                        "projectIds": ["10005"],
                    },
                ],
            },
            {
                "values": [{"value": "PO"}],
                "isLast": True,
                "maxResults": 100,
            },
        ]
        model = {
            "fields": {
                "custom_fields": [
                    {
                        "name": "Current Agent Role",
                        "type": "single_select",
                        "options_source": "enabled_role_visible_names",
                    }
                ]
            }
        }

        gaps = current_custom_field_option_gaps(
            client,
            model,
            role_ids={"ai-product-owner", "ai-scrum-master"},
            role_labels_by_id={
                "ai-product-owner": "PO",
                "ai-scrum-master": "Scrum Master",
            },
            project_id="10005",
        )

        self.assertEqual(gaps[0]["missing_options"], ["Scrum Master"])

    def test_current_custom_field_option_gaps_fails_on_duplicate_canonical_field_names(self) -> None:
        client = mock.Mock()
        client.request_json.side_effect = [
            {
                "values": [
                    {"name": "Current Agent Role", "id": "customfield_10223"},
                    {"name": "Current Agent Role", "id": "customfield_10444"},
                ],
                "isLast": True,
                "maxResults": 100,
            },
        ]
        model = {
            "fields": {
                "custom_fields": [
                    {
                        "name": "Current Agent Role",
                        "type": "single_select",
                        "options_source": "enabled_roles",
                    }
                ]
            }
        }

        with self.assertRaisesRegex(
            AtlassianPlatformError,
            "nomes duplicados para fields canonicos",
        ):
            current_custom_field_option_gaps(
                client,
                model,
                role_ids={"ai-product-owner", "ai-scrum-master"},
                project_id="10005",
            )

    def test_live_delta_payload_flags_exact_status_drift_and_ignores_disabled_fields(self) -> None:
        model = {
            "fields": {
                "custom_fields": [
                    {"name": "Current Agent Role", "type": "single_select"},
                    {"name": "Next Required Role", "type": "single_select"},
                    {
                        "name": "Needs SEO Review",
                        "type": "checkbox",
                        "enabled_when_role": "ai-seo-specialist",
                    },
                ]
            }
        }
        summary = {
            "model_path": "config/ai/jira-model.yaml",
            "project": {"key": "DOT", "name": "dotfiles", "style": "company-managed-software"},
            "board": {
                "name": "DOT - Autonomous Engineering",
                "type": "kanban",
                "columns": ["Backlog", "Doing"],
                "optional_columns": ["SEO Review"],
                "required_scopes": ["read:project:jira"],
            },
            "workflow_statuses": ["Doing", "Paused"],
            "issue_types": ["Task"],
            "custom_fields": ["Current Agent Role", "Next Required Role", "Needs SEO Review"],
            "components": ["ai-control-plane"],
            "labels": ["atlassian-ia"],
            "dashboards": [],
        }
        current = {
            "project": {"id": "10005", "key": "DOT", "name": "dotfiles", "style": "classic"},
            "issue_types": ["Task"],
            "statuses": ["DOING", "PAUSED"],
            "components": ["ai-control-plane"],
            "fields": ["Current Agent Role", "Next Required Role"],
            "board": {"status": "ok", "boards": []},
        }
        control_plane = mock.Mock()
        control_plane.repo_root = "."
        control_plane.enabled_roles.return_value = {"ai-product-owner", "ai-scrum-master"}
        control_plane.atlassian_definition.return_value = {}
        resolved = mock.Mock()

        with (
            mock.patch("scripts.ai_jira_model_lib.model_summary_payload", return_value=summary),
            mock.patch("scripts.ai_jira_model_lib.current_jira_state_payload", return_value=current),
            mock.patch("scripts.ai_jira_model_lib.load_jira_model", return_value=("path", model)),
            mock.patch("scripts.ai_jira_model_lib.load_ai_control_plane", return_value=control_plane),
            mock.patch("scripts.ai_jira_model_lib.resolve_atlassian_platform", return_value=resolved),
            mock.patch("scripts.ai_jira_model_lib.AtlassianHttpClient"),
            mock.patch(
                "scripts.ai_jira_model_lib.current_custom_field_option_gaps",
                return_value=[{"field": "Current Agent Role", "missing_options": ["ai-scrum-master"]}],
            ),
        ):
            payload = live_delta_payload(".")

        self.assertEqual(payload["delta"]["missing_statuses"], ["Doing", "Paused"])
        self.assertEqual(payload["delta"]["unexpected_statuses"], ["DOING", "PAUSED"])
        self.assertEqual(payload["delta"]["missing_custom_fields"], [])
        self.assertEqual(payload["delta"]["inactive_custom_fields"], ["Needs SEO Review"])
        self.assertEqual(
            payload["delta"]["custom_field_option_gaps"],
            [{"field": "Current Agent Role", "missing_options": ["ai-scrum-master"]}],
        )
        self.assertEqual(
            payload["delta"]["missing_custom_field_options"],
            [{"field": "Current Agent Role", "missing_options": ["ai-scrum-master"]}],
        )

    def test_repo_model_keeps_product_owner_priority_and_timeline_rules(self) -> None:
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        _, jira_model = load_jira_model(repo_root)
        execution_rules = ((jira_model.get("workflow") or {}).get("execution_rules")) or []
        self.assertIn("ordered-lists-must-remain-prioritized", execution_rules)
        self.assertIn("new-demand-must-enter-the-right-priority-position", execution_rules)
        self.assertIn("product-owner-must-maintain-start-and-due-dates-for-non-subtasks", execution_rules)

        agent_operations = load_yaml_map(repo_root / "config" / "ai" / "agent-operations.yaml")
        product_owner = ((agent_operations.get("roles") or {}).get("ai-product-owner")) or {}
        jira_payload = product_owner.get("jira") or {}
        primary_actions = jira_payload.get("primary_issue_actions") or []
        operating_steps = product_owner.get("operating_steps") or []

        self.assertIn("manter backlog, refinement e ready ordenados por prioridade real", primary_actions)
        self.assertIn(
            "manter timeline, start date e due date atualizados para itens acima de subtarefa",
            primary_actions,
        )
        self.assertIn(
            "posicionar o item novo no ponto correto da prioridade do backlog e das filas ordenadas do board",
            operating_steps,
        )
        self.assertIn(
            "revisar se Start date e Due date precisam ser estimados ou recalculados",
            operating_steps,
        )


if __name__ == "__main__":
    unittest.main()
