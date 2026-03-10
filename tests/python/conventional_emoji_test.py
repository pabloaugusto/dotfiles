from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / ".githooks" / "conventional_emoji.py"

SPEC = importlib.util.spec_from_file_location("conventional_emoji", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ConventionalEmojiTests(unittest.TestCase):
    def test_valid_message_with_expected_emoji(self) -> None:
        result = MODULE.validate_message("✨ feat(test-harness): add validator", require_emoji=True)
        self.assertTrue(result.ok)

    def test_rejects_wrong_emoji_for_type(self) -> None:
        result = MODULE.validate_message("🐛 feat(test-harness): add validator", require_emoji=True)
        self.assertFalse(result.ok)
        self.assertIn("Esperado", result.error)

    def test_rejects_missing_emoji_when_required(self) -> None:
        result = MODULE.validate_message("feat(test-harness): add validator", require_emoji=True)
        self.assertFalse(result.ok)
        self.assertIn("Emoji obrigatorio", result.error)

    def test_rejects_messages_longer_than_limit(self) -> None:
        description = "a" * 80
        result = MODULE.validate_message(
            f"✨ feat(test-harness): {description}", require_emoji=True
        )
        self.assertFalse(result.ok)
        self.assertIn("Maximo recomendado", result.error)

    def test_inject_emoji_normalizes_wrong_emoji(self) -> None:
        output = MODULE.inject_emoji("🐛 feat(test-harness): add validator\n")
        self.assertEqual(output, "✨ feat(test-harness): add validator\n")

    def test_branch_validation_accepts_expected_type(self) -> None:
        result = MODULE.validate_branch_name("release/test-harness-governance")
        self.assertTrue(result.ok)

    def test_branch_validation_accepts_canonical_jira_branch(self) -> None:
        result = MODULE.validate_branch_name("feat/DOT-81-git-traceability")
        self.assertTrue(result.ok)

    def test_branch_validation_allows_dependabot(self) -> None:
        result = MODULE.validate_branch_name("dependabot/npm_and_yarn/foo-1.2.3")
        self.assertTrue(result.ok)

    def test_branch_validation_rejects_uppercase(self) -> None:
        result = MODULE.validate_branch_name("Feat/test-harness")
        self.assertFalse(result.ok)
        self.assertIn("<type>/<jira-key>-<slug>", result.error)

    def test_extended_type_mapping_is_available(self) -> None:
        self.assertEqual(MODULE.COMMIT_TYPE_EMOJI["security"], "🔒")
        self.assertEqual(MODULE.COMMIT_TYPE_EMOJI["release"], "🔖")
        self.assertEqual(MODULE.COMMIT_TYPE_EMOJI["i18n"], "🌐")


if __name__ == "__main__":
    unittest.main()
