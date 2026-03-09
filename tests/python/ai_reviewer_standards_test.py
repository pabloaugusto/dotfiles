from __future__ import annotations

import pathlib
import unittest

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class AiReviewerStandardsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = yaml.safe_load((REPO_ROOT / "config" / "ai" / "agents.yaml").read_text(encoding="utf-8"))
        self.operations = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "agent-operations.yaml").read_text(encoding="utf-8")
        )
        self.standards = yaml.safe_load(
            (REPO_ROOT / "config" / "ai" / "reviewer-standards.yaml").read_text(encoding="utf-8")
        )

    def test_each_active_specialist_reviewer_has_a_standards_profile(self) -> None:
        roles = (self.agents.get("roles") or {})
        specialist_roles = {
            role_name
            for role_name, entry in roles.items()
            if isinstance(entry, dict)
            and role_name.startswith("ai-reviewer-")
            and bool(entry.get("enabled"))
        }
        profiles = (self.standards.get("profiles") or {})
        mapped_roles = {
            role
            for profile in profiles.values()
            if isinstance(profile, dict)
            for role in profile.get("roles") or []
        }
        self.assertFalse(
            specialist_roles - mapped_roles,
            f"Perfis normativos ausentes para reviewers: {sorted(specialist_roles - mapped_roles)}",
        )

    def test_each_profile_has_primary_references(self) -> None:
        profiles = (self.standards.get("profiles") or {})
        for profile_name, profile in profiles.items():
            with self.subTest(profile=profile_name):
                layers = profile.get("governance_layers") or []
                references = [
                    reference
                    for layer in layers
                    if isinstance(layer, dict)
                    for reference in (layer.get("references") or [])
                    if isinstance(reference, dict)
                ]
                self.assertGreaterEqual(len(references), 2)
                for reference in references:
                    self.assertTrue(str(reference.get("title", "")).strip())
                    self.assertTrue(str(reference.get("url", "")).startswith("https://"))

    def test_specialist_operations_reference_standards_profile(self) -> None:
        roles = self.operations.get("roles") or {}
        for role_name in (
            "ai-reviewer-python",
            "ai-reviewer-powershell",
            "ai-reviewer-automation",
            "ai-reviewer-config-policy",
        ):
            with self.subTest(role=role_name):
                entry = roles.get(role_name) or {}
                self.assertTrue(str(entry.get("standards_profile", "")).strip())
                rules = entry.get("operating_rules") or []
                self.assertIn(
                    "citar ao menos uma referencia normativa ou primaria quando o achado depender dela",
                    rules,
                )


if __name__ == "__main__":
    unittest.main()
