from __future__ import annotations

import pathlib
import tempfile
import unittest
from unittest import mock

from scripts.secrets_rotation_lib import (
    load_repo_context,
    plan_payload,
    preflight_payload,
    validate_payload,
)


def write_repo_fixture(repo: pathlib.Path) -> None:
    (repo / "config").mkdir(parents=True, exist_ok=True)
    (repo / "df" / "secrets").mkdir(parents=True, exist_ok=True)
    (repo / "docs").mkdir(parents=True, exist_ok=True)
    (repo / "config" / "secrets-rotation.yaml").write_text(
        "version: 1\n"
        "policy:\n"
        '  rotation_strategy: "blue_green"\n'
        "audit:\n"
        '  state_path: ".cache/secrets-rotation/audit.sops.yaml"\n'
        '  report_path: ".cache/secrets-rotation/last-report.json"\n'
        "targets:\n"
        "  github-ssh-auth:\n"
        "    enabled: true\n"
        '    kind: "github_ssh_identity"\n'
        '    automation: "fully_automated"\n'
        "    order: 10\n"
        '    source_of_truth: "1password"\n'
        '    publication_kind: "authentication"\n'
        '    validate_remote: "origin"\n'
        "  age-runtime:\n"
        "    enabled: true\n"
        '    kind: "age_runtime_key"\n'
        '    automation: "fully_automated"\n'
        "    order: 20\n"
        '    source_of_truth: "1password"\n'
        '    ref_key: "age.key"\n'
        '    sops_config_path: "df/secrets/dotfiles.sops.yaml"\n'
        "    encrypted_artifacts:\n"
        '      - path: "missing.env.sops"\n'
        '        input_type: "dotenv"\n',
        encoding="utf-8",
    )
    (repo / "df" / "secrets" / "secrets-ref.yaml").write_text(
        "---\n"
        "1password:\n"
        '  service-account: "op://secrets/dotfiles/1password/service-account"\n'
        "age:\n"
        '  key: "op://secrets/dotfiles/age/age.key"\n',
        encoding="utf-8",
    )
    (repo / "df" / "secrets" / "dotfiles.sops.yaml").write_text(
        "creation_rules:\n"
        "  - path_regex: ^df/secrets/.*$\n"
        "    age:\n"
        "      - age1REPLACE_WITH_YOUR_PUBLIC_AGE_KEY\n",
        encoding="utf-8",
    )


class SecretsRotationTests(unittest.TestCase):
    def test_load_repo_context_orders_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            write_repo_fixture(repo)
            context, _config, _refs, targets = load_repo_context(repo)
            self.assertEqual(context.repo_root, repo.resolve())
            self.assertEqual([target.target_id for target in targets], ["github-ssh-auth", "age-runtime"])

    @mock.patch("scripts.secrets_rotation_lib.command_exists")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_gitlab")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_github")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_op")
    def test_preflight_reports_missing_commands_and_auth(
        self,
        op_probe: mock.Mock,
        github_probe: mock.Mock,
        gitlab_probe: mock.Mock,
        command_exists: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            write_repo_fixture(repo)
            command_exists.side_effect = lambda name: name not in {"age-keygen", "ssh"}
            op_probe.return_value = {"required": True, "ok": True, "detail": "ok"}
            github_probe.return_value = {"required": True, "ok": False, "detail": "gh auth ausente"}
            gitlab_probe.return_value = {"required": False, "ok": True, "detail": "nao requerido"}

            payload = preflight_payload(repo_root=repo)

            self.assertEqual(payload["status"], "fail")
            github_target = next(item for item in payload["targets"] if item["target_id"] == "github-ssh-auth")
            self.assertIn("auth gh indisponivel: gh auth ausente", github_target["blockers"])
            age_target = next(item for item in payload["targets"] if item["target_id"] == "age-runtime")
            self.assertTrue(any("age-keygen" in blocker for blocker in age_target["blockers"]))

    def test_plan_payload_orders_steps_by_target_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            write_repo_fixture(repo)
            payload = plan_payload(repo_root=repo)
            self.assertEqual(payload["targets"][0]["target_id"], "github-ssh-auth")
            self.assertEqual(payload["targets"][1]["target_id"], "age-runtime")
            self.assertEqual(payload["targets"][0]["steps"][0]["step"], "Criar chave substituta no 1Password")

    @mock.patch("scripts.secrets_rotation_lib.GitHubDriver.validate_git_remote")
    @mock.patch("scripts.secrets_rotation_lib.GitHubDriver.validate_ssh_handshake")
    @mock.patch("scripts.secrets_rotation_lib.command_exists")
    @mock.patch("scripts.secrets_rotation_lib.SopsAgeDriver.recipient_from_secret")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_gitlab")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_github")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_op")
    def test_validate_detects_placeholder_age_recipient(
        self,
        op_probe: mock.Mock,
        github_probe: mock.Mock,
        gitlab_probe: mock.Mock,
        recipient_from_secret: mock.Mock,
        command_exists: mock.Mock,
        validate_ssh_handshake: mock.Mock,
        validate_git_remote: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            write_repo_fixture(repo)
            command_exists.return_value = True
            recipient_from_secret.return_value = "age1fixture"
            op_probe.return_value = {"required": True, "ok": True, "detail": "ok"}
            github_probe.return_value = {"required": True, "ok": True, "detail": "ok"}
            gitlab_probe.return_value = {"required": False, "ok": True, "detail": "nao requerido"}
            validate_ssh_handshake.return_value = (True, "auth ok")
            validate_git_remote.return_value = (True, "remote ok")

            payload = validate_payload(repo_root=repo)

            self.assertEqual(payload["status"], "fail")
            age_target = next(item for item in payload["targets"] if item["target_id"] == "age-runtime")
            self.assertTrue(any(check["name"] == "sops_recipient_materialized" for check in age_target["checks"]))
            self.assertTrue(any("placeholder" in blocker for blocker in age_target["blockers"]))

    @mock.patch.dict("os.environ", {"SOPS_AGE_KEY": "AGE-SECRET-KEY-1EXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLE"})
    @mock.patch("scripts.secrets_rotation_lib.command_exists")
    @mock.patch("scripts.secrets_rotation_lib.SopsAgeDriver.recipient_from_secret")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_gitlab")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_github")
    @mock.patch("scripts.secrets_rotation_lib.auth_probe_op")
    def test_age_runtime_uses_local_age_material_without_op_auth(
        self,
        op_probe: mock.Mock,
        github_probe: mock.Mock,
        gitlab_probe: mock.Mock,
        recipient_from_secret: mock.Mock,
        command_exists: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            write_repo_fixture(repo)
            config_path = repo / "config" / "secrets-rotation.yaml"
            config_path.write_text(
                config_path.read_text(encoding="utf-8").replace("    enabled: true\n    kind: \"github_ssh_identity\"\n", "    enabled: false\n    kind: \"github_ssh_identity\"\n", 1),
                encoding="utf-8",
            )
            (repo / "df" / "secrets" / "dotfiles.sops.yaml").write_text(
                "creation_rules:\n"
                "  - path_regex: ^df/secrets/.*$\n"
                "    age:\n"
                "      - age1fixture\n",
                encoding="utf-8",
            )
            command_exists.return_value = True
            recipient_from_secret.return_value = "age1fixture"
            op_probe.return_value = {"required": False, "ok": False, "detail": "op indisponivel"}
            github_probe.return_value = {"required": False, "ok": True, "detail": "nao requerido"}
            gitlab_probe.return_value = {"required": False, "ok": True, "detail": "nao requerido"}

            payload = validate_payload(repo_root=repo)

            age_target = next(item for item in payload["targets"] if item["target_id"] == "age-runtime")
            self.assertNotIn("auth op indisponivel: op indisponivel", age_target["blockers"])
            self.assertTrue(age_target["checks"][0]["ok"])
            self.assertEqual(age_target["status"], "warn")


if __name__ == "__main__":
    unittest.main()
