from __future__ import annotations

import json
import os
import re
import shlex
import smtplib
import socket
import ssl
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("config/secrets-rotation.yaml")
OP_REF_RE = re.compile(r"^op://(?P<body>.+)$")
SSH_PUBLIC_KEY_RE = re.compile(r"^ssh-[A-Za-z0-9@._+-]+\s+[A-Za-z0-9+/=]+(?:\s+.+)?$")
AGE_RECIPIENT_LINE_RE = re.compile(r"(?m)^(\s*-\s+)age[0-9a-z]+(?:\s*)$")


class SecretsRotationError(RuntimeError):
    """Raised when the rotation workflow cannot proceed safely."""


@dataclass(frozen=True)
class RepoContext:
    repo_root: Path
    config_path: Path
    report_path: Path
    state_path: Path


@dataclass(frozen=True)
class OpReference:
    raw: str
    vault: str
    item: str
    section: str
    field: str


@dataclass(frozen=True)
class RotationTarget:
    target_id: str
    kind: str
    automation: str
    order: int
    source_of_truth: str
    enabled: bool
    config: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def command_exists(name: str) -> bool:
    completed = subprocess.run(
        ["where", name] if os.name == "nt" else ["bash", "-lc", f"command -v {shlex.quote(name)}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def run_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise SecretsRotationError(
            f"Command failed ({' '.join(args)}): {detail or f'exit={completed.returncode}'}"
        )
    return completed


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    completed = run_command(["git", "rev-parse", "--show-toplevel"])
    return Path(completed.stdout.strip()).resolve()


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SecretsRotationError(f"Arquivo YAML nao encontrado: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise SecretsRotationError(f"YAML invalido em {path}: esperado objeto raiz.")
    return payload


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dotted_get(payload: dict[str, Any], dotted_key: str, default: str = "") -> str:
    current: Any = payload
    for chunk in dotted_key.split("."):
        if not isinstance(current, dict) or chunk not in current:
            return default
        current = current[chunk]
    return str(current or default).strip()


def expand_path(repo_root: Path, raw_path: str) -> Path:
    expanded = Path(os.path.expandvars(raw_path)).expanduser()
    if expanded.is_absolute():
        return expanded
    return (repo_root / expanded).resolve()


def parse_op_ref(op_ref: str) -> OpReference:
    match = OP_REF_RE.match((op_ref or "").strip())
    if not match:
        raise SecretsRotationError(f"Ref do 1Password invalida: {op_ref}")
    body = match.group("body").strip("/")
    parts = [chunk for chunk in body.split("/") if chunk]
    if len(parts) < 3:
        raise SecretsRotationError(f"Ref do 1Password incompleta: {op_ref}")
    vault = parts[0]
    item = parts[1]
    if len(parts) == 3:
        return OpReference(raw=op_ref, vault=vault, item=item, section="", field=parts[2])
    return OpReference(
        raw=op_ref,
        vault=vault,
        item=item,
        section="/".join(parts[2:-1]),
        field=parts[-1],
    )


def normalize_public_key(public_key: str) -> str:
    normalized = " ".join((public_key or "").strip().split())
    if not SSH_PUBLIC_KEY_RE.match(normalized):
        raise SecretsRotationError("Chave publica SSH invalida ou em formato nao suportado.")
    return normalized


def derive_ssh_public_key(private_key: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as handle:
        handle.write(private_key)
        handle.write("\n")
        private_path = Path(handle.name)
    try:
        private_path.chmod(0o600)
        completed = run_command(["ssh-keygen", "-y", "-f", str(private_path)])
        return normalize_public_key(completed.stdout)
    finally:
        if private_path.exists():
            private_path.unlink()


def ssh_public_key_fingerprint(public_key: str) -> str:
    normalized = normalize_public_key(public_key)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".pub") as handle:
        handle.write(normalized + "\n")
        public_path = Path(handle.name)
    try:
        completed = run_command(["ssh-keygen", "-lf", str(public_path)])
        return " ".join(completed.stdout.split()[:2])
    finally:
        if public_path.exists():
            public_path.unlink()


def load_secrets_refs(repo_root: Path) -> dict[str, Any]:
    return load_yaml_file(repo_root / "df" / "secrets" / "secrets-ref.yaml")


def resolve_secret_ref(secrets_refs: dict[str, Any], ref_key: str) -> str:
    if not ref_key:
        raise SecretsRotationError("ref_key vazio na configuracao de rotacao.")
    resolved = dotted_get(secrets_refs, ref_key)
    if not resolved:
        raise SecretsRotationError(
            f"Ref '{ref_key}' nao encontrada em df/secrets/secrets-ref.yaml."
        )
    return resolved


def load_rotation_targets(payload: dict[str, Any]) -> list[RotationTarget]:
    targets_payload = payload.get("targets") or {}
    if not isinstance(targets_payload, dict):
        raise SecretsRotationError("config/secrets-rotation.yaml precisa conter targets como mapa.")
    targets: list[RotationTarget] = []
    for target_id, entry in targets_payload.items():
        if not isinstance(entry, dict):
            raise SecretsRotationError(f"Target invalido em config/secrets-rotation.yaml: {target_id}")
        targets.append(
            RotationTarget(
                target_id=str(target_id),
                kind=str(entry.get("kind", "")),
                automation=str(entry.get("automation", "manual_blocked")),
                order=int(entry.get("order", 999)),
                source_of_truth=str(entry.get("source_of_truth", "1password")),
                enabled=bool(entry.get("enabled", False)),
                config=entry,
            )
        )
    return sorted(targets, key=lambda item: (item.order, item.target_id))


def load_repo_context(
    repo_root: str | Path | None = None,
    config_path: str | Path | None = None,
) -> tuple[RepoContext, dict[str, Any], dict[str, Any], list[RotationTarget]]:
    resolved_repo = resolve_repo_root(repo_root)
    config_file = (
        expand_path(resolved_repo, str(config_path))
        if config_path
        else (resolved_repo / DEFAULT_CONFIG_PATH).resolve()
    )
    config_payload = load_yaml_file(config_file)
    audit_payload = config_payload.get("audit") or {}
    if not isinstance(audit_payload, dict):
        raise SecretsRotationError("Sessao audit invalida em config/secrets-rotation.yaml.")
    report_path = expand_path(
        resolved_repo,
        str(audit_payload.get("report_path", ".cache/secrets-rotation/last-report.json")),
    )
    state_path = expand_path(
        resolved_repo,
        str(
            audit_payload.get(
                "state_path",
                "~/.config/dotfiles/secrets-rotation.audit.sops.yaml",
            )
        ),
    )
    context = RepoContext(
        repo_root=resolved_repo,
        config_path=config_file,
        report_path=report_path,
        state_path=state_path,
    )
    secrets_refs = load_secrets_refs(resolved_repo)
    targets = load_rotation_targets(config_payload)
    return context, config_payload, secrets_refs, targets


class OnePasswordDriver:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def whoami(self) -> dict[str, str]:
        completed = run_command(["op", "whoami"], cwd=self.repo_root)
        return {"ok": "true", "detail": " ".join(completed.stdout.split())}

    def read_ref(self, op_ref: str) -> str:
        return run_command(["op", "read", op_ref], cwd=self.repo_root).stdout.strip()

    def get_item_json(self, reference: OpReference) -> dict[str, Any]:
        completed = run_command(
            ["op", "item", "get", reference.item, "--vault", reference.vault, "--format", "json", "--reveal"],
            cwd=self.repo_root,
        )
        payload = json.loads(completed.stdout or "{}")
        if not isinstance(payload, dict):
            raise SecretsRotationError(f"Resposta inesperada de op item get para {reference.raw}.")
        return payload

    def update_ref_value(self, op_ref: str, new_value: str) -> dict[str, Any]:
        reference = parse_op_ref(op_ref)
        payload = self.get_item_json(reference)
        fields = payload.get("fields")
        if not isinstance(fields, list):
            raise SecretsRotationError(f"Item 1Password sem fields editaveis: {op_ref}")

        updated = False
        for field in fields:
            if not isinstance(field, dict):
                continue
            label = str(field.get("label", "")).strip()
            field_id = str(field.get("id", "")).strip()
            section = field.get("section") if isinstance(field.get("section"), dict) else {}
            section_label = str(section.get("label", "")).strip()
            if label != reference.field and field_id != reference.field:
                continue
            if reference.section and section_label != reference.section:
                continue
            field["value"] = new_value
            updated = True
            break

        if not updated:
            new_field: dict[str, Any] = {
                "id": reference.field,
                "label": reference.field,
                "type": "CONCEALED",
                "value": new_value,
            }
            if reference.section:
                new_field["section"] = {"label": reference.section}
            fields.append(new_field)

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".json") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.write("\n")
            template_path = Path(handle.name)
        try:
            run_command(
                [
                    "op",
                    "item",
                    "edit",
                    reference.item,
                    "--vault",
                    reference.vault,
                    "--template",
                    str(template_path),
                ],
                cwd=self.repo_root,
            )
        finally:
            if template_path.exists():
                template_path.unlink()
        return {"reference": reference.raw, "vault": reference.vault, "item": reference.item}

    def create_secure_note(
        self,
        *,
        vault: str,
        title: str,
        notes: str,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "title": title,
            "category": "SECURE_NOTE",
            "fields": [
                {
                    "id": "notesPlain",
                    "type": "STRING",
                    "purpose": "NOTES",
                    "label": "notesPlain",
                    "value": notes,
                }
            ],
        }
        args = ["op", "item", "create", "--vault", vault, "--format", "json", "-"]
        if tags:
            args.extend(["--tags", ",".join(tags)])
        completed = run_command(args, cwd=self.repo_root, input_text=json.dumps(payload))
        result = json.loads(completed.stdout or "{}")
        if not isinstance(result, dict):
            raise SecretsRotationError("Resposta inesperada ao criar Secure Note no 1Password.")
        return result

    def create_ssh_key_item(
        self,
        *,
        vault: str,
        title: str,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        args = [
            "op",
            "item",
            "create",
            "--category",
            "SSH Key",
            "--ssh-generate-key",
            "ed25519",
            "--title",
            title,
            "--vault",
            vault,
            "--format",
            "json",
        ]
        if tags:
            args.extend(["--tags", ",".join(tags)])
        completed = run_command(args, cwd=self.repo_root)
        payload = json.loads(completed.stdout or "{}")
        if not isinstance(payload, dict):
            raise SecretsRotationError("Resposta inesperada ao criar SSH Key no 1Password.")
        return payload

    def ssh_key_private_material(self, *, vault: str, item: str) -> str:
        payload = self.get_item_json(OpReference(raw="", vault=vault, item=item, section="", field=""))
        fields = payload.get("fields")
        if not isinstance(fields, list):
            raise SecretsRotationError(f"Item SSH Key invalido no 1Password: {vault}/{item}")
        for field in fields:
            if not isinstance(field, dict):
                continue
            if str(field.get("id", "")) == "private_key" or str(field.get("type", "")) == "SSHKEY":
                value = str(field.get("value", "")).strip()
                if value:
                    return value
        raise SecretsRotationError(f"private_key nao encontrada no item {vault}/{item}.")


class GitHubDriver:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def auth_status(self) -> str:
        completed = run_command(["gh", "auth", "status"], cwd=self.repo_root, check=False)
        return (completed.stdout or completed.stderr or "").strip()

    def api(self, endpoint: str, *, method: str = "GET") -> subprocess.CompletedProcess[str]:
        args = ["gh", "api", endpoint]
        if method != "GET":
            args.extend(["-X", method])
        return run_command(args, cwd=self.repo_root, check=False)

    def list_keys(self, *, publication_kind: str) -> tuple[bool, list[dict[str, Any]], str]:
        endpoint = "user/keys" if publication_kind == "authentication" else "user/ssh_signing_keys"
        completed = self.api(endpoint)
        if completed.returncode != 0:
            return False, [], (completed.stderr or completed.stdout or "").strip()
        payload = json.loads(completed.stdout or "[]")
        if not isinstance(payload, list):
            return False, [], "Resposta inesperada do GitHub."
        items = [item for item in payload if isinstance(item, dict)]
        return True, items, "ok"

    def add_key(self, *, public_key: str, title: str, publication_kind: str) -> dict[str, Any]:
        normalized = normalize_public_key(public_key)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".pub") as handle:
            handle.write(normalized + "\n")
            public_path = Path(handle.name)
        try:
            args = ["gh", "ssh-key", "add", str(public_path), "--title", title]
            if publication_kind == "signing":
                args.extend(["--type", "signing"])
            completed = run_command(args, cwd=self.repo_root)
        finally:
            if public_path.exists():
                public_path.unlink()
        return {
            "status": "added",
            "detail": (completed.stdout or completed.stderr or "").strip() or "gh ssh-key add ok",
        }

    def delete_key(self, *, publication_kind: str, key_id: int) -> None:
        endpoint = (
            f"user/keys/{key_id}"
            if publication_kind == "authentication"
            else f"user/ssh_signing_keys/{key_id}"
        )
        completed = self.api(endpoint, method="DELETE")
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise SecretsRotationError(f"Falha ao remover chave {key_id} do GitHub: {detail}")

    def validate_ssh_handshake(self) -> tuple[bool, str]:
        completed = run_command(
            [
                "ssh",
                "-T",
                "-o",
                "BatchMode=yes",
                "-o",
                "StrictHostKeyChecking=accept-new",
                "-o",
                "ConnectTimeout=10",
                "git@github.com",
            ],
            cwd=self.repo_root,
            check=False,
        )
        text = (completed.stderr or completed.stdout or "").strip()
        ok = "successfully authenticated" in text.lower()
        return ok, text or f"ssh exit={completed.returncode}"

    def validate_git_remote(self, remote: str) -> tuple[bool, str]:
        completed = run_command(["git", "ls-remote", remote], cwd=self.repo_root, check=False)
        text = (completed.stderr or completed.stdout or "").strip()
        return completed.returncode == 0, text or f"git ls-remote exit={completed.returncode}"


class GitLabDriver:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def auth_status(self) -> tuple[bool, str]:
        completed = run_command(["glab", "auth", "status"], cwd=self.repo_root, check=False)
        text = (completed.stdout or completed.stderr or "").strip()
        return completed.returncode == 0, text

    def rotate_token(self, token_name: str, *, user: str = "@me") -> tuple[bool, str]:
        completed = run_command(
            ["glab", "token", "rotate", "--user", user, "--output", "text", token_name],
            cwd=self.repo_root,
            check=False,
        )
        text = (completed.stdout or completed.stderr or "").strip()
        return completed.returncode == 0, text


class SopsAgeDriver:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def generate_age_key(self) -> tuple[str, str]:
        completed = run_command(["age-keygen"], cwd=self.repo_root)
        text = completed.stdout or completed.stderr
        secret = ""
        public = ""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# public key:"):
                public = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("AGE-SECRET-KEY-"):
                secret = stripped
        if not secret or not public:
            raise SecretsRotationError("Nao foi possivel gerar material age valido.")
        return secret, public

    def recipient_from_secret(self, secret_key: str) -> str:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as handle:
            handle.write(secret_key)
            handle.write("\n")
            secret_path = Path(handle.name)
        try:
            secret_path.chmod(0o600)
            completed = run_command(["age-keygen", "-y", str(secret_path)], cwd=self.repo_root)
            return completed.stdout.strip()
        finally:
            if secret_path.exists():
                secret_path.unlink()

    def update_sops_config_recipient(self, config_path: Path, new_recipient: str) -> None:
        content = config_path.read_text(encoding="utf-8")
        if "age1REPLACE_WITH_YOUR_PUBLIC_AGE_KEY" in content:
            content = content.replace("age1REPLACE_WITH_YOUR_PUBLIC_AGE_KEY", new_recipient)
        updated = AGE_RECIPIENT_LINE_RE.sub(rf"\1{new_recipient}", content)
        config_path.write_text(updated, encoding="utf-8", newline="\n")

    def rewrap_encrypted_artifact(self, path: Path, *, input_type: str, recipient: str) -> None:
        if not path.exists():
            return
        plain = run_command(
            ["sops", "--decrypt", "--input-type", input_type, "--output-type", input_type, str(path)],
            cwd=self.repo_root,
        ).stdout
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as handle:
            handle.write(plain)
            plain_path = Path(handle.name)
        try:
            run_command(
                [
                    "sops",
                    "--encrypt",
                    "--age",
                    recipient,
                    "--input-type",
                    input_type,
                    "--output-type",
                    input_type,
                    "--output",
                    str(path),
                    str(plain_path),
                ],
                cwd=self.repo_root,
            )
        finally:
            if plain_path.exists():
                plain_path.unlink()

    def write_encrypted_yaml(self, path: Path, *, recipient: str, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".yaml") as handle:
            yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
            plain_path = Path(handle.name)
        try:
            run_command(
                [
                    "sops",
                    "--encrypt",
                    "--age",
                    recipient,
                    "--input-type",
                    "yaml",
                    "--output-type",
                    "yaml",
                    "--output",
                    str(path),
                    str(plain_path),
                ],
                cwd=self.repo_root,
            )
        finally:
            if plain_path.exists():
                plain_path.unlink()


def current_hostname() -> str:
    return socket.gethostname().strip() or "unknown-host"


def current_timestamp_token() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def current_branch(repo_root: Path) -> str:
    completed = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    return completed.stdout.strip() or "unknown-branch"


def origin_remote(repo_root: Path) -> str:
    completed = run_command(["git", "remote", "get-url", "origin"], cwd=repo_root, check=False)
    return (completed.stdout or "").strip() or "origin"
