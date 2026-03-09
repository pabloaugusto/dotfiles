from __future__ import annotations

import unittest

from scripts.ai_jira_apply_lib import (
    active_custom_fields,
    current_workflows_by_name,
    normalize_status_name,
    project_has_issues,
    workflow_create_payload,
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
    def test_active_custom_fields_respects_enabled_when_role(self) -> None:
        model = {
            "fields": {
                "custom_fields": [
                    {"name": "Work Kind", "type": "single_select"},
                    {"name": "Needs SEO Review", "type": "checkbox", "enabled_when_role": "ai-seo-specialist"},
                ]
            }
        }

        fields = active_custom_fields(model, role_ids={"ai-product-owner"})
        self.assertEqual([entry["name"] for entry in fields], ["Work Kind"])

    def test_workflow_create_payload_reuses_existing_status_ids(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
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
        self.assertEqual(doing["name"], "DOING")
        self.assertEqual(doing["statusReference"], "3")
        self.assertEqual(statuses[-1]["id"], "10002")
        self.assertEqual(statuses[-1]["statusReference"], "10002")

    def test_workflow_create_payload_generates_uuid_for_new_status(self) -> None:
        model = {
            "workflow": {
                "name": "DOT - Autonomous Delivery Workflow",
                "statuses": [
                    {"name": "Backlog", "category": "To Do"},
                    {"name": "Refinement", "category": "To Do"},
                    {"name": "Ready", "category": "To Do"},
                    {"name": "Doing", "category": "In Progress"},
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


if __name__ == "__main__":
    unittest.main()
