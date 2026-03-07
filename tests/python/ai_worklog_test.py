from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ai-worklog.py"

DOING_START = "<!-- ai-worklog:doing:start -->"
DOING_END = "<!-- ai-worklog:doing:end -->"
LOG_START = "<!-- ai-worklog:log:start -->"
LOG_END = "<!-- ai-worklog:log:end -->"


def run_worklog(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def extract_section(text: str, start: str, end: str) -> str:
    start_idx = text.find(start)
    end_idx = text.find(end, start_idx + len(start))
    if start_idx < 0 or end_idx < 0:
        raise AssertionError(f"Marcadores ausentes: {start} / {end}")
    return text[start_idx + len(start) : end_idx]


class AiWorklogTests(unittest.TestCase):
    def test_check_fails_without_pending_action_when_doing_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa pendente",
                "--worklog-id",
                "WIP-TEST-CHECK",
            )
            result = run_worklog(
                "check",
                "--file",
                str(tracker),
                "--strict",
                "1",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            combined = f"{result.stdout}\n{result.stderr}"
            self.assertIn("concluir_primeiro", combined)
            self.assertIn("roadmap_pendente", combined)

    def test_preflight_marks_user_decision_when_pending_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa pendente",
                "--worklog-id",
                "WIP-TEST-PREFLIGHT",
            )
            result = run_worklog(
                "preflight",
                "--file",
                str(tracker),
                "--message",
                "retomar tarefa interrompida",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["pending_count"], 1)
            self.assertTrue(payload["must_ask_user"])
            self.assertIn("concluir_primeiro", payload["resolution_options"])

    def test_done_keeps_only_active_task_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog("start", "--file", str(tracker), "--message", "Tarefa A", "--worklog-id", "WIP-TEST-A")
            run_worklog("start", "--file", str(tracker), "--message", "Tarefa B", "--worklog-id", "WIP-TEST-B")
            run_worklog("update", "--file", str(tracker), "--worklog-id", "WIP-TEST-A", "--progress", "Checkpoint A")
            run_worklog("update", "--file", str(tracker), "--worklog-id", "WIP-TEST-B", "--progress", "Checkpoint B")
            run_worklog("done", "--file", str(tracker), "--worklog-id", "WIP-TEST-A", "--delivery", "Entrega A")

            rendered = tracker.read_text(encoding="utf-8")
            doing = extract_section(rendered, DOING_START, DOING_END)
            log = extract_section(rendered, LOG_START, LOG_END)

            self.assertNotIn("| WIP-TEST-A |", doing)
            self.assertIn("| WIP-TEST-B |", doing)
            self.assertNotIn("| WIP-TEST-A |", log)
            self.assertIn("| WIP-TEST-B |", log)

    def test_branch_check_blocks_pending_for_same_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa em branch especifica",
                "--worklog-id",
                "WIP-TEST-BRANCH",
                "--branch",
                "feat/test-branch-check",
                "--owner",
                "ai-agent",
            )
            failed = run_worklog(
                "branch-check",
                "--file",
                str(tracker),
                "--branch",
                "feat/test-branch-check",
                "--owner",
                "ai-agent",
                check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("WIP-TEST-BRANCH", f"{failed.stdout}\n{failed.stderr}")

    def test_roadmap_pending_registers_single_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            decisions = pathlib.Path(tmp) / "roadmap.md"
            run_worklog("start", "--file", str(tracker), "--message", "Tarefa roadmap", "--worklog-id", "WIP-TEST-ROADMAP")
            run_worklog(
                "roadmap-pending",
                "--file",
                str(tracker),
                "--worklog-id",
                "WIP-TEST-ROADMAP",
                "--decisions-file",
                str(decisions),
                "--suggestion",
                "Sugestao pendente por item",
            )
            self.assertIn("| WIP-TEST-ROADMAP |", tracker.read_text(encoding="utf-8"))
            decisions_content = decisions.read_text(encoding="utf-8")
            self.assertIn("SG-WIP-TEST-ROADMAP", decisions_content)
            self.assertIn("Sugestao pendente por item", decisions_content)

    def test_done_accepts_evidence_and_persists_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog("start", "--file", str(tracker), "--message", "Tarefa evidencia", "--worklog-id", "WIP-TEST-EVIDENCE")
            run_worklog(
                "done",
                "--file",
                str(tracker),
                "--worklog-id",
                "WIP-TEST-EVIDENCE",
                "--delivery",
                "Entrega concluida",
                "--evidence",
                "task ci:validate",
            )
            rendered = tracker.read_text(encoding="utf-8")
            self.assertIn("Entrega concluida", rendered)
            self.assertIn("evidencias: task ci:validate", rendered)


if __name__ == "__main__":
    unittest.main()
