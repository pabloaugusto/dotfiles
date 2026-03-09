from __future__ import annotations

import unittest

from scripts.ai_atlassian_backfill_lib import JIRA_SUMMARY_LIMIT, build_backfill_plan, build_jira_summary


class AtlassianBackfillPlanTests(unittest.TestCase):
    def test_build_backfill_plan_includes_expected_sections(self) -> None:
        payload = build_backfill_plan()

        self.assertIn("metadata", payload)
        self.assertIn("jira", payload)
        self.assertIn("confluence", payload)
        self.assertGreater(payload["jira"]["counts"]["total_records"], 0)
        self.assertGreater(payload["confluence"]["count"], 0)

    def test_backfill_plan_tracks_local_ids(self) -> None:
        payload = build_backfill_plan()
        roadmap_ids = {entry["external_id"] for entry in payload["jira"]["roadmap_backlog"]}
        self.assertIn("RM-001", roadmap_ids)

        worklog_ids = {entry["external_id"] for entry in payload["jira"]["worklog_doing"]}
        self.assertIn("WIP-20260307-ATLASSIAN-ADAPTERS", worklog_ids)

    def test_backfill_plan_includes_seed_activity_with_evidence(self) -> None:
        payload = build_backfill_plan()

        first_backlog = payload["jira"]["roadmap_backlog"][0]
        self.assertEqual(first_backlog["seed_activity"]["agent"], "ai-product-owner")
        self.assertGreater(len(first_backlog["seed_activity"]["evidencias"]), 0)
        self.assertEqual(
            payload["metadata"]["timestamp_policy"]["source_tracker_timezone"],
            "UTC",
        )

    def test_build_jira_summary_enforces_limit(self) -> None:
        summary = build_jira_summary("SG-1", "x" * 400)

        self.assertLessEqual(len(summary), JIRA_SUMMARY_LIMIT)
        self.assertTrue(summary.startswith("[SG-1] "))

    def test_all_exported_summaries_fit_jira_limit(self) -> None:
        payload = build_backfill_plan()
        all_records = []
        all_records.extend(payload["jira"]["roadmap_backlog"])
        all_records.extend(payload["jira"]["roadmap_suggestions"])
        all_records.extend(payload["jira"]["worklog_doing"])
        all_records.extend(payload["jira"]["worklog_done"])

        self.assertTrue(all_records)
        for record in all_records:
            self.assertLessEqual(len(record["summary"]), JIRA_SUMMARY_LIMIT)


if __name__ == "__main__":
    unittest.main()
