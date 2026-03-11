from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / ".githooks" / "conventional_emoji.py"

SPEC = importlib.util.spec_from_file_location("conventional_emoji", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
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

    def test_rejects_missing_issue_key_when_required(self) -> None:
        result = MODULE.validate_message(
            "✨ feat(test-harness): add validator",
            require_emoji=True,
            require_issue_key=True,
        )
        self.assertFalse(result.ok)
        self.assertIn("Chave Jira obrigatoria", result.error)

    def test_rejects_multiple_issue_keys_when_required(self) -> None:
        result = MODULE.validate_message(
            "✨ feat(test-harness): DOT-130 DOT-131 add validator",
            require_emoji=True,
            require_issue_key=True,
        )
        self.assertFalse(result.ok)
        self.assertIn("exatamente uma chave Jira", result.error)

    def test_rejects_messages_longer_than_limit(self) -> None:
        description = "a" * 80
        result = MODULE.validate_message(
            f"✨ feat(test-harness): {description}", require_emoji=True
        )
        self.assertFalse(result.ok)
        self.assertIn("Maximo recomendado", result.error)

    def test_requires_prompt_scope_when_requested(self) -> None:
        result = MODULE.validate_message(
            "📝 docs(git): DOT-179 document prompt namespace",
            require_emoji=True,
            require_issue_key=True,
            required_scope="prompt",
        )
        self.assertFalse(result.ok)
        self.assertIn("Scope obrigatorio", result.error)

    def test_inject_emoji_normalizes_wrong_emoji(self) -> None:
        output = MODULE.inject_emoji("🐛 feat(test-harness): add validator\n")
        self.assertEqual(output, "✨ feat(test-harness): add validator\n")

    def test_branch_validation_accepts_expected_type(self) -> None:
        result = MODULE.validate_branch_name("release/test-harness-governance")
        self.assertTrue(result.ok)

    def test_branch_validation_accepts_canonical_jira_branch(self) -> None:
        result = MODULE.validate_branch_name("feat/DOT-81-git-traceability")
        self.assertTrue(result.ok)

    def test_branch_validation_accepts_prompt_type(self) -> None:
        result = MODULE.validate_branch_name("prompt/DOT-179-agnostic-sync-outbox-foundation")
        self.assertTrue(result.ok)

    def test_branch_validation_allows_dependabot(self) -> None:
        result = MODULE.validate_branch_name("dependabot/npm_and_yarn/foo-1.2.3")
        self.assertTrue(result.ok)

    def test_branch_validation_rejects_uppercase(self) -> None:
        result = MODULE.validate_branch_name("Feat/test-harness")
        self.assertFalse(result.ok)
        self.assertIn("<type>/<jira-key>-<slug>", result.error)

    def test_branch_validation_requires_prompt_type_when_prompt_paths_are_present(self) -> None:
        result = MODULE.validate_branch_name(
            "feat/DOT-179-agnostic-sync-outbox-foundation",
            require_prompt_type=True,
        )
        self.assertFalse(result.ok)
        self.assertIn("prefixo 'prompt'", result.error)

    def test_required_scope_is_derived_from_prompt_paths(self) -> None:
        required_scope = MODULE.required_scope_for_paths_and_branch(
            [".agents/prompts/formal/pea-startup-governance/prompt.md"],
            "feat/DOT-178-pea-startup-governance",
        )
        self.assertEqual(required_scope, "prompt")

    def test_extended_type_mapping_is_available(self) -> None:
        self.assertEqual(MODULE.COMMIT_TYPE_EMOJI["security"], "🔒")
        self.assertEqual(MODULE.COMMIT_TYPE_EMOJI["release"], "🔖")
        self.assertEqual(MODULE.COMMIT_TYPE_EMOJI["i18n"], "🌐")


if __name__ == "__main__":
    unittest.main()
