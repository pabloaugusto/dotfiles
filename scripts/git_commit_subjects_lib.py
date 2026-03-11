from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


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
    return [
        str(entry["subject"])
        for entry in collect_commit_metadata(
            repo_root,
            remote=remote,
            range_spec=range_spec,
        )
    ]


def collect_commit_metadata(
    repo_root: str | Path,
    *,
    remote: str = "origin",
    range_spec: str = "",
) -> list[dict[str, Any]]:
    resolved_repo_root = Path(repo_root).resolve()
    if range_spec.strip():
        args = ["log", "--format=%H%x1f%s", range_spec.strip()]
    else:
        args = [
            "log",
            "--format=%H%x1f%s",
            "HEAD",
            "--not",
            f"--remotes={remote.strip() or 'origin'}",
        ]
    completed = _run_git(resolved_repo_root, args)
    metadata: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        sha, _, subject = stripped.partition("\x1f")
        files_completed = _run_git(
            resolved_repo_root,
            ["diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "-m", sha.strip()],
        )
        paths = sorted(
            {
                path.strip().replace("\\", "/")
                for path in files_completed.stdout.splitlines()
                if path.strip()
            }
        )
        metadata.append(
            {
                "sha": sha.strip(),
                "subject": subject.strip(),
                "paths": paths,
            }
        )
    return metadata
