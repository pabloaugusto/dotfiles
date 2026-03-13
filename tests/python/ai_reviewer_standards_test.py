from __future__ import annotations

import pathlib
import unittest

from scripts.config_context_lib import load_toml_map

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class AiReviewerStandardsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = load_toml_map(REPO_ROOT / ".agents" / "config" / "agents.toml")
        self.operations = load_toml_map(REPO_ROOT / ".agents" / "config" / "orchestration.toml")
        self.standards = (
            (load_toml_map(REPO_ROOT / ".agents" / "config" / "reviews.toml").get("standards"))
            or {}
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
                layers = profile.get("governance_layers") or {}
                references = [
                    reference
                    for layer in layers.values()
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
            if role_name not in roles:
                continue
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
