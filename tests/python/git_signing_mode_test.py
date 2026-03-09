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
    build_git_ssh_command,
    load_local_automation_public_key,
    load_secrets_refs,
    normalize_public_key,
    public_key_identity,
    resolve_local_ssh_sign_program,
    resolve_public_key_ref,
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

    def test_public_key_identity_ignores_comment_suffix(self) -> None:
        with_comment = VALID_KEY
        without_comment = VALID_KEY.rsplit(" ", 1)[0]
        self.assertEqual(public_key_identity(with_comment), public_key_identity(without_comment))

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

    def test_build_git_ssh_command_is_agentless_and_key_scoped(self) -> None:
        command = build_git_ssh_command(pathlib.Path("C:/tmp/id_ed25519"))
        self.assertIn('-i "C:/tmp/id_ed25519"', command)
        self.assertIn("-o IdentitiesOnly=yes", command)
        self.assertIn("-o IdentityAgent=none", command)

    def test_resolve_public_key_ref_falls_back_to_local_automation_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            automation_dir = repo / ".git" / "dotfiles" / "automation-signing"
            automation_dir.mkdir(parents=True)
            (automation_dir / "id_ed25519.pub").write_text(VALID_KEY + "\n", encoding="utf-8")

            chosen_ref, resolved_key = resolve_public_key_ref(repo)

            self.assertEqual(chosen_ref, "")
            self.assertEqual(resolved_key, VALID_KEY)

    def test_load_local_automation_public_key_reads_pub_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            automation_dir = repo / ".git" / "dotfiles" / "automation-signing"
            automation_dir.mkdir(parents=True)
            (automation_dir / "id_ed25519.pub").write_text(VALID_KEY + "\n", encoding="utf-8")

            resolved = load_local_automation_public_key(repo)

            self.assertEqual(resolved, VALID_KEY)

    def test_apply_automation_mode_writes_worktree_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            automation_dir = repo / ".git" / "dotfiles" / "automation-signing"
            automation_dir.mkdir(parents=True)
            (automation_dir / "id_ed25519").write_text("PRIVATE", encoding="utf-8")
            (automation_dir / "id_ed25519.pub").write_text(VALID_KEY + "\n", encoding="utf-8")

            payload = apply_automation_mode(repo, public_key=VALID_KEY)

            self.assertEqual(payload["mode"], "automation")
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "config",
                        "--worktree",
                        "--get",
                        "dotfiles.signing.mode",
                    ],
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
                str(automation_dir / "id_ed25519"),
            )
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "config",
                        "--worktree",
                        "--get",
                        "dotfiles.github.authMode",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                "automation",
            )
            ssh_command = subprocess.run(
                ["git", "-C", str(repo), "config", "--worktree", "--get", "core.sshCommand"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            signer_program = subprocess.run(
                ["git", "-C", str(repo), "config", "--worktree", "--get", "gpg.ssh.program"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            self.assertIn("IdentityAgent=none", ssh_command)
            self.assertIn("IdentitiesOnly=yes", ssh_command)
            self.assertEqual(signer_program, resolve_local_ssh_sign_program())

    def test_apply_human_mode_unsets_worktree_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            automation_dir = repo / ".git" / "dotfiles" / "automation-signing"
            automation_dir.mkdir(parents=True)
            (automation_dir / "id_ed25519").write_text("PRIVATE", encoding="utf-8")
            (automation_dir / "id_ed25519.pub").write_text(VALID_KEY + "\n", encoding="utf-8")
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
            ssh_command = subprocess.run(
                ["git", "-C", str(repo), "config", "--worktree", "--get", "core.sshCommand"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(ssh_command.returncode, 0)

    def test_status_payload_reports_current_worktree_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            automation_dir = repo / ".git" / "dotfiles" / "automation-signing"
            automation_dir.mkdir(parents=True)
            (automation_dir / "id_ed25519").write_text("PRIVATE", encoding="utf-8")
            (automation_dir / "id_ed25519.pub").write_text(VALID_KEY + "\n", encoding="utf-8")
            apply_automation_mode(repo, public_key=VALID_KEY)

            payload = status_payload(repo)

            self.assertTrue(payload["worktree_config_enabled"])
            self.assertEqual(payload["mode"], "automation")
            self.assertEqual(payload["effective_signing_key"], str(automation_dir / "id_ed25519"))


if __name__ == "__main__":
    unittest.main()
