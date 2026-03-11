from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.ai_fallback_governance_lib import (
    LEDGER_PATH,
    capture_fallback_record,
    ensure_fallback_ledger_file,
    fallback_status_payload,
    load_fallback_ledger,
    resolve_fallback_record,
)


class AiFallbackGovernanceTests(unittest.TestCase):
    def test_status_is_primary_without_active_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            ledger = repo / LEDGER_PATH
            ensure_fallback_ledger_file(ledger)
            payload = fallback_status_payload(
                repo,
                ledger_path=ledger,
                tracker_path=repo / "docs" / "AI-WIP-TRACKER.md",
                jira_probe=lambda _: (True, "ok"),
            )
            self.assertEqual(payload["mode"], "primary")
            self.assertEqual(payload["active_fallback_count"], 0)

    def test_status_is_degraded_when_jira_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            ledger = repo / LEDGER_PATH
            ensure_fallback_ledger_file(ledger)
            payload = fallback_status_payload(
                repo,
                ledger_path=ledger,
                tracker_path=repo / "docs" / "AI-WIP-TRACKER.md",
                jira_probe=lambda _: (False, "service-unavailable"),
            )
            self.assertEqual(payload["mode"], "degraded")
            self.assertFalse(payload["jira_available"])

    def test_capture_and_resolve_lifecycle_moves_row_between_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            ledger = repo / LEDGER_PATH
            ensure_fallback_ledger_file(ledger)

            capture_payload = capture_fallback_record(
                repo,
                tracker_relative="docs/AI-WIP-TRACKER.md",
                local_reference="WIP-TEST-FALLBACK",
                summary="Jira indisponivel durante a continuidade local",
                next_step="Registrar progresso local ate o retorno do Jira",
                jira_issue="DOT-106",
                ledger_path=ledger,
                jira_probe=lambda _: (False, "gateway-timeout"),
            )
            self.assertEqual(capture_payload["action"], "captured")
            active, resolved = load_fallback_ledger(ledger)
            self.assertEqual(len(active), 1)
            self.assertEqual(len(resolved), 0)
            self.assertEqual(active[0]["Estado"], "captured")

            resolve_payload = resolve_fallback_record(
                repo,
                tracker_relative="docs/AI-WIP-TRACKER.md",
                local_reference="WIP-TEST-FALLBACK",
                outcome="obsolete",
                result="Registro local encerrou sem backlog vivo remanescente.",
                summary="Uso local encerrado",
                ledger_path=ledger,
                sync_jira=False,
            )
            self.assertEqual(resolve_payload["outcome"], "obsolete")
            active, resolved = load_fallback_ledger(ledger)
            self.assertEqual(len(active), 0)
            self.assertEqual(len(resolved), 1)
            self.assertEqual(resolved[0]["Estado"], "obsolete")

    def test_capture_blocks_while_jira_is_available_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            ledger = repo / LEDGER_PATH
            ensure_fallback_ledger_file(ledger)
            with self.assertRaisesRegex(Exception, "Fallback local bloqueado"):
                capture_fallback_record(
                    repo,
                    tracker_relative="docs/ROADMAP-DECISIONS.md",
                    local_reference="SG-TESTE",
                    summary="Tentativa indevida de usar fallback",
                    next_step="Nao deveria capturar",
                    ledger_path=ledger,
                    jira_probe=lambda _: (True, "ok"),
                )

    def test_capture_rejects_trackers_outside_the_contract_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            ledger = repo / LEDGER_PATH
            ensure_fallback_ledger_file(ledger)
            with self.assertRaisesRegex(Exception, "Tracker invalido"):
                capture_fallback_record(
                    repo,
                    tracker_relative="docs/ARBITRARY.md",
                    local_reference="WIP-TEST-INVALID",
                    summary="Uso fora do contrato",
                    next_step="Nao deveria capturar",
                    ledger_path=ledger,
                    jira_probe=lambda _: (False, "unreachable"),
                )

    def test_resolve_drained_syncs_structured_comment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            ledger = repo / LEDGER_PATH
            ensure_fallback_ledger_file(ledger)

            capture_fallback_record(
                repo,
                tracker_relative="docs/AI-WIP-TRACKER.md",
                local_reference="WIP-TEST-DRAIN",
                summary="Falha primaria temporaria",
                next_step="Reconciliar com o Jira quando voltar",
                jira_issue="DOT-106",
                ledger_path=ledger,
                jira_probe=lambda _: (False, "unreachable"),
            )

            class StubJira:
                pass

            def resolver(_: pathlib.Path) -> StubJira:
                return StubJira()

            from scripts import ai_fallback_governance_lib as module

            def stub_issue_url(_jira: object, issue_key: str) -> str:
                return f"https://jira.local/browse/{issue_key}"

            def stub_ensure_comment(
                jira: object,
                issue_key: str,
                body_text: str,
            ) -> dict[str, str]:
                del jira, body_text
                return {
                    "id": "comment-1",
                    "issue_key": issue_key,
                    "body_text": "comment",
                }

            with (
                patch.object(module, "issue_url", stub_issue_url),
                patch.object(module, "ensure_comment", stub_ensure_comment),
            ):
                payload = resolve_fallback_record(
                    repo,
                    tracker_relative="docs/AI-WIP-TRACKER.md",
                    local_reference="WIP-TEST-DRAIN",
                    outcome="drained",
                    result="Registro drenado para o Jira.",
                    jira_issue="DOT-106",
                    summary="Sincronizacao concluida",
                    agent="ai-developer-config-policy",
                    ledger_path=ledger,
                    sync_jira=True,
                    jira_resolver=resolver,
                )

            self.assertEqual(payload["jira_comment_id"], "comment-1")
            active, resolved = load_fallback_ledger(ledger)
            self.assertEqual(len(active), 0)
            self.assertEqual(len(resolved), 1)
            self.assertEqual(resolved[0]["Estado"], "drained")
            self.assertIn("DOT-106", resolved[0]["Jira"])

    def test_external_ledger_path_is_reported_without_relative_to_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            repo = tmp_root / "repo"
            repo.mkdir(parents=True, exist_ok=True)
            external_root = tmp_root / "external"
            external_root.mkdir(parents=True, exist_ok=True)
            ledger = external_root / "fallback.md"
            ensure_fallback_ledger_file(ledger)

            payload = capture_fallback_record(
                repo,
                tracker_relative="docs/AI-WIP-TRACKER.md",
                local_reference="WIP-TEST-EXTERNAL-LEDGER",
                summary="Ledger externo para teste",
                next_step="Resolver sem quebrar o retorno",
                ledger_path=ledger,
                jira_probe=lambda _: (False, "unreachable"),
            )
            self.assertEqual(payload["ledger_path"], ledger.resolve().as_posix())

            resolved_payload = resolve_fallback_record(
                repo,
                tracker_relative="docs/AI-WIP-TRACKER.md",
                local_reference="WIP-TEST-EXTERNAL-LEDGER",
                outcome="obsolete",
                result="Encerrado sem backlog vivo",
                ledger_path=ledger,
                sync_jira=False,
            )
            self.assertEqual(resolved_payload["ledger_path"], ledger.resolve().as_posix())

    def test_cli_resolves_repo_relative_paths_against_repo_root_instead_of_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = pathlib.Path(tmp)
            repo = tmp_root / "repo"
            repo.mkdir(parents=True, exist_ok=True)
            external_cwd = tmp_root / "external-cwd"
            external_cwd.mkdir(parents=True, exist_ok=True)
            script = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "ai-fallback.py"

            status = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "status",
                    "--repo-root",
                    str(repo),
                    "--ledger-file",
                    "docs/AI-FALLBACK-LEDGER.md",
                    "--tracker-file",
                    "docs/AI-WIP-TRACKER.md",
                ],
                cwd=external_cwd,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, msg=status.stderr)
            status_payload = json.loads(status.stdout)
            self.assertEqual(status_payload["ledger_path"], "docs/AI-FALLBACK-LEDGER.md")
            self.assertEqual(status_payload["tracker_path"], "docs/AI-WIP-TRACKER.md")
            self.assertTrue((repo / "docs" / "AI-FALLBACK-LEDGER.md").is_file())
            self.assertFalse((external_cwd / "docs" / "AI-FALLBACK-LEDGER.md").exists())

            capture = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "capture",
                    "--repo-root",
                    str(repo),
                    "--ledger-file",
                    "docs/AI-FALLBACK-LEDGER.md",
                    "--tracker",
                    "docs/AI-WIP-TRACKER.md",
                    "--local-reference",
                    "WIP-CLI-ROOT",
                    "--summary",
                    "Teste de caminho relativo no CLI",
                    "--next-step",
                    "Validar escrita no repo-root",
                ],
                cwd=external_cwd,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(capture.returncode, 0, msg=capture.stderr)
            capture_payload = json.loads(capture.stdout)
            self.assertEqual(capture_payload["ledger_path"], "docs/AI-FALLBACK-LEDGER.md")
            self.assertTrue((repo / "docs" / "AI-FALLBACK-LEDGER.md").is_file())
            self.assertFalse((external_cwd / "docs" / "AI-FALLBACK-LEDGER.md").exists())


if __name__ == "__main__":
    unittest.main()
