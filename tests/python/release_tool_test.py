from __future__ import annotations

import unittest

from scripts.release_tool import load_tool_spec, platform_asset_key


class ReleaseToolTest(unittest.TestCase):
    def test_tool_specs_load_from_config(self) -> None:
        actionlint = load_tool_spec("actionlint")
        gitleaks = load_tool_spec("gitleaks")

        self.assertEqual(actionlint.version, "1.7.11")
        self.assertEqual(gitleaks.version, "8.30.0")
        self.assertIn("windows_x64", actionlint.assets)
        self.assertIn("linux_x64", gitleaks.assets)

    def test_platform_asset_key_matches_supported_platforms(self) -> None:
        self.assertIn(platform_asset_key(), {"windows_x64", "linux_x64", "linux_arm64"})


if __name__ == "__main__":
    unittest.main()
