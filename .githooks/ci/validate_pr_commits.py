#!/usr/bin/env python3
"""Validador dos commits de um Pull Request usando a API do GitHub."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import conventional_emoji  # noqa: E402


def gh_headers() -> dict[str, str]:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN/GITHUB_TOKEN nao definido no ambiente.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "conventional-emoji-validator",
    }


def get_pr_commits(repo: str, pr_number: int) -> list[dict[str, Any]]:
    commits: list[dict[str, Any]] = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits"
        req_url = f"{url}?{parse.urlencode({'per_page': per_page, 'page': page})}"
        req = request.Request(req_url, headers=gh_headers(), method="GET")
        try:
            with request.urlopen(req, timeout=30) as response:
                status = response.getcode()
                payload = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Falha ao buscar commits do PR: HTTP {exc.code}\n{detail}")
        except error.URLError as exc:
            raise SystemExit(f"Falha de rede ao buscar commits do PR: {exc}")

        if status != 200:
            raise SystemExit(f"Falha ao buscar commits do PR: HTTP {status}\n{payload}")

        batch = json.loads(payload)
        if not isinstance(batch, list):
            raise SystemExit(f"Resposta inesperada da API do GitHub: {batch!r}")

        commits.extend(batch)
        if len(batch) < per_page:
            break
        page += 1

    return commits


def get_pull_request(repo: str, pr_number: int) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    req = request.Request(url, headers=gh_headers(), method="GET")
    try:
        with request.urlopen(req, timeout=30) as response:
            status = response.getcode()
            payload = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Falha ao buscar PR: HTTP {exc.code}\n{detail}")
    except error.URLError as exc:
        raise SystemExit(f"Falha de rede ao buscar PR: {exc}")

    if status != 200:
        raise SystemExit(f"Falha ao buscar PR: HTTP {status}\n{payload}")

    pr_payload = json.loads(payload)
    if not isinstance(pr_payload, dict):
        raise SystemExit(f"Resposta inesperada da API do GitHub para PR: {pr_payload!r}")
    return pr_payload


def get_pr_files(repo: str, pr_number: int) -> list[str]:
    files: list[str] = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        req_url = f"{url}?{parse.urlencode({'per_page': per_page, 'page': page})}"
        req = request.Request(req_url, headers=gh_headers(), method="GET")
        try:
            with request.urlopen(req, timeout=30) as response:
                status = response.getcode()
                payload = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Falha ao buscar arquivos do PR: HTTP {exc.code}\n{detail}")
        except error.URLError as exc:
            raise SystemExit(f"Falha de rede ao buscar arquivos do PR: {exc}")

        if status != 200:
            raise SystemExit(f"Falha ao buscar arquivos do PR: HTTP {status}\n{payload}")

        batch = json.loads(payload)
        if not isinstance(batch, list):
            raise SystemExit(f"Resposta inesperada da API do GitHub para arquivos do PR: {batch!r}")

        files.extend(
            str(entry.get("filename", "")).strip()
            for entry in batch
            if isinstance(entry, dict) and str(entry.get("filename", "")).strip()
        )
        if len(batch) < per_page:
            break
        page += 1

    return files


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Uso: validate_pr_commits.py <owner/repo> <pr_number>", file=sys.stderr)
        return 2

    repo = argv[0]
    pr_number = int(argv[1])
    pr_payload = get_pull_request(repo, pr_number)
    head_ref = str(((pr_payload.get("head") or {}).get("ref")) or "").strip()
    pr_files = get_pr_files(repo, pr_number)
    branch_result = conventional_emoji.validate_branch_name(
        head_ref,
        require_prompt_type=conventional_emoji.requires_prompt_prefix(pr_files),
    )
    commits = get_pr_commits(repo, pr_number)
    if not commits:
        print("PR sem commits?", file=sys.stderr)
        return 0

    errors: list[str] = []
    if not branch_result.ok:
        errors.append(f"- branch {head_ref or '(vazia)'}\n  ↳ {branch_result.error}")
    required_scope = conventional_emoji.required_scope_for_paths_and_branch(pr_files, head_ref)
    for commit in commits:
        sha = commit.get("sha", "")[:7]
        message = ((commit.get("commit") or {}).get("message") or "").strip()
        subject = message.splitlines()[0] if message else ""
        result = conventional_emoji.validate_message(
            subject,
            require_emoji=True,
            require_issue_key=True,
            required_scope=required_scope,
        )
        if not result.ok:
            errors.append(f"- {sha}: {subject}\n  ↳ {result.error}")

    if errors:
        print("Commits invalidos no PR:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        print(
            "\nDica: ajuste com rebase/amend para seguir o padrao obrigatorio.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(commits)} commits validados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
