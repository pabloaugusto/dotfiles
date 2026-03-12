from __future__ import annotations

import unittest

from scripts.ai_atlassian_backfill_lib import (
    JIRA_SUMMARY_LIMIT,
    build_backfill_plan,
    build_jira_summary,
)


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
        self.assertTrue(any(item.startswith("WIP-") for item in worklog_ids))

    def test_backfill_plan_includes_seed_activity_with_evidence(self) -> None:
        payload = build_backfill_plan()

        first_backlog = payload["jira"]["roadmap_backlog"][0]
        self.assertEqual(first_backlog["seed_activity"]["agent"], "PO")
        self.assertGreater(len(first_backlog["seed_activity"]["evidencias"]), 0)
        self.assertTrue(
            first_backlog["seed_activity"]["evidencias"][0].startswith(
                "https://github.com/pabloaugusto/dotfiles/blob/main/"
            )
        )
        self.assertEqual(
            payload["metadata"]["timestamp_policy"]["source_tracker_timezone"],
            "UTC",
        )
        self.assertIn(
            first_backlog["seed_activity"]["status"],
            {"backlog", "refinement", "ready", "doing", "paused", "testing", "review", "done"},
        )

    def test_accepted_roadmap_suggestion_uses_canonical_backlog_status_in_comment(self) -> None:
        payload = build_backfill_plan()
        accepted = next(
            entry for entry in payload["jira"]["roadmap_suggestions"] if "aceita" in entry["labels"]
        )

        self.assertEqual(accepted["state_hint"], "backlog")
        self.assertEqual(accepted["seed_activity"]["status"], "backlog")

    def test_backfill_issue_descriptions_now_include_acceptance_criteria(self) -> None:
        payload = build_backfill_plan()
        first_story = next(
            entry for entry in payload["jira"]["roadmap_backlog"] if entry["issue_type"] == "Story"
        )
        description = "\n".join(first_story["description_lines"])

        self.assertIn("## Historia", description)
        self.assertIn("## Criterios de aceite", description)
        self.assertIn("## Referencias", description)
        self.assertIn("Artefato de origem no GitHub:", description)

    def test_worklog_task_descriptions_use_human_narrative_sections(self) -> None:
        payload = build_backfill_plan()
        first_worklog = payload["jira"]["worklog_doing"][0]
        description = "\n".join(first_worklog["description_lines"])

        self.assertIn("## Contexto", description)
        self.assertIn("## Resultado esperado", description)
        self.assertIn("## Escopo tecnico", description)
        self.assertIn("## Criterios de aceite", description)

    def test_worklog_seed_activity_uses_documentation_sync_role(self) -> None:
        payload = build_backfill_plan()
        first_worklog = payload["jira"]["worklog_doing"][0]
        seed_activity = first_worklog["seed_activity"]

        self.assertEqual(seed_activity["agent"], "Sync Documental")
        self.assertIn("documentation-link", seed_activity["proximo_passo"])

    def test_build_jira_summary_enforces_limit(self) -> None:
        summary = build_jira_summary("SG-1", "x" * 400)

        self.assertLessEqual(len(summary), JIRA_SUMMARY_LIMIT)
        self.assertFalse(summary.startswith("[SG-1] "))

    def test_build_jira_summary_strips_markdown_noise(self) -> None:
        summary = build_jira_summary(
            "SG-1",
            "Mover o arquivo [LICOES-APRENDIDAS.md](LICOES-APRENDIDAS.md) para `docs/`",
        )
        self.assertEqual(summary, "Mover o arquivo LICOES-APRENDIDAS.md para docs/")

    def test_build_jira_summary_prefers_semantic_head_before_truncating(self) -> None:
        summary = build_jira_summary(
            "SG-1",
            "Implementar o modulo de rotacionamento automatizado de secrets, chaves SSH, tokens e artefatos sops+age, com tarefas isoladas e task unificada",
        )
        self.assertEqual(
            summary,
            "Implementar o modulo de rotacionamento automatizado de secrets",
        )

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
