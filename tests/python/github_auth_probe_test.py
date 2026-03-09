from __future__ import annotations

import unittest

from scripts.github_auth_probe_lib import (
    build_probe_env,
    classify_endpoint_probe,
    parse_active_sources,
)


class GitHubAuthProbeTests(unittest.TestCase):
    def test_build_probe_env_can_remove_env_tokens(self) -> None:
        env = {
            "GH_TOKEN": "gh-env-token",
            "GITHUB_TOKEN": "github-env-token",
            "OTHER_VAR": "kept",
        }
        sanitized = build_probe_env(env, clear_token_env=True)
        self.assertNotIn("GH_TOKEN", sanitized)
        self.assertNotIn("GITHUB_TOKEN", sanitized)
        self.assertEqual(sanitized["OTHER_VAR"], "kept")

    def test_parse_active_sources_reads_gh_status_blocks(self) -> None:
        output = """
github.com
  Logged in to github.com account pabloaugusto (GH_TOKEN)
  - Active account: true
  - Git operations protocol: ssh

  Logged in to github.com account pabloaugusto (keyring)
  - Active account: false
"""
        self.assertEqual(parse_active_sources(output), ["GH_TOKEN"])

    def test_classify_endpoint_probe_flags_github_app_requirement(self) -> None:
        classification = classify_endpoint_probe(
            "user/installations",
            exit_code=1,
            output=(
                "gh: You must authenticate with an access token authorized to a "
                "GitHub App in order to list installations (HTTP 403)"
            ),
        )
        self.assertEqual(classification["status"], "requires_github_app_user_token")

    def test_classify_endpoint_probe_accepts_empty_signing_key_list(self) -> None:
        classification = classify_endpoint_probe(
            "user/ssh_signing_keys",
            exit_code=0,
            output="[]",
        )
        self.assertEqual(classification["status"], "ok")
        self.assertIn("nenhuma SSH signing key", classification["note"])
