from __future__ import annotations

import subprocess
from pathlib import Path


class GitCommitSubjectsError(RuntimeError):
    """Raised when commit subjects cannot be collected safely."""


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
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
        detail = (completed.stderr or completed.stdout or "").strip()
        raise GitCommitSubjectsError(
            f"Falha ao executar git {' '.join(args)}: {detail or f'exit={completed.returncode}'}"
        )
    return completed


def collect_commit_subjects(
    repo_root: str | Path,
    *,
    remote: str = "origin",
    range_spec: str = "",
) -> list[str]:
    resolved_repo_root = Path(repo_root).resolve()
    if range_spec.strip():
        args = ["log", "--format=%s", range_spec.strip()]
    else:
        args = ["log", "--format=%s", "HEAD", "--not", f"--remotes={remote.strip() or 'origin'}"]
    completed = _run_git(resolved_repo_root, args)
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
