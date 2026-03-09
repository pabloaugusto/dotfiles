from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONTROL_PLANE_ROOT = Path("config/ai")
ENV_PREFIX = "env://"
OP_PREFIX = "op://"
OP_REF_RE = re.compile(r"^op://(?P<body>.+)$")
_OP_ITEM_CACHE: dict[tuple[str, str], dict[str, str]] = {}
_OP_VALUE_CACHE: dict[str, str] = {}
_OP_RATELIMIT_CACHE: dict[str, Any] | None = None


class AiControlPlaneError(RuntimeError):
    """Raised when the AI control plane cannot be loaded or resolved safely."""


@dataclass(frozen=True)
class AtlassianPlatformDefinition:
    enabled: bool
    provider: str
    auth_mode: str
    site_url_spec: str
    email_spec: str
    token_spec: str
    service_account_spec: str
    cloud_id_spec: str
    jira_enabled: bool
    jira_project_key_spec: str
    confluence_enabled: bool
    confluence_space_key_spec: str


@dataclass(frozen=True)
class ResolvedAtlassianPlatform:
    enabled: bool
    provider: str
    auth_mode: str
    site_url: str
    email: str
    token: str
    service_account: str
    cloud_id: str
    jira_enabled: bool
    jira_project_key: str
    confluence_enabled: bool
    confluence_space_key: str


@dataclass(frozen=True)
class OpReference:
    raw: str
    vault: str
    item: str
    section: str
    field: str


@dataclass(frozen=True)
class AiControlPlane:
    repo_root: Path
    config_root: Path
    platforms_path: Path
    platforms_local_path: Path
    agents_path: Path
    agents_local_path: Path
    agent_operations_path: Path
    agent_operations_local_path: Path
    contracts_path: Path
    contracts_local_path: Path
    platforms_payload: dict[str, Any]
    agents_payload: dict[str, Any]
    agent_operations_payload: dict[str, Any]
    contracts_payload: dict[str, Any]

    def roles_payload(self) -> dict[str, Any]:
        roles = self.agents_payload.get("roles") or {}
        if not isinstance(roles, dict):
            raise AiControlPlaneError("config/ai/agents.yaml precisa conter roles como mapa.")
        return roles

    def enabled_roles(self) -> list[str]:
        roles = self.roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and bool(entry.get("enabled", False))
        )

    def required_roles(self) -> list[str]:
        roles = self.roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and bool(entry.get("required", False))
        )

    def disabled_roles(self) -> list[str]:
        roles = self.roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and not bool(entry.get("enabled", False))
        )

    def agent_operation_roles_payload(self) -> dict[str, Any]:
        roles = self.agent_operations_payload.get("roles") or {}
        if not isinstance(roles, dict):
            raise AiControlPlaneError(
                "config/ai/agent-operations.yaml precisa conter roles como mapa."
            )
        return roles

    def roles_with_operation_contracts(self) -> list[str]:
        return sorted(
            role_id
            for role_id, entry in self.agent_operation_roles_payload().items()
            if isinstance(role_id, str) and isinstance(entry, dict)
        )

    def roles_missing_operation_contracts(self) -> list[str]:
        operation_roles = set(self.roles_with_operation_contracts())
        return sorted(role_id for role_id in self.roles_payload() if role_id not in operation_roles)

    def operation_contracts_without_roles(self) -> list[str]:
        declared_roles = set(self.roles_payload())
        return sorted(
            role_id
            for role_id in self.agent_operation_roles_payload()
            if role_id not in declared_roles
        )

    def effective_workflow_columns(self) -> list[str]:
        workflow = ensure_mapping(
            self.contracts_payload.get("workflow"),
            "config/ai/contracts.yaml workflow",
        )
        always_enabled = ensure_string_list(
            workflow.get("always_enabled_columns"),
            "config/ai/contracts.yaml workflow.always_enabled_columns",
        )
        columns = list(always_enabled)
        optional_columns = workflow.get("optional_columns") or []
        if not isinstance(optional_columns, list):
            raise AiControlPlaneError(
                "config/ai/contracts.yaml workflow.optional_columns precisa ser lista."
            )
        enabled_roles = set(self.enabled_roles())
        for entry in optional_columns:
            if not isinstance(entry, dict):
                raise AiControlPlaneError(
                    "config/ai/contracts.yaml workflow.optional_columns aceita apenas mapas."
                )
            name = str(entry.get("name", "")).strip()
            enabled_when_role = str(entry.get("enabled_when_role", "")).strip()
            if not name:
                continue
            if enabled_when_role and enabled_when_role not in enabled_roles:
                continue
            columns.append(name)
        return columns

    def atlassian_definition(self) -> AtlassianPlatformDefinition:
        platforms = ensure_mapping(
            self.platforms_payload.get("platforms"),
            "config/ai/platforms.yaml platforms",
        )
        atlassian = ensure_mapping(
            platforms.get("atlassian"),
            "config/ai/platforms.yaml platforms.atlassian",
        )
        auth = ensure_mapping(
            atlassian.get("auth"),
            "config/ai/platforms.yaml platforms.atlassian.auth",
        )
        jira = ensure_mapping(
            atlassian.get("jira"),
            "config/ai/platforms.yaml platforms.atlassian.jira",
        )
        confluence = ensure_mapping(
            atlassian.get("confluence"),
            "config/ai/platforms.yaml platforms.atlassian.confluence",
        )
        return AtlassianPlatformDefinition(
            enabled=bool(atlassian.get("enabled", False)),
            provider=str(atlassian.get("provider", "")).strip(),
            auth_mode=str(auth.get("mode", "")).strip(),
            site_url_spec=str(auth.get("site_url", "")).strip(),
            email_spec=str(auth.get("email", "")).strip(),
            token_spec=str(auth.get("token", "")).strip(),
            service_account_spec=str(auth.get("service_account", "")).strip(),
            cloud_id_spec=str(auth.get("cloud_id", "")).strip(),
            jira_enabled=bool(jira.get("enabled", False)),
            jira_project_key_spec=str(jira.get("project_key", "")).strip(),
            confluence_enabled=bool(confluence.get("enabled", False)),
            confluence_space_key_spec=str(confluence.get("space_key", "")).strip(),
        )


def run_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise AiControlPlaneError(
            f"Command failed ({' '.join(args)}): {detail or f'exit={completed.returncode}'}"
        )
    return completed


def is_op_rate_limited(detail: str) -> bool:
    normalized = (detail or "").strip().lower()
    return "too many requests" in normalized or "rate-limited" in normalized or "429" in normalized


def run_op_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    max_attempts: int = 3,
    initial_delay_seconds: int = 5,
) -> subprocess.CompletedProcess[str]:
    attempt = 1
    delay = initial_delay_seconds
    while True:
        completed = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            return completed
        detail = (completed.stderr or completed.stdout or "").strip()
        if attempt >= max_attempts or not is_op_rate_limited(detail):
            if cwd is not None and args[:3] != ["op", "service-account", "ratelimit"]:
                try:
                    ratelimit = service_account_ratelimit_payload(cwd, force_refresh=True)
                except AiControlPlaneError:
                    ratelimit = {}
                account_row = ratelimit.get("account_read_write") or {}
                if bool(ratelimit.get("account_read_write_exhausted", False)):
                    raise AiControlPlaneError(
                        "1Password service account rate limit esgotado: "
                        f"account.read_write remaining={account_row.get('remaining', 0)}, "
                        f"reset={account_row.get('reset_human', 'n/a')}."
                    )
            raise AiControlPlaneError(
                f"Command failed ({' '.join(args)}): {detail or f'exit={completed.returncode}'}"
            )
        time.sleep(delay)
        attempt += 1
        delay *= 2


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    completed = run_command(["git", "rev-parse", "--show-toplevel"])
    return Path(completed.stdout.strip()).resolve()


def ensure_mapping(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AiControlPlaneError(f"{label} precisa ser um mapa.")
    return payload


def ensure_string_list(payload: Any, label: str) -> list[str]:
    if not isinstance(payload, list):
        raise AiControlPlaneError(f"{label} precisa ser lista.")
    values: list[str] = []
    for entry in payload:
        if not isinstance(entry, str):
            raise AiControlPlaneError(f"{label} aceita apenas strings.")
        values.append(entry.strip())
    return values


def load_yaml_map(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AiControlPlaneError(f"Arquivo YAML nao encontrado: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise AiControlPlaneError(f"YAML invalido em {path}: esperado objeto raiz.")
    return payload


def overlay_path_for(base_path: Path) -> Path:
    return base_path.with_name(f"{base_path.stem}.local{base_path.suffix}")


def merge_maps(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, override_value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, Mapping):
            merged[key] = merge_maps(base_value, override_value)
            continue
        merged[key] = override_value
    return merged


def load_yaml_map_with_optional_overlay(base_path: Path) -> tuple[dict[str, Any], Path]:
    payload = load_yaml_map(base_path)
    local_path = overlay_path_for(base_path)
    if not local_path.exists():
        return payload, local_path
    return merge_maps(payload, load_yaml_map(local_path)), local_path


def load_ai_control_plane(repo_root: str | Path | None = None) -> AiControlPlane:
    resolved_repo_root = resolve_repo_root(repo_root)
    config_root = (resolved_repo_root / DEFAULT_CONTROL_PLANE_ROOT).resolve()
    platforms_path = config_root / "platforms.yaml"
    agents_path = config_root / "agents.yaml"
    agent_operations_path = config_root / "agent-operations.yaml"
    contracts_path = config_root / "contracts.yaml"
    platforms_payload, platforms_local_path = load_yaml_map_with_optional_overlay(platforms_path)
    agents_payload, agents_local_path = load_yaml_map_with_optional_overlay(agents_path)
    agent_operations_payload, agent_operations_local_path = load_yaml_map_with_optional_overlay(
        agent_operations_path
    )
    contracts_payload, contracts_local_path = load_yaml_map_with_optional_overlay(contracts_path)
    return AiControlPlane(
        repo_root=resolved_repo_root,
        config_root=config_root,
        platforms_path=platforms_path,
        platforms_local_path=platforms_local_path,
        agents_path=agents_path,
        agents_local_path=agents_local_path,
        agent_operations_path=agent_operations_path,
        agent_operations_local_path=agent_operations_local_path,
        contracts_path=contracts_path,
        contracts_local_path=contracts_local_path,
        platforms_payload=platforms_payload,
        agents_payload=agents_payload,
        agent_operations_payload=agent_operations_payload,
        contracts_payload=contracts_payload,
    )


def normalize_url(value: str) -> str:
    return value.strip().rstrip("/")


def clear_secret_resolver_cache() -> None:
    global _OP_RATELIMIT_CACHE
    _OP_ITEM_CACHE.clear()
    _OP_VALUE_CACHE.clear()
    _OP_RATELIMIT_CACHE = None


def parse_op_ref(op_ref: str) -> OpReference:
    match = OP_REF_RE.match((op_ref or "").strip())
    if not match:
        raise AiControlPlaneError(f"Ref do 1Password invalida: {op_ref}")
    body = match.group("body").strip("/")
    parts = [chunk for chunk in body.split("/") if chunk]
    if len(parts) < 3:
        raise AiControlPlaneError(f"Ref do 1Password incompleta: {op_ref}")
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


def op_field_cache_key(section: str, field_name: str) -> str:
    return f"{section.strip().lower()}::{field_name.strip().lower()}"


def format_reset_seconds(raw_seconds: Any) -> str:
    try:
        seconds = int(raw_seconds)
    except (TypeError, ValueError):
        return "n/a"
    if seconds <= 0:
        return "now"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def service_account_ratelimit_payload(
    repo_root: str | Path | None = None,
    *,
    force_refresh: bool = False,
) -> dict[str, Any]:
    global _OP_RATELIMIT_CACHE
    if _OP_RATELIMIT_CACHE is not None and not force_refresh:
        return dict(_OP_RATELIMIT_CACHE)

    resolved_repo_root = resolve_repo_root(repo_root)
    completed = run_command(
        ["op", "service-account", "ratelimit", "--format", "json"],
        cwd=resolved_repo_root,
    )
    try:
        raw_payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise AiControlPlaneError("op service-account ratelimit retornou JSON invalido.") from exc
    if not isinstance(raw_payload, list):
        raise AiControlPlaneError("op service-account ratelimit retornou payload inesperado.")

    rows: list[dict[str, Any]] = []
    by_key: dict[str, dict[str, Any]] = {}
    for entry in raw_payload:
        if not isinstance(entry, dict):
            continue
        normalized = {
            "type": str(entry.get("type", "")).strip(),
            "action": str(entry.get("action", "")).strip(),
            "limit": int(entry.get("limit", 0) or 0),
            "used": int(entry.get("used", 0) or 0),
            "remaining": int(entry.get("remaining", 0) or 0),
            "reset_seconds": int(entry.get("reset", 0) or 0),
        }
        normalized["reset_human"] = format_reset_seconds(normalized["reset_seconds"])
        rows.append(normalized)
        by_key[f"{normalized['type']}:{normalized['action']}"] = normalized

    account_row = by_key.get("account:read_write", {})
    payload = {
        "rows": rows,
        "by_key": by_key,
        "account_read_write": account_row,
        "account_read_write_exhausted": bool(account_row) and int(account_row.get("remaining", 0)) <= 0,
    }
    _OP_RATELIMIT_CACHE = dict(payload)
    return payload


def ensure_service_account_capacity(repo_root: Path) -> None:
    payload = service_account_ratelimit_payload(repo_root)
    if not bool(payload.get("account_read_write_exhausted", False)):
        return
    account_row = payload.get("account_read_write") or {}
    raise AiControlPlaneError(
        "1Password service account rate limit esgotado: "
        f"account.read_write remaining={account_row.get('remaining', 0)}, "
        f"reset={account_row.get('reset_human', 'n/a')}."
    )


def prime_op_ref_cache(raw_specs: list[str], *, repo_root: Path) -> None:
    refs = [spec.strip() for spec in raw_specs if spec.strip().startswith(OP_PREFIX)]
    pending_refs = [ref for ref in refs if ref not in _OP_VALUE_CACHE]
    if not pending_refs:
        return
    ensure_service_account_capacity(repo_root)

    env_names = [f"AI_CP_SECRET_{index}" for index in range(len(pending_refs))]
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".env",
        delete=False,
    ) as handle:
        env_file = Path(handle.name)
        for env_name, ref in zip(env_names, pending_refs, strict=False):
            handle.write(f"{env_name}={ref}\n")

    helper_code = (
        "import json, os, sys; "
        "print(json.dumps({name: os.environ.get(name, '') for name in sys.argv[1:]}))"
    )
    try:
        completed = run_op_command(
            [
                "op",
                "run",
                "--env-file",
                str(env_file),
                "--",
                sys.executable,
                "-c",
                helper_code,
                *env_names,
            ],
            cwd=repo_root,
        )
    except AiControlPlaneError:
        if env_file.exists():
            env_file.unlink()
        raise
    finally:
        if env_file.exists():
            env_file.unlink()

    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AiControlPlaneError("op run retornou JSON invalido ao resolver secrets em lote.") from exc
    if not isinstance(payload, dict):
        raise AiControlPlaneError("op run retornou payload invalido ao resolver secrets em lote.")

    for env_name, ref in zip(env_names, pending_refs, strict=False):
        resolved = str(payload.get(env_name, "") or "").strip()
        if resolved:
            _OP_VALUE_CACHE[ref] = resolved


def load_op_item_fields(op_ref: OpReference, *, repo_root: Path) -> dict[str, str]:
    cache_key = (op_ref.vault, op_ref.item)
    cached = _OP_ITEM_CACHE.get(cache_key)
    if cached is not None:
        return cached
    ensure_service_account_capacity(repo_root)

    completed = run_op_command(
        [
            "op",
            "item",
            "get",
            op_ref.item,
            "--vault",
            op_ref.vault,
            "--format",
            "json",
        ],
        cwd=repo_root,
    )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AiControlPlaneError(
            f"Item do 1Password retornou JSON invalido para {op_ref.vault}/{op_ref.item}."
        ) from exc

    fields = payload.get("fields", [])
    if not isinstance(fields, list):
        raise AiControlPlaneError(
            f"Item do 1Password sem lista de fields para {op_ref.vault}/{op_ref.item}."
        )

    result: dict[str, str] = {}
    for entry in fields:
        if not isinstance(entry, dict):
            continue
        raw_value = entry.get("value")
        value = "" if raw_value is None else str(raw_value).strip()
        section_payload = entry.get("section")
        section_name = ""
        if isinstance(section_payload, dict):
            section_name = str(
                section_payload.get("label", "") or section_payload.get("name", "")
            ).strip()
        for candidate in (entry.get("id"), entry.get("label")):
            name = str(candidate or "").strip()
            if not name:
                continue
            result[op_field_cache_key(section_name, name)] = value
            if not section_name:
                result[op_field_cache_key("", name)] = value

    _OP_ITEM_CACHE[cache_key] = result
    return result


def resolve_op_value(op_ref_raw: str, *, repo_root: Path, allow_empty: bool = False) -> str:
    cached = _OP_VALUE_CACHE.get(op_ref_raw)
    if cached is not None:
        if cached or allow_empty:
            return cached
        raise AiControlPlaneError(f"Ref do 1Password vazia para a control plane: {op_ref_raw}")

    op_ref = parse_op_ref(op_ref_raw)
    cached_fields = load_op_item_fields(op_ref, repo_root=repo_root)
    candidates = [op_field_cache_key(op_ref.section, op_ref.field)]
    if op_ref.section:
        candidates.append(op_field_cache_key("", op_ref.field))
    for key in candidates:
        if key in cached_fields:
            resolved = cached_fields[key]
            if resolved or allow_empty:
                return resolved
            raise AiControlPlaneError(f"Ref do 1Password vazia para a control plane: {op_ref_raw}")

    ensure_service_account_capacity(repo_root)
    resolved = run_op_command(["op", "read", op_ref_raw], cwd=repo_root).stdout.strip()
    if resolved or allow_empty:
        return resolved
    raise AiControlPlaneError(f"Ref do 1Password vazia para a control plane: {op_ref_raw}")


def resolve_value_spec(raw_value: str, *, repo_root: Path, allow_empty: bool = False) -> str:
    value = str(raw_value or "").strip()
    if not value:
        if allow_empty:
            return ""
        raise AiControlPlaneError("Valor obrigatorio ausente na control plane.")
    if value.startswith(ENV_PREFIX):
        env_name = value.removeprefix(ENV_PREFIX).strip()
        resolved = os.getenv(env_name, "").strip()
        if resolved or allow_empty:
            return resolved
        raise AiControlPlaneError(
            f"Variavel de ambiente obrigatoria ausente para a control plane: {env_name}"
        )
    if value.startswith(OP_PREFIX):
        return resolve_op_value(value, repo_root=repo_root, allow_empty=allow_empty)
    return value


def resolve_atlassian_platform(
    definition: AtlassianPlatformDefinition,
    *,
    repo_root: Path,
    site_url_override: str = "",
) -> ResolvedAtlassianPlatform:
    site_url_spec = site_url_override.strip() or definition.site_url_spec
    prime_op_ref_cache(
        [
            site_url_spec,
            definition.email_spec,
            definition.token_spec,
            definition.service_account_spec,
            definition.cloud_id_spec,
            definition.jira_project_key_spec,
            definition.confluence_space_key_spec,
        ],
        repo_root=repo_root,
    )
    site_url = normalize_url(resolve_value_spec(site_url_spec, repo_root=repo_root))
    email = resolve_value_spec(definition.email_spec, repo_root=repo_root)
    token = resolve_value_spec(definition.token_spec, repo_root=repo_root)
    service_account = resolve_value_spec(
        definition.service_account_spec,
        repo_root=repo_root,
        allow_empty=True,
    )
    cloud_id = resolve_value_spec(
        definition.cloud_id_spec,
        repo_root=repo_root,
        allow_empty=True,
    )
    jira_project_key = resolve_value_spec(
        definition.jira_project_key_spec,
        repo_root=repo_root,
        allow_empty=not definition.jira_enabled,
    )
    confluence_space_key = resolve_value_spec(
        definition.confluence_space_key_spec,
        repo_root=repo_root,
        allow_empty=not definition.confluence_enabled,
    )
    return ResolvedAtlassianPlatform(
        enabled=definition.enabled,
        provider=definition.provider,
        auth_mode=definition.auth_mode,
        site_url=site_url,
        email=email,
        token=token,
        service_account=service_account,
        cloud_id=cloud_id,
        jira_enabled=definition.jira_enabled,
        jira_project_key=jira_project_key,
        confluence_enabled=definition.confluence_enabled,
        confluence_space_key=confluence_space_key,
    )


def summary_payload(
    repo_root: str | Path | None = None,
    *,
    control_plane: AiControlPlane | None = None,
) -> dict[str, Any]:
    loaded = control_plane or load_ai_control_plane(repo_root)
    definition = loaded.atlassian_definition()
    return {
        "repo_root": str(loaded.repo_root),
        "config_root": str(loaded.config_root),
        "platforms_path": str(loaded.platforms_path),
        "platforms_local_path": str(loaded.platforms_local_path),
        "agents_path": str(loaded.agents_path),
        "agents_local_path": str(loaded.agents_local_path),
        "agent_operations_path": str(loaded.agent_operations_path),
        "agent_operations_local_path": str(loaded.agent_operations_local_path),
        "contracts_path": str(loaded.contracts_path),
        "contracts_local_path": str(loaded.contracts_local_path),
        "local_overrides": {
            "platforms": loaded.platforms_local_path.exists(),
            "agents": loaded.agents_local_path.exists(),
            "agent_operations": loaded.agent_operations_local_path.exists(),
            "contracts": loaded.contracts_local_path.exists(),
        },
        "enabled_roles": loaded.enabled_roles(),
        "required_roles": loaded.required_roles(),
        "disabled_roles": loaded.disabled_roles(),
        "role_operation_coverage": {
            "covered_roles": loaded.roles_with_operation_contracts(),
            "missing_roles": loaded.roles_missing_operation_contracts(),
            "orphan_contracts": loaded.operation_contracts_without_roles(),
        },
        "workflow_columns": loaded.effective_workflow_columns(),
        "platforms": {
            "atlassian": {
                "enabled": definition.enabled,
                "provider": definition.provider,
                "auth_mode": definition.auth_mode,
                "uses_env_site_url": definition.site_url_spec.startswith(ENV_PREFIX),
                "jira_enabled": definition.jira_enabled,
                "confluence_enabled": definition.confluence_enabled,
            }
        },
    }
