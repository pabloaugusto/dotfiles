from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ai-worklog.py"
REVIEW_SCRIPT = ROOT / "scripts" / "ai-review.py"

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


def run_review(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REVIEW_SCRIPT), *args],
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


def init_git_repo(path: pathlib.Path) -> None:
    subprocess.run(["git", "init"], cwd=path, text=True, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.name", "AI Agent"],
        cwd=path,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "ai@example.com"],
        cwd=path,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"],
        cwd=path,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "core.hooksPath", ".git/hooks"],
        cwd=path,
        text=True,
        capture_output=True,
        check=True,
    )


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
            self.assertIn("destrava diretamente", payload["resolution_guidance"]["concluir_primeiro"])

    def test_check_requires_checkpoint_commit_when_worktree_dirty_without_doing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            tracker = repo / "tracker.md"
            roadmap = repo / "ROADMAP.md"
            decisions = repo / "ROADMAP-DECISIONS.md"
            lessons = repo / "LICOES-APRENDIDAS.md"
            init_git_repo(repo)
            run_worklog(
                "ensure",
                "--file",
                str(tracker),
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
                "--lessons-file",
                str(lessons),
            )
            subprocess.run(
                ["git", "add", "."], cwd=repo, text=True, capture_output=True, check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "chore: init"],
                cwd=repo,
                text=True,
                capture_output=True,
                check=True,
            )
            (repo / "dirty.txt").write_text("checkpoint pendente\n", encoding="utf-8")

            failed = run_worklog(
                "check",
                "--file",
                str(tracker),
                "--repo-root",
                str(repo),
                check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("Checkpoint commit obrigatorio", f"{failed.stdout}\n{failed.stderr}")

    def test_check_allows_dirty_worktree_when_round_is_still_in_doing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            tracker = repo / "tracker.md"
            roadmap = repo / "ROADMAP.md"
            decisions = repo / "ROADMAP-DECISIONS.md"
            lessons = repo / "LICOES-APRENDIDAS.md"
            init_git_repo(repo)
            run_worklog(
                "ensure",
                "--file",
                str(tracker),
                "--roadmap-file",
                str(roadmap),
                "--decisions-file",
                str(decisions),
                "--lessons-file",
                str(lessons),
            )
            subprocess.run(
                ["git", "add", "."], cwd=repo, text=True, capture_output=True, check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "chore: init"],
                cwd=repo,
                text=True,
                capture_output=True,
                check=True,
            )
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa ativa",
                "--worklog-id",
                "WIP-TEST-DIRTY-DOING",
            )

            result = run_worklog(
                "check",
                "--file",
                str(tracker),
                "--repo-root",
                str(repo),
                "--pending-action",
                "concluir_primeiro",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["pending_count"], 1)
            self.assertTrue(payload["ok"])
            self.assertIn("destrava diretamente", payload["resolution_guidance"]["concluir_primeiro"])

    def test_done_keeps_only_active_task_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            lessons = pathlib.Path(tmp) / "lessons.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa A",
                "--worklog-id",
                "WIP-TEST-A",
            )
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa B",
                "--worklog-id",
                "WIP-TEST-B",
            )
            run_worklog(
                "update",
                "--file",
                str(tracker),
                "--worklog-id",
                "WIP-TEST-A",
                "--progress",
                "Checkpoint A",
            )
            run_worklog(
                "update",
                "--file",
                str(tracker),
                "--worklog-id",
                "WIP-TEST-B",
                "--progress",
                "Checkpoint B",
            )
            run_worklog(
                "done",
                "--file",
                str(tracker),
                "--lessons-file",
                str(lessons),
                "--worklog-id",
                "WIP-TEST-A",
                "--delivery",
                "Entrega A",
                "--lessons-decision",
                "sem_nova_licao",
                "--lessons-summary",
                "Nao houve licao nova neste fechamento de teste",
            )

            rendered = tracker.read_text(encoding="utf-8")
            doing = extract_section(rendered, DOING_START, DOING_END)
            log = extract_section(rendered, LOG_START, LOG_END)

            self.assertNotIn("| WIP-TEST-A |", doing)
            self.assertIn("| WIP-TEST-B |", doing)
            self.assertNotIn("| WIP-TEST-A |", log)
            self.assertIn("| WIP-TEST-B |", log)

    def test_update_log_uses_progress_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa com progresso",
                "--worklog-id",
                "WIP-TEST-PROGRESS",
            )
            run_worklog(
                "update",
                "--file",
                str(tracker),
                "--worklog-id",
                "WIP-TEST-PROGRESS",
                "--progress",
                "Checkpoint real de progresso",
                "--next-step",
                "Aplicar ajuste final",
            )

            rendered = tracker.read_text(encoding="utf-8")
            log = extract_section(rendered, LOG_START, LOG_END)

            self.assertIn("Checkpoint real de progresso", log)
            self.assertIn("Aplicar ajuste final", log)

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
            roadmap = pathlib.Path(tmp) / "ROADMAP.md"
            decisions = pathlib.Path(tmp) / "ROADMAP-DECISIONS.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa roadmap",
                "--worklog-id",
                "WIP-TEST-ROADMAP",
            )
            run_worklog(
                "roadmap-pending",
                "--file",
                str(tracker),
                "--roadmap-file",
                str(roadmap),
                "--worklog-id",
                "WIP-TEST-ROADMAP",
                "--decisions-file",
                str(decisions),
                "--suggestion",
                "Sugestao pendente por item",
            )
            self.assertIn("| WIP-TEST-ROADMAP |", tracker.read_text(encoding="utf-8"))
            roadmap_content = roadmap.read_text(encoding="utf-8")
            decisions_content = decisions.read_text(encoding="utf-8")
            self.assertIn("Sugestao pendente por item", roadmap_content)
            self.assertIn("SG-WIP-TEST-ROADMAP", decisions_content)
            self.assertIn("Sugestao pendente por item", decisions_content)

    def test_done_accepts_evidence_and_persists_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            lessons = pathlib.Path(tmp) / "lessons.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa evidencia",
                "--worklog-id",
                "WIP-TEST-EVIDENCE",
            )
            run_worklog(
                "done",
                "--file",
                str(tracker),
                "--lessons-file",
                str(lessons),
                "--worklog-id",
                "WIP-TEST-EVIDENCE",
                "--delivery",
                "Entrega concluida",
                "--evidence",
                "task ci:validate",
                "--lessons-decision",
                "sem_nova_licao",
                "--lessons-summary",
                "Encerramento de teste sem aprendizado novo",
            )
            rendered = tracker.read_text(encoding="utf-8")
            self.assertIn("Entrega concluida", rendered)
            self.assertIn("evidencias: task ci:validate", rendered)

    def test_done_requires_explicit_lessons_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Tarefa review",
                "--worklog-id",
                "WIP-TEST-LESSONS",
            )
            failed = run_worklog(
                "done",
                "--file",
                str(tracker),
                "--worklog-id",
                "WIP-TEST-LESSONS",
                "--delivery",
                "Entrega",
                check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("--lessons-decision", f"{failed.stdout}\n{failed.stderr}")

    def test_done_blocks_without_specialized_review_for_python_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            lessons = pathlib.Path(tmp) / "lessons.md"
            reviews = pathlib.Path(tmp) / "reviews.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Ajustar validador Python",
                "--worklog-id",
                "WIP-TEST-PY-REVIEW",
            )
            failed = run_worklog(
                "done",
                "--file",
                str(tracker),
                "--lessons-file",
                str(lessons),
                "--review-file",
                str(reviews),
                "--repo-root",
                str(ROOT),
                "--review-paths",
                "scripts/validate-ai-assets.py",
                "--worklog-id",
                "WIP-TEST-PY-REVIEW",
                "--delivery",
                "Entrega Python",
                "--lessons-decision",
                "sem_nova_licao",
                "--lessons-summary",
                "Sem nova licao nesta regressao",
                check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("python-reviewer", f"{failed.stdout}\n{failed.stderr}")

    def test_done_allows_specialized_review_after_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            lessons = pathlib.Path(tmp) / "lessons.md"
            reviews = pathlib.Path(tmp) / "reviews.md"
            run_worklog(
                "start",
                "--file",
                str(tracker),
                "--message",
                "Ajustar validador Python",
                "--worklog-id",
                "WIP-TEST-PY-REVIEW-OK",
            )
            run_review(
                "record",
                "--review-file",
                str(reviews),
                "--worklog-id",
                "WIP-TEST-PY-REVIEW-OK",
                "--reviewer",
                "python-reviewer",
                "--status",
                "aprovado",
                "--summary",
                "Revisao especializada aprovada.",
                "--paths",
                "scripts/validate-ai-assets.py",
                "--evidence",
                "task test:unit:python:windows",
            )
            completed = run_worklog(
                "done",
                "--file",
                str(tracker),
                "--lessons-file",
                str(lessons),
                "--review-file",
                str(reviews),
                "--repo-root",
                str(ROOT),
                "--review-paths",
                "scripts/validate-ai-assets.py",
                "--worklog-id",
                "WIP-TEST-PY-REVIEW-OK",
                "--delivery",
                "Entrega Python",
                "--lessons-decision",
                "sem_nova_licao",
                "--lessons-summary",
                "Sem nova licao nesta regressao",
            )
            self.assertEqual(completed.returncode, 0, msg=f"{completed.stdout}\n{completed.stderr}")


if __name__ == "__main__":
    unittest.main()
