from __future__ import annotations

import pathlib
import unittest
from typing import cast

from scripts.ai_atlassian_openapi_lib import spec_catalog_payload

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLASSIAN_SCRIPT_PATHS = [
    ROOT / "scripts" / "ai_jira_apply_lib.py",
    ROOT / "scripts" / "atlassian_platform_lib.py",
]


class AtlassianOpenApiCatalogTests(unittest.TestCase):
    def test_spec_catalog_payload_exposes_jira_and_confluence(self) -> None:
        payload = spec_catalog_payload()
        specs = cast(dict[str, object], payload["specs"])
        self.assertIsInstance(specs, dict)
        jira_spec = cast(dict[str, object], specs["jira"])
        confluence_spec = cast(dict[str, object], specs["confluence"])
        self.assertIsInstance(jira_spec, dict)
        self.assertIsInstance(confluence_spec, dict)

        self.assertIn("jira", specs)
        self.assertIn("confluence", specs)
        self.assertTrue(str(jira_spec["vendor_path"]).endswith("jira-openapi.json"))
        self.assertTrue(str(confluence_spec["vendor_path"]).endswith("confluence-openapi.json"))

    def test_atlassian_scripts_stay_on_jira_v3_and_confluence_v2(self) -> None:
        forbidden_literals = [
            "/rest/api/2/",
            "/rest/api/3/search\"",
            "/wiki/rest/api/",
            "/wiki/api/v1/",
        ]

        for path in ATLASSIAN_SCRIPT_PATHS:
            raw = path.read_text(encoding="utf-8")
            for literal in forbidden_literals:
                self.assertNotIn(literal, raw, msg=f"endpoint legado detectado em {path}: {literal}")

        jira_apply = (ROOT / "scripts" / "ai_jira_apply_lib.py").read_text(encoding="utf-8")
        platform = (ROOT / "scripts" / "atlassian_platform_lib.py").read_text(encoding="utf-8")
        self.assertIn("/rest/api/3/search/jql", jira_apply)
        self.assertIn("/rest/api/3/search/jql", platform)
        self.assertIn("/wiki/api/v2/spaces", platform)
        self.assertIn("/wiki/api/v2/pages", platform)


if __name__ == "__main__":
    unittest.main()
