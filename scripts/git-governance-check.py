#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} falhou: {stderr}")
    return completed


def resolve_repo_root(explicit_root: Path | None) -> Path:
    start = explicit_root.resolve() if explicit_root else Path(__file__).resolve().parents[1]
    completed = run_git(start, "rev-parse", "--show-toplevel")
    return Path(completed.stdout.strip()).resolve()


def resolve_base_ref(repo_root: Path, requested: str | None) -> str:
    candidates: list[str] = []
    if requested:
        candidates.append(requested)
    candidates.extend(["origin/main", "main"])

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        completed = run_git(repo_root, "rev-parse", "--verify", "--quiet", candidate, check=False)
        if completed.returncode == 0:
            return candidate

    raise RuntimeError(
        "Nao foi possivel resolver a base ref. Informe --base-ref ou garanta origin/main ou main."
    )


def base_branch_name(base_ref: str) -> str:
    if base_ref.startswith("origin/"):
        return base_ref.split("/", 1)[1]
    return base_ref


def current_branch_name(repo_root: Path) -> str:
    return run_git(repo_root, "branch", "--show-current").stdout.strip()


def local_branches(repo_root: Path) -> list[str]:
    completed = run_git(repo_root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return sorted(line.strip() for line in completed.stdout.splitlines() if line.strip())


def merged_local_branches(repo_root: Path, base_ref: str) -> set[str]:
    completed = run_git(repo_root, "branch", "--format=%(refname:short)", "--merged", base_ref)
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def normalize_path(path: Path) -> str:
    return str(path.resolve()).casefold()


def parse_worktree_porcelain(raw_text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = value.strip()
        elif key == "branch":
            branch_ref = value.strip()
            prefix = "refs/heads/"
            if branch_ref.startswith(prefix):
                branch_ref = branch_ref[len(prefix) :]
            current["branch"] = branch_ref
        elif key == "HEAD":
            current["head"] = value.strip()
        elif key == "detached":
            current["detached"] = "true"
    if current:
        entries.append(current)
    return entries


def build_payload(repo_root: Path, base_ref: str) -> dict[str, Any]:
    current_branch = current_branch_name(repo_root)
    base_branch = base_branch_name(base_ref)
    merged_branches = merged_local_branches(repo_root, base_ref)

    protected = {base_branch}
    if current_branch:
        protected.add(current_branch)

    residual_branches = [
        branch
        for branch in local_branches(repo_root)
        if branch in merged_branches and branch not in protected
    ]

    worktree_completed = run_git(repo_root, "worktree", "list", "--porcelain")
    worktrees = parse_worktree_porcelain(worktree_completed.stdout)
    repo_root_norm = normalize_path(repo_root)
    residual_worktrees: list[dict[str, str]] = []
    for entry in worktrees:
        branch = entry.get("branch", "")
        path_value = entry.get("path", "")
        if not branch or not path_value:
            continue
        if branch not in merged_branches or branch in protected:
            continue
        if normalize_path(Path(path_value)) == repo_root_norm:
            continue
        residual_worktrees.append(
            {
                "branch": branch,
                "path": str(Path(path_value).resolve()),
            }
        )

    return {
        "repo_root": str(repo_root),
        "base_ref": base_ref,
        "base_branch": base_branch,
        "current_branch": current_branch,
        "merged_local_branches": residual_branches,
        "merged_worktrees": residual_worktrees,
        "status": "fail" if residual_branches or residual_worktrees else "ok",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida higiene Git e acusa branches ou worktrees residuais ja absorvidas."
    )
    parser.add_argument("--repo-root", type=Path, default=Path(""))
    parser.add_argument("--base-ref", default="")
    parser.add_argument("--strict", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    requested_root = args.repo_root if str(args.repo_root) else None

    try:
        repo_root = resolve_repo_root(requested_root)
        base_ref = resolve_base_ref(repo_root, args.base_ref or None)
        payload = build_payload(repo_root, base_ref)
    except RuntimeError as exc:
        payload = {
            "status": "error",
            "error": str(exc),
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(payload, ensure_ascii=True, indent=2))

    branch_count = len(payload["merged_local_branches"])
    worktree_count = len(payload["merged_worktrees"])
    if args.strict and (branch_count or worktree_count):
        print(
            "Higiene Git reprovada: "
            f"{branch_count} branch(es) local(is) e "
            f"{worktree_count} worktree(s) residual(is) ja foram absorvidas em {payload['base_ref']}.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
