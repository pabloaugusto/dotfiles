from __future__ import annotations

import pathlib
import tempfile
import textwrap
import unittest

from scripts.config_context_docs_lib import generated_reference_docs
from scripts.config_context_lib import (
    load_context_manifest,
    resolve_config_ref,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]


class ConfigContextTests(unittest.TestCase):
    def test_resolve_config_ref_supports_nested_toml_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            (repo_root / "config").mkdir(parents=True)
            (repo_root / "config" / "config.toml").write_text(
                textwrap.dedent(
                    """\
                    version = 1

                    [project]
                    id = "dotfiles"
                    source_of_truth = "config/config.toml"
                    default_config_ref_convention = "arquivo::chave"

                    [contexts]
                    dev_root = "config"
                    dev_manifest = "config/config.toml"
                    runtime_root = "app/config"
                    runtime_manifest = "app/config/config.toml"
                    ai_root = ".agents/config"
                    ai_manifest = ".agents/config/config.toml"

                    [resolution]
                    precedence = ["defaults", "context_config", "domain_files", "local_overlay", "environment", "cli"]
                    literal_lint_enabled = true
                    generated_tables_enabled = true
                    single_resolution_library_required = true

                    [regionalization]
                    timezone_name = "America/Sao_Paulo"
                    locale = "pt-BR"
                    language = "pt-BR"
                    currency = "BRL"
                    calendar_system = "gregorian"

                    [domains]
                    dev = "config/dev.toml"
                    integrations = "config/integrations.toml"
                    quality = "config/quality.toml"
                    time_surfaces = "config/time-surfaces.yaml"
                    schema = "config/schema.json"
                    """
                ),
                encoding="utf-8",
            )

            value = resolve_config_ref(
                "config/config.toml::regionalization.timezone_name",
                repo_root=repo_root,
            )

        self.assertEqual(value, "America/Sao_Paulo")

    def test_resolve_config_ref_supports_wildcard_registry_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            registry_dir = repo_root / ".agents" / "registry"
            registry_dir.mkdir(parents=True)
            (registry_dir / "ai-product-owner.toml").write_text(
                'id = "ai-product-owner"\ndisplay_name = "PO"\n',
                encoding="utf-8",
            )
            (registry_dir / "ai-startup-governor.toml").write_text(
                'id = "ai-startup-governor"\ndisplay_name = "Guardiao de Startup"\n',
                encoding="utf-8",
            )

            payload = resolve_config_ref(
                ".agents/registry/*.toml::display_name",
                repo_root=repo_root,
            )

        self.assertEqual(payload["ai-product-owner"], "PO")
        self.assertEqual(payload["ai-startup-governor"], "Guardiao de Startup")

    def test_generated_reference_docs_reads_current_repo_config(self) -> None:
        docs = generated_reference_docs(ROOT)

        self.assertIn("docs/config-reference.md", docs)
        self.assertIn("docs/AI-AGENTS-CATALOG.md", docs)
        self.assertIn("config/config.toml", docs["docs/config-reference.md"])
        self.assertIn(".agents/config/communication.toml", docs["docs/AI-AGENTS-CATALOG.md"])

    def test_load_context_manifest_reads_current_repo_manifests(self) -> None:
        root_path, root_payload = load_context_manifest(ROOT, context="root")
        app_path, app_payload = load_context_manifest(ROOT, context="app")
        ai_path, ai_payload = load_context_manifest(ROOT, context="ai")

        self.assertTrue(root_path.as_posix().endswith("config/config.toml"))
        self.assertTrue(app_path.as_posix().endswith("app/config/config.toml"))
        self.assertTrue(ai_path.as_posix().endswith(".agents/config/config.toml"))
        self.assertIn("regionalization", root_payload)
        self.assertIn("domains", app_payload)
        self.assertIn("compatibility", ai_payload)


if __name__ == "__main__":
    unittest.main()
