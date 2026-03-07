from __future__ import annotations

import pathlib
import subprocess
import tempfile
import unittest

from scripts.git_signing_lib import (
    GitSigningError,
    apply_automation_mode,
    apply_human_mode,
    build_default_title,
    load_secrets_refs,
    normalize_public_key,
    status_payload,
)


VALID_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITestAutomationPublicKey dotfiles-ai"


class GitSigningModeTests(unittest.TestCase):
    def test_normalize_public_key_accepts_valid_input(self) -> None:
        normalized = normalize_public_key(f"  {VALID_KEY}\n")
        self.assertEqual(normalized, VALID_KEY)

    def test_normalize_public_key_rejects_invalid_input(self) -> None:
        with self.assertRaises(GitSigningError):
            normalize_public_key("not-a-key")

    def test_load_secrets_refs_reads_automation_public_key_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            refs_path = repo / "df" / "secrets"
            refs_path.mkdir(parents=True)
            (refs_path / "secrets-ref.yaml").write_text(
                "---\n"
                "git-signing:\n"
                '  automation-public-key: "op://secrets/dotfiles/git-automation/public key"\n',
                encoding="utf-8",
            )
            refs = load_secrets_refs(repo)
            self.assertEqual(
                refs["automation_public_key_ref"],
                "op://secrets/dotfiles/git-automation/public key",
            )

    def test_build_default_title_uses_hostname(self) -> None:
        self.assertEqual(
            build_default_title("my-host.local"),
            "dotfiles-automation-signing-my-host.local",
        )

    def test_apply_automation_mode_writes_worktree_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            payload = apply_automation_mode(repo, public_key=VALID_KEY)

            self.assertEqual(payload["mode"], "automation")
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(repo), "config", "--worktree", "--get", "dotfiles.signing.mode"],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                "automation",
            )
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(repo), "config", "--worktree", "--get", "user.signingkey"],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                VALID_KEY,
            )

    def test_apply_human_mode_unsets_worktree_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            apply_automation_mode(repo, public_key=VALID_KEY)

            payload = apply_human_mode(repo)

            self.assertEqual(payload["mode"], "human")
            worktree_mode = subprocess.run(
                ["git", "-C", str(repo), "config", "--worktree", "--get", "dotfiles.signing.mode"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(worktree_mode.returncode, 0)

    def test_status_payload_reports_current_worktree_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            apply_automation_mode(repo, public_key=VALID_KEY)

            payload = status_payload(repo)

            self.assertTrue(payload["worktree_config_enabled"])
            self.assertEqual(payload["mode"], "automation")
            self.assertEqual(payload["effective_signing_key"], VALID_KEY)


if __name__ == "__main__":
    unittest.main()
