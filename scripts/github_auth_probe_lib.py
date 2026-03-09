from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

TOKEN_ENV_VARS = ("GH_TOKEN", "GITHUB_TOKEN")
_STATUS_SOURCE_RE = re.compile(r"Logged in to github\.com account .* \(([^)]+)\)")


class GitHubAuthProbeError(RuntimeError):
    """Raised when the GitHub auth probe cannot execute safely."""


def build_probe_env(
    base_env: Mapping[str, str] | None = None, *, clear_token_env: bool = False
) -> dict[str, str]:
    env = dict(base_env or os.environ)
    if clear_token_env:
        for key in TOKEN_ENV_VARS:
            env.pop(key, None)
    return env


def merge_streams(stdout: str, stderr: str) -> str:
    parts = [part.strip() for part in (stdout, stderr) if part.strip()]
    return "\n".join(parts)


def parse_active_sources(status_output: str) -> list[str]:
    active_sources: list[str] = []
    pending_source = ""
    for raw_line in status_output.splitlines():
        line = raw_line.strip()
        match = _STATUS_SOURCE_RE.search(line)
        if match:
            pending_source = match.group(1).strip()
            continue
        if pending_source and line.startswith("- Active account:"):
            if line.split(":", 1)[1].strip().lower() == "true":
                active_sources.append(pending_source)
            pending_source = ""
    return active_sources


def classify_endpoint_probe(endpoint: str, *, exit_code: int, output: str) -> dict[str, str]:
    normalized = output.strip()
    if exit_code == 0:
        note = "endpoint acessivel com a credencial atual."
        if endpoint == "user/ssh_signing_keys" and normalized == "[]":
            note = "endpoint acessivel; nenhuma SSH signing key cadastrada no GitHub."
        return {"status": "ok", "note": note}
    if endpoint == "user/installations" and "GitHub App" in normalized:
        return {
            "status": "requires_github_app_user_token",
            "note": (
                "esse endpoint exige GitHub App user access token; PAT e token salvo do gh "
                "nao bastam para esse probe."
            ),
        }
    if "Resource not accessible by personal access token" in normalized:
        return {
            "status": "resource_not_accessible_by_pat",
            "note": "o endpoint nao ficou acessivel com a credencial PAT atual.",
        }
    return {
        "status": "error",
        "note": "probe falhou; revisar stderr e a credencial efetiva do gh.",
    }


def run_gh(
    args: list[str], *, repo_root: Path, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["gh", *args],
            cwd=repo_root,
            env=dict(env) if env is not None else None,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitHubAuthProbeError("GitHub CLI (`gh`) nao encontrado no PATH.") from exc


def command_payload(command: list[str], result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "command": ["gh", *command],
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "output": merge_streams(result.stdout, result.stderr),
    }


def probe_github_auth(repo_root: Path) -> dict[str, Any]:
    current_env = build_probe_env()
    sanitized_env = build_probe_env(current_env, clear_token_env=True)

    status_current = run_gh(["auth", "status"], repo_root=repo_root, env=current_env)
    status_sanitized = run_gh(["auth", "status"], repo_root=repo_root, env=sanitized_env)
    ssh_signing_keys = run_gh(["api", "user/ssh_signing_keys"], repo_root=repo_root, env=sanitized_env)
    user_installations = run_gh(["api", "user/installations"], repo_root=repo_root, env=sanitized_env)

    current_output = merge_streams(status_current.stdout, status_current.stderr)
    sanitized_output = merge_streams(status_sanitized.stdout, status_sanitized.stderr)
    current_sources = parse_active_sources(current_output)
    sanitized_sources = parse_active_sources(sanitized_output)

    payload = {
        "token_env_present": {key: bool(current_env.get(key)) for key in TOKEN_ENV_VARS},
        "auth_status": {
            "current_shell": {
                **command_payload(["auth", "status"], status_current),
                "active_sources": current_sources,
            },
            "without_env_tokens": {
                **command_payload(["auth", "status"], status_sanitized),
                "active_sources": sanitized_sources,
            },
        },
        "endpoint_probes": {
            "user/ssh_signing_keys": {
                **command_payload(["api", "user/ssh_signing_keys"], ssh_signing_keys),
                **classify_endpoint_probe(
                    "user/ssh_signing_keys",
                    exit_code=ssh_signing_keys.returncode,
                    output=merge_streams(ssh_signing_keys.stdout, ssh_signing_keys.stderr),
                ),
            },
            "user/installations": {
                **command_payload(["api", "user/installations"], user_installations),
                **classify_endpoint_probe(
                    "user/installations",
                    exit_code=user_installations.returncode,
                    output=merge_streams(user_installations.stdout, user_installations.stderr),
                ),
            },
        },
        "recommendations": [],
    }

    recommendations: list[str] = payload["recommendations"]
    if any(payload["token_env_present"].values()):
        recommendations.append(
            "Limpar `GH_TOKEN` e `GITHUB_TOKEN` quando o objetivo for usar a credencial salva do `gh`."
        )
    if current_sources != sanitized_sources:
        recommendations.append(
            "A fonte de auth mudou quando os env vars foram removidos; o shell estava mascarando a credencial do keyring."
        )
    if payload["endpoint_probes"]["user/installations"]["status"] == "requires_github_app_user_token":
        recommendations.append(
            "Validar instalacao do `GitHub for Atlassian` pela UI do GitHub/Atlassian; esse endpoint nao e um probe valido com PAT."
        )
    if payload["endpoint_probes"]["user/ssh_signing_keys"]["status"] == "ok":
        recommendations.append(
            "Usar `gh api user/ssh_signing_keys` como probe real para verificar permissao de SSH signing key."
        )
    return payload
