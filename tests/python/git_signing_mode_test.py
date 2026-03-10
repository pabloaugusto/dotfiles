from __future__ import annotations

import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.git_signing_lib import (
    GitSigningError,
    RepoContext,
    apply_automation_mode,
    apply_human_mode,
    build_default_title,
    default_allowed_signers_path,
    default_local_automation_key_path,
    ensure_github_signing_key,
    ensure_local_automation_keypair,
    load_secrets_refs,
    normalize_public_key,
    public_key_identity,
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
        without_comment = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITestAutomationPublicKey"
        self.assertEqual(public_key_identity(VALID_KEY), public_key_identity(without_comment))

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
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)

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
                VALID_KEY,
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
                        "gpg.ssh.allowedSignersFile",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                str(default_allowed_signers_path(RepoContext(repo, repo / ".git", repo / ".git"))),
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
                        "dotfiles.signing.automationBackend",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                "agent-backed",
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
                        "dotfiles.signing.automationPublicKey",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                VALID_KEY,
            )

    def test_apply_automation_mode_generates_local_key_when_no_ref_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)

            payload = apply_automation_mode(repo)

            private_key_path = pathlib.Path(str(payload["private_key_path"]))
            self.assertEqual(payload["mode"], "automation")
            self.assertEqual(payload["backend"], "local-key")
            self.assertTrue(private_key_path.exists())
            self.assertTrue(private_key_path.with_suffix(".pub").exists())
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "config",
                        "--worktree",
                        "--get",
                        "user.signingkey",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                str(private_key_path),
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
                        "dotfiles.signing.automationPrivateKeyPath",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip(),
                str(private_key_path),
            )
            self.assertTrue(
                str(payload["effective_gpg_program"]).lower().endswith("ssh-keygen")
                or str(payload["effective_gpg_program"]).lower().endswith("ssh-keygen.exe")
            )

    def test_apply_automation_mode_supports_signed_commit_with_local_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.name", "dotfiles automation"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.email", "automation@example.com"],
                check=True,
            )

            payload = apply_automation_mode(repo)
            self.assertEqual(payload["backend"], "local-key")

            completed = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "commit",
                    "--allow-empty",
                    "-S",
                    "-m",
                    "🔧 chore(git): DOT-12 validar signer local",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"git commit -S falhou: stdout={completed.stdout!r} stderr={completed.stderr!r}",
            )
            verification = subprocess.run(
                ["git", "-C", str(repo), "log", "--show-signature", "-1", "--format=fuller", "HEAD"],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn('Good "git" signature for automation@example.com', verification.stdout)

    def test_apply_human_mode_unsets_worktree_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
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
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            apply_automation_mode(repo, public_key=VALID_KEY)

            payload = status_payload(repo)

            self.assertTrue(payload["worktree_config_enabled"])
            self.assertEqual(payload["mode"], "automation")
            self.assertEqual(payload["effective_signing_key"], VALID_KEY)
            self.assertTrue(payload["worktree_automation_public_key_cached"])
            self.assertEqual(payload["worktree_automation_backend"], "agent-backed")
            self.assertEqual(payload["effective_signing_principal"], "test@example.com")
            self.assertTrue(str(payload["effective_allowed_signers_file"]).endswith("allowed_signers"))

    def test_resolve_public_key_ref_falls_back_to_cached_key_when_op_read_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "-C", str(repo), "config", "extensions.worktreeConfig", "true"],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "config",
                    "--worktree",
                    "dotfiles.signing.automationPublicKeyRef",
                    "op://secrets/dotfiles/git-automation/public key",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "config",
                    "--worktree",
                    "dotfiles.signing.automationPublicKey",
                    VALID_KEY,
                ],
                check=True,
            )

            with patch(
                "scripts.git_signing_lib.read_public_key_from_1password",
                side_effect=GitSigningError("rate limited"),
            ):
                chosen_ref, resolved_key = resolve_public_key_ref(repo)

            self.assertEqual(
                chosen_ref,
                "op://secrets/dotfiles/git-automation/public key",
            )
            self.assertEqual(resolved_key, VALID_KEY)

    def test_resolve_public_key_ref_uses_cached_key_without_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "-C", str(repo), "config", "extensions.worktreeConfig", "true"],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "config",
                    "--worktree",
                    "dotfiles.signing.automationPublicKey",
                    VALID_KEY,
                ],
                check=True,
            )

            chosen_ref, resolved_key = resolve_public_key_ref(repo)

            self.assertEqual(chosen_ref, "")
            self.assertEqual(resolved_key, VALID_KEY)

    def test_ensure_local_automation_keypair_reuses_existing_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            repo_context = RepoContext(
                repo_root=repo,
                git_dir=repo / ".git",
                common_dir=repo / ".git",
            )
            first = ensure_local_automation_keypair(repo_context, title="dotfiles-test")
            second = ensure_local_automation_keypair(repo_context, title="dotfiles-test")

            self.assertTrue(pathlib.Path(str(first["private_key_path"])).exists())
            self.assertEqual(first["public_key"], second["public_key"])
            self.assertFalse(bool(second["created"]))

    def test_default_local_automation_key_path_stays_inside_git_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            context = RepoContext(
                repo_root=repo,
                git_dir=repo / ".git",
                common_dir=repo / ".git",
            )
            key_path = default_local_automation_key_path(context)
            self.assertTrue(str(key_path).startswith(str(repo / ".git")))

    def test_ensure_github_signing_key_retries_after_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            responses = [
                [],
                [],
                [{"id": 123, "title": "dotfiles-test", "key": VALID_KEY}],
            ]

            with patch(
                "scripts.git_signing_lib.list_github_signing_keys",
                side_effect=responses,
            ), patch("scripts.git_signing_lib.run_command"), patch(
                "scripts.git_signing_lib.time.sleep"
            ):
                payload = ensure_github_signing_key(
                    repo,
                    public_key=VALID_KEY,
                    title="dotfiles-test",
                )

            self.assertEqual(payload["status"], "created")
            self.assertEqual(payload["id"], 123)


if __name__ == "__main__":
    unittest.main()
