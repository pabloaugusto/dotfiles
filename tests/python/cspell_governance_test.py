from __future__ import annotations

import pathlib
import tempfile
import unittest
from unittest import mock

from scripts import cspell_governance_lib as lib


class CSpellGovernanceTests(unittest.TestCase):
    def test_parse_unknown_word_findings_extracts_file_line_column_and_word(self) -> None:
        output = (
            "docs/README.md:12:9 - Unknown word (Pascoalete)\n"
            "AGENTS.md:3:1 - Unknown word (worklog)\n"
        )

        findings = lib.parse_unknown_word_findings(output)

        self.assertEqual(2, len(findings))
        self.assertEqual("docs/README.md", findings[0].path)
        self.assertEqual(12, findings[0].line)
        self.assertEqual(9, findings[0].column)
        self.assertEqual("Pascoalete", findings[0].word)

    def test_build_external_only_config_removes_project_dictionary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = pathlib.Path(temp_dir_name)
            config_path = temp_dir / ".cspell.json"
            words_path = temp_dir / ".cspell" / "project-words.txt"
            words_path.parent.mkdir(parents=True)
            words_path.write_text("worklog\n", encoding="utf-8")
            config_path.write_text(
                """
                {
                  "dictionaryDefinitions": [
                    {"name": "project-words", "path": "./.cspell/project-words.txt"}
                  ],
                  "dictionaries": ["pt_BR", "project-words"]
                }
                """,
                encoding="utf-8",
            )

            payload = lib.build_external_only_config(
                config_path=config_path,
                project_words_path=words_path,
            )

            self.assertEqual([], payload["dictionaryDefinitions"])
            self.assertEqual(["pt_BR"], payload["dictionaries"])

    def test_find_redundant_project_words_detects_external_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = pathlib.Path(temp_dir_name)
            config_path = temp_dir / ".cspell.json"
            words_path = temp_dir / ".cspell" / "project-words.txt"
            words_path.parent.mkdir(parents=True)
            words_path.write_text("worklog\nPascoalete\n", encoding="utf-8")
            config_path.write_text(
                """
                {
                  "dictionaryDefinitions": [
                    {"name": "project-words", "path": "./.cspell/project-words.txt"}
                  ],
                  "dictionaries": ["pt_BR", "project-words"]
                }
                """,
                encoding="utf-8",
            )

            def fake_runner(args: list[str]):
                class Result:
                    def __init__(self, returncode: int) -> None:
                        self.returncode = returncode

                return Result(0 if "worklog" in pathlib.Path(args[1]).read_text(encoding="utf-8") else 1)

            redundant = lib.find_redundant_project_words(
                config_path=config_path,
                project_words_path=words_path,
                runner=fake_runner,
            )

            self.assertEqual(["worklog"], redundant)

    def test_orthography_suggestion_id_is_deterministic_per_worklog(self) -> None:
        suggestion_id = lib.orthography_suggestion_id("WIP-20260307-SECRETS-ROTATION")
        self.assertEqual("SG-ORTHO-WIP-20260307-SECRETS-ROTATION", suggestion_id)

    def test_review_paths_registers_pending_backlog_when_findings_remain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = pathlib.Path(temp_dir_name)
            ledger_path = temp_dir / "AI-ORTHOGRAPHY-LEDGER.md"
            roadmap_path = temp_dir / "ROADMAP.md"
            decisions_path = temp_dir / "ROADMAP-DECISIONS.md"
            fake_result = mock.Mock(returncode=1, stdout="README.md:1:1 - Unknown word (Pascoalete)\n", stderr="")

            with mock.patch.object(lib, "find_redundant_project_words", return_value=[]), mock.patch.object(
                lib, "run_cspell", return_value=fake_result
            ):
                payload = lib.review_paths(
                    worklog_id="WIP-TEST-ORTHO",
                    reviewer="pascoalete",
                    paths=["README.md"],
                    ledger_path=ledger_path,
                    roadmap_path=roadmap_path,
                    decisions_path=decisions_path,
                )

            self.assertFalse(payload["ok"])
            self.assertEqual("SG-ORTHO-WIP-TEST-ORTHO", payload["backlog_id"])
            self.assertIn("README.md", ledger_path.read_text(encoding="utf-8"))
            roadmap_text = roadmap_path.read_text(encoding="utf-8")
            self.assertIn("Corrigir pendencias ortograficas remanescentes do worklog", roadmap_text)
            decisions_text = decisions_path.read_text(encoding="utf-8")
            self.assertIn("SG-ORTHO-WIP-TEST-ORTHO", decisions_text)
            self.assertIn("aceita", decisions_text)

    def test_review_paths_discards_pending_backlog_when_scope_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = pathlib.Path(temp_dir_name)
            ledger_path = temp_dir / "AI-ORTHOGRAPHY-LEDGER.md"
            roadmap_path = temp_dir / "ROADMAP.md"
            decisions_path = temp_dir / "ROADMAP-DECISIONS.md"
            failing_result = mock.Mock(returncode=1, stdout="README.md:1:1 - Unknown word (Pascoalete)\n", stderr="")
            clean_result = mock.Mock(returncode=0, stdout="", stderr="")

            with mock.patch.object(lib, "find_redundant_project_words", return_value=[]), mock.patch.object(
                lib, "run_cspell", return_value=failing_result
            ):
                lib.review_paths(
                    worklog_id="WIP-TEST-ORTHO",
                    reviewer="pascoalete",
                    paths=["README.md"],
                    ledger_path=ledger_path,
                    roadmap_path=roadmap_path,
                    decisions_path=decisions_path,
                )

            with mock.patch.object(lib, "find_redundant_project_words", return_value=[]), mock.patch.object(
                lib, "run_cspell", return_value=clean_result
            ):
                payload = lib.review_paths(
                    worklog_id="WIP-TEST-ORTHO",
                    reviewer="pascoalete",
                    paths=["README.md"],
                    ledger_path=ledger_path,
                    roadmap_path=roadmap_path,
                    decisions_path=decisions_path,
                )

            self.assertTrue(payload["ok"])
            self.assertEqual("SG-ORTHO-WIP-TEST-ORTHO", payload["backlog_id"])
            decisions_text = decisions_path.read_text(encoding="utf-8")
            self.assertIn("SG-ORTHO-WIP-TEST-ORTHO", decisions_text)
            self.assertIn("descartada", decisions_text)


if __name__ == "__main__":
    unittest.main()
