from __future__ import annotations

import unittest

from scripts.ai_atlassian_agent_comment_audit_lib import (
    evaluate_issue_comment_contract,
    parse_structured_comment,
)
from scripts.atlassian_platform_lib import adf_text_document


def structured_comment(
    *, agent: str, status: str, interaction_type: str = "progress-update"
) -> dict[str, object]:
    raw = "\n".join(
        [
            f"Agente: {agent}",
            f"Tipo de interacao: {interaction_type}",
            f"Status atual: {status}",
            "",
            "## Contexto",
            "- checkpoint",
        ]
    )
    return {
        "id": f"{agent}-{status}",
        "created": "2026-03-08T10:00:00.000+0000",
        "updated": "2026-03-08T10:00:00.000+0000",
        "body": adf_text_document(raw),
    }


def default_role_reference_map() -> dict[str, str]:
    return {
        "ai-developer-python": "ai-developer-python",
        "dev python": "ai-developer-python",
        "ai-reviewer": "ai-reviewer",
        "revisor": "ai-reviewer",
        "ai-product-owner": "ai-product-owner",
        "po": "ai-product-owner",
        "ai-engineering-architect": "ai-engineering-architect",
        "arquiteto": "ai-engineering-architect",
        "ai-devops": "ai-devops",
        "devops": "ai-devops",
        "ai-qa": "ai-qa",
        "testador (qa)": "ai-qa",
        "ai-reviewer-config-policy": "ai-reviewer-config-policy",
        "revisor config policy": "ai-reviewer-config-policy",
        "ai-documentation-agent": "ai-documentation-agent",
        "ai-documentation-writer": "ai-documentation-writer",
        "ai-documentation-sync": "ai-documentation-sync",
        "ai-documentation-reviewer": "ai-documentation-reviewer",
        "ai-linguistic-reviewer": "ai-linguistic-reviewer",
        "pascoalete": "ai-linguistic-reviewer",
    }


class ParseStructuredCommentTest(unittest.TestCase):
    def test_parse_structured_comment_extracts_header_and_lists(self) -> None:
        parsed = parse_structured_comment(
            "\n".join(
                [
                    "Agente: ai-devops",
                    "Tipo de interacao: progress-update",
                    "Status atual: doing",
                    "",
                    "## Contexto",
                    "- item 1",
                    "- item 2",
                ]
            )
        )
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed["agent"], "ai-devops")
        self.assertEqual(parsed["status"], "doing")
        self.assertEqual(parsed["contexto"], ["item 1", "item 2"])


class EvaluateIssueCommentContractTest(unittest.TestCase):
    def test_accepts_status_alias_when_comment_matches_issue_semantically(self) -> None:
        issue = {
            "key": "DOT-0",
            "fields": {
                "summary": "Teste",
                "status": {"name": "DOING"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": {"value": "Dev Python"},
                "customfield_2": {"value": "Revisor"},
            },
        }
        comments = [structured_comment(agent="ai-developer-python", status="In Progress")]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        self.assertNotIn(
            "latest_comment_status_mismatch",
            {entry["code"] for entry in report["findings"]},
        )

    def test_flags_latest_comment_status_mismatch(self) -> None:
        issue = {
            "key": "DOT-1",
            "fields": {
                "summary": "Teste",
                "status": {"name": "Backlog"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": {"value": "ai-product-owner"},
                "customfield_2": {"value": "ai-engineering-architect"},
            },
        }
        comments = [structured_comment(agent="ai-product-owner", status="doing")]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        self.assertIn(
            "latest_comment_status_mismatch",
            {entry["code"] for entry in report["findings"]},
        )

    def test_flags_missing_current_agent_comment(self) -> None:
        issue = {
            "key": "DOT-2",
            "fields": {
                "summary": "Teste",
                "status": {"name": "DOING"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "High"},
                "customfield_1": {"value": "ai-devops"},
                "customfield_2": {"value": "ai-reviewer"},
            },
        }
        comments = [structured_comment(agent="ai-product-owner", status="doing")]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        self.assertIn(
            "missing_current_agent_comment",
            {entry["code"] for entry in report["findings"]},
        )

    def test_flags_technical_id_drift_in_fields_and_comments(self) -> None:
        issue = {
            "key": "DOT-2A",
            "fields": {
                "summary": "Teste",
                "status": {"name": "DOING"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "High"},
                "customfield_1": {"value": "ai-devops"},
                "customfield_2": {"value": "ai-product-owner"},
            },
        }
        comments = [structured_comment(agent="ai-devops", status="doing")]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        codes = {entry["code"] for entry in report["findings"]}
        self.assertIn("current_agent_role_uses_technical_id", codes)
        self.assertIn("next_required_role_uses_technical_id", codes)
        self.assertIn("structured_comment_agent_uses_technical_id", codes)

    def test_flags_done_delivery_issue_missing_qa_and_reviewer(self) -> None:
        issue = {
            "key": "DOT-3",
            "fields": {
                "summary": "Teste",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": None,
                "customfield_2": None,
            },
        }
        comments = [structured_comment(agent="ai-devops", status="done")]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        codes = {entry["code"] for entry in report["findings"]}
        self.assertIn("missing_qa_comment", codes)
        self.assertIn("missing_reviewer_comment", codes)

    def test_accepts_specialized_reviewer_roles(self) -> None:
        issue = {
            "key": "DOT-4",
            "fields": {
                "summary": "Teste",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": None,
                "customfield_2": None,
            },
        }
        comments = [
            structured_comment(agent="ai-developer-python", status="done"),
            structured_comment(agent="ai-qa", status="done", interaction_type="test-success"),
            structured_comment(
                agent="ai-reviewer-config-policy",
                status="done",
                interaction_type="approval",
            ),
        ]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        self.assertNotIn(
            "missing_reviewer_comment",
            {entry["code"] for entry in report["findings"]},
        )

    def test_accepts_documentation_agent_as_delivery_for_done_issue(self) -> None:
        issue = {
            "key": "DOT-5",
            "fields": {
                "summary": "Teste",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": None,
                "customfield_2": None,
            },
        }
        comments = [
            structured_comment(agent="ai-documentation-agent", status="done"),
            structured_comment(agent="ai-qa", status="done", interaction_type="test-success"),
            structured_comment(agent="pascoalete", status="done", interaction_type="approval"),
        ]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        self.assertNotIn(
            "missing_delivery_agent_comment",
            {entry["code"] for entry in report["findings"]},
        )

    def test_accepts_documentation_writer_and_sync_roles_as_delivery(self) -> None:
        issue = {
            "key": "DOT-6",
            "fields": {
                "summary": "Teste",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": None,
                "customfield_2": None,
            },
        }
        comments = [
            structured_comment(agent="ai-documentation-writer", status="done"),
            structured_comment(agent="ai-documentation-sync", status="done"),
            structured_comment(agent="ai-qa", status="done", interaction_type="test-success"),
            structured_comment(
                agent="ai-documentation-reviewer",
                status="done",
                interaction_type="approval",
            ),
        ]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        codes = {entry["code"] for entry in report["findings"]}
        self.assertNotIn("missing_delivery_agent_comment", codes)
        self.assertNotIn("missing_reviewer_comment", codes)

    def test_accepts_linguistic_reviewer_as_reviewer_role(self) -> None:
        issue = {
            "key": "DOT-7",
            "fields": {
                "summary": "Teste",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "customfield_1": None,
                "customfield_2": None,
            },
        }
        comments = [
            structured_comment(agent="ai-documentation-writer", status="done"),
            structured_comment(agent="ai-qa", status="done", interaction_type="test-success"),
            structured_comment(
                agent="ai-linguistic-reviewer",
                status="done",
                interaction_type="approval",
            ),
        ]
        report = evaluate_issue_comment_contract(
            issue,
            comments,
            current_agent_field_id="customfield_1",
            next_required_field_id="customfield_2",
            role_reference_map=default_role_reference_map(),
        )
        self.assertNotIn(
            "missing_reviewer_comment",
            {entry["code"] for entry in report["findings"]},
        )


if __name__ == "__main__":
    unittest.main()
