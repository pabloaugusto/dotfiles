from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ai_atlassian_seed_lib import (
    build_seed_plan,
    flatten_page_tree,
    jira_board_layout_confirmed,
    normalize_status_label,
    state_hint_to_logical_status,
)
from scripts.ai_control_plane_lib import load_yaml_map


class AtlassianSeedPlanTests(unittest.TestCase):
    def test_build_seed_plan_reports_records_and_pages(self) -> None:
        payload = build_seed_plan()

        self.assertEqual(payload["metadata"]["project_key"], "DOT")
        self.assertEqual(payload["metadata"]["space_key"], "DOT")
        self.assertGreater(payload["jira"]["total_records"], 0)
        self.assertGreater(payload["confluence"]["total_pages"], 0)
        self.assertFalse(payload["preconditions"]["board_layout_confirmed"])
        self.assertEqual(
            payload["preconditions"]["board_layout_status"],
            "blocked-until-board-layout-confirmed",
        )

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
        self.assertEqual(state_hint_to_logical_status("pendente"), "backlog")
        self.assertEqual(normalize_status_label(" Changes   Requested "), "changes requested")

    def test_board_layout_confirmation_defaults_to_false(self) -> None:
        model = load_yaml_map(Path("config/ai/jira-model.yaml"))
        self.assertFalse(jira_board_layout_confirmed(model))


if __name__ == "__main__":
    unittest.main()
