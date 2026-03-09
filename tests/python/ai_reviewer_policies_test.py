from __future__ import annotations

import pathlib
import json
import unittest

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class AiReviewerPoliciesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.operations = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "agent-operations.yaml").read_text(encoding="utf-8")
        )
        self.policies = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "reviewer-policies.yaml").read_text(encoding="utf-8")
        )
        self.review_output_schema = json.loads(
            (REPO_ROOT / "config" / "ai" / "review-output.schema.json").read_text(encoding="utf-8")
        )

    def test_common_policy_has_structured_output_contract(self) -> None:
        common = self.policies.get("common") or {}
        required_output = common.get("required_output") or []
        for field in (
            "decision",
            "summary",
            "findings",
            "quality_regression",
            "jira_action",
        ):
            self.assertIn(field, required_output)

    def test_python_policy_covers_expected_result_questions(self) -> None:
        profiles = self.policies.get("profiles") or {}
        python_policy = profiles.get("python-review-policy") or {}
        expected = python_policy.get("expected_result") or []
        self.assertIn("o-que-esta-correto", expected)
        self.assertIn("qual-comentario-publicar-no-jira", expected)
        self.assertIn("para-qual-status-a-issue-deve-ser-movida", expected)

    def test_specialist_reviewer_roles_reference_decision_policies(self) -> None:
        roles = self.operations.get("roles") or {}
        expected = {
            "ai-reviewer-python": "python-review-policy",
            "ai-reviewer-powershell": "powershell-review-policy",
            "ai-reviewer-automation": "automation-review-policy",
            "ai-reviewer-config-policy": "config-policy-review-policy",
        }
        for role_name, policy_name in expected.items():
            with self.subTest(role=role_name):
                self.assertEqual((roles.get(role_name) or {}).get("decision_policy"), policy_name)

    def test_common_policy_declares_schema_and_posture(self) -> None:
        metadata = self.policies.get("metadata") or {}
        self.assertEqual(metadata.get("review_output_schema"), "config/ai/review-output.schema.json")
        common = self.policies.get("common") or {}
        posture_rules = common.get("posture_rules") or []
        self.assertIn("nunca-aprovar-por-omissao", posture_rules)
        precedence = common.get("sources_of_truth_precedence") or []
        self.assertGreaterEqual(len(precedence), 5)

    def test_review_output_schema_contains_required_contract_fields(self) -> None:
        self.assertEqual(self.review_output_schema.get("type"), "object")
        required = self.review_output_schema.get("required") or []
        for field in (
            "review_scope",
            "decision",
            "confidence",
            "summary",
            "findings",
            "quality_regression",
            "validation_needed",
            "jira_action",
        ):
            self.assertIn(field, required)

    def test_python_policy_covers_workflow_steps_and_scope(self) -> None:
        profiles = self.policies.get("profiles") or {}
        python_policy = profiles.get("python-review-policy") or {}
        workflow_steps = python_policy.get("workflow_steps") or []
        self.assertIn("decisao-formal", workflow_steps)
        review_scope = python_policy.get("review_scope") or []
        self.assertIn("module", review_scope)


if __name__ == "__main__":
    unittest.main()
