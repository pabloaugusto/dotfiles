from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

PUBLIC_KEY_RE = re.compile(r"^ssh-[A-Za-z0-9@._+-]+\s+[A-Za-z0-9+/=]+(?:\s+.+)?$")
WORKTREE_MODE_KEY = "dotfiles.signing.mode"
WORKTREE_PUBLIC_KEY_REF_KEY = "dotfiles.signing.automationPublicKeyRef"
WORKTREE_PUBLIC_KEY_CACHE_KEY = "dotfiles.signing.automationPublicKey"
WORKTREE_PRIVATE_KEY_PATH_KEY = "dotfiles.signing.automationPrivateKeyPath"
WORKTREE_BACKEND_KEY = "dotfiles.signing.automationBackend"
WORKTREE_ALLOWED_SIGNERS_PATH_KEY = "dotfiles.signing.automationAllowedSignersFile"


class GitSigningError(RuntimeError):
    """Raised when the signing orchestration cannot complete safely."""


@dataclass(frozen=True)
class RepoContext:
    repo_root: Path
    git_dir: Path
    common_dir: Path

    @property
    def worktree_config_path(self) -> Path:
        return self.git_dir / "config.worktree"


def run_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        input=input_text,
        env=env,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise GitSigningError(
            f"Command failed ({' '.join(args)}): {detail or f'exit={completed.returncode}'}"
        )
    return completed


def resolve_repo_context(repo_root: str | Path | None = None) -> RepoContext:
    cwd = Path(repo_root).resolve() if repo_root else Path.cwd()
    repo = Path(run_command(["git", "rev-parse", "--show-toplevel"], cwd=cwd).stdout.strip())
    git_dir = Path(run_command(["git", "rev-parse", "--git-dir"], cwd=repo).stdout.strip())
    common_dir = Path(
        run_command(["git", "rev-parse", "--git-common-dir"], cwd=repo).stdout.strip()
    )
    return RepoContext(
        repo_root=(repo if repo.is_absolute() else (cwd / repo)).resolve(),
        git_dir=(git_dir if git_dir.is_absolute() else (repo / git_dir)).resolve(),
        common_dir=(common_dir if common_dir.is_absolute() else (repo / common_dir)).resolve(),
    )


def git_get(repo: Path, *args: str) -> str:
    completed = run_command(["git", "-C", str(repo), *args], check=False)
    return (completed.stdout or "").strip()


def git_set(repo: Path, *args: str) -> None:
    run_command(["git", "-C", str(repo), *args], cwd=repo)


def git_unset(repo: Path, *args: str) -> None:
    run_command(["git", "-C", str(repo), *args], cwd=repo, check=False)


def normalize_public_key(public_key: str) -> str:
    normalized = " ".join(public_key.strip().split())
    if not PUBLIC_KEY_RE.match(normalized):
        raise GitSigningError("SSH public key invalida ou em formato nao suportado.")
    return normalized


def public_key_identity(public_key: str) -> str:
    normalized = normalize_public_key(public_key)
    parts = normalized.split()
    return " ".join(parts[:2])


def resolve_ssh_keygen_program() -> str:
    candidates: list[str] = []
    if os.name == "nt":
        candidates.extend(
            [
                r"C:\Windows\System32\OpenSSH\ssh-keygen.exe",
                r"C:\Windows\Sysnative\OpenSSH\ssh-keygen.exe",
            ]
        )
    resolved = shutil.which("ssh-keygen")
    if resolved:
        candidates.append(resolved)
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise GitSigningError("ssh-keygen nao encontrado para assinar commits em modo autonomo.")


def load_secrets_refs(repo_root: Path) -> dict[str, str]:
    refs_path = repo_root / "df" / "secrets" / "secrets-ref.yaml"
    if not refs_path.exists():
        return {}
    parsed = yaml.safe_load(refs_path.read_text(encoding="utf-8")) or {}
    git_signing = parsed.get("git-signing") or {}
    if not isinstance(git_signing, dict):
        return {}
    value = git_signing.get("automation-public-key")
    return {
        "automation_public_key_ref": str(value or "").strip(),
    }


def load_worktree_signing_refs(repo_root: Path) -> dict[str, str]:
    cached_public_key = git_get(
        repo_root,
        "config",
        "--worktree",
        "--get",
        WORKTREE_PUBLIC_KEY_CACHE_KEY,
    )
    normalized_cached_public_key = ""
    if cached_public_key:
        try:
            normalized_cached_public_key = normalize_public_key(cached_public_key)
        except GitSigningError:
            normalized_cached_public_key = ""
    return {
        "automation_public_key_ref": git_get(
            repo_root,
            "config",
            "--worktree",
            "--get",
            WORKTREE_PUBLIC_KEY_REF_KEY,
        ),
        "automation_public_key": normalized_cached_public_key,
        "automation_private_key_path": git_get(
            repo_root,
            "config",
            "--worktree",
            "--get",
            WORKTREE_PRIVATE_KEY_PATH_KEY,
        ),
        "automation_backend": git_get(
            repo_root,
            "config",
            "--worktree",
            "--get",
            WORKTREE_BACKEND_KEY,
        ),
    }


def read_public_key_from_1password(repo_root: Path, public_key_ref: str) -> str:
    resolved = run_command(["op", "read", public_key_ref], cwd=repo_root).stdout
    return normalize_public_key(resolved)


def resolve_public_key_ref(
    repo_root: Path,
    *,
    public_key_ref: str = "",
    public_key: str = "",
) -> tuple[str, str]:
    explicit_key = public_key.strip()
    if explicit_key:
        return "", normalize_public_key(explicit_key)

    worktree_refs = load_worktree_signing_refs(repo_root)
    chosen_ref = (
        public_key_ref.strip()
        or worktree_refs.get("automation_public_key_ref", "")
        or load_secrets_refs(repo_root).get("automation_public_key_ref", "")
    )
    cached_public_key = worktree_refs.get("automation_public_key", "")
    if not chosen_ref and cached_public_key:
        return "", cached_public_key
    if not chosen_ref:
        local_public_key = load_local_automation_public_key(repo_root)
        if local_public_key:
            return "", local_public_key
        raise GitSigningError(
            "Nenhuma ref de chave publica de automacao configurada. "
            "Configure git.automation_signing_key_ref no bootstrap local ou passe "
            "--public-key-ref/--public-key."
        )

    try:
        return chosen_ref, read_public_key_from_1password(repo_root, chosen_ref)
    except GitSigningError:
        worktree_ref = worktree_refs.get("automation_public_key_ref", "")
        if cached_public_key and worktree_ref and worktree_ref == chosen_ref:
            return chosen_ref, cached_public_key
        raise


def ensure_worktree_config_enabled(repo_root: Path) -> bool:
    current = git_get(repo_root, "config", "--bool", "extensions.worktreeConfig").lower()
    if current == "true":
        return False
    git_set(repo_root, "config", "extensions.worktreeConfig", "true")
    return True


def build_default_title(hostname: str | None = None) -> str:
    suffix = re.sub(r"[^A-Za-z0-9._-]+", "-", (hostname or socket.gethostname()).strip()).strip("-")
    return f"dotfiles-automation-signing-{suffix or 'host'}"


def build_default_auth_title(hostname: str | None = None) -> str:
    suffix = re.sub(r"[^A-Za-z0-9._-]+", "-", (hostname or socket.gethostname()).strip()).strip("-")
    return f"dotfiles-automation-auth-{suffix or 'host'}"


def default_local_automation_key_path(context: RepoContext) -> Path:
    return context.git_dir / "dotfiles" / "automation-signing" / "id_ed25519"


def build_automation_private_key_path(context: RepoContext) -> Path:
    return default_local_automation_key_path(context)


def build_automation_public_key_path(context: RepoContext) -> Path:
    return build_automation_private_key_path(context).with_suffix(".pub")


def default_allowed_signers_path(context: RepoContext) -> Path:
    return context.git_dir / "dotfiles" / "automation-signing" / "allowed_signers"


def load_local_automation_public_key(repo_root: Path) -> str:
    context = resolve_repo_context(repo_root)
    public_key_path = build_automation_public_key_path(context)
    if not public_key_path.exists():
        return ""
    return normalize_public_key(public_key_path.read_text(encoding="utf-8"))


def resolve_signing_principal(repo_root: Path) -> str:
    return git_get(repo_root, "config", "--includes", "--get", "user.email").strip()


def build_git_ssh_command(private_key_path: Path) -> str:
    normalized = private_key_path.resolve().as_posix()
    return (
        f'ssh -i "{normalized}" '
        "-o IdentitiesOnly=yes "
        "-o IdentityAgent=none "
        "-o StrictHostKeyChecking=accept-new "
        "-o ConnectTimeout=10"
    )


def ensure_allowed_signers_file(context: RepoContext, public_key: str) -> dict[str, str]:
    principal = resolve_signing_principal(context.repo_root)
    if not principal:
        return {"path": "", "principal": ""}
    allowed_signers_path = default_allowed_signers_path(context)
    allowed_signers_path.parent.mkdir(parents=True, exist_ok=True)
    allowed_signers_path.write_text(
        f"{principal} {normalize_public_key(public_key)}\n",
        encoding="ascii",
    )
    return {
        "path": str(allowed_signers_path),
        "principal": principal,
    }


def ensure_local_automation_keypair(
    context: RepoContext,
    *,
    title: str = "",
) -> dict[str, str | bool]:
    private_key_path = default_local_automation_key_path(context)
    public_key_path = private_key_path.with_suffix(".pub")
    ssh_keygen = resolve_ssh_keygen_program()
    created = False
    if not private_key_path.exists() or not public_key_path.exists():
        private_key_path.parent.mkdir(parents=True, exist_ok=True)
        desired_title = title.strip() or build_default_title()
        run_command(
            [
                ssh_keygen,
                "-t",
                "ed25519",
                "-N",
                "",
                "-C",
                desired_title,
                "-f",
                str(private_key_path),
            ],
            cwd=context.repo_root,
        )
        created = True
    public_key = normalize_public_key(public_key_path.read_text(encoding="utf-8"))
    return {
        "private_key_path": str(private_key_path),
        "public_key_path": str(public_key_path),
        "public_key": public_key,
        "ssh_keygen_program": ssh_keygen,
        "created": created,
    }


def should_use_local_backend(
    context: RepoContext,
    *,
    public_key_ref: str = "",
    public_key: str = "",
) -> bool:
    if public_key_ref.strip() or public_key.strip():
        return False
    worktree_refs = load_worktree_signing_refs(context.repo_root)
    if worktree_refs.get("automation_backend", "").strip() == "local-key":
        return True
    private_key_path = worktree_refs.get("automation_private_key_path", "").strip()
    if private_key_path and Path(private_key_path).exists():
        return True
    candidate = default_local_automation_key_path(context)
    return candidate.exists() and candidate.with_suffix(".pub").exists()


def resolve_local_ssh_sign_program() -> str:
    return resolve_ssh_keygen_program()


def _github_cli_env_without_runtime_tokens() -> dict[str, str]:
    sanitized = dict(os.environ)
    sanitized.pop("GH_TOKEN", None)
    sanitized.pop("GITHUB_TOKEN", None)
    return sanitized


def run_github_command(
    repo_root: Path,
    args: list[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = run_command(args, cwd=repo_root, check=False)
    detail = (completed.stderr or completed.stdout or "").strip()
    if completed.returncode == 0:
        return completed

    should_retry_without_env_token = (
        "Resource not accessible by personal access token" in detail
        or "Resource not accessible by integration" in detail
    ) and (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    if should_retry_without_env_token:
        completed = run_command(
            args,
            cwd=repo_root,
            check=False,
            env=_github_cli_env_without_runtime_tokens(),
        )

    if check and completed.returncode != 0:
        final_detail = (completed.stderr or completed.stdout or "").strip()
        raise GitSigningError(
            f"GitHub command failed ({' '.join(args)}): {final_detail or f'exit={completed.returncode}'}"
        )
    return completed


def list_github_keys(repo_root: Path, *, publication_kind: str) -> list[dict[str, object]]:
    endpoint = "user/ssh_signing_keys" if publication_kind == "signing" else "user/keys"
    completed = run_github_command(repo_root, ["gh", "api", endpoint])
    payload = json.loads(completed.stdout or "[]")
    if not isinstance(payload, list):
        raise GitSigningError(f"Resposta inesperada de gh api {endpoint}.")
    return [item for item in payload if isinstance(item, dict)]


def list_github_signing_keys(repo_root: Path) -> list[dict[str, object]]:
    return list_github_keys(repo_root, publication_kind="signing")


def ensure_github_key(
    repo_root: Path,
    *,
    publication_kind: str,
    public_key_ref: str = "",
    public_key: str = "",
    title: str = "",
) -> dict[str, object]:
    context = resolve_repo_context(repo_root)
    if should_use_local_backend(
        context,
        public_key_ref=public_key_ref,
        public_key=public_key,
    ):
        local_key = ensure_local_automation_keypair(context, title=title)
        chosen_ref = ""
        resolved_key = str(local_key["public_key"])
        private_key_path = str(local_key["private_key_path"])
        backend = "local-key"
    else:
        try:
            chosen_ref, resolved_key = resolve_public_key_ref(
                repo_root,
                public_key_ref=public_key_ref,
                public_key=public_key,
            )
            backend = "agent-backed"
            private_key_path = ""
        except GitSigningError as exc:
            if "Nenhuma ref de chave publica de automacao configurada." not in str(exc):
                raise
            local_key = ensure_local_automation_keypair(context, title=title)
            chosen_ref = ""
            resolved_key = str(local_key["public_key"])
            private_key_path = str(local_key["private_key_path"])
            backend = "local-key"

    for item in list_github_keys(repo_root, publication_kind=publication_kind):
        if public_key_identity(str(item.get("key", ""))) == public_key_identity(resolved_key):
            return {
                "status": "already_present",
                "id": item.get("id"),
                "title": item.get("title"),
                "publication_kind": publication_kind,
                "public_key_ref": chosen_ref,
                "public_key": resolved_key,
                "private_key_path": private_key_path,
                "backend": backend,
            }

    desired_title = title.strip() or (
        build_default_title() if publication_kind == "signing" else build_default_auth_title()
    )
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".pub",
            delete=False,
        ) as handle:
            handle.write(resolved_key + "\n")
            temp_path = handle.name

        args = ["gh", "ssh-key", "add", temp_path, "--title", desired_title]
        if publication_kind == "signing":
            args.extend(["--type", "signing"])
        run_github_command(repo_root, args)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    for _ in range(5):
        for item in list_github_keys(repo_root, publication_kind=publication_kind):
            if public_key_identity(str(item.get("key", ""))) == public_key_identity(resolved_key):
                return {
                    "status": "created",
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "publication_kind": publication_kind,
                    "public_key_ref": chosen_ref,
                    "public_key": resolved_key,
                    "private_key_path": private_key_path,
                    "backend": backend,
                }
        time.sleep(1.0)

    raise GitSigningError(
        "A chave foi enviada ao GitHub, mas nao foi localizada na listagem final."
    )


def ensure_github_signing_key(
    repo_root: Path,
    *,
    public_key_ref: str = "",
    public_key: str = "",
    title: str = "",
) -> dict[str, object]:
    return ensure_github_key(
        repo_root,
        publication_kind="signing",
        public_key_ref=public_key_ref,
        public_key=public_key,
        title=title,
    )


def ensure_github_auth_key(
    repo_root: Path,
    *,
    public_key_ref: str = "",
    public_key: str = "",
    title: str = "",
) -> dict[str, object]:
    return ensure_github_key(
        repo_root,
        publication_kind="authentication",
        public_key_ref=public_key_ref,
        public_key=public_key,
        title=title,
    )


def status_payload(repo_root: str | Path | None = None) -> dict[str, object]:
    context = resolve_repo_context(repo_root)
    refs = load_secrets_refs(context.repo_root)
    worktree_refs = load_worktree_signing_refs(context.repo_root)
    worktree_mode = git_get(context.repo_root, "config", "--worktree", "--get", WORKTREE_MODE_KEY)
    effective_key = git_get(context.repo_root, "config", "--includes", "--get", "user.signingkey")
    effective_program = git_get(
        context.repo_root, "config", "--includes", "--get", "gpg.ssh.program"
    )
    effective_allowed_signers_file = git_get(
        context.repo_root,
        "config",
        "--includes",
        "--get",
        "gpg.ssh.allowedSignersFile",
    )
    effective_commit_sign = git_get(
        context.repo_root, "config", "--includes", "--get", "commit.gpgsign"
    )
    effective_format = git_get(context.repo_root, "config", "--includes", "--get", "gpg.format")
    effective_core_ssh_command = git_get(
        context.repo_root, "config", "--includes", "--get", "core.sshCommand"
    )
    return {
        "repo_root": str(context.repo_root),
        "git_dir": str(context.git_dir),
        "common_dir": str(context.common_dir),
        "worktree_config_path": str(context.worktree_config_path),
        "worktree_config_enabled": git_get(
            context.repo_root, "config", "--bool", "extensions.worktreeConfig"
        ).lower()
        == "true",
        "mode": worktree_mode or "human",
        "worktree_mode": worktree_mode or "",
        "configured_automation_public_key_ref": refs.get("automation_public_key_ref", ""),
        "worktree_automation_public_key_ref": worktree_refs.get("automation_public_key_ref", ""),
        "worktree_automation_public_key_cached": bool(
            worktree_refs.get("automation_public_key", "")
        ),
        "worktree_automation_private_key_path": worktree_refs.get(
            "automation_private_key_path", ""
        ),
        "worktree_signing_private_key_path": worktree_refs.get(
            "automation_private_key_path", ""
        ),
        "worktree_automation_backend": worktree_refs.get("automation_backend", ""),
        "worktree_automation_allowed_signers_file": git_get(
            context.repo_root,
            "config",
            "--worktree",
            "--get",
            WORKTREE_ALLOWED_SIGNERS_PATH_KEY,
        ),
        "worktree_auth_mode": git_get(
            context.repo_root, "config", "--worktree", "--get", "dotfiles.github.authMode"
        ),
        "worktree_auth_key_path": git_get(
            context.repo_root,
            "config",
            "--worktree",
            "--get",
            "dotfiles.github.automationSshKeyPath",
        ),
        "effective_signing_principal": resolve_signing_principal(context.repo_root),
        "effective_signing_key": effective_key,
        "effective_gpg_program": effective_program,
        "effective_allowed_signers_file": effective_allowed_signers_file,
        "effective_commit_gpgsign": effective_commit_sign,
        "effective_gpg_format": effective_format,
        "effective_core_ssh_command": effective_core_ssh_command,
    }


def apply_automation_mode(
    repo_root: str | Path | None = None,
    *,
    public_key_ref: str = "",
    public_key: str = "",
    ensure_github: bool = False,
    title: str = "",
) -> dict[str, object]:
    context = resolve_repo_context(repo_root)
    changed_worktree_config = ensure_worktree_config_enabled(context.repo_root)
    private_key_path = ""
    ssh_keygen_program = ""
    backend = "agent-backed"
    local_key_payload: dict[str, str | bool] | None = None
    if should_use_local_backend(
        context,
        public_key_ref=public_key_ref,
        public_key=public_key,
    ):
        local_key_payload = ensure_local_automation_keypair(context, title=title)
        chosen_ref = ""
        resolved_key = str(local_key_payload["public_key"])
        private_key_path = str(local_key_payload["private_key_path"])
        ssh_keygen_program = str(local_key_payload["ssh_keygen_program"])
        backend = "local-key"
    else:
        try:
            chosen_ref, resolved_key = resolve_public_key_ref(
                context.repo_root,
                public_key_ref=public_key_ref,
                public_key=public_key,
            )
        except GitSigningError as exc:
            if "Nenhuma ref de chave publica de automacao configurada." not in str(exc):
                raise
            local_key_payload = ensure_local_automation_keypair(context, title=title)
            chosen_ref = ""
            resolved_key = str(local_key_payload["public_key"])
            private_key_path = str(local_key_payload["private_key_path"])
            ssh_keygen_program = str(local_key_payload["ssh_keygen_program"])
            backend = "local-key"

    git_set(context.repo_root, "config", "--worktree", WORKTREE_MODE_KEY, "automation")
    git_set(context.repo_root, "config", "--worktree", WORKTREE_BACKEND_KEY, backend)
    if chosen_ref:
        git_set(
            context.repo_root,
            "config",
            "--worktree",
            WORKTREE_PUBLIC_KEY_REF_KEY,
            chosen_ref,
        )
    else:
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            WORKTREE_PUBLIC_KEY_REF_KEY,
        )
    if private_key_path:
        git_set(
            context.repo_root,
            "config",
            "--worktree",
            WORKTREE_PRIVATE_KEY_PATH_KEY,
            private_key_path,
        )
        git_set(context.repo_root, "config", "--worktree", "gpg.ssh.program", ssh_keygen_program)
        git_set(context.repo_root, "config", "--worktree", "dotfiles.github.authMode", "automation")
        git_set(
            context.repo_root,
            "config",
            "--worktree",
            "dotfiles.github.automationSshKeyPath",
            private_key_path,
        )
        git_set(
            context.repo_root,
            "config",
            "--worktree",
            "core.sshCommand",
            build_git_ssh_command(Path(private_key_path)),
        )
    else:
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            WORKTREE_PRIVATE_KEY_PATH_KEY,
        )
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            "gpg.ssh.program",
        )
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            "dotfiles.github.authMode",
        )
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            "dotfiles.github.automationSshKeyPath",
        )
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            "core.sshCommand",
        )
    git_set(
        context.repo_root,
        "config",
        "--worktree",
        WORKTREE_PUBLIC_KEY_CACHE_KEY,
        resolved_key,
    )
    allowed_signers = ensure_allowed_signers_file(context, resolved_key)
    if allowed_signers["path"]:
        git_set(
            context.repo_root,
            "config",
            "--worktree",
            WORKTREE_ALLOWED_SIGNERS_PATH_KEY,
            allowed_signers["path"],
        )
        git_set(
            context.repo_root,
            "config",
            "--worktree",
            "gpg.ssh.allowedSignersFile",
            allowed_signers["path"],
        )
    else:
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            WORKTREE_ALLOWED_SIGNERS_PATH_KEY,
        )
        git_unset(
            context.repo_root,
            "config",
            "--worktree",
            "--unset-all",
            "gpg.ssh.allowedSignersFile",
        )
    git_set(context.repo_root, "config", "--worktree", "gpg.format", "ssh")
    git_set(context.repo_root, "config", "--worktree", "commit.gpgsign", "true")
    git_set(
        context.repo_root,
        "config",
        "--worktree",
        "user.signingkey",
        private_key_path or resolved_key,
    )

    github_payload: dict[str, object] | None = None
    github_auth_payload: dict[str, object] | None = None
    if ensure_github:
        github_payload = ensure_github_signing_key(
            context.repo_root,
            public_key_ref=chosen_ref,
            public_key=resolved_key,
            title=title,
        )
        if private_key_path:
            github_auth_payload = ensure_github_auth_key(
                context.repo_root,
                public_key=build_automation_public_key_path(context)
                .read_text(encoding="utf-8")
                .strip(),
            )

    payload = status_payload(context.repo_root)
    payload.update(
        {
            "action": "use_automation",
            "changed_worktree_config": changed_worktree_config,
            "public_key_ref": chosen_ref,
            "public_key": resolved_key,
            "private_key_path": private_key_path,
            "automation_private_key_path": private_key_path,
            "backend": backend,
            "local_key": local_key_payload,
            "github": github_payload,
            "github_signing": github_payload,
            "github_auth": github_auth_payload,
        }
    )
    return payload


def apply_human_mode(repo_root: str | Path | None = None) -> dict[str, object]:
    context = resolve_repo_context(repo_root)
    ensure_worktree_config_enabled(context.repo_root)
    keys = [
        WORKTREE_MODE_KEY,
        WORKTREE_BACKEND_KEY,
        WORKTREE_PUBLIC_KEY_REF_KEY,
        WORKTREE_PUBLIC_KEY_CACHE_KEY,
        WORKTREE_PRIVATE_KEY_PATH_KEY,
        WORKTREE_ALLOWED_SIGNERS_PATH_KEY,
        "dotfiles.github.authMode",
        "dotfiles.github.automationSshKeyPath",
        "gpg.format",
        "commit.gpgsign",
        "gpg.ssh.program",
        "gpg.ssh.allowedSignersFile",
        "user.signingkey",
        "core.sshCommand",
    ]
    for key in keys:
        git_unset(context.repo_root, "config", "--worktree", "--unset-all", key)

    payload = status_payload(context.repo_root)
    payload.update({"action": "use_human"})
    return payload
