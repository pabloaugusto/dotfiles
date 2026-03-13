from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for Python < 3.11
    tomllib = None  # type: ignore[assignment]

from scripts.ai_agent_execution_lib import load_context
from scripts.ai_atlassian_actor_lib import actor_runtime_state
from scripts.ai_control_plane_lib import load_ai_control_plane, resolve_atlassian_platform
from scripts.ai_fallback_governance_lib import fallback_status_payload
from scripts.ai_rules_lib import rules_projection_payload as load_rules_projection_payload
from scripts.atlassian_platform_lib import connectivity_payload
from scripts.github_auth_probe_lib import GitHubAuthProbeError, probe_github_auth

MANIFEST_PATH = Path("docs/AI-STARTUP-GOVERNANCE-MANIFEST.md")
CHAT_CONTRACTS_REGISTER_PATH = Path("docs/AI-CHAT-CONTRACTS-REGISTER.md")
TRACKER_PATH = Path("docs/AI-WIP-TRACKER.md")
PROMPTS_CATALOG_PATH = Path(".agents/prompts/CATALOG.md")
PEA_PROMPT_ROOT = Path(".agents/prompts/formal/startup-alignment")
REGISTRY_ROOT = Path(".agents/registry")
DEFAULT_REPORT_PATH = Path(".cache/ai/startup-session.md")
DEFAULT_READINESS_PATH = Path(".cache/ai/startup-ready.json")
WORKLOG_DOING_START = "<!-- ai-worklog:doing:start -->"
WORKLOG_DOING_END = "<!-- ai-worklog:doing:end -->"
WORKLOG_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Ultima atualizacao UTC",
    "Proximo passo",
    "Bloqueios",
]
GITHUB_FALLBACK_CHAIN = [
    "reaproveitar sessao existente do gh",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "op://secrets/dotfiles/github/token",
    "op://secrets/github/api/token",
    "op://Personal/github/token-full-access",
]
STARTUP_GOVERNOR_AGENT = "ai-startup-governor"
STARTUP_GOVERNOR_DISPLAY_NAME = "Guardiao de Startup"
ALLOWED_PENDING_ACTIONS = {"", "concluir_primeiro", "roadmap_pendente"}

PENDING_MARKERS = (
    "<!-- ai-chat-contracts:pending:start -->",
    "<!-- ai-chat-contracts:pending:end -->",
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ISSUE_KEY_RE = re.compile(r"([A-Z][A-Z0-9]+-\d+)")

CHAT_COMMUNICATION_RULES = [
    "usar portugues nas respostas operacionais do repo",
    "preferir display_name oficial quando ele existir",
    "usar links absolutos em Markdown para arquivos do repo no chat",
    "usar links web canonicos para Jira e Confluence",
    "manter resumos curtos, humanos e sem substituir a rastreabilidade oficial",
]

SUBAGENT_CONTEXT_RULES = [
    "nao delegar antes de carregar ou referenciar o startup oficial da rodada",
    "entregar a issue dona, a branch atual e o proximo passo objetivo ao subagente",
    "entregar tambem os arquivos normativos e as regras aplicaveis ao papel delegado",
    "quando houver PEA, repassar classificacao, assuncoes relevantes e ambiguidades abertas ao subagente",
    "tratar trabalho sem contexto minimo de subagente como rejeitavel",
]

GIT_GOVERNANCE_STARTUP_SOURCES = [
    "AGENTS.md",
    "docs/git-conventions.md",
    "Taskfile.yml",
    ".githooks/",
    ".github/pull_request_template.md",
]

GIT_GOVERNANCE_STARTUP_RULES = [
    "commits devem ser atomicos, ligados a uma unica issue e preferencialmente auto-testaveis",
    "cada branch deve carregar um unico contexto coerente e ser podada apos merge seguro",
    "task ai:worklog:check e git-governance-check seguem como gates canonicos antes de empilhar escopo",
]

PEA_EXECUTION_MODES = [
    "fast_lane",
    "alinhamento_resumido_e_execucao",
    "aguardando_confirmacao_humana",
    "bloqueado_por_pre_condicao",
]

PEA_REQUIRED_PATHS = [
    ".agents/prompts/CATALOG.md",
    ".agents/prompts/formal/startup-alignment/prompt.md",
    ".agents/prompts/formal/startup-alignment/context.md",
    ".agents/prompts/formal/startup-alignment/meta.yaml",
]

ATLASSIAN_RECOVERY_RULES = [
    "rodar task ai:atlassian:check antes de assumir bloqueio estrutural",
    "preferir op run para resolver refs Atlassian em lote na borda do processo",
    "usar op item get --format json como fallback por item quando o batch falhar",
    "lembrar que service-account-api-token usa api.atlassian.com com cloud_id",
]


@dataclass(frozen=True)
class ChatContractEntry:
    contract_id: str
    summary: str
    evidence: str
    owner: str
    destination: str
    status: str


def _normalize_pending_action(pending_action: str) -> str:
    normalized = str(pending_action or "").strip()
    if normalized not in ALLOWED_PENDING_ACTIONS:
        raise ValueError("pending_action invalida. Use concluir_primeiro ou roadmap_pendente.")
    return normalized


def _read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_textual_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    return True


def _run_command(
    command: list[str],
    *,
    repo_root: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(message or "comando falhou sem stderr legivel")
    return completed


def _load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None or not path.is_file():
        return {}
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    return payload if isinstance(payload, dict) else {}


def _extract_issue_key(text: str) -> str:
    match = ISSUE_KEY_RE.search(str(text or ""))
    return match.group(1) if match else ""


def _resolve_recursive_directory(repo_root: Path, relative_dir: str) -> list[str]:
    directory = (repo_root / relative_dir).resolve()
    if not directory.is_dir():
        return []
    resolved: list[str] = []
    for candidate in sorted(directory.rglob("*")):
        if _is_textual_file(candidate):
            resolved.append(candidate.relative_to(repo_root).as_posix())
    return resolved


def _resolve_ai_docs(repo_root: Path, relative_dir: str) -> list[str]:
    directory = (repo_root / relative_dir).resolve()
    if not directory.is_dir():
        return []
    resolved: list[str] = []
    for candidate in sorted(directory.rglob("AI-*")):
        if _is_textual_file(candidate):
            resolved.append(candidate.relative_to(repo_root).as_posix())
    return resolved


def _table_rows_between(content: str, start_marker: str, end_marker: str) -> list[list[str]]:
    if start_marker not in content or end_marker not in content:
        return []
    section = content.split(start_marker, 1)[1].split(end_marker, 1)[0]
    rows: list[list[str]] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        values = [item.strip() for item in line.strip("|").split("|")]
        if values and values[0] in {"ID", "(sem itens)"}:
            continue
        rows.append(values)
    return rows


def _parse_worktree_porcelain(raw_text: str) -> list[dict[str, str]]:
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


def load_agent_display_names(repo_root: Path) -> dict[str, str]:
    registry_dir = (repo_root / REGISTRY_ROOT).resolve()
    if not registry_dir.is_dir():
        return {}
    display_names: dict[str, str] = {}
    for candidate in sorted(registry_dir.glob("*.toml")):
        payload = _load_toml(candidate)
        agent_id = str(payload.get("id", "")).strip() or candidate.stem
        display_name = str(payload.get("display_name", "")).strip()
        if agent_id and display_name:
            display_names[agent_id] = display_name
    return display_names


def agent_identity_payload(repo_root: Path, active_execution: dict[str, Any]) -> dict[str, Any]:
    active_agent = str(active_execution.get("agent_id", "")).strip() or str(
        active_execution.get("agent", "")
    ).strip()
    try:
        control_plane = load_ai_control_plane(repo_root)
    except Exception:
        display_names = load_agent_display_names(repo_root)
        return {
            "status": "ok" if display_names else "missing",
            "registry_count": len(display_names),
            "active_agent": active_agent,
            "active_display_name": display_names.get(active_agent, active_agent or "desconhecido"),
            "active_chat_name": display_names.get(active_agent, active_agent or "desconhecido"),
            "fallback_display": "technical-id",
            "chat_name_fallback_order": ["display_name", "technical-id"],
        }
    display_names = control_plane.registry_agent_display_names()
    return {
        "status": "ok" if display_names else "missing",
        "registry_count": len(display_names),
        "active_agent": active_agent,
        "active_display_name": control_plane.formal_name_for_agent(active_agent)
        or active_agent
        or "desconhecido",
        "active_chat_name": control_plane.visible_name_for_agent(active_agent)
        or active_agent
        or "desconhecido",
        "fallback_display": "technical-id",
        "chat_name_fallback_order": control_plane.chat_name_fallback_order(),
    }


def agent_enablement_payload(repo_root: Path) -> dict[str, Any]:
    try:
        control_plane = load_ai_control_plane(repo_root)
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    return {
        "status": "ok",
        "agents_path": control_plane.agents_path.relative_to(repo_root).as_posix(),
        "overlay_path": control_plane.agent_enablement_path.relative_to(repo_root).as_posix(),
        "overlay_local_path": control_plane.agent_enablement_local_path.relative_to(
            repo_root
        ).as_posix(),
        "overlay_local_active": control_plane.agent_enablement_local_path.exists(),
        "declared_roles": control_plane.declared_enablement_roles(),
        "overridden_roles": control_plane.enablement_overridden_roles(),
        "enabled_roles": control_plane.enabled_roles(),
        "disabled_roles": control_plane.disabled_roles(),
        "required_roles_disabled": control_plane.required_roles_disabled(),
        "enabled_registry_agents": control_plane.enabled_registry_agents(),
        "disabled_registry_agents": control_plane.disabled_registry_agents(),
    }


def agent_runtime_payload(repo_root: Path) -> dict[str, Any]:
    try:
        control_plane = load_ai_control_plane(repo_root)
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    declared_roles = sorted(control_plane.roles_payload())
    return {
        "status": "ok",
        "runtime_path": control_plane.agent_runtime_path.relative_to(repo_root).as_posix(),
        "runtime_local_path": control_plane.agent_runtime_local_path.relative_to(
            repo_root
        ).as_posix(),
        "runtime_local_active": control_plane.agent_runtime_local_path.exists(),
        "covered_roles": control_plane.roles_with_runtime_contracts(),
        "missing_roles": control_plane.roles_missing_runtime_contracts(),
        "orphan_role_contracts": control_plane.runtime_contracts_without_roles(),
        "covered_registry_agents": control_plane.registry_agents_with_runtime_contracts(),
        "missing_registry_agents": control_plane.registry_agents_missing_runtime_contracts(),
        "orphan_registry_contracts": control_plane.runtime_contracts_without_registry_agents(),
        "enabled_roles_without_operational_runtime": control_plane.enabled_roles_without_operational_runtime(),
        "required_roles_without_operational_runtime": control_plane.required_roles_without_operational_runtime(),
        "enabled_registry_agents_without_operational_runtime": control_plane.enabled_registry_agents_without_operational_runtime(),
        "chat_owner_capable_roles": control_plane.chat_owner_capable_roles(),
        "chat_owner_capable_registry_agents": control_plane.chat_owner_capable_registry_agents(),
        "chat_name_fallback_order": control_plane.chat_name_fallback_order(),
        "role_visible_names": {
            role_id: control_plane.visible_name_for_agent(role_id) for role_id in declared_roles
        },
        "enabled_role_visible_names": control_plane.enabled_role_visible_names(),
        "duplicate_enabled_role_visible_names": control_plane.duplicate_enabled_role_visible_names(),
        "jira_assignable_roles": control_plane.jira_assignable_roles(),
        "enabled_roles_missing_jira_assignee_mapping": control_plane.enabled_roles_missing_jira_assignee_mapping(),
        "enabled_roles_with_atlassian_actor": control_plane.enabled_roles_with_atlassian_actor(),
        "enabled_roles_using_global_atlassian_actor": control_plane.enabled_roles_using_global_atlassian_actor(),
        "enabled_roles_with_incomplete_atlassian_actor": control_plane.enabled_roles_with_incomplete_atlassian_actor(),
        "atlassian_actor_surface_matrix": control_plane.role_atlassian_actor_surface_matrix(),
    }


def manifest_evidence_payload(repo_root: Path, resolved_paths: list[str]) -> dict[str, Any]:
    digest = hashlib.sha256()
    total_bytes = 0
    total_lines = 0
    missing_paths: list[str] = []
    for relative in resolved_paths:
        candidate = (repo_root / relative).resolve()
        if not candidate.is_file():
            missing_paths.append(relative)
            continue
        content = _read_utf8(candidate)
        encoded = content.encode("utf-8")
        total_bytes += len(encoded)
        total_lines += len(content.splitlines())
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(encoded)
        digest.update(b"\0")
    status = "ok" if resolved_paths and not missing_paths else "missing"
    return {
        "status": status,
        "resolved_count": len(resolved_paths),
        "textual_line_count": total_lines,
        "textual_bytes": total_bytes,
        "sha256": digest.hexdigest() if resolved_paths else "",
        "missing_paths": missing_paths,
    }


def rules_projections_payload(repo_root: Path) -> dict[str, Any]:
    payload = load_rules_projection_payload(repo_root)
    if payload.get("status") == "error":
        return payload
    projections = payload.get("projections", {})
    return {
        **payload,
        "projection_count": len(projections) if isinstance(projections, dict) else 0,
        "loaded_required_count": len(payload.get("loaded_for_startup", [])),
    }


def _projection_rules(
    rules_projections: dict[str, Any],
    projection_id: str,
    fallback_rules: list[str],
) -> tuple[str, str, list[str]]:
    projections = rules_projections.get("projections", {})
    if not isinstance(projections, dict):
        return "", "", list(fallback_rules)
    projection = projections.get(projection_id, {})
    if not isinstance(projection, dict):
        return "", "", list(fallback_rules)
    rules = [str(item).strip() for item in projection.get("must", []) if str(item).strip()]
    return (
        str(projection.get("human_source", "")).strip(),
        str(projection.get("machine_projection", "")).strip(),
        rules or list(fallback_rules),
    )


def chat_communication_payload(
    repo_root: Path, rules_projections: dict[str, Any] | None = None
) -> dict[str, Any]:
    resolved_projections = rules_projections or rules_projections_payload(repo_root)
    human_source, machine_projection, rules = _projection_rules(
        resolved_projections,
        "chat",
        CHAT_COMMUNICATION_RULES,
    )
    return {
        "status": "ok" if rules else "missing",
        "human_source": human_source,
        "machine_projection": machine_projection,
        "rules": rules,
    }


def git_governance_payload(
    repo_root: Path, rules_projections: dict[str, Any] | None = None
) -> dict[str, Any]:
    resolved_projections = rules_projections or rules_projections_payload(repo_root)
    human_source, machine_projection, rules = _projection_rules(
        resolved_projections,
        "git",
        GIT_GOVERNANCE_STARTUP_RULES,
    )
    return {
        "status": "ok" if rules else "missing",
        "human_source": human_source,
        "machine_projection": machine_projection,
        "sources": list(GIT_GOVERNANCE_STARTUP_SOURCES),
        "rules": rules,
        "enforcement_note": (
            "o startup relembra a governanca Git, mas o enforcement real continua nos hooks, "
            "tasks e gates oficiais do repo"
        ),
    }


def pea_status_payload(repo_root: Path, resolved_paths: list[str]) -> dict[str, Any]:
    catalog_path = (repo_root / PROMPTS_CATALOG_PATH).resolve()
    prompt_root = (repo_root / PEA_PROMPT_ROOT).resolve()
    required_files = [
        prompt_root / "prompt.md",
        prompt_root / "context.md",
        prompt_root / "meta.yaml",
    ]
    missing = [
        path.relative_to(repo_root).as_posix() for path in required_files if not path.is_file()
    ]
    startup_loads_pack = all(relative in resolved_paths for relative in PEA_REQUIRED_PATHS)
    return {
        "status": "ok"
        if catalog_path.is_file() and not missing and startup_loads_pack
        else "missing",
        "catalog_path": PROMPTS_CATALOG_PATH.as_posix(),
        "pack_root": PEA_PROMPT_ROOT.as_posix(),
        "required_paths": list(PEA_REQUIRED_PATHS),
        "missing_paths": missing,
        "startup_loads_pack": startup_loads_pack,
        "execution_modes": list(PEA_EXECUTION_MODES),
        "separation_note": (
            "startup rele a camada e expoe pea_status; PEA alinha entendimento; enforcement real "
            "permanece em hooks, tasks, validadores, reviews, Jira e closeout"
        ),
    }


def branch_lifecycle_payload(repo_root: Path, current_branch: str) -> dict[str, Any]:
    normalized_branch = str(current_branch).strip()
    lifecycle: dict[str, Any] = {
        "branch": normalized_branch,
        "upstream": "",
        "ahead_count": 0,
        "behind_count": 0,
        "has_upstream": False,
        "absorbed_in_origin_main": False,
        "origin_main_probe": "skipped",
        "prune_candidate": False,
    }
    if not normalized_branch or normalized_branch.startswith("("):
        return lifecycle

    upstream_probe = _run_command(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        repo_root=repo_root,
        check=False,
    )
    upstream = upstream_probe.stdout.strip() if upstream_probe.returncode == 0 else ""
    lifecycle["upstream"] = upstream
    lifecycle["has_upstream"] = bool(upstream)

    if upstream:
        counts_probe = _run_command(
            ["git", "rev-list", "--left-right", "--count", f"{upstream}...HEAD"],
            repo_root=repo_root,
            check=False,
        )
        counts = counts_probe.stdout.strip().split()
        if counts_probe.returncode == 0 and len(counts) >= 2:
            lifecycle["behind_count"] = int(counts[0])
            lifecycle["ahead_count"] = int(counts[1])

    origin_main_probe = _run_command(
        ["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"],
        repo_root=repo_root,
        check=False,
    )
    if origin_main_probe.returncode in {0, 1}:
        lifecycle["origin_main_probe"] = "ok"
        lifecycle["absorbed_in_origin_main"] = origin_main_probe.returncode == 0
    else:
        lifecycle["origin_main_probe"] = "error"
    lifecycle["prune_candidate"] = bool(
        normalized_branch != "main" and lifecycle["absorbed_in_origin_main"]
    )
    return lifecycle


def startup_drift_payload(
    active_execution: dict[str, Any],
    active_worklog_items: list[dict[str, str]],
    git_inventory: dict[str, Any],
) -> dict[str, Any]:
    findings: list[str] = []
    current_branch = str(git_inventory.get("current_branch", "")).strip()
    branch_issue = _extract_issue_key(current_branch)
    active_issue = str(active_execution.get("issue_key", "")).strip()

    if active_execution.get("status") == "ok":
        context_branch = str(active_execution.get("branch", "")).strip()
        if context_branch and current_branch and context_branch != current_branch:
            findings.append(
                f"contexto ativo aponta para `{context_branch}`, mas a branch atual e `{current_branch}`"
            )
        if branch_issue and active_issue and branch_issue != active_issue:
            findings.append(
                f"branch atual sugere `{branch_issue}`, mas o contexto ativo esta em `{active_issue}`"
            )

    if active_worklog_items:
        worklog = active_worklog_items[0]
        worklog_branch = str(worklog.get("Branch", "")).strip()
        worklog_issue = _extract_issue_key(worklog_branch) or _extract_issue_key(
            str(worklog.get("Tarefa", ""))
        )
        if worklog_branch and current_branch and worklog_branch != current_branch:
            findings.append(
                f"worklog ativo aponta para `{worklog_branch}`, mas a branch atual e `{current_branch}`"
            )
        if branch_issue and worklog_issue and branch_issue != worklog_issue:
            findings.append(
                f"branch atual sugere `{branch_issue}`, mas o worklog ativo aponta para `{worklog_issue}`"
            )
        if active_issue and worklog_issue and active_issue != worklog_issue:
            findings.append(
                f"contexto ativo aponta para `{active_issue}`, mas o worklog ativo aponta para `{worklog_issue}`"
            )

    if (
        git_inventory.get("dirty_entries")
        and active_execution.get("status") != "ok"
        and not active_worklog_items
    ):
        findings.append("arvore dirty sem contexto ativo nem worklog Doing correspondente")

    lifecycle = git_inventory.get("branch_lifecycle", {})
    if lifecycle.get("prune_candidate") and (
        active_execution.get("status") == "ok" or active_worklog_items
    ):
        findings.append(
            "branch atual ja foi absorvida em origin/main, mas ainda aparece como trilha ativa"
        )

    return {
        "status": "clean" if not findings else "drift",
        "findings": findings,
    }


def delegation_context_payload(
    prioritized_work_item: dict[str, str],
    git_inventory: dict[str, Any],
) -> dict[str, Any]:
    current_branch = str(git_inventory.get("current_branch", "")).strip()
    return {
        "status": "ok",
        "owner_issue": prioritized_work_item.get("identifier", ""),
        "current_branch": current_branch,
        "required_paths": [
            "AGENTS.md",
            "config/ai/agent-enablement.yaml",
            "docs/AI-STARTUP-AND-RESTART.md",
            "docs/AI-DELEGATION-FLOW.md",
            "docs/ai-operating-model.md",
            "docs/AI-WIP-TRACKER.md",
            "docs/AI-CHAT-CONTRACTS-REGISTER.md",
            ".agents/prompts/CATALOG.md",
            ".agents/prompts/formal/startup-alignment/prompt.md",
        ],
        "rules": list(SUBAGENT_CONTEXT_RULES),
    }


def resolve_startup_manifest_paths(repo_root: Path) -> list[str]:
    manifest_path = (repo_root / MANIFEST_PATH).resolve()
    content = _read_utf8(manifest_path)
    resolved: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        match = MARKDOWN_LINK_RE.search(line)
        if match is None:
            continue
        target = match.group(1).strip()
        candidate = (manifest_path.parent / target).resolve()
        relative_target = candidate.relative_to(repo_root).as_posix()
        if "todos os arquivos `AI-*` em" in line:
            resolved.update(_resolve_ai_docs(repo_root, relative_target))
            continue
        if "todos os arquivos em" in line:
            resolved.update(_resolve_recursive_directory(repo_root, relative_target))
            continue
        if _is_textual_file(candidate):
            resolved.add(relative_target)
    return sorted(resolved)


def _merged_local_branches(repo_root: Path, base_ref: str) -> list[str]:
    merged = _run_command(
        ["git", "branch", "--format=%(refname:short)", "--merged", base_ref],
        repo_root=repo_root,
    )
    local = _run_command(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"],
        repo_root=repo_root,
    )
    current_branch = _run_command(
        ["git", "branch", "--show-current"],
        repo_root=repo_root,
    ).stdout.strip()
    protected = {"main"}
    if current_branch:
        protected.add(current_branch)
    merged_names = {line.strip() for line in merged.stdout.splitlines() if line.strip()}
    return sorted(
        branch.strip()
        for branch in local.stdout.splitlines()
        if branch.strip() in merged_names and branch.strip() not in protected
    )


def git_inventory_payload(repo_root: Path) -> dict[str, Any]:
    try:
        current_branch = _run_command(
            ["git", "branch", "--show-current"],
            repo_root=repo_root,
        ).stdout.strip()
        status_lines = _run_command(
            ["git", "status", "--short", "--branch"],
            repo_root=repo_root,
        ).stdout.splitlines()
        dirty_entries = [line for line in status_lines[1:] if line.strip()]
        local_branches = [
            line.strip()
            for line in _run_command(
                ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"],
                repo_root=repo_root,
            ).stdout.splitlines()
            if line.strip()
        ]
        worktrees = _parse_worktree_porcelain(
            _run_command(
                ["git", "worktree", "list", "--porcelain"],
                repo_root=repo_root,
            ).stdout
        )
        branch_lifecycle = branch_lifecycle_payload(repo_root, current_branch)
        branch_lifecycle["prune_candidate"] = bool(
            branch_lifecycle.get("prune_candidate", False) and not dirty_entries
        )
        open_prs: list[dict[str, Any]] = []
        pr_probe_note = ""
        pr_probe_status = "skipped" if not current_branch else "ok"
        if current_branch:
            pr_probe = _run_command(
                [
                    "gh",
                    "pr",
                    "list",
                    "--head",
                    current_branch,
                    "--json",
                    "number,state,title,url",
                ],
                repo_root=repo_root,
                check=False,
            )
            pr_probe_status = "ok" if pr_probe.returncode == 0 else "error"
            pr_probe_note = (
                "" if pr_probe.returncode == 0 else (pr_probe.stderr or pr_probe.stdout).strip()
            )
            try:
                parsed = json.loads(pr_probe.stdout or "[]")
                if isinstance(parsed, list):
                    open_prs = parsed
            except json.JSONDecodeError:
                pr_probe_status = "error"
                pr_probe_note = (pr_probe.stdout or pr_probe.stderr).strip()
        return {
            "status": "ok",
            "current_branch": current_branch or "(detached-or-unknown)",
            "dirty_entries": dirty_entries,
            "local_branch_count": len(local_branches),
            "merged_local_branches": _merged_local_branches(repo_root, "origin/main"),
            "worktrees": worktrees,
            "branch_lifecycle": branch_lifecycle,
            "open_prs_for_current_branch": open_prs,
            "pr_probe_status": pr_probe_status,
            "pr_probe_note": pr_probe_note,
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "current_branch": "",
            "dirty_entries": [],
            "local_branch_count": 0,
            "merged_local_branches": [],
            "worktrees": [],
            "open_prs_for_current_branch": [],
            "pr_probe_status": "error",
            "pr_probe_note": str(exc),
        }


def load_active_worklog_items(repo_root: Path) -> list[dict[str, str]]:
    tracker_path = (repo_root / TRACKER_PATH).resolve()
    if not tracker_path.is_file():
        return []
    content = _read_utf8(tracker_path)
    items: list[dict[str, str]] = []
    for row in _table_rows_between(content, WORKLOG_DOING_START, WORKLOG_DOING_END):
        if len(row) != len(WORKLOG_HEADERS):
            continue
        items.append({WORKLOG_HEADERS[idx]: row[idx] for idx in range(len(WORKLOG_HEADERS))})
    return items


def active_execution_payload(repo_root: Path) -> dict[str, Any]:
    try:
        context = load_context(repo_root)
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    if context is None:
        return {"status": "missing"}
    return {
        "status": "ok",
        "issue_key": context.issue_key,
        "issue_summary": context.issue_summary,
        "issue_url": context.issue_url,
        "agent": context.agent,
        "agent_id": context.agent_id,
        "agent_display_name": context.agent,
        "workflow_status": context.status,
        "current_agent_role": context.current_agent_role,
        "current_agent_role_id": context.current_agent_role_id,
        "next_required_role": context.next_required_role,
        "next_required_role_id": context.next_required_role_id,
        "branch": context.branch,
        "worktree_root": context.worktree_root,
        "started_at": context.started_at,
        "updated_at": context.updated_at,
    }


def github_auth_summary(repo_root: Path) -> dict[str, Any]:
    try:
        payload = probe_github_auth(repo_root)
        graphql_probe = _run_command(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                "query=query { viewer { login } }",
            ],
            repo_root=repo_root,
            check=False,
        )
        graphql_output = (graphql_probe.stdout or graphql_probe.stderr).strip()
        graphql_status = "ok" if graphql_probe.returncode == 0 else "error"
        if "Resource not accessible by personal access token" in graphql_output:
            graphql_status = "resource_not_accessible_by_pat"
        return {
            "status": "ok"
            if payload["auth_status"]["current_shell"]["exit_code"] == 0
            else "error",
            "fallback_chain": GITHUB_FALLBACK_CHAIN,
            "active_sources_current_shell": payload["auth_status"]["current_shell"][
                "active_sources"
            ],
            "active_sources_without_env_tokens": payload["auth_status"]["without_env_tokens"][
                "active_sources"
            ],
            "ssh_signing_keys_probe": payload["endpoint_probes"]["user/ssh_signing_keys"]["status"],
            "user_installations_probe": payload["endpoint_probes"]["user/installations"]["status"],
            "graphql_probe": {
                "status": graphql_status,
                "note": graphql_output,
            },
            "recommendations": payload["recommendations"],
        }
    except (GitHubAuthProbeError, RuntimeError) as exc:
        return {
            "status": "error",
            "error": str(exc),
            "fallback_chain": GITHUB_FALLBACK_CHAIN,
            "active_sources_current_shell": [],
            "active_sources_without_env_tokens": [],
            "ssh_signing_keys_probe": "error",
            "user_installations_probe": "error",
            "graphql_probe": {"status": "error", "note": str(exc)},
            "recommendations": [],
        }


def atlassian_connectivity_summary(repo_root: Path) -> dict[str, Any]:
    try:
        control_plane = load_ai_control_plane(repo_root)
        resolved = resolve_atlassian_platform(
            control_plane.atlassian_definition(),
            repo_root=control_plane.repo_root,
        )
        payload = connectivity_payload(repo_root)
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    atlassian = payload.get("atlassian", {})
    jira_payload = payload.get("jira", {})
    confluence_payload = payload.get("confluence", {})
    if not atlassian.get("enabled", False):
        return {"status": "disabled", "overall_ok": True, "recovery_hints": []}
    return {
        "status": "ok" if payload.get("overall_ok", False) else "error",
        "overall_ok": bool(payload.get("overall_ok", False)),
        "auth_mode": str(atlassian.get("auth_mode", "")).strip(),
        "site_url": str(atlassian.get("site_url", "")).strip(),
        "cloud_id": getattr(resolved, "cloud_id", ""),
        "jira_project_key": getattr(resolved, "jira_project_key", ""),
        "confluence_space_key": getattr(resolved, "confluence_space_key", ""),
        "jira_status": str(jira_payload.get("status", "")).strip(),
        "jira_project": jira_payload.get("project", {}),
        "confluence_status": str(confluence_payload.get("status", "")).strip(),
        "confluence_space": confluence_payload.get("space", {}),
        "recovery_hints": list(ATLASSIAN_RECOVERY_RULES),
    }


def prioritized_work_item_payload(
    active_execution: dict[str, Any], active_worklog_items: list[dict[str, str]]
) -> dict[str, str]:
    if active_execution.get("status") == "ok" and active_execution.get("issue_key"):
        return {
            "source": "active-execution",
            "identifier": str(active_execution["issue_key"]),
            "summary": str(active_execution.get("issue_summary", "")).strip(),
        }
    if active_worklog_items:
        first = active_worklog_items[0]
        identifier = _extract_issue_key(str(first.get("Branch", ""))) or _extract_issue_key(
            str(first.get("Tarefa", ""))
        )
        return {
            "source": "worklog-doing",
            "identifier": identifier or str(first.get("ID", "")).strip(),
            "summary": str(first.get("Tarefa", "")).strip(),
        }
    return {
        "source": "jira-board-required",
        "identifier": "",
        "summary": "Ler o Jira board para definir o proximo work item da rodada.",
    }


def startup_governor_status_payload(
    repo_root: Path,
    *,
    manifest_evidence: dict[str, Any],
    pending_contracts: list[ChatContractEntry],
    git_inventory: dict[str, Any],
    active_worklog_items: list[dict[str, str]],
    active_execution: dict[str, Any],
    agent_identity: dict[str, Any],
    agent_enablement: dict[str, Any],
    agent_runtime: dict[str, Any],
    rules_projections: dict[str, Any],
    chat_communication: dict[str, Any],
    git_governance: dict[str, Any],
    pea_status: dict[str, Any],
    startup_drift: dict[str, Any],
    fallback_status: dict[str, Any],
    github_auth: dict[str, Any],
    atlassian_connectivity: dict[str, Any],
    prioritized_work_item: dict[str, str],
    pending_action: str = "",
) -> dict[str, Any]:
    normalized_pending_action = _normalize_pending_action(pending_action)
    display_names = load_agent_display_names(repo_root)
    role_visible_names = agent_runtime.get("role_visible_names", {})
    governor_display_name = str(
        role_visible_names.get(STARTUP_GOVERNOR_AGENT, STARTUP_GOVERNOR_DISPLAY_NAME)
    ).strip() or STARTUP_GOVERNOR_DISPLAY_NAME
    blockers: list[str] = []
    warnings: list[str] = []
    progression = ["not_started"]
    state = "not_started"

    if manifest_evidence.get("status") == "ok":
        state = "reading_manifest"
        progression.append(state)
    else:
        blockers.append("manifest canonico nao foi relido integralmente com prova valida")

    if rules_projections.get("status") == "ok" and not rules_projections.get("missing_required"):
        state = "rules_projections_loaded"
        progression.append(state)
    else:
        blockers.append("projecoes .rules obrigatorias do startup nao ficaram carregadas")

    if pending_contracts:
        warnings.append(
            f"existem {len(pending_contracts)} contratos nascidos no chat ainda pendentes de promocao"
        )

    if chat_communication.get("status") == "ok":
        state = "chat_contract_loaded"
        progression.append(state)
    else:
        blockers.append("contrato de comunicacao do chat nao ficou carregado corretamente")

    if agent_identity.get("status") == "ok":
        state = "identity_loaded"
        progression.append(state)
    else:
        blockers.append("camada de display_name nao ficou carregada corretamente")

    if agent_enablement.get("status") != "ok":
        blockers.append("overlay declarativo de enablement de agentes nao ficou carregado")
    elif agent_enablement.get("required_roles_disabled"):
        blockers.append(
            "existem agentes marcados como required em config/ai/agents.yaml e desabilitados no overlay declarativo"
        )

    if agent_runtime.get("status") != "ok":
        blockers.append("camada declarativa de runtime operacional dos agentes nao ficou carregada")
    else:
        if agent_runtime.get("missing_roles"):
            blockers.append("existem papeis declarados sem contrato de runtime operacional")
        if agent_runtime.get("orphan_role_contracts"):
            blockers.append("config/ai/agent-runtime.yaml contem papeis sem declaracao em agents.yaml")
        if agent_runtime.get("missing_registry_agents"):
            blockers.append("existem agentes declarativos sem contrato de runtime operacional")
        if agent_runtime.get("orphan_registry_contracts"):
            blockers.append(
                "config/ai/agent-runtime.yaml contem contratos de registry sem agente declarativo correspondente"
            )
        if agent_runtime.get("required_roles_without_operational_runtime"):
            blockers.append(
                "existem papeis required habilitados sem runtime operacional/consultivo valido"
            )
        if agent_runtime.get("enabled_registry_agents_without_operational_runtime"):
            blockers.append(
                "existem agentes declarativos habilitados sem runtime operacional/consultivo valido"
            )
        if agent_runtime.get("duplicate_enabled_role_visible_names"):
            blockers.append(
                "existem aliases visiveis duplicados entre roles habilitados para Jira/chat"
            )
        if agent_runtime.get("enabled_roles_missing_jira_assignee_mapping"):
            warnings.append(
                "nem todos os papeis habilitados possuem principal Jira mapeado para sync de assignee"
            )
        if agent_runtime.get("enabled_roles_with_incomplete_atlassian_actor"):
            warnings.append(
                "existem agentes com service account propria declarada, mas com configuracao Atlassian incompleta"
            )

    if git_inventory.get("status") == "ok" and git_governance.get("status") == "ok":
        state = "git_context_loaded"
        progression.append(state)
    else:
        blockers.append("governanca Git ou inventario de branch/worktree falhou no startup")

    if pea_status.get("status") != "ok":
        blockers.append("catalogo de prompt packs ou pack formal de startup/PEA nao foi carregado")

    if git_inventory.get("pr_probe_status") == "error":
        blockers.append("nao foi possivel capturar PRs abertos da branch atual no startup")

    github_status = str(github_auth.get("status", "")).strip()
    graphql_status = str(github_auth.get("graphql_probe", {}).get("status", "")).strip()
    if github_status not in {"ok", "skipped"}:
        blockers.append("gh auth status ou probes basicos do GitHub falharam no startup")
    if graphql_status not in {"ok", "skipped"}:
        blockers.append("probe GraphQL falhou durante o startup")

    atlassian_status = str(atlassian_connectivity.get("status", "")).strip()
    fallback_mode = str(fallback_status.get("mode", "")).strip()
    if atlassian_status not in {"ok", "disabled", "skipped"}:
        if fallback_mode in {"degraded", "recovery"}:
            warnings.append(
                "Atlassian indisponivel no probe resumido; fallback local esta ativo e precisa de reconciliacao dirigida"
            )
        else:
            blockers.append(
                "saude minima de Jira/Confluence nao ficou comprovada e nenhum fallback ativo foi detectado"
            )

    if github_status in {"ok", "skipped"} and graphql_status in {"ok", "skipped"}:
        if atlassian_status in {"ok", "disabled", "skipped"} or fallback_mode in {
            "degraded",
            "recovery",
        }:
            state = "probes_passed"
            progression.append(state)

    if startup_drift.get("status") != "clean":
        blockers.extend(
            f"drift operacional detectado: {finding}"
            for finding in startup_drift.get("findings", [])
        )

    if active_worklog_items and normalized_pending_action == "":
        state = "wip_decision_pending"
        progression.append(state)
        blockers.append(
            "task ai:worklog:check exige decisao humana explicita: concluir_primeiro ou roadmap_pendente"
        )
    elif normalized_pending_action == "roadmap_pendente":
        state = "wip_decision_pending"
        progression.append(state)
        blockers.append(
            "pending_action=roadmap_pendente mantem a sessao sem ready_for_work ate a retomada correta da rodada"
        )

    current_branch = str(git_inventory.get("current_branch", "")).strip()
    worklog_ids = [
        str(item.get("ID", "")).strip() for item in active_worklog_items if item.get("ID")
    ]
    snapshot = {
        "manifest_sha256": str(manifest_evidence.get("sha256", "")).strip(),
        "current_branch": current_branch,
        "dirty_entry_count": len(git_inventory.get("dirty_entries", [])),
        "active_execution_issue": str(active_execution.get("issue_key", "")).strip(),
        "active_execution_agent": str(active_execution.get("agent", "")).strip(),
        "active_execution_agent_id": str(active_execution.get("agent_id", "")).strip(),
        "active_worklog_ids": worklog_ids,
        "enabled_roles": list(agent_enablement.get("enabled_roles", [])),
        "disabled_roles": list(agent_enablement.get("disabled_roles", [])),
        "fallback_mode": fallback_mode,
        "github_status": github_status,
        "graphql_status": graphql_status,
        "atlassian_status": atlassian_status,
        "pending_action": normalized_pending_action,
        "prioritized_work_item": str(prioritized_work_item.get("identifier", "")).strip(),
    }
    fingerprint = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    next_owner_role = str(active_execution.get("agent_id", "")).strip() or str(
        active_execution.get("agent", "")
    ).strip()
    if not next_owner_role and active_worklog_items:
        next_owner_role = str(active_worklog_items[0].get("Responsavel", "")).strip()
    if not next_owner_role and prioritized_work_item.get("identifier"):
        next_owner_role = "ai-product-owner"
    next_owner_display_name = str(role_visible_names.get(next_owner_role, "")).strip()
    if not next_owner_display_name:
        next_owner_display_name = display_names.get(next_owner_role, next_owner_role or "a definir")
    disabled_roles = set(agent_enablement.get("disabled_roles", []))
    if STARTUP_GOVERNOR_AGENT in disabled_roles:
        blockers.append("ai-startup-governor esta desabilitado no overlay declarativo")
    if "ai-scrum-master" in disabled_roles:
        blockers.append("ai-scrum-master esta desabilitado no overlay declarativo")
    if next_owner_role and next_owner_role in disabled_roles:
        blockers.append(
            f"papel operacional priorizado esta desabilitado no overlay declarativo: {next_owner_role}"
        )
    chat_owner_capable_roles = set(agent_runtime.get("chat_owner_capable_roles", []))
    if next_owner_role and next_owner_role not in chat_owner_capable_roles:
        blockers.append(
            f"papel operacional priorizado nao tem runtime apto a ownership visivel de chat: {next_owner_role}"
        )

    if blockers and state != "wip_decision_pending":
        state = "startup_failed"
        progression.append(state)

    clearance_granted = not blockers
    if clearance_granted:
        state = "ready_for_work"
        progression.append(state)

    return {
        "owner_role": STARTUP_GOVERNOR_AGENT,
        "owner_display_name": governor_display_name,
        "audit_owner_role": "ai-scrum-master",
        "state": state,
        "clearance": "granted" if clearance_granted else "blocked",
        "clearance_granted": clearance_granted,
        "pending_action": normalized_pending_action,
        "progression": progression,
        "blocking_findings": blockers,
        "warnings": warnings,
        "blocked_actions": []
        if clearance_granted
        else ["operational-output", "subagent-delegation", "operational-handoff"],
        "harness": {
            "report_path": DEFAULT_REPORT_PATH.as_posix(),
            "readiness_artifact": DEFAULT_READINESS_PATH.as_posix(),
        },
        "handoff": {
            "allowed": clearance_granted,
            "current_chat_owner_role": STARTUP_GOVERNOR_AGENT,
            "current_chat_owner_display_name": governor_display_name,
            "next_owner_role": next_owner_role,
            "next_owner_display_name": next_owner_display_name,
        },
        "context_snapshot": snapshot,
        "context_fingerprint": fingerprint,
        "invalidate_when": [
            "branch atual mudar",
            "dirty tree mudar",
            "active execution mudar",
            "worklog Doing mudar",
            "status de GitHub/GraphQL mudar",
            "status de Jira/Confluence ou fallback mudar",
            "agent enablement mudar",
            "pending_action mudar",
            "manifest evidence mudar",
        ],
    }


def load_pending_chat_contracts(repo_root: Path) -> list[ChatContractEntry]:
    register_path = (repo_root / CHAT_CONTRACTS_REGISTER_PATH).resolve()
    content = _read_utf8(register_path)
    entries: list[ChatContractEntry] = []
    for row in _table_rows_between(content, *PENDING_MARKERS):
        if len(row) != 6:
            continue
        entries.append(
            ChatContractEntry(
                contract_id=row[0],
                summary=row[1],
                evidence=row[2],
                owner=row[3],
                destination=row[4],
                status=row[5],
            )
        )
    return entries


def startup_session_payload(
    repo_root: Path,
    *,
    include_runtime_probes: bool = True,
    pending_action: str = "",
) -> dict[str, Any]:
    normalized_pending_action = _normalize_pending_action(pending_action)
    resolved_paths = resolve_startup_manifest_paths(repo_root)
    manifest_evidence = manifest_evidence_payload(repo_root, resolved_paths)
    pending_contracts = load_pending_chat_contracts(repo_root)
    git_inventory = git_inventory_payload(repo_root)
    active_worklog_items = load_active_worklog_items(repo_root)
    active_execution = active_execution_payload(repo_root)
    agent_identity = agent_identity_payload(repo_root, active_execution)
    enablement = agent_enablement_payload(repo_root)
    agent_runtime = agent_runtime_payload(repo_root)
    atlassian_actor_state = actor_runtime_state(repo_root)
    if active_execution.get("status") == "ok":
        active_execution["agent_display_name"] = agent_identity["active_display_name"]
    prioritized_work_item = prioritized_work_item_payload(active_execution, active_worklog_items)
    startup_drift = startup_drift_payload(active_execution, active_worklog_items, git_inventory)
    rules_projections = rules_projections_payload(repo_root)
    chat_communication = chat_communication_payload(repo_root, rules_projections)
    git_governance = git_governance_payload(repo_root, rules_projections)
    pea_status = pea_status_payload(repo_root, resolved_paths)
    delegation_context = delegation_context_payload(prioritized_work_item, git_inventory)
    fallback_status = (
        fallback_status_payload(repo_root)
        if include_runtime_probes
        else {
            "mode": "skipped",
            "jira_available": False,
            "jira_reason": "runtime-probes-disabled",
            "active_fallback_count": 0,
            "resolved_fallback_count": 0,
            "tracker_doing_count": len(active_worklog_items),
            "active_records": [],
            "guidance": "Runtime probes desabilitados para este payload.",
            "ledger_path": "docs/AI-FALLBACK-LEDGER.md",
            "tracker_path": "docs/AI-WIP-TRACKER.md",
        }
    )
    github_auth = (
        github_auth_summary(repo_root)
        if include_runtime_probes
        else {
            "status": "skipped",
            "fallback_chain": GITHUB_FALLBACK_CHAIN,
            "active_sources_current_shell": [],
            "active_sources_without_env_tokens": [],
            "ssh_signing_keys_probe": "skipped",
            "user_installations_probe": "skipped",
            "graphql_probe": {"status": "skipped", "note": "runtime-probes-disabled"},
            "recommendations": [],
        }
    )
    atlassian_connectivity = (
        atlassian_connectivity_summary(repo_root)
        if include_runtime_probes
        else {"status": "skipped", "overall_ok": False, "recovery_hints": []}
    )
    startup_governor_status = startup_governor_status_payload(
        repo_root,
        manifest_evidence=manifest_evidence,
        pending_contracts=pending_contracts,
        git_inventory=git_inventory,
        active_worklog_items=active_worklog_items,
        active_execution=active_execution,
        agent_identity=agent_identity,
        agent_enablement=enablement,
        agent_runtime=agent_runtime,
        rules_projections=rules_projections,
        chat_communication=chat_communication,
        git_governance=git_governance,
        pea_status=pea_status,
        startup_drift=startup_drift,
        fallback_status=fallback_status,
        github_auth=github_auth,
        atlassian_connectivity=atlassian_connectivity,
        prioritized_work_item=prioritized_work_item,
        pending_action=normalized_pending_action,
    )
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "manifest_path": MANIFEST_PATH.as_posix(),
        "chat_contracts_register_path": CHAT_CONTRACTS_REGISTER_PATH.as_posix(),
        "resolved_paths": resolved_paths,
        "resolved_count": len(resolved_paths),
        "manifest_evidence": manifest_evidence,
        "pending_chat_contracts": [asdict(entry) for entry in pending_contracts],
        "pending_chat_contract_count": len(pending_contracts),
        "default_report_path": DEFAULT_REPORT_PATH.as_posix(),
        "default_readiness_path": DEFAULT_READINESS_PATH.as_posix(),
        "pending_action": normalized_pending_action,
        "git_inventory": git_inventory,
        "active_worklog_items": active_worklog_items,
        "active_worklog_count": len(active_worklog_items),
        "active_execution": active_execution,
        "agent_identity": agent_identity,
        "agent_enablement": enablement,
        "agent_runtime": agent_runtime,
        "atlassian_actor_state": atlassian_actor_state,
        "rules_projections": rules_projections,
        "chat_communication": chat_communication,
        "git_governance": git_governance,
        "pea_status": pea_status,
        "delegation_context": delegation_context,
        "startup_drift": startup_drift,
        "fallback_status": fallback_status,
        "github_auth": github_auth,
        "atlassian_connectivity": atlassian_connectivity,
        "prioritized_work_item": prioritized_work_item,
        "startup_governor_status": startup_governor_status,
    }


def render_startup_session_markdown(payload: dict[str, Any]) -> str:
    manifest_evidence = payload["manifest_evidence"]
    lines = [
        "# AI Startup Session Report",
        "",
        f"- Gerado em: `{payload['generated_at']}`",
        f"- Manifest canonico: `{payload['manifest_path']}`",
        f"- Registro de contratos do chat: `{payload['chat_contracts_register_path']}`",
        f"- Total de arquivos textuais resolvidos: `{payload['resolved_count']}`",
        f"- Linhas textuais relidas: `{manifest_evidence.get('textual_line_count', 0)}`",
        f"- Bytes textuais relidos: `{manifest_evidence.get('textual_bytes', 0)}`",
        f"- Digest do startup: `{manifest_evidence.get('sha256', '')}`",
        f"- Total de contratos do chat ainda pendentes: `{payload['pending_chat_contract_count']}`",
        f"- Worklogs ativos no fallback local: `{payload['active_worklog_count']}`",
        f"- Pending action aplicada: `{payload.get('pending_action', '') or 'nenhuma'}`",
        "",
        "## Arquivos canonicos resolvidos",
        "",
    ]
    for relative in payload["resolved_paths"]:
        lines.append(f"- `{relative}`")
    if manifest_evidence.get("missing_paths"):
        for relative in manifest_evidence.get("missing_paths", []):
            lines.append(f"- caminho ausente ao reler o manifest: `{relative}`")
    lines.extend(["", "## Contratos do chat ainda pendentes", ""])
    pending = payload["pending_chat_contracts"]
    if not pending:
        lines.append("- nenhum contrato pendente registrado")
    else:
        lines.extend(
            [
                "| ID | Contrato resumido | Work item dono | Destino perene esperado |",
                "| --- | --- | --- | --- |",
            ]
        )
        for entry in pending:
            lines.append(
                f"| {entry['contract_id']} | {entry['summary']} | {entry['owner']} | {entry['destination']} |"
            )

    chat_communication = payload["chat_communication"]
    agent_identity = payload["agent_identity"]
    agent_enablement = payload["agent_enablement"]
    agent_runtime = payload["agent_runtime"]
    rules_projections = payload["rules_projections"]
    lines.extend(["", "## Comunicacao no chat e identidade", ""])
    lines.append(
        f"- agente ativo visivel: `{agent_identity.get('active_display_name', 'desconhecido')}`"
    )
    lines.append(
        f"- agente ativo no chat: `{agent_identity.get('active_chat_name', 'desconhecido')}`"
    )
    lines.append(
        f"- fallback de exibicao quando faltar display_name: `{agent_identity.get('fallback_display', 'technical-id')}`"
    )
    lines.append(
        "- ordem de fallback do nome visivel: "
        f"`{', '.join(agent_identity.get('chat_name_fallback_order', [])) or 'technical-id'}`"
    )
    for rule in chat_communication.get("rules", []):
        lines.append(f"- regra de comunicacao: {rule}")
    if chat_communication.get("human_source"):
        lines.append(f"- fonte humana: `{chat_communication.get('human_source', '')}`")
    if chat_communication.get("machine_projection"):
        lines.append(f"- projecao executavel: `{chat_communication.get('machine_projection', '')}`")

    lines.extend(["", "## Projecoes .rules criticas", ""])
    lines.append(f"- catalogo declarativo: `{rules_projections.get('catalog_path', '')}`")
    lines.append(
        "- projecoes obrigatorias no startup: "
        f"`{', '.join(rules_projections.get('required_for_startup', [])) or 'nenhuma'}`"
    )
    lines.append(
        "- projecoes carregadas: "
        f"`{', '.join(rules_projections.get('loaded_for_startup', [])) or 'nenhuma'}`"
    )
    if rules_projections.get("missing_required"):
        lines.append(
            f"- projecoes faltantes: `{', '.join(rules_projections.get('missing_required', []))}`"
        )
    for projection_id, entry in sorted((rules_projections.get("projections") or {}).items()):
        if not isinstance(entry, dict):
            continue
        lines.append(
            f"- {projection_id}: `{entry.get('machine_projection', '')}` <- "
            f"`{entry.get('human_source', '')}` ({entry.get('status', 'unknown')})"
        )

    lines.extend(["", "## Enablement efetivo de agentes", ""])
    lines.append(f"- status: `{agent_enablement.get('status', 'unknown')}`")
    lines.append(f"- base declarativa: `{agent_enablement.get('agents_path', '')}`")
    lines.append(f"- overlay declarativo: `{agent_enablement.get('overlay_path', '')}`")
    lines.append(f"- overlay local ativo: `{agent_enablement.get('overlay_local_active', False)}`")
    lines.append(
        f"- total de roles declaradas no overlay: `{len(agent_enablement.get('declared_roles', []))}`"
    )
    lines.append(
        f"- roles efetivamente habilitadas: `{len(agent_enablement.get('enabled_roles', []))}`"
    )
    lines.append(
        f"- roles efetivamente desabilitadas: `{len(agent_enablement.get('disabled_roles', []))}`"
    )
    lines.append(
        "- agentes declarativos desabilitados: "
        f"`{', '.join(agent_enablement.get('disabled_registry_agents', [])) or 'nenhum'}`"
    )
    if agent_enablement.get("overridden_roles"):
        lines.append(
            "- overrides efetivos de enablement: "
            f"`{', '.join(agent_enablement.get('overridden_roles', []))}`"
        )
    if agent_enablement.get("required_roles_disabled"):
        lines.append(
            "- required desabilitados no overlay: "
            f"`{', '.join(agent_enablement.get('required_roles_disabled', []))}`"
        )
    if agent_enablement.get("error"):
        lines.append(f"- erro: `{agent_enablement.get('error', '')}`")

    lines.extend(["", "## Runtime operacional de agentes", ""])
    lines.append(f"- status: `{agent_runtime.get('status', 'unknown')}`")
    lines.append(f"- contrato de runtime: `{agent_runtime.get('runtime_path', '')}`")
    lines.append(
        f"- overlay local de runtime ativo: `{agent_runtime.get('runtime_local_active', False)}`"
    )
    lines.append(
        "- fallback visivel de chat/Jira: "
        f"`{', '.join(agent_runtime.get('chat_name_fallback_order', [])) or 'technical-id'}`"
    )
    lines.append(
        f"- roles cobertos por runtime: `{len(agent_runtime.get('covered_roles', []))}`"
    )
    lines.append(
        f"- agentes declarativos cobertos por runtime: `{len(agent_runtime.get('covered_registry_agents', []))}`"
    )
    lines.append(
        "- roles aptos a ownership de chat: "
        f"`{', '.join(agent_runtime.get('chat_owner_capable_roles', [])) or 'nenhum'}`"
    )
    lines.append(
        "- roles habilitados sem principal Jira mapeado: "
        f"`{', '.join(agent_runtime.get('enabled_roles_missing_jira_assignee_mapping', [])) or 'nenhum'}`"
    )
    lines.append(
        "- roles com service account propria: "
        f"`{', '.join(agent_runtime.get('enabled_roles_with_atlassian_actor', [])) or 'nenhum'}`"
    )
    lines.append(
        "- roles em fallback global Atlassian: "
        f"`{', '.join(agent_runtime.get('enabled_roles_using_global_atlassian_actor', [])) or 'nenhum'}`"
    )
    lines.append(
        "- roles com service account incompleta: "
        f"`{', '.join(agent_runtime.get('enabled_roles_with_incomplete_atlassian_actor', [])) or 'nenhum'}`"
    )
    surface_matrix = agent_runtime.get("atlassian_actor_surface_matrix", {})
    if isinstance(surface_matrix, dict) and surface_matrix:
        for role_id, surfaces in sorted(surface_matrix.items()):
            if not isinstance(surfaces, list):
                continue
            lines.append(
                f"- surfaces Atlassian de `{role_id}`: `{', '.join(str(item) for item in surfaces) or 'nenhuma'}`"
            )
    actor_state = payload.get("atlassian_actor_state", {})
    if isinstance(actor_state, dict):
        lines.append(
            "- resolucoes com search fallback na ultima rodada: "
            f"`{', '.join(actor_state.get('search_fallback_resolutions', [])) or 'nenhuma'}`"
        )
    if agent_runtime.get("missing_roles"):
        lines.append(
            "- roles sem runtime: "
            f"`{', '.join(agent_runtime.get('missing_roles', []))}`"
        )
    if agent_runtime.get("missing_registry_agents"):
        lines.append(
            "- agentes declarativos sem runtime: "
            f"`{', '.join(agent_runtime.get('missing_registry_agents', []))}`"
        )
    if agent_runtime.get("required_roles_without_operational_runtime"):
        lines.append(
            "- roles required sem runtime operacional: "
            f"`{', '.join(agent_runtime.get('required_roles_without_operational_runtime', []))}`"
        )
    if agent_runtime.get("duplicate_enabled_role_visible_names"):
        lines.append(
            "- aliases visiveis duplicados: "
            f"`{', '.join(agent_runtime.get('duplicate_enabled_role_visible_names', []))}`"
        )
    if agent_runtime.get("error"):
        lines.append(f"- erro: `{agent_runtime.get('error', '')}`")

    git_governance = payload["git_governance"]
    lines.extend(["", "## Governanca Git carregada no startup", ""])
    for source in git_governance.get("sources", []):
        lines.append(f"- fonte carregada: `{source}`")
    for rule in git_governance.get("rules", []):
        lines.append(f"- contrato Git lembrado: {rule}")
    if git_governance.get("human_source"):
        lines.append(f"- fonte humana: `{git_governance.get('human_source', '')}`")
    if git_governance.get("machine_projection"):
        lines.append(f"- projecao executavel: `{git_governance.get('machine_projection', '')}`")
    lines.append(f"- enforcement: {git_governance.get('enforcement_note', '')}")

    pea_status = payload["pea_status"]
    lines.extend(["", "## PEA carregado no startup", ""])
    lines.append(f"- status: `{pea_status.get('status', 'unknown')}`")
    lines.append(f"- catalogo: `{pea_status.get('catalog_path', '')}`")
    lines.append(f"- pack formal: `{pea_status.get('pack_root', '')}`")
    lines.append(
        f"- startup carrega o pack formal: `{pea_status.get('startup_loads_pack', False)}`"
    )
    if pea_status.get("missing_paths"):
        for path in pea_status.get("missing_paths", []):
            lines.append(f"- caminho ausente: `{path}`")
    for mode in pea_status.get("execution_modes", []):
        lines.append(f"- modo PEA suportado: `{mode}`")
    lines.append(f"- separacao de camadas: {pea_status.get('separation_note', '')}")

    git_inventory = payload["git_inventory"]
    lines.extend(["", "## Inventario Git e worktree", ""])
    if git_inventory.get("status") != "ok":
        lines.append(
            f"- inventario indisponivel: `{git_inventory.get('error', 'erro nao detalhado')}`"
        )
    else:
        lines.append(f"- branch atual: `{git_inventory['current_branch']}`")
        lines.append(f"- branches locais abertas: `{git_inventory['local_branch_count']}`")
        lines.append(
            "- branches locais ja absorvidas e ainda abertas: "
            f"`{len(git_inventory['merged_local_branches'])}`"
        )
        lifecycle = git_inventory.get("branch_lifecycle", {})
        lines.append(f"- upstream da branch atual: `{lifecycle.get('upstream', '') or 'nenhum'}`")
        lines.append(
            f"- ahead/behind da branch atual: `+{lifecycle.get('ahead_count', 0)} / -{lifecycle.get('behind_count', 0)}`"
        )
        lines.append(
            f"- branch atual absorvida em origin/main: `{lifecycle.get('absorbed_in_origin_main', False)}`"
        )
        lines.append(
            f"- branch atual candidata a poda: `{lifecycle.get('prune_candidate', False)}`"
        )
        lines.append(f"- worktrees abertas: `{len(git_inventory['worktrees'])}`")
        lines.append(f"- dirty entries: `{len(git_inventory['dirty_entries'])}`")
        for branch in git_inventory["merged_local_branches"]:
            lines.append(f"- branch residual absorvida: `{branch}`")
        for worktree in git_inventory["worktrees"]:
            lines.append(
                f"- worktree: `{worktree.get('path', '')}` | branch=`{worktree.get('branch', '') or '(detached)'}`"
            )
        if git_inventory["open_prs_for_current_branch"]:
            for pr in git_inventory["open_prs_for_current_branch"]:
                lines.append(
                    f"- PR aberto da branch atual: [#{pr.get('number')} - {pr.get('title')}]({pr.get('url')})"
                )
        else:
            lines.append("- PRs abertos da branch atual: nenhum detectado")
        if git_inventory.get("pr_probe_status") != "ok":
            lines.append(f"- probe de PRs do gh: `{git_inventory.get('pr_probe_note', '')}`")

    lines.extend(["", "## Execucao ativa e worklog", ""])
    active_execution = payload["active_execution"]
    if active_execution.get("status") == "ok":
        lines.append(
            f"- contexto ativo: `{active_execution['issue_key']}` - {active_execution['issue_summary']}"
        )
        lines.append(f"- agente ativo: `{active_execution['agent_display_name']}`")
        lines.append(f"- id tecnico do agente ativo: `{active_execution['agent']}`")
        lines.append(f"- status do fluxo: `{active_execution['workflow_status']}`")
        lines.append(f"- branch do contexto ativo: `{active_execution['branch']}`")
    else:
        lines.append("- contexto ativo: nenhum contexto local valido encontrado")
    if payload["active_worklog_items"]:
        lines.extend(
            [
                "",
                "| ID | Tarefa | Branch | Proximo passo |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in payload["active_worklog_items"]:
            lines.append(
                f"| {item['ID']} | {item['Tarefa']} | {item['Branch']} | {item['Proximo passo']} |"
            )
    else:
        lines.append("- worklogs ativos no tracker local: nenhum")

    startup_drift = payload["startup_drift"]
    lines.extend(["", "## Drift operacional detectado", ""])
    if startup_drift.get("status") == "clean":
        lines.append("- nenhum drift objetivo detectado entre branch, worklog e contexto ativo")
    else:
        for finding in startup_drift.get("findings", []):
            lines.append(f"- drift: {finding}")

    fallback_status = payload["fallback_status"]
    lines.extend(["", "## Fallback local", ""])
    lines.append(f"- modo: `{fallback_status.get('mode', 'desconhecido')}`")
    lines.append(f"- Jira disponivel: `{fallback_status.get('jira_available', False)}`")
    lines.append(f"- motivo/probe: `{fallback_status.get('jira_reason', '')}`")
    lines.append(f"- guidance: {fallback_status.get('guidance', '')}")

    github_auth = payload["github_auth"]
    lines.extend(["", "## GitHub auth e fallback", ""])
    lines.append(f"- status do probe GitHub: `{github_auth.get('status', 'unknown')}`")
    lines.append(
        "- fontes ativas no shell atual: "
        f"`{', '.join(github_auth.get('active_sources_current_shell', [])) or 'nenhuma'}`"
    )
    lines.append(
        "- fontes ativas sem env tokens: "
        f"`{', '.join(github_auth.get('active_sources_without_env_tokens', [])) or 'nenhuma'}`"
    )
    lines.append(
        f"- probe user/ssh_signing_keys: `{github_auth.get('ssh_signing_keys_probe', 'unknown')}`"
    )
    lines.append(
        f"- probe user/installations: `{github_auth.get('user_installations_probe', 'unknown')}`"
    )
    graphql_probe = github_auth.get("graphql_probe", {})
    lines.append(f"- probe GraphQL: `{graphql_probe.get('status', 'unknown')}`")
    if graphql_probe.get("note"):
        lines.append(f"- detalhe GraphQL: `{graphql_probe.get('note')}`")
    lines.append("- cadeia documentada de fallback GitHub/PAT:")
    for entry in github_auth.get("fallback_chain", []):
        lines.append(f"  - `{entry}`")
    for recommendation in github_auth.get("recommendations", []):
        lines.append(f"- recomendacao: {recommendation}")

    atlassian = payload["atlassian_connectivity"]
    lines.extend(["", "## Atlassian", ""])
    lines.append(f"- status do probe Atlassian: `{atlassian.get('status', 'unknown')}`")
    if atlassian.get("site_url"):
        lines.append(f"- site: `{atlassian['site_url']}`")
    if atlassian.get("auth_mode"):
        lines.append(f"- auth mode: `{atlassian['auth_mode']}`")
    if atlassian.get("cloud_id"):
        lines.append(f"- cloud_id: `{atlassian['cloud_id']}`")
    if atlassian.get("jira_project_key"):
        lines.append(f"- projeto Jira: `{atlassian['jira_project_key']}`")
    if atlassian.get("confluence_space_key"):
        lines.append(f"- space Confluence: `{atlassian['confluence_space_key']}`")
    if atlassian.get("jira_status"):
        lines.append(f"- Jira: `{atlassian['jira_status']}`")
    if atlassian.get("confluence_status"):
        lines.append(f"- Confluence: `{atlassian['confluence_status']}`")
    for hint in atlassian.get("recovery_hints", []):
        lines.append(f"- recovery Atlassian: {hint}")

    prioritized = payload["prioritized_work_item"]
    lines.extend(["", "## Work item priorizado", ""])
    lines.append(f"- fonte: `{prioritized['source']}`")
    if prioritized.get("identifier"):
        lines.append(f"- identificador: `{prioritized['identifier']}`")
    lines.append(f"- resumo: {prioritized['summary']}")

    delegation = payload["delegation_context"]
    lines.extend(["", "## Delegacao e subagentes", ""])
    if delegation.get("owner_issue"):
        lines.append(f"- issue dona para delegacao: `{delegation['owner_issue']}`")
    lines.append(f"- branch base para delegacao: `{delegation.get('current_branch', '')}`")
    for path in delegation.get("required_paths", []):
        lines.append(f"- arquivo obrigatorio para contexto de subagente: `{path}`")
    for rule in delegation.get("rules", []):
        lines.append(f"- regra de subagente: {rule}")
    lines.append("- regra de subagente: repassar classificacao do PEA quando aplicavel")

    governor = payload["startup_governor_status"]
    lines.extend(["", "## startup_governor_status", ""])
    lines.append(f"- owner_role: `{governor.get('owner_role', '')}`")
    lines.append(f"- owner_display_name: `{governor.get('owner_display_name', '')}`")
    lines.append(f"- audit_owner_role: `{governor.get('audit_owner_role', '')}`")
    lines.append(f"- state: `{governor.get('state', 'unknown')}`")
    lines.append(f"- clearance: `{governor.get('clearance', 'blocked')}`")
    lines.append(
        f"- readiness_artifact: `{payload.get('readiness_artifact_path', payload.get('default_readiness_path', ''))}`"
    )
    lines.append(
        f"- current_chat_owner: `{governor.get('handoff', {}).get('current_chat_owner_display_name', '')}`"
    )
    if governor.get("handoff", {}).get("next_owner_role"):
        lines.append(
            "- proximo owner operacional elegivel: "
            f"`{governor.get('handoff', {}).get('next_owner_display_name', '')}` "
            f"(`{governor.get('handoff', {}).get('next_owner_role', '')}`)"
        )
    if governor.get("blocking_findings"):
        for finding in governor.get("blocking_findings", []):
            lines.append(f"- bloqueio: {finding}")
    else:
        lines.append("- bloqueio: nenhum")
    for warning in governor.get("warnings", []):
        lines.append(f"- aviso: {warning}")
    lines.append(f"- context_fingerprint: `{governor.get('context_fingerprint', '')}`")

    lines.extend(
        [
            "",
            "## Acoes obrigatorias da sessao",
            "",
            "- reler integralmente todos os arquivos resolvidos antes de operar",
            "- avisar o usuario se a tabela de contratos pendentes nao estiver vazia",
            "- carregar o contrato de comunicacao e a camada de display_name antes da primeira resposta operacional ao usuario",
            "- carregar o catalogo de prompt packs e expor `pea_status` antes de operar por memoria residual",
            "- materializar `startup_governor_status` e `.cache/ai/startup-ready.json` antes do handoff operacional",
            "- validar `gh auth status` e, se o fluxo de GitHub ou GraphQL falhar, consultar a cadeia de fallback documentada em `docs/secrets-and-auth.md` antes de concluir que o `gh` esta bloqueado",
            "- quando a rodada depender de Jira ou Confluence, confirmar tambem o probe resumido dessas plataformas antes de operar por memoria",
            "- nao delegar para subagentes sem pacote minimo de contexto, owner issue e regras aplicaveis",
            "- cruzar branch, worktree e work item antes de decidir commit, PR ou redistribuicao",
        ]
    )
    return "\n".join(lines) + "\n"


def write_startup_session_report(
    repo_root: Path,
    *,
    out_path: Path | None = None,
    ready_out: Path | None = None,
    include_runtime_probes: bool = True,
    pending_action: str = "",
) -> dict[str, Any]:
    payload = startup_session_payload(
        repo_root,
        include_runtime_probes=include_runtime_probes,
        pending_action=pending_action,
    )
    report_path = (repo_root / (out_path or DEFAULT_REPORT_PATH)).resolve()
    readiness_path = (repo_root / (ready_out or DEFAULT_READINESS_PATH)).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    readiness_path.parent.mkdir(parents=True, exist_ok=True)
    payload["report_path"] = report_path.relative_to(repo_root).as_posix()
    payload["readiness_artifact_path"] = readiness_path.relative_to(repo_root).as_posix()
    governor_status = dict(payload["startup_governor_status"])
    governor_status["harness"] = {
        **governor_status.get("harness", {}),
        "report_path": payload["report_path"],
        "readiness_artifact": payload["readiness_artifact_path"],
    }
    payload["startup_governor_status"] = governor_status
    report_text = render_startup_session_markdown(payload)
    report_path.write_text(report_text, encoding="utf-8")
    readiness_path.write_text(
        json.dumps(payload["startup_governor_status"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload


def payload_as_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
