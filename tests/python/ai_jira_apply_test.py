from __future__ import annotations

import unittest
from typing import Any, cast
from unittest import mock

from scripts.ai_jira_apply_lib import (
    active_custom_fields,
    apply_jira_model,
    configured_custom_field_options,
    current_workflow_detail_by_name,
    current_workflows_by_name,
    default_workflow_transition_specs,
    ensure_field_options,
    ensure_field_on_default_screen,
    field_screens,
    normalize_status_name,
    project_has_issues,
    wait_for_workflow_convergence,
    workflow_status_metadata_gaps,
    workflow_create_payload,
    workflow_requires_update,
    workflow_update_payload,
    workflow_update_validation_payload,
    workflow_validation_payload,
)


class FakeAtlassianHttpClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def request_json(
        self,
        product: str,
        path: str,
        *,
        method: str = "GET",
        params: dict[str, str] | None = None,
        payload: object | None = None,
    ) -> dict[str, object]:
        self.calls.append(
            {
                "product": product,
                "path": path,
                "method": method,
                "params": params,
                "payload": payload,
            }
        )
        return self.response


class AiJiraApplyTests(unittest.TestCase):
    def test_default_workflow_transition_specs_preserves_legacy_flow(self) -> None:
        self.assertEqual(
            default_workflow_transition_specs(),
            [
                {"from": "Backlog", "to": "Refinement"},
                {"from": "Refinement", "to": "Ready"},
                {"from": "Ready", "to": "Doing"},
                {"from": "Doing", "to": "Paused"},
                {"from": "Paused", "to": "Doing"},
                {"from": "Doing", "to": "Testing"},
                {"from": "Testing", "to": "Review"},
                {"from": "Review", "to": "Done"},
                {"from": "Testing", "to": "Changes Requested"},
                {"from": "Review", "to": "Changes Requested"},
                {"from": "Changes Requested", "to": "Doing"},
            ],
        )

    def test_active_custom_fields_respects_enabled_when_role(self) -> None:
        model = {
            "fields": {
                "custom_fields": [
                    {"name": "Work Kind", "type": "single_select"},
                    {
                        "name": "Needs SEO Review",
                        "type": "checkbox",
                        "enabled_when_role": "ai-seo-specialist",
                    },
                ]
            }
        }

        fields = active_custom_fields(model, role_ids={"ai-product-owner"})
        self.assertEqual([entry["name"] for entry in fields], ["Work Kind"])

    def test_configured_custom_field_options_can_follow_enabled_roles(self) -> None:
        options = configured_custom_field_options(
            {
                "name": "Current Agent Role",
                "type": "single_select",
                "options_source": "enabled_roles",
            },
            {"supports_options": True},
            role_ids={"ai-reviewer-python", "ai-product-owner", "ai-tech-lead"},
        )

        self.assertEqual(
            options,
            ["ai-product-owner", "ai-reviewer-python", "ai-tech-lead"],
        )

    def test_configured_custom_field_options_can_follow_visible_role_labels(self) -> None:
        options = configured_custom_field_options(
            {
                "name": "Current Agent Role",
                "type": "single_select",
                "options_source": "enabled_role_visible_names",
            },
            {"supports_options": True},
            role_ids={"ai-reviewer-python", "ai-product-owner", "ai-tech-lead"},
            role_labels_by_id={
                "ai-product-owner": "PO",
                "ai-reviewer-python": "Revisor Python",
                "ai-tech-lead": "Tech Lead",
            },
        )

        self.assertEqual(options, ["PO", "Revisor Python", "Tech Lead"])

    def test_field_screens_returns_values_list(self) -> None:
        client = FakeAtlassianHttpClient(
            {
                "values": [
                    {"id": 1, "name": "Default Screen"},
                ]
            }
        )

        screens = field_screens(client, "customfield_10001")  # type: ignore[arg-type]

        self.assertEqual(screens, [{"id": 1, "name": "Default Screen"}])
        self.assertEqual(client.calls[0]["path"], "/rest/api/3/field/customfield_10001/screens")

    def test_ensure_field_on_default_screen_only_calls_post_when_detached(self) -> None:
        client = mock.Mock()
        client.request_json.side_effect = [
            {"values": [], "isLast": True},
            {"status": "CREATED"},
        ]

        changed = ensure_field_on_default_screen(cast(Any, client), "customfield_10001")

        self.assertTrue(changed)
        self.assertEqual(
            client.request_json.call_args_list[0].args,
            ("jira", "/rest/api/3/field/customfield_10001/screens"),
        )
        self.assertEqual(
            client.request_json.call_args_list[1].args,
            ("jira", "/rest/api/3/screens/addToDefault/customfield_10001"),
        )

    def test_ensure_field_on_default_screen_skips_when_already_attached(self) -> None:
        client = mock.Mock()
        client.request_json.return_value = {"values": [{"id": 1, "name": "Default Screen"}]}

        changed = ensure_field_on_default_screen(cast(Any, client), "customfield_10001")

        self.assertFalse(changed)
        client.request_json.assert_called_once_with(
            "jira",
            "/rest/api/3/field/customfield_10001/screens",
        )

    def test_ensure_field_options_updates_only_project_applicable_context(self) -> None:
        client = mock.Mock()
        client.request_json.side_effect = [
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
                ]
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
                ]
            },
            {
                "values": [{"value": "ai-product-owner"}],
                "isLast": True,
                "maxResults": 100,
            },
            {"status": "CREATED"},
        ]

        result = ensure_field_options(
            cast(Any, client),
            "customfield_10223",
            ["ai-product-owner", "ai-scrum-master"],
            project_id="10005",
        )

        self.assertEqual(
            result,
            {
                "context_id": "10333",
                "created_options": ["ai-scrum-master"],
                "created_context": False,
                "updated_contexts": [
                    {
                        "context_id": "10333",
                        "context_name": "DOT Roles",
                        "is_global_context": False,
                        "created_options": ["ai-scrum-master"],
                    }
                ],
            },
        )
        self.assertEqual(
            [call.args[1] for call in client.request_json.call_args_list],
            [
                "/rest/api/3/field/customfield_10223/context",
                "/rest/api/3/field/customfield_10223/context",
                "/rest/api/3/field/customfield_10223/context/10333/option",
                "/rest/api/3/field/customfield_10223/context/10333/option",
            ],
        )

    def test_workflow_create_payload_reuses_existing_status_ids(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Paused", "category": "In Progress"},
                    {"name": "Testing", "category": "In Progress"},
                    {"name": "Review", "category": "In Progress"},
                    {"name": "Changes Requested", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                ],
            }
        }

        payload = workflow_create_payload(
            model,
            current_statuses={
                normalize_status_name("Backlog"): {"id": "10000", "name": "Backlog"},
                normalize_status_name("DOING"): {"id": "3", "name": "DOING"},
                normalize_status_name("Done"): {"id": "10002", "name": "Done"},
            },
        )

        statuses = payload["statuses"]
        self.assertEqual(statuses[0]["id"], "10000")
        doing = next(entry for entry in statuses if entry["statusReference"] == "3")
        self.assertEqual(doing["id"], "3")
        self.assertEqual(doing["name"], "Doing")
        self.assertEqual(doing["statusReference"], "3")
        self.assertEqual(statuses[-1]["id"], "10002")
        self.assertEqual(statuses[-1]["statusReference"], "10002")

    def test_workflow_status_metadata_gaps_detects_alias_name_drift(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "statuses": [
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Paused", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                ],
            }
        }

        gaps = workflow_status_metadata_gaps(
            model,
            current_statuses={
                normalize_status_name("Doing"): {
                    "id": "3",
                    "name": "DOING",
                    "statusCategory": "In Progress",
                },
                normalize_status_name("Paused"): {
                    "id": "10011",
                    "name": "PAUSED",
                    "statusCategory": "In Progress",
                },
                normalize_status_name("Done"): {
                    "id": "10002",
                    "name": "Done",
                    "statusCategory": "Done",
                },
            },
        )

        self.assertEqual(
            gaps,
            [
                {
                    "desired_name": "Doing",
                    "current_name": "DOING",
                    "desired_category": "In Progress",
                    "current_category": "In Progress",
                    "status_id": "3",
                },
                {
                    "desired_name": "Paused",
                    "current_name": "PAUSED",
                    "desired_category": "In Progress",
                    "current_category": "In Progress",
                    "status_id": "10011",
                },
            ],
        )

    def test_workflow_create_payload_uses_configured_transitions(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Review", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                    {"name": "Cancelled", "category": "Done"},
                ],
                "transitions": [
                    {"from": "Backlog", "to": "Refinement"},
                    {"from": "Refinement", "to": "Ready"},
                    {"from": "Ready", "to": "Doing"},
                    {"from": "Doing", "to": "Review"},
                    {"from": "Review", "to": "Done"},
                    {"from": "Review", "to": "Cancelled"},
                ],
            }
        }

        payload = workflow_create_payload(
            model,
            current_statuses={
                normalize_status_name("Backlog"): {"id": "10000", "name": "Backlog"},
                normalize_status_name("Refinement"): {"id": "10065", "name": "Refinement"},
                normalize_status_name("Ready"): {"id": "10066", "name": "Ready"},
                normalize_status_name("Doing"): {"id": "3", "name": "DOING"},
                normalize_status_name("Review"): {"id": "10067", "name": "Review"},
                normalize_status_name("Done"): {"id": "10002", "name": "Done"},
                normalize_status_name("Cancelled"): {"id": "10099", "name": "Cancelled"},
            },
        )

        transitions = payload["workflows"][0]["transitions"]
        self.assertEqual(transitions[-1]["name"], "Move to Cancelled")
        self.assertEqual(transitions[-1]["toStatusReference"], "10099")

    def test_wait_for_workflow_convergence_retries_until_payload_matches(self) -> None:
        desired_payload = {
            "workflows": [
                {
                    "statuses": [
                        {
                            "statusReference": "10000",
                            "layout": {"x": 0.0, "y": 0.0},
                            "properties": {},
                        }
                    ],
                    "transitions": [
                        {
                            "id": "1",
                            "name": "Create",
                            "type": "INITIAL",
                            "toStatusReference": "10000",
                            "links": [],
                        }
                    ],
                }
            ]
        }
        stale_payload = {
            "statuses": [],
            "transitions": [],
        }
        converged_payload = {
            "statuses": [
                {"statusReference": "10000", "layout": {"x": 0.0, "y": 0.0}, "properties": {}}
            ],
            "transitions": [
                {
                    "id": "1",
                    "name": "Create",
                    "type": "INITIAL",
                    "toStatusReference": "10000",
                    "links": [],
                }
            ],
        }

        with (
            mock.patch(
                "scripts.ai_jira_apply_lib.current_workflow_detail_by_name",
                side_effect=[stale_payload, converged_payload],
            ),
            mock.patch("scripts.ai_jira_apply_lib.time.sleep"),
        ):
            result = wait_for_workflow_convergence(
                cast(Any, object()),
                "DOT - Autonomous Delivery Workflow",
                desired_payload,
                attempts=2,
                sleep_seconds=0,
            )

        self.assertEqual(result, converged_payload)

    def test_workflow_create_payload_generates_uuid_for_new_status(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Paused", "category": "In Progress"},
                    {"name": "Testing", "category": "In Progress"},
                    {"name": "Review", "category": "In Progress"},
                    {"name": "Changes Requested", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                ],
            }
        }

        payload = workflow_create_payload(
            model,
            current_statuses={
                normalize_status_name("Backlog"): {"id": "10000", "name": "Backlog"},
                normalize_status_name("Done"): {"id": "10002", "name": "Done"},
            },
        )

        refinement = payload["statuses"][1]
        self.assertRegex(
            refinement["statusReference"],
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        )
        self.assertNotIn("id", refinement)

    def test_project_has_issues_uses_search_jql_endpoint(self) -> None:
        client = FakeAtlassianHttpClient({"issues": [{"key": "DOT-1"}]})

        result = project_has_issues(client, "DOT")  # type: ignore[arg-type]

        self.assertTrue(result)
        self.assertEqual(client.calls[0]["product"], "jira")
        self.assertEqual(client.calls[0]["path"], "/rest/api/3/search/jql")
        self.assertEqual(client.calls[0]["method"], "GET")
        self.assertEqual(
            client.calls[0]["params"],
            {
                "jql": 'project = "DOT" ORDER BY created DESC',
                "maxResults": "1",
                "fields": "summary",
            },
        )
        self.assertIsNone(client.calls[0]["payload"])

    def test_workflow_validation_payload_wraps_create_payload(self) -> None:
        create_payload = {
            "scope": {"type": "GLOBAL"},
            "statuses": [],
            "workflows": [],
        }

        payload = workflow_validation_payload(create_payload)

        self.assertEqual(payload["payload"], create_payload)
        self.assertEqual(payload["validationOptions"], {"levels": ["ERROR", "WARNING"]})

    def test_workflow_update_validation_payload_wraps_update_payload(self) -> None:
        update_payload = {
            "statuses": [],
            "workflows": [],
        }

        payload = workflow_update_validation_payload(update_payload)

        self.assertEqual(payload["payload"], update_payload)
        self.assertEqual(payload["validationOptions"], {"levels": ["ERROR", "WARNING"]})

    def test_current_workflows_by_name_reads_name_from_nested_id(self) -> None:
        client = FakeAtlassianHttpClient(
            {
                "values": [
                    {
                        "id": {
                            "name": "DOT - Autonomous Delivery Workflow",
                            "entityId": "abc",
                        }
                    }
                ]
            }
        )

        workflows = current_workflows_by_name(client)  # type: ignore[arg-type]

        self.assertIn("DOT - Autonomous Delivery Workflow", workflows)

    def test_current_workflow_detail_by_name_returns_matching_workflow(self) -> None:
        client = FakeAtlassianHttpClient(
            {
                "values": [
                    {"name": "Outro workflow"},
                    {
                        "name": "DOT - Autonomous Delivery Workflow",
                        "id": "workflow-id",
                        "version": {"id": "version-id", "versionNumber": 1},
                    },
                ]
            }
        )

        workflow = current_workflow_detail_by_name(
            cast(Any, client),
            "DOT - Autonomous Delivery Workflow",
        )

        self.assertIsNotNone(workflow)
        workflow_map = cast(dict[str, object], workflow)
        self.assertEqual(workflow_map["id"], "workflow-id")
        self.assertEqual(
            client.calls[0]["params"],
            {
                "workflowName": "DOT - Autonomous Delivery Workflow",
                "expand": "usage,values.transitions",
            },
        )

    def test_workflow_requires_update_detects_missing_paused_transition(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "description": "Workflow canonico",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Paused", "category": "In Progress"},
                    {"name": "Testing", "category": "In Progress"},
                    {"name": "Review", "category": "In Progress"},
                    {"name": "Changes Requested", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                ],
            }
        }
        desired_payload = workflow_create_payload(
            model,
            current_statuses={
                normalize_status_name("Backlog"): {"id": "10000", "name": "Backlog"},
                normalize_status_name("Refinement"): {"id": "10065", "name": "Refinement"},
                normalize_status_name("Ready"): {"id": "10066", "name": "Ready"},
                normalize_status_name("Doing"): {"id": "3", "name": "DOING"},
                normalize_status_name("Paused"): {"id": "10011", "name": "PAUSED"},
                normalize_status_name("Testing"): {"id": "10005", "name": "TESTING"},
                normalize_status_name("Review"): {"id": "10067", "name": "Review"},
                normalize_status_name("Changes Requested"): {
                    "id": "10068",
                    "name": "Changes Requested",
                },
                normalize_status_name("Done"): {"id": "10002", "name": "Done"},
            },
        )
        existing_workflow = {
            "id": "workflow-id",
            "version": {"id": "version-id", "versionNumber": 0},
            "description": "Workflow canonico",
            "statuses": [
                {"statusReference": "10000", "layout": {"x": 0.0, "y": 0.0}, "properties": {}},
                {"statusReference": "10065", "layout": {"x": 220.0, "y": 0.0}, "properties": {}},
                {"statusReference": "10066", "layout": {"x": 440.0, "y": 0.0}, "properties": {}},
                {"statusReference": "3", "layout": {"x": 660.0, "y": 0.0}, "properties": {}},
                {"statusReference": "10005", "layout": {"x": 880.0, "y": 0.0}, "properties": {}},
                {"statusReference": "10067", "layout": {"x": 1100.0, "y": 0.0}, "properties": {}},
                {"statusReference": "10068", "layout": {"x": 1320.0, "y": 0.0}, "properties": {}},
                {"statusReference": "10002", "layout": {"x": 1540.0, "y": 0.0}, "properties": {}},
            ],
            "transitions": [
                {
                    "id": "1",
                    "name": "Create",
                    "type": "INITIAL",
                    "toStatusReference": "10000",
                    "links": [],
                },
                {
                    "id": "11",
                    "name": "Move to Refinement",
                    "type": "DIRECTED",
                    "toStatusReference": "10065",
                    "links": [{"fromStatusReference": "10000", "fromPort": 0, "toPort": 1}],
                },
                {
                    "id": "21",
                    "name": "Move to Ready",
                    "type": "DIRECTED",
                    "toStatusReference": "10066",
                    "links": [{"fromStatusReference": "10065", "fromPort": 0, "toPort": 1}],
                },
                {
                    "id": "31",
                    "name": "Move to Doing",
                    "type": "DIRECTED",
                    "toStatusReference": "3",
                    "links": [{"fromStatusReference": "10066", "fromPort": 0, "toPort": 1}],
                },
                {
                    "id": "41",
                    "name": "Move to Testing",
                    "type": "DIRECTED",
                    "toStatusReference": "10005",
                    "links": [{"fromStatusReference": "3", "fromPort": 0, "toPort": 1}],
                },
            ],
        }

        self.assertTrue(workflow_requires_update(existing_workflow, desired_payload))

    def test_workflow_update_payload_uses_existing_id_and_version(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "description": "Workflow canonico",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Paused", "category": "In Progress"},
                    {"name": "Testing", "category": "In Progress"},
                    {"name": "Review", "category": "In Progress"},
                    {"name": "Changes Requested", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                ],
            }
        }
        payload = workflow_update_payload(
            model,
            current_statuses={
                normalize_status_name("Backlog"): {"id": "10000", "name": "Backlog"},
                normalize_status_name("Refinement"): {"id": "10065", "name": "Refinement"},
                normalize_status_name("Ready"): {"id": "10066", "name": "Ready"},
                normalize_status_name("Doing"): {"id": "3", "name": "DOING"},
                normalize_status_name("Paused"): {"id": "10011", "name": "PAUSED"},
                normalize_status_name("Testing"): {"id": "10005", "name": "TESTING"},
                normalize_status_name("Review"): {"id": "10067", "name": "Review"},
                normalize_status_name("Changes Requested"): {
                    "id": "10068",
                    "name": "Changes Requested",
                },
                normalize_status_name("Done"): {"id": "10002", "name": "Done"},
            },
            existing_workflow={
                "id": "workflow-id",
                "version": {"id": "version-id", "versionNumber": 7},
            },
        )

        self.assertEqual(payload["workflows"][0]["id"], "workflow-id")
        self.assertEqual(
            payload["workflows"][0]["version"], {"id": "version-id", "versionNumber": 7}
        )
        self.assertEqual(payload["statuses"][4]["id"], "10011")

    def test_apply_jira_model_reconciles_options_for_existing_select_field(self) -> None:
        control_plane = mock.Mock()
        control_plane.repo_root = "."
        control_plane.enabled_roles.return_value = {
            "ai-product-owner",
            "ai-reviewer",
            "ai-reviewer-python",
        }
        control_plane.atlassian_definition.return_value = {}
        resolved = mock.Mock(jira_project_key="DOT")
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "scheme_name": "DOT - Workflow Scheme",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
                    {"name": "Paused", "category": "In Progress"},
                    {"name": "Testing", "category": "In Progress"},
                    {"name": "Review", "category": "In Progress"},
                    {"name": "Changes Requested", "category": "In Progress"},
                    {"name": "Done", "category": "Done"},
                ],
            },
            "fields": {
                "custom_fields": [
                    {
                        "name": "Current Agent Role",
                        "type": "single_select",
                        "options_source": "enabled_roles",
                    }
                ]
            },
            "dashboards": [],
        }

        with (
            mock.patch(
                "scripts.ai_jira_apply_lib.load_ai_control_plane", return_value=control_plane
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.resolve_atlassian_platform", return_value=resolved
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.load_jira_model",
                return_value=("config/ai/jira-model.yaml", model),
            ),
            mock.patch("scripts.ai_jira_apply_lib.AtlassianHttpClient", return_value=mock.Mock()),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_project_payload", return_value={"id": "10005"}
            ),
            mock.patch("scripts.ai_jira_apply_lib.project_has_issues", return_value=True),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_status_catalog",
                return_value={
                    "backlog": {"id": "10000", "name": "Backlog", "statusCategory": "To Do"},
                    "refinement": {
                        "id": "10065",
                        "name": "Refinement",
                        "statusCategory": "To Do",
                    },
                    "ready": {"id": "10066", "name": "Ready", "statusCategory": "To Do"},
                    "doing": {"id": "3", "name": "Doing", "statusCategory": "In Progress"},
                    "paused": {
                        "id": "10011",
                        "name": "Paused",
                        "statusCategory": "In Progress",
                    },
                    "testing": {
                        "id": "10005",
                        "name": "Testing",
                        "statusCategory": "In Progress",
                    },
                    "review": {
                        "id": "10067",
                        "name": "Review",
                        "statusCategory": "In Progress",
                    },
                    "changes requested": {
                        "id": "10068",
                        "name": "Changes Requested",
                        "statusCategory": "In Progress",
                    },
                    "done": {"id": "10002", "name": "Done", "statusCategory": "Done"},
                },
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_workflows_by_name",
                return_value={
                    "DOT - Autonomous Delivery Workflow": {
                        "name": "DOT - Autonomous Delivery Workflow"
                    }
                },
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_workflow_detail_by_name",
                return_value={"statuses": [], "transitions": []},
            ),
            mock.patch("scripts.ai_jira_apply_lib.workflow_requires_update", return_value=False),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_workflow_schemes_by_name",
                return_value={"DOT - Workflow Scheme": {"id": "30001"}},
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_workflow_scheme_association",
                return_value={"workflowScheme": {"id": "30001"}},
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.current_fields_by_name",
                return_value={"Current Agent Role": {"id": "customfield_10223"}},
            ),
            mock.patch(
                "scripts.ai_jira_apply_lib.resolve_named_fields",
                return_value={"Current Agent Role": {"id": "customfield_10223"}},
            ),
            mock.patch("scripts.ai_jira_apply_lib.current_dashboards_by_name", return_value={}),
            mock.patch(
                "scripts.ai_jira_apply_lib.ensure_field_options",
                return_value={"context_id": "10333", "created_options": ["ai-reviewer-python"]},
            ) as ensure_options,
            mock.patch(
                "scripts.ai_jira_apply_lib.ensure_field_on_default_screen", return_value=False
            ),
        ):
            result = apply_jira_model(".")

        ensure_options.assert_called_once_with(
            mock.ANY,
            "customfield_10223",
            ["ai-product-owner", "ai-reviewer", "ai-reviewer-python"],
            project_id="10005",
        )
        self.assertEqual(
            result["custom_fields"]["options_updated"],
            [
                {
                    "field": "Current Agent Role",
                    "context_id": "10333",
                    "created_options": ["ai-reviewer-python"],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
