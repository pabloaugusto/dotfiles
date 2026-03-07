from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ai-roadmap.py"


def run_roadmap(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


class AiRoadmapTests(unittest.TestCase):
    def test_ensure_creates_both_files_with_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            roadmap = pathlib.Path(tmp) / "ROADMAP.md"
            decisions = pathlib.Path(tmp) / "ROADMAP-DECISIONS.md"

            run_roadmap(
                "ensure",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
            )

            roadmap_text = roadmap.read_text(encoding="utf-8")
            decisions_text = decisions.read_text(encoding="utf-8")

            self.assertIn("<!-- roadmap:backlog:start -->", roadmap_text)
            self.assertIn("<!-- roadmap:pending:end -->", roadmap_text)
            self.assertIn("<!-- roadmap:suggestions:start -->", decisions_text)
            self.assertIn("<!-- roadmap:autolog:end -->", decisions_text)

    def test_register_updates_roadmap_and_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            roadmap = pathlib.Path(tmp) / "ROADMAP.md"
            decisions = pathlib.Path(tmp) / "ROADMAP-DECISIONS.md"

            run_roadmap(
                "ensure",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
            )
            run_roadmap(
                "register",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
                "--decision",
                "pending",
                "--horizon",
                "next",
                "--suggestion",
                "Retomar hardening de harness Windows",
                "--suggestion-id",
                "SG-TEST-001",
                "--notes",
                "worklog=WIP-TEST-001",
            )

            roadmap_text = roadmap.read_text(encoding="utf-8")
            decisions_text = decisions.read_text(encoding="utf-8")

            self.assertIn("Retomar hardening de harness Windows", roadmap_text)
            self.assertIn("SG-TEST-001", decisions_text)
            self.assertIn("worklog=WIP-TEST-001", decisions_text)

    def test_refresh_deduplicates_cycle_history_for_same_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            roadmap = pathlib.Path(tmp) / "ROADMAP.md"
            decisions = pathlib.Path(tmp) / "ROADMAP-DECISIONS.md"

            run_roadmap(
                "ensure",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
            )

            duplicated_cycles = """<!-- roadmap:cycles:start -->
### Ciclo 2026-Q1 @ 2026-03-07 01:49 UTC

- Top sequencia recomendada: `RM-003, RM-001, RM-002`
- Decisao final permanece humana.
- Acao de governanca: decidir pendencias antes de novo escopo amplo.
- Sugestoes pendentes no fechamento: `(nenhuma)`
### Ciclo 2026-Q1 @ 2026-03-07 01:46 UTC
- Top sequencia recomendada: `RM-003, RM-001, RM-002`
- Decisao final permanece humana.
- Acao de governanca: decidir pendencias antes de novo escopo amplo.
- Sugestoes pendentes no fechamento: `(nenhuma)`
### Ciclo 2025-Q4 @ 2025-12-31 23:59 UTC
- Top sequencia recomendada: `RM-001`
- Decisao final permanece humana.
- Acao de governanca: ciclo historico anterior.
- Sugestoes pendentes no fechamento: `(nenhuma)`
<!-- roadmap:cycles:end -->"""

            decisions_text = decisions.read_text(encoding="utf-8")
            start_marker = "<!-- roadmap:cycles:start -->"
            end_marker = "<!-- roadmap:cycles:end -->"
            start_idx = decisions_text.index(start_marker)
            end_idx = decisions_text.index(end_marker, start_idx)
            rewritten = (
                decisions_text[:start_idx]
                + duplicated_cycles
                + decisions_text[end_idx + len(end_marker) :]
            )
            decisions.write_text(rewritten, encoding="utf-8")

            run_roadmap(
                "refresh",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
                "--cycle",
                "2026-Q1",
            )

            decisions_text = decisions.read_text(encoding="utf-8")

            self.assertEqual(decisions_text.count("### Ciclo 2026-Q1 @"), 1)
            self.assertEqual(decisions_text.count("### Ciclo 2025-Q4 @"), 1)

    def test_register_accepted_removes_pending_entry_even_with_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            roadmap = pathlib.Path(tmp) / "ROADMAP.md"
            decisions = pathlib.Path(tmp) / "ROADMAP-DECISIONS.md"

            suggestion = (
                "Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, "
                "incluindo artefatos hoje ja movidos para `archive/` e outros scripts experimentais."
            )

            run_roadmap(
                "ensure",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
            )
            run_roadmap(
                "register",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
                "--decision",
                "pending",
                "--horizon",
                "next",
                "--suggestion",
                suggestion,
                "--suggestion-id",
                "SG-TEST-LINK",
            )

            roadmap_text = roadmap.read_text(encoding="utf-8").replace(
                "`archive/`", "[`archive/`](archive/)"
            )
            roadmap_text = roadmap_text.replace("backups decl...", "backups decla...")
            roadmap.write_text(roadmap_text, encoding="utf-8")

            run_roadmap(
                "register",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
                "--decision",
                "accepted",
                "--horizon",
                "next",
                "--suggestion",
                suggestion,
                "--suggestion-id",
                "SG-TEST-LINK",
            )

            roadmap_text = roadmap.read_text(encoding="utf-8")

            self.assertIn("### Next", roadmap_text)
            self.assertIn("Consolidar ou arquivar o legado historico versionado", roadmap_text)
            self.assertIn("<!-- roadmap:pending:start -->\n- (sem itens)\n<!-- roadmap:pending:end -->", roadmap_text)

    def test_register_deduplicates_same_autolog_signature_on_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            roadmap = pathlib.Path(tmp) / "ROADMAP.md"
            decisions = pathlib.Path(tmp) / "ROADMAP-DECISIONS.md"

            suggestion = "Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup."

            run_roadmap(
                "ensure",
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
            )

            for _ in range(2):
                run_roadmap(
                    "register",
                    "--roadmap-file",
                    str(roadmap),
                    "--decisions-file",
                    str(decisions),
                    "--decision",
                    "accepted",
                    "--horizon",
                    "next",
                    "--suggestion",
                    suggestion,
                    "--suggestion-id",
                    "SG-TEST-DUPE",
                )

            decisions_text = decisions.read_text(encoding="utf-8")

            self.assertEqual(
                decisions_text.count(
                    "| decisao=accepted | horizonte=next | item=Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup."
                ),
                1,
            )


if __name__ == "__main__":
    unittest.main()
