from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
LESSONS_SCRIPT = ROOT / "scripts" / "ai-lessons.py"
WORKLOG_SCRIPT = ROOT / "scripts" / "ai-worklog.py"


def run_lessons(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LESSONS_SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def run_worklog(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(WORKLOG_SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


TRACKER_TEMPLATE = """# AI WIP Tracker

## Doing

<!-- ai-worklog:doing:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Ultima atualizacao UTC | Proximo passo | Bloqueios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-worklog:doing:end -->

## Done

<!-- ai-worklog:done:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Concluido UTC | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| WIP-TEST-MISSING | Tarefa faltando revisao | feat/test | ai-agent | 2026-03-07 00:00 UTC | 2026-03-07 00:10 UTC | Entrega |
<!-- ai-worklog:done:end -->

## Log incremental - Tarefas nao finalizadas ainda

<!-- ai-worklog:log:start -->
| Data/Hora UTC | ID | Status | Resumo | Proximo passo | Bloqueios | Contexto | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-worklog:log:end -->
"""


class AiLessonsTests(unittest.TestCase):
    def test_add_review_and_check_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            lessons = pathlib.Path(tmp) / "lessons.md"

            run_worklog("start", "--file", str(tracker), "--message", "Tarefa lessons", "--worklog-id", "WIP-TEST-LESSONS")
            run_lessons(
                "add",
                "--file",
                str(lessons),
                "--lesson-id",
                "LA-001",
                "--title",
                "Licao de teste",
                "--context",
                "Fluxo controlado por teste",
                "--rule",
                "Sempre registrar licao quando houver aprendizagem nova",
                "--validated-solution",
                "Usar ai-lessons no fechamento",
                "--prevention",
                "Bloquear closeout sem revisao",
                "--validation",
                "task ai:lessons:check",
                "--worklog-id",
                "WIP-TEST-LESSONS",
            )
            run_worklog(
                "done",
                "--file",
                str(tracker),
                "--lessons-file",
                str(lessons),
                "--worklog-id",
                "WIP-TEST-LESSONS",
                "--delivery",
                "Entrega concluida",
                "--lessons-decision",
                "capturada",
                "--lessons-summary",
                "O teste gerou uma licao nova",
                "--lessons-ids",
                "LA-001",
            )
            checked = run_lessons("check", "--file", str(lessons), "--tracker-file", str(tracker))
            self.assertIn('"status": "checked"', checked.stdout)

    def test_check_fails_when_done_worklog_has_no_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            lessons = pathlib.Path(tmp) / "lessons.md"
            tracker.write_text(TRACKER_TEMPLATE, encoding="utf-8")
            run_lessons("ensure", "--file", str(lessons))

            failed = run_lessons("check", "--file", str(lessons), "--tracker-file", str(tracker), check=False)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("WIP-TEST-MISSING", f"{failed.stdout}\n{failed.stderr}")

    def test_sync_preserves_single_review_per_worklog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lessons = pathlib.Path(tmp) / "lessons.md"
            run_lessons("ensure", "--file", str(lessons))
            run_lessons(
                "add",
                "--file",
                str(lessons),
                "--lesson-id",
                "LA-001",
                "--title",
                "Licao",
                "--context",
                "Contexto",
                "--rule",
                "Regra",
                "--validated-solution",
                "Solucao",
                "--prevention",
                "Prevencao",
                "--validation",
                "Validacao",
            )
            run_lessons(
                "review",
                "--file",
                str(lessons),
                "--worklog-id",
                "WIP-TEST-DUPE",
                "--decision",
                "capturada",
                "--summary",
                "Primeira revisao",
                "--lesson-ids",
                "LA-001",
            )
            content = lessons.read_text(encoding="utf-8")
            duplicated_table = """| Data/Hora UTC | Worklog ID | Decisao | Resumo | Licoes | Evidencia |
| --- | --- | --- | --- | --- | --- |
| 2026-03-07 00:10 UTC | WIP-TEST-DUPE | capturada | Primeira revisao | LA-001 | - |
| 2026-03-07 00:00 UTC | WIP-TEST-DUPE | capturada | Revisao duplicada | LA-001 | - |"""
            duplicated = re.sub(
                r"<!-- ai-lessons:reviews:start -->.*?<!-- ai-lessons:reviews:end -->",
                "<!-- ai-lessons:reviews:start -->\n" + duplicated_table + "\n<!-- ai-lessons:reviews:end -->",
                content,
                flags=re.S,
            )
            lessons.write_text(duplicated, encoding="utf-8")
            run_lessons("sync", "--file", str(lessons))
            final_content = lessons.read_text(encoding="utf-8")
            self.assertEqual(final_content.count("| WIP-TEST-DUPE |"), 1)


if __name__ == "__main__":
    unittest.main()
