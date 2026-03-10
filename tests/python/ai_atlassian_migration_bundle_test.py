from __future__ import annotations

import json
import pathlib
import tempfile
import unittest
import zipfile

from scripts.ai_atlassian_migration_bundle_lib import build_migration_bundle


class AtlassianMigrationBundleTests(unittest.TestCase):
    def test_build_migration_bundle_writes_manifest_and_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = build_migration_bundle(output_root=tmp)

            manifest_path = pathlib.Path(payload["manifest_path"])
            zip_path = pathlib.Path(payload["zip_path"])

            self.assertTrue(manifest_path.exists())
            self.assertTrue(zip_path.exists())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            source_paths = {entry["path"] for entry in manifest["source_files"]}
            generated_paths = {entry["path"] for entry in manifest["generated_files"]}

            self.assertIn("config/ai/jira-model.yaml", source_paths)
            self.assertIn("config/ai/confluence-model.yaml", source_paths)
            self.assertIn("generated/backfill-plan.json", generated_paths)

            with zipfile.ZipFile(zip_path) as archive:
                names = set(archive.namelist())
            self.assertIn("manifest.json", names)
            self.assertIn("generated/backfill-plan.json", names)
            self.assertIn("repo/config/ai/jira-model.yaml", names)


if __name__ == "__main__":
    unittest.main()
