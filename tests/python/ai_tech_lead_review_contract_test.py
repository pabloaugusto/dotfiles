from __future__ import annotations

import pathlib
import unittest

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class AiTechLeadReviewContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "agents.yaml").read_text(encoding="utf-8")
        )
        self.operations = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "agent-operations.yaml").read_text(encoding="utf-8")
        )
        self.jira_model = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "jira-model.yaml").read_text(encoding="utf-8")
        )

    def test_ai_tech_lead_declares_mandatory_review_responsibilities(self) -> None:
        roles = self.agents.get("roles") or {}
        tech_lead = roles.get("ai-tech-lead") or {}
        responsibilities = tech_lead.get("responsibilities") or []
        self.assertIn("mandatory-pr-review", responsibilities)
        self.assertIn("official-review-approval", responsibilities)
        self.assertIn("origin-review-equivalent", responsibilities)

    def test_ai_tech_lead_operation_contract_requires_final_review(self) -> None:
        roles = self.operations.get("roles") or {}
        tech_lead = roles.get("ai-tech-lead") or {}
        self.assertEqual(tech_lead.get("decision_policy"), "tech-lead-review-policy")
        authority = tech_lead.get("review_authority") or {}
        self.assertTrue(authority.get("final_decision"))
        self.assertTrue(authority.get("specialist_reviews_remain_required"))
        self.assertEqual(
            authority.get("mandatory_for"),
            ["pull-request", "equivalent-origin-review"],
        )

    def test_jira_model_keeps_tech_lead_in_review_closure_and_filter(self) -> None:
        workflow = self.jira_model.get("workflow") or {}
        transitions = workflow.get("transitions") or []

        review_done_roles = next(
            transition.get("roles") or []
            for transition in transitions
            if transition.get("from") == "Review" and transition.get("to") == "Done"
        )
        review_changes_roles = next(
            transition.get("roles") or []
            for transition in transitions
            if transition.get("from") == "Review" and transition.get("to") == "Changes Requested"
        )

        self.assertIn("ai-tech-lead", review_done_roles)
        self.assertIn("ai-tech-lead", review_changes_roles)

        quick_filters = (
            ((self.jira_model.get("project") or {}).get("target_board") or {}).get("quick_filters")
            or []
        )
        tech_lead_filters = [
            entry for entry in quick_filters if entry.get("name") == "Ready for Tech Lead Review"
        ]
        self.assertEqual(len(tech_lead_filters), 1)
        self.assertEqual(
            tech_lead_filters[0].get("jql"),
            'status = Review AND "Next Required Role" = "ai-tech-lead"',
        )


if __name__ == "__main__":
    unittest.main()
