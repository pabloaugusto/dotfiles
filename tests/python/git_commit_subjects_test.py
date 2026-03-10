from __future__ import annotations

import pathlib
import subprocess
import tempfile
import unittest

from scripts.git_commit_subjects_lib import collect_commit_subjects


class GitCommitSubjectsTests(unittest.TestCase):
    def _git(
        self,
        repo_root: pathlib.Path,
        *args: str,
    ) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(
                f"git {' '.join(args)} falhou: {(completed.stderr or completed.stdout).strip()}"
            )
        return completed.stdout.strip()

    def _commit(self, repo_root: pathlib.Path, message: str, file_name: str) -> str:
        target = repo_root / file_name
        target.write_text(message, encoding="utf-8")
        self._git(repo_root, "add", file_name)
        self._git(repo_root, "-c", "commit.gpgsign=false", "commit", "-m", message)
        return self._git(repo_root, "rev-parse", "HEAD")

    def test_collects_only_subjects_exclusive_to_remote(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            remote_root = temp_root / "remote.git"
            repo_root = temp_root / "repo"

            self._git(temp_root, "init", "--bare", str(remote_root))
            self._git(temp_root, "init", "-b", "main", str(repo_root))
            self._git(repo_root, "config", "user.name", "Codex")
            self._git(repo_root, "config", "user.email", "codex@example.com")
            self._git(repo_root, "remote", "add", "origin", str(remote_root))

            self._commit(repo_root, "🔧 chore(repo): DOT-1 bootstrap main", "main.txt")
            self._git(repo_root, "push", "-u", "origin", "main")

            self._git(repo_root, "checkout", "-b", "feat/DOT-81-base")
            base_subject = "✨ feat(git): DOT-81 base remote branch"
            self._commit(repo_root, base_subject, "base.txt")
            self._git(repo_root, "push", "-u", "origin", "feat/DOT-81-base")

            self._git(repo_root, "checkout", "-b", "fix/DOT-113-pre-push")
            local_subject = "🐛 fix(git): DOT-113 stacked branch range"
            self._commit(repo_root, local_subject, "stacked.txt")

            subjects = collect_commit_subjects(repo_root, remote="origin")

            self.assertEqual(subjects, [local_subject])

    def test_collects_explicit_range_when_provided(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            remote_root = temp_root / "remote.git"
            repo_root = temp_root / "repo"

            self._git(temp_root, "init", "--bare", str(remote_root))
            self._git(temp_root, "init", "-b", "main", str(repo_root))
            self._git(repo_root, "config", "user.name", "Codex")
            self._git(repo_root, "config", "user.email", "codex@example.com")
            self._git(repo_root, "remote", "add", "origin", str(remote_root))

            first_subject = "🔧 chore(repo): DOT-1 base"
            second_subject = "✨ feat(git): DOT-2 extra"
            self._commit(repo_root, first_subject, "first.txt")
            self._git(repo_root, "push", "-u", "origin", "main")
            self._commit(repo_root, second_subject, "second.txt")

            subjects = collect_commit_subjects(repo_root, range_spec="origin/main..HEAD")

            self.assertEqual(subjects, [second_subject])


if __name__ == "__main__":
    unittest.main()
