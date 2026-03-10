from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "git-governance-check.py"


def run_git(repo: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )


def run_script(repo: pathlib.Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=check,
    )


def init_repo(repo: pathlib.Path) -> None:
    run_git(repo, "init")
    run_git(repo, "branch", "-M", "main")
    run_git(repo, "config", "user.name", "AI Agent")
    run_git(repo, "config", "user.email", "ai@example.com")
    run_git(repo, "config", "commit.gpgsign", "false")


def commit_file(repo: pathlib.Path, relative: str, content: str, message: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    run_git(repo, "add", relative)
    run_git(repo, "commit", "-m", message)


class GitGovernanceCheckTests(unittest.TestCase):
    def test_passes_when_there_is_no_residual_branch_or_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            init_repo(repo)
            commit_file(repo, "README.md", "base\n", "🔧 chore(repo): DOT-130 init repo")

            completed = run_script(repo, "--base-ref", "main", "--strict")
            payload = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["merged_local_branches"], [])
            self.assertEqual(payload["merged_worktrees"], [])

    def test_fails_when_a_merged_local_branch_still_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            init_repo(repo)
            commit_file(repo, "README.md", "base\n", "🔧 chore(repo): DOT-130 init repo")

            run_git(repo, "checkout", "-b", "feat/DOT-130-branch-residual")
            commit_file(
                repo,
                "feature.txt",
                "residual branch\n",
                "✨ feat(repo): DOT-130 add residual branch",
            )
            run_git(repo, "checkout", "main")
            run_git(
                repo,
                "merge",
                "--no-ff",
                "feat/DOT-130-branch-residual",
                "-m",
                "🔀 merge(repo): DOT-130 merge residual branch",
            )

            completed = run_script(repo, "--base-ref", "main", "--strict", check=False)
            payload = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(payload["status"], "fail")
            self.assertIn("feat/DOT-130-branch-residual", payload["merged_local_branches"])
            self.assertIn("Higiene Git reprovada", completed.stderr)

    def test_fails_when_a_merged_worktree_still_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            init_repo(repo)
            commit_file(repo, "README.md", "base\n", "🔧 chore(repo): DOT-130 init repo")

            worktree_path = repo / "worktrees" / "dot131"
            run_git(repo, "worktree", "add", str(worktree_path), "-b", "feat/DOT-131-worktree-residual")
            commit_file(
                worktree_path,
                "worktree.txt",
                "residual worktree\n",
                "✨ feat(repo): DOT-131 add residual worktree",
            )
            run_git(repo, "checkout", "main")
            run_git(
                repo,
                "merge",
                "--no-ff",
                "feat/DOT-131-worktree-residual",
                "-m",
                "🔀 merge(repo): DOT-131 merge residual worktree",
            )

            completed = run_script(repo, "--base-ref", "main", "--strict", check=False)
            payload = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(len(payload["merged_worktrees"]), 1)
            self.assertEqual(
                payload["merged_worktrees"][0]["branch"],
                "feat/DOT-131-worktree-residual",
            )
            self.assertEqual(
                pathlib.Path(payload["merged_worktrees"][0]["path"]).resolve(),
                worktree_path.resolve(),
            )


if __name__ == "__main__":
    unittest.main()
