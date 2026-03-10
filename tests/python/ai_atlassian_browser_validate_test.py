from __future__ import annotations

import pathlib
import tempfile
import unittest

from scripts.ai_atlassian_browser_validate_lib import (
    evaluate_expected_text_checks,
    evaluate_title_check,
    validation_config,
)


class AtlassianBrowserValidateTests(unittest.TestCase):
    def test_validation_config_uses_repo_cache_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            config = validation_config(repo_root=repo_root, target_url="https://example.invalid")

        self.assertTrue(str(config.storage_state_path).endswith("storage-state.json"))
        self.assertIn(".cache", str(config.evidence_dir))
        self.assertEqual(config.target_url, "https://example.invalid")
        self.assertTrue(config.headless)

    def test_validation_config_normalizes_expected_texts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = validation_config(
                repo_root=tmp,
                target_url="https://example.invalid",
                expected_texts=[" DOT board ", "", "BACKLOG"],
                headless=False,
            )

        self.assertEqual(config.expected_texts, ("DOT board", "BACKLOG"))
        self.assertFalse(config.headless)

    def test_evaluate_title_check_prefers_browser_title(self) -> None:
        title_ok, match_mode = evaluate_title_check(
            "Board settings",
            title="Board settings - Jira",
            body_text="Map statuses to columns",
        )

        self.assertTrue(title_ok)
        self.assertEqual(match_mode, "title")

    def test_evaluate_title_check_accepts_body_fallback(self) -> None:
        title_ok, match_mode = evaluate_title_check(
            "Board settings",
            title="Jira",
            body_text="Board settings\nMap statuses to columns\nPaused",
        )

        self.assertTrue(title_ok)
        self.assertEqual(match_mode, "body-fallback")

    def test_evaluate_title_check_reports_missing_match(self) -> None:
        title_ok, match_mode = evaluate_title_check(
            "Board settings",
            title="Jira",
            body_text="Map statuses to columns\nPaused",
        )

        self.assertFalse(title_ok)
        self.assertEqual(match_mode, "missing")

    def test_evaluate_expected_text_checks_accepts_title_or_body(self) -> None:
        checks = evaluate_expected_text_checks(
            ("DOT - Agile Operating Manual", "Workflow alvo", "Inexistente"),
            title="DOT - Agile Operating Manual - Confluence",
            body_text="Manual de agilidade do control plane\nWorkflow alvo\nPaused",
        )

        self.assertEqual(
            checks,
            {
                "DOT - Agile Operating Manual": True,
                "Workflow alvo": True,
                "Inexistente": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
