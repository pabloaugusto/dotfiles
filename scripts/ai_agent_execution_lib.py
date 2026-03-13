from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any
from urllib.parse import quote

from scripts.ai_atlassian_actor_lib import global_jira_adapter, with_jira_actor
from scripts.ai_control_plane_lib import load_ai_control_plane
from scripts.atlassian_platform_lib import JiraAdapter

WORKFLOW_ORDER = [
    ("backlog", {"backlog"}),
    ("refinement", {"refinement"}),
    ("ready", {"ready", "selected for development", "selected for dev"}),
    ("doing", {"doing", "in progress", "in_progress", "executando"}),
    ("paused", {"paused", "on hold", "pausado"}),
    ("testing", {"testing"}),
    ("review", {"review"}),
    ("changes requested", {"changes requested", "changes_requested"}),
    ("done", {"done", "completed", "complete", "closed", "concluido", "concluida"}),
    ("cancelled", {"cancelled", "canceled"}),
]
MAINLINE_ORDER = ["backlog", "refinement", "ready", "doing", "testing", "review", "done"]
MAINLINE_INDEX = {name: idx for idx, name in enumerate(MAINLINE_ORDER)}
WORKFLOW_INDEX = {name: idx for idx, (name, _) in enumerate(WORKFLOW_ORDER)}
WORKFLOW_STATUS_ALIASES = {
    "backlog": "backlog",
    "triage": "backlog",
    "refinement": "refinement",
    "ready": "ready",
    "selected for development": "ready",
    "selected for dev": "ready",
    "doing": "doing",
    "in progress": "doing",
    "in_progress": "doing",
    "executando": "doing",
    "paused": "paused",
    "on hold": "paused",
    "pausado": "paused",
    "testing": "testing",
    "review": "review",
    "changes requested": "changes requested",
    "changes_requested": "changes requested",
    "done": "done",
    "completed": "done",
    "complete": "done",
    "closed": "done",
    "concluido": "done",
    "concluida": "done",
    "cancelled": "cancelled",
    "canceled": "cancelled",
}


class AgentExecutionError(RuntimeError):
    """Raised when the local agent execution contract cannot be applied safely."""


@dataclass(frozen=True)
class AgentExecutionContext:
    issue_key: str
    issue_summary: str
    issue_url: str
    agent: str
    agent_id: str
    status: str
    current_agent_role: str
    current_agent_role_id: str
    next_required_role: str
    next_required_role_id: str
    branch: str
    worktree_root: str
    started_at: str
    updated_at: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def default_context_path(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    return root / ".cache" / "ai" / "active-execution.json"


def normalize_status(value: str) -> str:
    normalized = str(value or "").strip().casefold()
    return WORKFLOW_STATUS_ALIASES.get(normalized, normalized)


def current_branch(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    branch = (completed.stdout or "").strip()
    return branch or "unknown"


def resolve_jira(repo_root: Path) -> JiraAdapter:
    return global_jira_adapter(repo_root)


def issue_url(jira: JiraAdapter, issue_key: str) -> str:
    resolved = getattr(jira.client, "resolved", None)
    site_url = str(getattr(resolved, "site_url", "")).strip().rstrip("/")
    if not site_url:
        return issue_key
    return f"{site_url}/browse/{issue_key}"


def role_reference_payload(repo_root: Path, raw_reference: str) -> dict[str, str]:
    normalized = str(raw_reference or "").strip()
    if not normalized:
        return {
            "role_id": "",
            "visible_name": "",
            "formal_name": "",
            "assignee_account_id": "",
        }
    try:
        control_plane = load_ai_control_plane(repo_root)
        resolved_role_id = control_plane.resolve_role_reference(normalized) or normalized
    except Exception:
        resolved_role_id = normalized
    return role_visibility_payload(repo_root, resolved_role_id)


def load_context_identity(
    repo_root: Path,
    *,
    visible_value: str,
    role_id: str,
) -> tuple[str, str]:
    normalized_visible = str(visible_value or "").strip()
    normalized_role_id = str(role_id or "").strip()
    if normalized_role_id:
        payload = role_reference_payload(repo_root, normalized_role_id)
        visible = normalized_visible
        if not visible or visible == normalized_role_id:
            visible = (
                payload.get("visible_name", "").strip()
                or payload.get("formal_name", "").strip()
                or normalized_role_id
            )
        return visible, (payload.get("role_id", "").strip() or normalized_role_id)
    if normalized_visible:
        payload = role_reference_payload(repo_root, normalized_visible)
        visible = (
            payload.get("visible_name", "").strip()
            or payload.get("formal_name", "").strip()
            or normalized_visible
        )
        return visible, (payload.get("role_id", "").strip() or normalized_visible)
    return "", ""


def load_context(repo_root: str | Path | None = None) -> AgentExecutionContext | None:
    context_path = default_context_path(repo_root)
    if not context_path.exists():
        return None
    try:
        payload = json.loads(context_path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        raise AgentExecutionError(f"Contexto ativo corrompido em {context_path}.") from exc
    if not isinstance(payload, dict):
        raise AgentExecutionError("Contexto ativo em formato invalido.")
    repo = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    agent, agent_id = load_context_identity(
        repo,
        visible_value=str(payload.get("agent", "")).strip(),
        role_id=str(payload.get("agent_id", "")).strip(),
    )
    current_agent_role, current_agent_role_id = load_context_identity(
        repo,
        visible_value=str(payload.get("current_agent_role", "")).strip(),
        role_id=str(payload.get("current_agent_role_id", "")).strip(),
    )
    next_required_role, next_required_role_id = load_context_identity(
        repo,
        visible_value=str(payload.get("next_required_role", "")).strip(),
        role_id=str(payload.get("next_required_role_id", "")).strip(),
    )
    return AgentExecutionContext(
        issue_key=str(payload.get("issue_key", "")).strip(),
        issue_summary=str(payload.get("issue_summary", "")).strip(),
        issue_url=str(payload.get("issue_url", "")).strip(),
        agent=agent,
        agent_id=agent_id,
        status=normalize_status(str(payload.get("status", "")).strip()),
        current_agent_role=current_agent_role,
        current_agent_role_id=current_agent_role_id,
        next_required_role=next_required_role,
        next_required_role_id=next_required_role_id,
        branch=str(payload.get("branch", "")).strip(),
        worktree_root=str(payload.get("worktree_root", "")).strip(),
        started_at=str(payload.get("started_at", "")).strip(),
        updated_at=str(payload.get("updated_at", "")).strip(),
    )


def save_context(context: AgentExecutionContext, repo_root: str | Path | None = None) -> Path:
    context_path = default_context_path(repo_root)
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(
        json.dumps(asdict(context), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return context_path


def clear_context(repo_root: str | Path | None = None) -> None:
    context_path = default_context_path(repo_root)
    if context_path.exists():
        context_path.unlink()


def issue_summary(jira: JiraAdapter, issue_key: str) -> str:
    issue = jira.get_issue(issue_key, fields=["summary"])
    fields = issue.get("fields") or {}
    summary = str(fields.get("summary", "")).strip()
    if not summary:
        raise AgentExecutionError(f"Issue sem summary legivel: {issue_key}")
    return summary


def adf_to_text(node: Any) -> str:
    if isinstance(node, dict):
        if str(node.get("type", "")).strip() == "text":
            return str(node.get("text", ""))
        content = node.get("content")
        if isinstance(content, list):
            return "".join(adf_to_text(item) for item in content)
        return ""
    if isinstance(node, list):
        return "".join(adf_to_text(item) for item in node)
    return ""


def normalize_text_for_dedup(value: str) -> str:
    return " ".join(str(value or "").split()).strip().casefold()


def render_structured_comment(
    *,
    agent: str,
    interaction_type: str,
    status: str,
    contexto: list[str],
    evidencias: list[str],
    proximo_passo: str,
) -> str:
    lines = [
        f"Agent: {agent}",
        f"Interaction Type: {interaction_type}",
        f"Status: {status}",
    ]
    if contexto:
        lines.extend(["", "Contexto:"])
        lines.extend(f"- {item}" for item in contexto)
    if evidencias:
        lines.extend(["", "Evidencias:"])
        lines.extend(f"- {item}" for item in evidencias)
    if proximo_passo.strip():
        lines.extend(["", f"Proximo passo: {proximo_passo.strip()}"])
    return "\n".join(lines).strip()


def list_comments(
    jira: JiraAdapter, issue_key: str, *, max_results: int = 200
) -> list[dict[str, Any]]:
    payload = jira.client.request_json(
        "jira",
        f"/rest/api/3/issue/{quote(issue_key, safe='')}/comment",
        params={"maxResults": str(max_results)},
    )
    if not isinstance(payload, dict):
        raise AgentExecutionError("Jira list_comments retornou payload inesperado.")
    comments = payload.get("comments")
    if not isinstance(comments, list):
        raise AgentExecutionError("Jira list_comments retornou comments em formato inesperado.")
    return [entry for entry in comments if isinstance(entry, dict)]


def ensure_comment(jira: JiraAdapter, issue_key: str, body_text: str) -> dict[str, Any]:
    desired = normalize_text_for_dedup(body_text)
    for comment in list_comments(jira, issue_key):
        current = normalize_text_for_dedup(adf_to_text(comment.get("body")))
        if current == desired:
            return comment
    return jira.add_comment(issue_key, body_text)


def field_catalog_by_name(jira: JiraAdapter) -> dict[str, str]:
    start_at = 0
    catalog: dict[str, str] = {}
    while True:
        payload = jira.client.request_json(
            "jira",
            "/rest/api/3/field/search",
            params={"startAt": str(start_at), "maxResults": "100"},
        )
        if not isinstance(payload, dict):
            raise AgentExecutionError("Jira field search retornou payload inesperado.")
        values = payload.get("values")
        if not isinstance(values, list):
            raise AgentExecutionError("Jira field search retornou values em formato inesperado.")
        for item in values:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            field_id = str(item.get("id", "")).strip()
            if name and field_id:
                catalog[name] = field_id
        if payload.get("isLast") is True or not values:
            break
        start_at += len(values)
    return catalog


def role_visibility_payload(repo_root: Path, role_id: str) -> dict[str, str]:
    normalized_role_id = role_id.strip()
    if not normalized_role_id:
        return {
            "role_id": "",
            "visible_name": "",
            "formal_name": "",
        }
    try:
        control_plane = load_ai_control_plane(repo_root)
    except Exception:
        return {
            "role_id": normalized_role_id,
            "visible_name": normalized_role_id,
            "formal_name": normalized_role_id,
        }
    return {
        "role_id": normalized_role_id,
        "visible_name": control_plane.visible_name_for_agent(normalized_role_id),
        "formal_name": control_plane.formal_name_for_agent(normalized_role_id)
        or normalized_role_id,
    }


def sync_agent_roles(
    jira: JiraAdapter,
    issue_key: str,
    *,
    repo_root: Path,
    acting_agent: str,
    current_agent_role: str,
    next_required_role: str,
    assignee_account_id: str = "",
) -> dict[str, Any]:
    current_visibility = role_visibility_payload(repo_root, current_agent_role)
    next_visibility = role_visibility_payload(repo_root, next_required_role)
    acting_visibility = role_visibility_payload(repo_root, acting_agent or current_agent_role)
    try:
        control_plane = load_ai_control_plane(repo_root)
        jira_field_names = control_plane.jira_field_names()
    except Exception:
        jira_field_names = {
            "current_agent_role": "Current Agent Role",
            "next_required_role": "Next Required Role",
        }
    fields_catalog = field_catalog_by_name(jira)
    payload_fields: dict[str, Any] = {}
    current_field_id = fields_catalog.get(jira_field_names["current_agent_role"], "")
    next_field_id = fields_catalog.get(jira_field_names["next_required_role"], "")
    if current_field_id:
        payload_fields[current_field_id] = (
            {"value": current_visibility["visible_name"]}
            if current_visibility["visible_name"]
            else None
        )
    if next_field_id:
        payload_fields[next_field_id] = (
            {"value": next_visibility["visible_name"]} if next_visibility["visible_name"] else None
        )
    assignee_status = "skipped"
    normalized_assignee_account_id = str(assignee_account_id or "").strip()
    if normalized_assignee_account_id:
        payload_fields["assignee"] = {"accountId": normalized_assignee_account_id}
        assignee_status = "synced"
    elif acting_visibility["role_id"]:
        assignee_status = "unmapped"
    update_result = jira.update_issue_fields(issue_key, payload_fields) if payload_fields else {}
    return {
        "update_result": update_result,
        "current_agent_role_display": current_visibility["visible_name"],
        "next_required_role_display": next_visibility["visible_name"],
        "acting_agent_display": acting_visibility["visible_name"],
        "assignee_status": assignee_status,
        "assignee_account_id": normalized_assignee_account_id,
    }


def _choose_transition(jira: JiraAdapter, issue_key: str, target_status: str) -> dict[str, Any]:
    transitions = jira.get_transitions(issue_key)
    target = normalize_status(target_status)
    for transition in transitions:
        to_name = normalize_status(str(((transition.get("to") or {}).get("name")) or "").strip())
        if to_name == target:
            return transition
    raise AgentExecutionError(
        f"Nao foi encontrada transicao para {target_status!r} na issue {issue_key}."
    )


def ensure_issue_status(jira: JiraAdapter, issue_key: str, target_status: str) -> None:
    target = normalize_status(target_status)
    issue = jira.get_issue(issue_key, fields=["status"])
    current = normalize_status(
        str(((issue.get("fields") or {}).get("status") or {}).get("name") or "")
    )
    if current == target:
        return
    while current != target:
        transition = None
        try:
            transition = _choose_transition(jira, issue_key, target)
        except AgentExecutionError:
            if current in {"paused", "changes requested"} and target != current:
                transition = _choose_transition(jira, issue_key, "doing")
            else:
                current_index = MAINLINE_INDEX.get(current, -1)
                target_index = MAINLINE_INDEX.get(target, -1)
                if current_index < 0 or target_index < 0:
                    raise AgentExecutionError(
                        f"Nao foi possivel mapear a transicao logica de {current!r} para {target!r}."
                    )
                direction = 1 if target_index > current_index else -1
                next_index = current_index + direction
                next_status = MAINLINE_ORDER[next_index]
                transition = _choose_transition(jira, issue_key, next_status)
        jira.transition_issue(issue_key, str(transition.get("id", "")).strip())
        issue = jira.get_issue(issue_key, fields=["status"])
        updated = normalize_status(
            str(((issue.get("fields") or {}).get("status") or {}).get("name") or "")
        )
        if updated == current:
            raise AgentExecutionError(
                "Jira nao refletiu a transicao esperada para a issue "
                f"{issue_key}: status permaneceu em {current!r}."
            )
        current = updated


def read_issue_status(jira: JiraAdapter, issue_key: str) -> str:
    issue = jira.get_issue(issue_key, fields=["status"])
    return normalize_status(
        str(((issue.get("fields") or {}).get("status") or {}).get("name") or "")
    )


def build_context(
    *,
    repo_root: Path,
    jira: JiraAdapter,
    issue_key: str,
    agent: str,
    status: str,
    current_agent_role: str,
    next_required_role: str,
    previous: AgentExecutionContext | None = None,
) -> AgentExecutionContext:
    timestamp = now_iso()
    summary = issue_summary(jira, issue_key)
    started_at = previous.started_at if previous else timestamp
    agent_payload = role_reference_payload(repo_root, agent)
    current_payload = role_reference_payload(repo_root, current_agent_role)
    next_payload = role_reference_payload(repo_root, next_required_role)
    return AgentExecutionContext(
        issue_key=issue_key.strip().upper(),
        issue_summary=summary,
        issue_url=issue_url(jira, issue_key.strip().upper()),
        agent=(
            agent_payload.get("visible_name", "").strip()
            or agent_payload.get("formal_name", "").strip()
            or agent.strip()
        ),
        agent_id=agent_payload.get("role_id", "").strip() or agent.strip(),
        status=normalize_status(status),
        current_agent_role=(
            current_payload.get("visible_name", "").strip()
            or current_payload.get("formal_name", "").strip()
            or current_agent_role.strip()
        ),
        current_agent_role_id=current_payload.get("role_id", "").strip()
        or current_agent_role.strip(),
        next_required_role=(
            next_payload.get("visible_name", "").strip()
            or next_payload.get("formal_name", "").strip()
            or next_required_role.strip()
        ),
        next_required_role_id=next_payload.get("role_id", "").strip() or next_required_role.strip(),
        branch=current_branch(repo_root),
        worktree_root=str(repo_root),
        started_at=started_at,
        updated_at=timestamp,
    )


def record_activity(
    *,
    repo_root: str | Path | None = None,
    issue_key: str = "",
    agent: str = "",
    interaction_type: str,
    status: str,
    contexto: list[str] | None = None,
    evidencias: list[str] | None = None,
    proximo_passo: str = "",
    current_agent_role: str = "",
    next_required_role: str = "",
    transition_issue: bool = True,
    clear_after: bool = False,
    sync_roles: bool = True,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    jira = resolve_jira(repo)
    existing = load_context(repo)
    resolved_issue_key = issue_key.strip().upper() or (existing.issue_key if existing else "")
    resolved_agent = agent.strip() or (existing.agent_id if existing else "")
    if not resolved_issue_key or not resolved_agent:
        raise AgentExecutionError("Issue e agente sao obrigatorios para registrar a atividade.")
    normalized_status = normalize_status(status)
    if transition_issue:
        ensure_issue_status(jira, resolved_issue_key, normalized_status)
        actual_status = read_issue_status(jira, resolved_issue_key)
        if actual_status != normalized_status:
            raise AgentExecutionError(
                "Jira ficou em status divergente apos a transicao: "
                f"{resolved_issue_key} esperado={normalized_status!r} atual={actual_status!r}."
            )
    acting_visibility = role_visibility_payload(repo, resolved_agent)
    comment_agent_name = (
        acting_visibility.get("visible_name", "").strip()
        or acting_visibility.get("formal_name", "").strip()
        or resolved_agent
    )
    rendered_comment = render_structured_comment(
        agent=comment_agent_name,
        interaction_type=interaction_type,
        status=normalized_status,
        contexto=contexto or [],
        evidencias=evidencias or [],
        proximo_passo=proximo_passo,
    )
    comment, comment_actor = with_jira_actor(
        repo,
        resolved_agent,
        "jira-comment",
        lambda actor_jira, _actor: ensure_comment(actor_jira, resolved_issue_key, rendered_comment),
        context_issue_key=resolved_issue_key,
    )
    role_payload: dict[str, Any] = {}
    role_actor_mode = ""
    role_actor_account_id_source = ""
    if sync_roles:
        role_payload, role_actor = with_jira_actor(
            repo,
            resolved_agent,
            "jira-assignee",
            lambda actor_jira, actor: sync_agent_roles(
                actor_jira,
                resolved_issue_key,
                repo_root=repo,
                acting_agent=resolved_agent,
                current_agent_role=current_agent_role.strip(),
                next_required_role=next_required_role.strip(),
                assignee_account_id=actor.account_id,
            ),
            context_issue_key=resolved_issue_key,
        )
        role_actor_mode = role_actor.actor_mode
        role_actor_account_id_source = role_actor.account_id_source
    payload = {
        "comment": comment,
        "comment_actor_mode": comment_actor.actor_mode,
        "comment_actor_account_id_source": comment_actor.account_id_source,
        "role_actor_mode": role_actor_mode,
        "role_actor_account_id_source": role_actor_account_id_source,
        "current_agent_role": current_agent_role.strip(),
        "next_required_role": next_required_role.strip(),
        "current_agent_role_display": role_payload.get("current_agent_role_display", ""),
        "next_required_role_display": role_payload.get("next_required_role_display", ""),
        "role_sync": role_payload,
        "status": normalized_status,
    }
    if clear_after:
        clear_context(repo)
        return {
            "context": None,
            "jira": payload,
            "context_path": str(default_context_path(repo)),
        }
    context = build_context(
        repo_root=repo,
        jira=jira,
        issue_key=resolved_issue_key,
        agent=resolved_agent,
        status=normalized_status,
        current_agent_role=current_agent_role.strip(),
        next_required_role=next_required_role.strip(),
        previous=existing if existing and existing.issue_key == resolved_issue_key else None,
    )
    context_path = save_context(context, repo)
    return {
        "context": asdict(context),
        "jira": payload,
        "context_path": str(context_path),
    }
