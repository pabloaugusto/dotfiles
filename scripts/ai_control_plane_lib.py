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
from urllib.parse import quote

import yaml

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for Python < 3.11
    tomllib = None  # type: ignore[assignment]

DEFAULT_CONTROL_PLANE_ROOT = Path("config/ai")
ENV_PREFIX = "env://"
OP_PREFIX = "op://"
OP_REF_RE = re.compile(r"^op://(?P<body>.+)$")
_OP_ITEM_CACHE: dict[tuple[str, str], dict[str, str]] = {}
_OP_VALUE_CACHE: dict[str, str] = {}
_OP_RATELIMIT_CACHE: dict[str, Any] | None = None
_REPO_WEB_CONTEXT_CACHE: dict[str, RepoWebContext] = {}
_TRACKED_REPO_FILES_CACHE: dict[str, set[str]] = {}


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
class RepoWebContext:
    github_base_url: str
    default_branch: str


@dataclass(frozen=True)
class AiControlPlane:
    repo_root: Path
    config_root: Path
    platforms_path: Path
    platforms_local_path: Path
    agents_path: Path
    agents_local_path: Path
    agent_enablement_path: Path
    agent_enablement_local_path: Path
    agent_operations_path: Path
    agent_operations_local_path: Path
    contracts_path: Path
    contracts_local_path: Path
    agent_runtime_path: Path
    agent_runtime_local_path: Path
    platforms_payload: dict[str, Any]
    agents_payload: dict[str, Any]
    agent_enablement_payload: dict[str, Any]
    agent_operations_payload: dict[str, Any]
    contracts_payload: dict[str, Any]
    agent_runtime_payload: dict[str, Any]

    def roles_payload(self) -> dict[str, Any]:
        roles = self.agents_payload.get("roles") or {}
        if not isinstance(roles, dict):
            raise AiControlPlaneError("config/ai/agents.yaml precisa conter roles como mapa.")
        return roles

    def agent_enablement_roles_payload(self) -> dict[str, Any]:
        roles = self.agent_enablement_payload.get("roles") or {}
        if not isinstance(roles, dict):
            raise AiControlPlaneError(
                "config/ai/agent-enablement.yaml precisa conter roles como mapa."
            )
        return roles

    def role_enablement_overrides(self) -> dict[str, bool]:
        roles = self.roles_payload()
        overrides: dict[str, bool] = {}
        unknown_roles: list[str] = []
        for role_id, entry in self.agent_enablement_roles_payload().items():
            if role_id not in roles:
                unknown_roles.append(str(role_id))
                continue
            if not isinstance(entry, dict):
                raise AiControlPlaneError(
                    "config/ai/agent-enablement.yaml roles aceita apenas mapas por agente."
                )
            enabled = entry.get("enabled")
            if not isinstance(enabled, bool):
                raise AiControlPlaneError(
                    "config/ai/agent-enablement.yaml roles.<agent>.enabled precisa ser booleano."
                )
            overrides[str(role_id)] = enabled
        if unknown_roles:
            raise AiControlPlaneError(
                "config/ai/agent-enablement.yaml contem roles desconhecidos: "
                + ", ".join(sorted(unknown_roles))
            )
        return overrides

    def effective_roles_payload(self) -> dict[str, dict[str, Any]]:
        overrides = self.role_enablement_overrides()
        effective: dict[str, dict[str, Any]] = {}
        for role_id, entry in self.roles_payload().items():
            if not isinstance(role_id, str) or not isinstance(entry, dict):
                continue
            effective_entry = dict(entry)
            if role_id in overrides:
                effective_entry["enabled"] = overrides[role_id]
            effective[role_id] = effective_entry
        return effective

    def declared_enablement_roles(self) -> list[str]:
        return sorted(str(role_id) for role_id in self.agent_enablement_roles_payload())

    def enablement_overridden_roles(self) -> list[str]:
        roles = self.roles_payload()
        overrides = self.role_enablement_overrides()
        return sorted(
            role_id
            for role_id, enabled in overrides.items()
            if bool(roles.get(role_id, {}).get("enabled", False)) != enabled
        )

    def enabled_roles(self) -> list[str]:
        roles = self.effective_roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and bool(entry.get("enabled", False))
        )

    def required_roles(self) -> list[str]:
        roles = self.effective_roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and bool(entry.get("required", False))
        )

    def required_roles_disabled(self) -> list[str]:
        roles = self.effective_roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and bool(entry.get("required", False))
            and not bool(entry.get("enabled", False))
        )

    def disabled_roles(self) -> list[str]:
        roles = self.effective_roles_payload()
        return sorted(
            role_id
            for role_id, entry in roles.items()
            if isinstance(role_id, str)
            and isinstance(entry, dict)
            and not bool(entry.get("enabled", False))
        )

    def registry_agents_enablement_payload(self) -> dict[str, Any]:
        registry_agents = self.agent_enablement_payload.get("registry_agents") or {}
        if not isinstance(registry_agents, dict):
            raise AiControlPlaneError(
                "config/ai/agent-enablement.yaml precisa conter registry_agents como mapa."
            )
        return registry_agents

    def registry_agents_enabled_by_default(self) -> bool:
        defaults = self.agent_enablement_payload.get("defaults") or {}
        if defaults in ({}, None):
            return True
        if not isinstance(defaults, dict):
            raise AiControlPlaneError(
                "config/ai/agent-enablement.yaml defaults precisa ser mapa quando definido."
            )
        raw_value = defaults.get("registry_agents_enabled_by_default", True)
        if not isinstance(raw_value, bool):
            raise AiControlPlaneError(
                "config/ai/agent-enablement.yaml defaults.registry_agents_enabled_by_default precisa ser booleano."
            )
        return raw_value

    def effective_registry_agents_payload(self) -> dict[str, dict[str, Any]]:
        registry_dir = (self.repo_root / ".agents" / "registry").resolve()
        registry_agents = sorted(candidate.stem for candidate in registry_dir.glob("*.toml"))
        overrides = self.registry_agents_enablement_payload()
        effective_roles = self.effective_roles_payload()
        unknown_agents = [str(agent_id) for agent_id in overrides if agent_id not in registry_agents]
        if unknown_agents:
            raise AiControlPlaneError(
                "config/ai/agent-enablement.yaml contem agentes declarativos desconhecidos: "
                + ", ".join(sorted(unknown_agents))
            )
        effective: dict[str, dict[str, Any]] = {}
        for agent_id in registry_agents:
            if agent_id in effective_roles:
                enabled = bool(effective_roles[agent_id].get("enabled", False))
            else:
                enabled = self.registry_agents_enabled_by_default()
            override_entry = overrides.get(agent_id)
            if override_entry is not None:
                if not isinstance(override_entry, dict):
                    raise AiControlPlaneError(
                        "config/ai/agent-enablement.yaml registry_agents aceita apenas mapas por agente."
                    )
                raw_enabled = override_entry.get("enabled")
                if not isinstance(raw_enabled, bool):
                    raise AiControlPlaneError(
                        "config/ai/agent-enablement.yaml registry_agents.<agent>.enabled precisa ser booleano."
                    )
                if agent_id in effective_roles and raw_enabled != enabled:
                    raise AiControlPlaneError(
                        "config/ai/agent-enablement.yaml registry_agents nao pode divergir do enablement da role para agentes com role correspondente: "
                        f"{agent_id}"
                    )
                enabled = raw_enabled
            effective[agent_id] = {"enabled": enabled}
        return effective

    def enabled_registry_agents(self) -> list[str]:
        registry_agents = self.effective_registry_agents_payload()
        return sorted(
            agent_id
            for agent_id, entry in registry_agents.items()
            if isinstance(agent_id, str)
            and isinstance(entry, dict)
            and bool(entry.get("enabled", False))
        )

    def disabled_registry_agents(self) -> list[str]:
        registry_agents = self.effective_registry_agents_payload()
        return sorted(
            agent_id
            for agent_id, entry in registry_agents.items()
            if isinstance(agent_id, str)
            and isinstance(entry, dict)
            and not bool(entry.get("enabled", False))
        )

    def declared_registry_agents(self) -> list[str]:
        registry_dir = (self.repo_root / ".agents" / "registry").resolve()
        return sorted(candidate.stem for candidate in registry_dir.glob("*.toml"))

    def registry_agent_display_names(self) -> dict[str, str]:
        registry_dir = (self.repo_root / ".agents" / "registry").resolve()
        display_names: dict[str, str] = {}
        for candidate in sorted(registry_dir.glob("*.toml")):
            payload = _load_toml(candidate)
            agent_id = str(payload.get("id", "")).strip() or candidate.stem
            display_name = str(payload.get("display_name", "")).strip()
            if agent_id and display_name:
                display_names[agent_id] = display_name
        return display_names

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

    def agent_runtime_roles_payload(self) -> dict[str, Any]:
        roles = self.agent_runtime_payload.get("roles") or {}
        if not isinstance(roles, dict):
            raise AiControlPlaneError(
                "config/ai/agent-runtime.yaml precisa conter roles como mapa."
            )
        return roles

    def agent_runtime_registry_agents_payload(self) -> dict[str, Any]:
        registry_agents = self.agent_runtime_payload.get("registry_agents") or {}
        if not isinstance(registry_agents, dict):
            raise AiControlPlaneError(
                "config/ai/agent-runtime.yaml precisa conter registry_agents como mapa."
            )
        return registry_agents

    def agent_runtime_policies_payload(self) -> dict[str, Any]:
        policies = self.agent_runtime_payload.get("policies") or {}
        if not isinstance(policies, dict):
            raise AiControlPlaneError(
                "config/ai/agent-runtime.yaml precisa conter policies como mapa."
            )
        return policies

    def runtime_status_allowlist(self, policy_name: str) -> list[str]:
        policies = self.agent_runtime_policies_payload()
        default_policies = {
            "enabled_role_statuses": ["operational", "consultive"],
            "required_role_statuses": ["operational", "consultive"],
            "enabled_registry_statuses": ["operational", "consultive"],
            "chat_owner_statuses": ["operational", "consultive"],
            "chat_name_fallback_order": ["chat_alias", "display_name", "technical_id"],
        }
        payload = policies.get(policy_name, default_policies.get(policy_name, []))
        return ensure_string_list(
            payload,
            f"config/ai/agent-runtime.yaml policies.{policy_name}",
        )

    def chat_name_fallback_order(self) -> list[str]:
        return self.runtime_status_allowlist("chat_name_fallback_order")

    def role_runtime_entry(self, role_id: str) -> dict[str, Any]:
        entry = self.agent_runtime_roles_payload().get(role_id) or {}
        return entry if isinstance(entry, dict) else {}

    def registry_agent_runtime_entry(self, agent_id: str) -> dict[str, Any]:
        entry = self.agent_runtime_registry_agents_payload().get(agent_id) or {}
        return entry if isinstance(entry, dict) else {}

    def role_runtime_status(self, role_id: str) -> str:
        return str(self.role_runtime_entry(role_id).get("status", "")).strip()

    def registry_agent_runtime_status(self, agent_id: str) -> str:
        status = str(self.registry_agent_runtime_entry(agent_id).get("status", "")).strip()
        if status:
            return status
        return self.role_runtime_status(agent_id)

    def roles_with_runtime_contracts(self) -> list[str]:
        return sorted(
            role_id
            for role_id, entry in self.agent_runtime_roles_payload().items()
            if isinstance(role_id, str) and isinstance(entry, dict)
        )

    def roles_missing_runtime_contracts(self) -> list[str]:
        runtime_roles = set(self.roles_with_runtime_contracts())
        return sorted(role_id for role_id in self.roles_payload() if role_id not in runtime_roles)

    def runtime_contracts_without_roles(self) -> list[str]:
        declared_roles = set(self.roles_payload())
        return sorted(
            role_id
            for role_id in self.agent_runtime_roles_payload()
            if role_id not in declared_roles
        )

    def registry_agents_with_runtime_contracts(self) -> list[str]:
        declared_agents = set(self.declared_registry_agents())
        covered = {
            agent_id
            for agent_id, entry in self.agent_runtime_registry_agents_payload().items()
            if isinstance(agent_id, str) and isinstance(entry, dict)
        }
        covered.update(
            role_id for role_id in self.roles_with_runtime_contracts() if role_id in declared_agents
        )
        return sorted(covered)

    def registry_agents_missing_runtime_contracts(self) -> list[str]:
        runtime_registry_agents = set(self.registry_agents_with_runtime_contracts())
        return sorted(
            agent_id
            for agent_id in self.declared_registry_agents()
            if agent_id not in runtime_registry_agents
        )

    def runtime_contracts_without_registry_agents(self) -> list[str]:
        declared_agents = set(self.declared_registry_agents())
        return sorted(
            agent_id
            for agent_id in self.agent_runtime_registry_agents_payload()
            if agent_id not in declared_agents
        )

    def _is_runtime_status_allowed(self, status: str, policy_name: str) -> bool:
        return status.strip() in set(self.runtime_status_allowlist(policy_name))

    def enabled_roles_without_operational_runtime(self) -> list[str]:
        return sorted(
            role_id
            for role_id in self.enabled_roles()
            if not self._is_runtime_status_allowed(
                self.role_runtime_status(role_id),
                "enabled_role_statuses",
            )
        )

    def required_roles_without_operational_runtime(self) -> list[str]:
        return sorted(
            role_id
            for role_id in self.required_roles()
            if not self._is_runtime_status_allowed(
                self.role_runtime_status(role_id),
                "required_role_statuses",
            )
        )

    def enabled_registry_agents_without_operational_runtime(self) -> list[str]:
        return sorted(
            agent_id
            for agent_id in self.enabled_registry_agents()
            if not self._is_runtime_status_allowed(
                self.registry_agent_runtime_status(agent_id),
                "enabled_registry_statuses",
            )
        )

    def chat_owner_capable_roles(self) -> list[str]:
        return sorted(
            role_id
            for role_id in self.roles_with_runtime_contracts()
            if bool(self.role_runtime_entry(role_id).get("chat_owner_supported", False))
            and self._is_runtime_status_allowed(
                self.role_runtime_status(role_id),
                "chat_owner_statuses",
            )
        )

    def chat_owner_capable_registry_agents(self) -> list[str]:
        return sorted(
            agent_id
            for agent_id in self.registry_agents_with_runtime_contracts()
            if bool(self.registry_agent_runtime_entry(agent_id).get("chat_owner_supported", False))
            and self._is_runtime_status_allowed(
                self.registry_agent_runtime_status(agent_id),
                "chat_owner_statuses",
            )
        )

    def formal_name_for_agent(self, agent_id: str) -> str:
        role_entry = self.roles_payload().get(agent_id)
        if isinstance(role_entry, dict):
            display_name = str(role_entry.get("display_name", "")).strip()
            if display_name:
                return display_name
        return self.registry_agent_display_names().get(agent_id, "")

    def chat_alias_for_agent(self, agent_id: str) -> str:
        role_entry = self.role_runtime_entry(agent_id)
        if role_entry:
            return str(role_entry.get("chat_alias", "")).strip()
        registry_entry = self.registry_agent_runtime_entry(agent_id)
        return str(registry_entry.get("chat_alias", "")).strip()

    def visible_name_for_agent(
        self,
        agent_id: str,
        *,
        order: list[str] | None = None,
    ) -> str:
        fallback_order = order or self.chat_name_fallback_order()
        candidate_values = {
            "chat_alias": self.chat_alias_for_agent(agent_id),
            "display_name": self.formal_name_for_agent(agent_id),
            "technical_id": str(agent_id).strip(),
        }
        for key in fallback_order:
            value = candidate_values.get(key, "").strip()
            if value:
                return value
        return candidate_values["technical_id"]

    def visible_name_for_reference(self, raw_value: str) -> str:
        normalized = str(raw_value or "").strip()
        if not normalized:
            return ""
        role_id = self.resolve_role_reference(normalized)
        if role_id:
            visible = self.visible_name_for_agent(role_id)
            if visible:
                return visible
        return normalized

    def resolve_role_reference(self, raw_value: str) -> str:
        normalized = str(raw_value or "").strip().casefold()
        if not normalized:
            return ""
        if normalized in {role_id.casefold(): role_id for role_id in self.roles_payload()}:
            return {
                role_id.casefold(): role_id for role_id in self.roles_payload()
            }[normalized]
        for role_id in self.roles_payload():
            candidates = {
                role_id.strip().casefold(),
                self.formal_name_for_agent(role_id).casefold(),
                self.visible_name_for_agent(role_id).casefold(),
                self.chat_alias_for_agent(role_id).casefold(),
            }
            if normalized in {candidate for candidate in candidates if candidate}:
                return role_id
        return ""

    def enabled_role_visible_names(self) -> list[str]:
        return sorted(self.visible_name_for_agent(role_id) for role_id in self.enabled_roles())

    def enabled_role_visible_names_by_id(self) -> dict[str, str]:
        return {
            role_id: self.visible_name_for_agent(role_id)
            for role_id in self.enabled_roles()
        }

    def duplicate_enabled_role_visible_names(self) -> list[str]:
        occurrences: dict[str, int] = {}
        for name in self.enabled_role_visible_names():
            normalized = name.casefold()
            occurrences[normalized] = occurrences.get(normalized, 0) + 1
        return sorted(
            name
            for name in self.enabled_role_visible_names()
            if occurrences.get(name.casefold(), 0) > 1
        )

    def role_jira_assignee_payload(self, role_id: str) -> dict[str, Any]:
        runtime_entry = self.role_runtime_entry(role_id)
        payload = runtime_entry.get("jira_assignee") or {}
        return payload if isinstance(payload, dict) else {}

    def enabled_roles_missing_jira_assignee_mapping(self) -> list[str]:
        return sorted(
            role_id
            for role_id in self.enabled_roles()
            if bool(self.role_runtime_entry(role_id).get("chat_owner_supported", False))
            and not str(self.role_jira_assignee_payload(role_id).get("account_id", "")).strip()
        )

    def jira_assignable_roles(self) -> list[str]:
        return sorted(
            role_id
            for role_id in self.enabled_roles()
            if str(self.role_jira_assignee_payload(role_id).get("account_id", "")).strip()
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


def normalize_github_remote_url(raw_remote_url: str) -> str:
    normalized = raw_remote_url.strip()
    if not normalized:
        raise AiControlPlaneError("Remote origin do repo esta vazio.")
    if normalized.startswith("git@github.com:"):
        normalized = normalized.replace("git@github.com:", "https://github.com/", 1)
    elif normalized.startswith("ssh://git@github.com/"):
        normalized = normalized.replace("ssh://git@github.com/", "https://github.com/", 1)
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    if normalized.startswith("https://github.com/"):
        return normalized.rstrip("/")
    raise AiControlPlaneError(
        f"Remote origin nao aponta para um repositorio GitHub suportado: {raw_remote_url}"
    )


def resolve_repo_web_context(repo_root: str | Path | None = None) -> RepoWebContext:
    resolved_repo_root = resolve_repo_root(repo_root)
    cache_key = str(resolved_repo_root).lower()
    cached = _REPO_WEB_CONTEXT_CACHE.get(cache_key)
    if cached is not None:
        return cached
    remote_url = run_command(
        ["git", "remote", "get-url", "origin"],
        cwd=resolved_repo_root,
    ).stdout.strip()
    branch_ref = run_command(
        ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd=resolved_repo_root,
        check=False,
    ).stdout.strip()
    default_branch = "main"
    if branch_ref.startswith("refs/remotes/origin/"):
        default_branch = branch_ref.split("/", 3)[-1].strip() or "main"
    context = RepoWebContext(
        github_base_url=normalize_github_remote_url(remote_url),
        default_branch=default_branch,
    )
    _REPO_WEB_CONTEXT_CACHE[cache_key] = context
    return context


def github_blob_url(
    repo_root: str | Path | None,
    repo_relative_path: str | Path,
    *,
    ref: str = "",
) -> str:
    context = resolve_repo_web_context(repo_root)
    raw_path = str(repo_relative_path).replace("\\", "/").strip()
    while raw_path.startswith("./"):
        raw_path = raw_path[2:]
    raw_path = raw_path.lstrip("/")
    if not raw_path:
        raise AiControlPlaneError("github_blob_url exige um path relativo do repo.")
    encoded_path = quote(raw_path, safe="/._-")
    effective_ref = ref.strip() or context.default_branch
    return f"{context.github_base_url}/blob/{quote(effective_ref, safe='._-/')}/{encoded_path}"


REPO_PATH_RE = re.compile(
    r"(?P<prefix>^|[\s(>:-])(?P<path>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+)(?P<suffix>$|[\s),.;:!?])",
    re.MULTILINE,
)


def resolve_tracked_repo_files(repo_root: str | Path | None = None) -> set[str]:
    resolved_repo_root = resolve_repo_root(repo_root)
    cache_key = str(resolved_repo_root).lower()
    cached = _TRACKED_REPO_FILES_CACHE.get(cache_key)
    if cached is not None:
        return cached
    completed = run_command(
        ["git", "ls-files", "-z"],
        cwd=resolved_repo_root,
    )
    tracked = {
        entry.replace("\\", "/").strip() for entry in completed.stdout.split("\0") if entry.strip()
    }
    _TRACKED_REPO_FILES_CACHE[cache_key] = tracked
    return tracked


def linkify_repo_relative_paths(text: str, *, repo_root: str | Path | None) -> str:
    try:
        resolved_repo_root = resolve_repo_root(repo_root)
        resolve_repo_web_context(resolved_repo_root)
        tracked_files = resolve_tracked_repo_files(resolved_repo_root)
    except AiControlPlaneError:
        return text

    def replacer(match: re.Match[str]) -> str:
        prefix = match.group("prefix")
        raw_path = match.group("path")
        suffix = match.group("suffix")
        normalized_path = raw_path.replace("\\", "/").strip()
        while normalized_path.startswith("./"):
            normalized_path = normalized_path[2:]
        normalized_path = normalized_path.lstrip("/")
        if normalized_path not in tracked_files:
            return match.group(0)
        candidate = (resolved_repo_root / raw_path).resolve()
        try:
            candidate.relative_to(resolved_repo_root)
        except ValueError:
            return match.group(0)
        if not candidate.exists() or not candidate.is_file():
            return match.group(0)
        try:
            github_url = github_blob_url(resolved_repo_root, normalized_path)
        except AiControlPlaneError:
            return match.group(0)
        return f"{prefix}[{normalized_path}]({github_url}){suffix}"

    return REPO_PATH_RE.sub(replacer, text)


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


def _load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        raise AiControlPlaneError("tomllib nao esta disponivel neste runtime Python.")
    if not path.exists():
        raise AiControlPlaneError(f"Arquivo TOML nao encontrado: {path}")
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    if not isinstance(payload, dict):
        raise AiControlPlaneError(f"TOML invalido em {path}: esperado objeto raiz.")
    return payload


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
    agent_enablement_path = config_root / "agent-enablement.yaml"
    agent_operations_path = config_root / "agent-operations.yaml"
    contracts_path = config_root / "contracts.yaml"
    agent_runtime_path = config_root / "agent-runtime.yaml"
    platforms_payload, platforms_local_path = load_yaml_map_with_optional_overlay(platforms_path)
    agents_payload, agents_local_path = load_yaml_map_with_optional_overlay(agents_path)
    agent_enablement_payload, agent_enablement_local_path = load_yaml_map_with_optional_overlay(
        agent_enablement_path
    )
    agent_operations_payload, agent_operations_local_path = load_yaml_map_with_optional_overlay(
        agent_operations_path
    )
    contracts_payload, contracts_local_path = load_yaml_map_with_optional_overlay(contracts_path)
    agent_runtime_payload, agent_runtime_local_path = load_yaml_map_with_optional_overlay(
        agent_runtime_path
    )
    return AiControlPlane(
        repo_root=resolved_repo_root,
        config_root=config_root,
        platforms_path=platforms_path,
        platforms_local_path=platforms_local_path,
        agents_path=agents_path,
        agents_local_path=agents_local_path,
        agent_enablement_path=agent_enablement_path,
        agent_enablement_local_path=agent_enablement_local_path,
        agent_operations_path=agent_operations_path,
        agent_operations_local_path=agent_operations_local_path,
        contracts_path=contracts_path,
        contracts_local_path=contracts_local_path,
        agent_runtime_path=agent_runtime_path,
        agent_runtime_local_path=agent_runtime_local_path,
        platforms_payload=platforms_payload,
        agents_payload=agents_payload,
        agent_enablement_payload=agent_enablement_payload,
        agent_operations_payload=agent_operations_payload,
        contracts_payload=contracts_payload,
        agent_runtime_payload=agent_runtime_payload,
    )


def normalize_url(value: str) -> str:
    return value.strip().rstrip("/")


def clear_secret_resolver_cache() -> None:
    global _OP_RATELIMIT_CACHE
    _OP_ITEM_CACHE.clear()
    _OP_VALUE_CACHE.clear()
    _REPO_WEB_CONTEXT_CACHE.clear()
    _TRACKED_REPO_FILES_CACHE.clear()
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
        "account_read_write_exhausted": bool(account_row)
        and int(account_row.get("remaining", 0)) <= 0,
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
        raise AiControlPlaneError(
            "op run retornou JSON invalido ao resolver secrets em lote."
        ) from exc
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
        "agent_enablement_path": str(loaded.agent_enablement_path),
        "agent_enablement_local_path": str(loaded.agent_enablement_local_path),
        "agent_operations_path": str(loaded.agent_operations_path),
        "agent_operations_local_path": str(loaded.agent_operations_local_path),
        "contracts_path": str(loaded.contracts_path),
        "contracts_local_path": str(loaded.contracts_local_path),
        "agent_runtime_path": str(loaded.agent_runtime_path),
        "agent_runtime_local_path": str(loaded.agent_runtime_local_path),
        "local_overrides": {
            "platforms": loaded.platforms_local_path.exists(),
            "agents": loaded.agents_local_path.exists(),
            "agent_enablement": loaded.agent_enablement_local_path.exists(),
            "agent_operations": loaded.agent_operations_local_path.exists(),
            "contracts": loaded.contracts_local_path.exists(),
            "agent_runtime": loaded.agent_runtime_local_path.exists(),
        },
        "enabled_roles": loaded.enabled_roles(),
        "required_roles": loaded.required_roles(),
        "disabled_roles": loaded.disabled_roles(),
        "enabled_registry_agents": loaded.enabled_registry_agents(),
        "disabled_registry_agents": loaded.disabled_registry_agents(),
        "role_enablement": {
            "declared_roles": loaded.declared_enablement_roles(),
            "overridden_roles": loaded.enablement_overridden_roles(),
            "required_roles_disabled": loaded.required_roles_disabled(),
        },
        "role_operation_coverage": {
            "covered_roles": loaded.roles_with_operation_contracts(),
            "missing_roles": loaded.roles_missing_operation_contracts(),
            "orphan_contracts": loaded.operation_contracts_without_roles(),
        },
        "role_runtime_coverage": {
            "covered_roles": loaded.roles_with_runtime_contracts(),
            "missing_roles": loaded.roles_missing_runtime_contracts(),
            "orphan_contracts": loaded.runtime_contracts_without_roles(),
        },
        "registry_runtime_coverage": {
            "covered_registry_agents": loaded.registry_agents_with_runtime_contracts(),
            "missing_registry_agents": loaded.registry_agents_missing_runtime_contracts(),
            "orphan_contracts": loaded.runtime_contracts_without_registry_agents(),
        },
        "runtime_operability": {
            "enabled_roles_without_operational_runtime": loaded.enabled_roles_without_operational_runtime(),
            "required_roles_without_operational_runtime": loaded.required_roles_without_operational_runtime(),
            "enabled_registry_agents_without_operational_runtime": loaded.enabled_registry_agents_without_operational_runtime(),
            "enabled_roles_missing_jira_assignee_mapping": loaded.enabled_roles_missing_jira_assignee_mapping(),
            "jira_assignable_roles": loaded.jira_assignable_roles(),
        },
        "chat_identity_runtime": {
            "chat_name_fallback_order": loaded.chat_name_fallback_order(),
            "chat_owner_capable_roles": loaded.chat_owner_capable_roles(),
            "chat_owner_capable_registry_agents": loaded.chat_owner_capable_registry_agents(),
            "enabled_role_visible_names": loaded.enabled_role_visible_names(),
            "enabled_role_visible_names_by_id": loaded.enabled_role_visible_names_by_id(),
            "duplicate_enabled_role_visible_names": loaded.duplicate_enabled_role_visible_names(),
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
