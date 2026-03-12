from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    load_ai_control_plane,
    load_yaml_map,
    resolve_atlassian_platform,
    resolve_repo_root,
)
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    AtlassianPlatformError,
)

DEFAULT_JIRA_MODEL_PATH = Path("config/ai/jira-model.yaml")
OPTION_DEFAULTS_BY_TYPE = {
    "checkbox": ["required"],
}


def load_jira_model(repo_root: str | Path | None = None) -> tuple[Path, dict[str, Any]]:
    resolved_repo_root = resolve_repo_root(repo_root)
    model_path = resolved_repo_root / DEFAULT_JIRA_MODEL_PATH
    return model_path, load_yaml_map(model_path)


def ensure_string_list(payload: Any, label: str) -> list[str]:
    if not isinstance(payload, list):
        raise AiControlPlaneError(f"{label} precisa ser lista.")
    values: list[str] = []
    for entry in payload:
        if not isinstance(entry, str):
            raise AiControlPlaneError(f"{label} aceita apenas strings.")
        values.append(entry.strip())
    return values


def active_custom_fields(
    model: dict[str, Any],
    *,
    role_ids: set[str],
) -> list[dict[str, Any]]:
    fields = (model.get("fields") or {}).get("custom_fields") or []
    if not isinstance(fields, list):
        raise AiControlPlaneError(
            "config/ai/jira-model.yaml fields.custom_fields precisa ser lista."
        )
    result: list[dict[str, Any]] = []
    for entry in fields:
        if not isinstance(entry, dict):
            raise AiControlPlaneError("fields.custom_fields aceita apenas mapas.")
        enabled_when_role = str(entry.get("enabled_when_role", "")).strip()
        if enabled_when_role and enabled_when_role not in role_ids:
            continue
        result.append(entry)
    return result


def active_custom_field_names(model: dict[str, Any], *, role_ids: set[str]) -> list[str]:
    return [
        str(entry.get("name", "")).strip()
        for entry in active_custom_fields(model, role_ids=role_ids)
        if str(entry.get("name", "")).strip()
    ]


def configured_custom_field_options(
    field: dict[str, Any],
    *,
    role_ids: set[str],
    role_labels_by_id: dict[str, str] | None = None,
) -> list[str]:
    options_source = str(field.get("options_source", "")).strip()
    if options_source == "enabled_roles":
        return sorted(role_ids)
    if options_source == "enabled_role_visible_names":
        if role_labels_by_id:
            return sorted(
                label.strip()
                for role_id, label in role_labels_by_id.items()
                if role_id in role_ids and label.strip()
            )
        return sorted(role_ids)
    raw_options = field.get("options")
    if isinstance(raw_options, list):
        return [str(option).strip() for option in raw_options if str(option).strip()]
    field_type = str(field.get("type", "")).strip()
    return list(OPTION_DEFAULTS_BY_TYPE.get(field_type, []))


def current_field_entries_by_name(client: AtlassianHttpClient) -> dict[str, list[dict[str, Any]]]:
    start_at = 0
    result: dict[str, list[dict[str, Any]]] = {}
    while True:
        payload = client.request_json(
            "jira",
            "/rest/api/3/field/search",
            params={"startAt": str(start_at), "maxResults": "100"},
        )
        values = payload.get("values", [])
        if not isinstance(values, list):
            raise AtlassianPlatformError(
                "Jira field search retornou values em formato inesperado."
            )
        for entry in values:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "")).strip()
            if not name:
                continue
            result.setdefault(name, []).append(entry)
        if payload.get("isLast", True):
            break
        start_at += int(payload.get("maxResults", 100) or 100)
    return result


def current_fields_by_name(client: AtlassianHttpClient) -> dict[str, dict[str, Any]]:
    entries_by_name = current_field_entries_by_name(client)
    return {
        name: entries[0]
        for name, entries in entries_by_name.items()
        if entries
    }


def resolve_named_fields(
    client: AtlassianHttpClient,
    field_names: set[str] | list[str] | tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    desired_names = sorted({str(name).strip() for name in field_names if str(name).strip()})
    entries_by_name = current_field_entries_by_name(client)
    resolved: dict[str, dict[str, Any]] = {}
    duplicated = [
        name for name in desired_names if len(entries_by_name.get(name, [])) > 1
    ]
    if duplicated:
        quoted = ", ".join(repr(name) for name in duplicated)
        raise AtlassianPlatformError(
            "Jira field search retornou nomes duplicados para fields canonicos: "
            f"{quoted}. Corrija a ambiguidade no tenant antes de aplicar o schema."
        )
    for name in desired_names:
        entries = entries_by_name.get(name, [])
        if entries:
            resolved[name] = entries[0]
    return resolved


def field_context_entries(client: AtlassianHttpClient, field_id: str) -> list[dict[str, Any]]:
    contexts_payload = client.request_json(
        "jira",
        f"/rest/api/3/field/{field_id}/context",
    )
    contexts = contexts_payload.get("values", [])
    if not isinstance(contexts, list):
        raise AtlassianPlatformError(
            "Jira field context retornou values em formato inesperado."
        )
    return [entry for entry in contexts if isinstance(entry, dict)]


def field_context_applies_to_project(context: dict[str, Any], *, project_id: str) -> bool:
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        return True
    if bool(context.get("isGlobalContext", False)):
        return True
    raw_project_ids = context.get("projectIds")
    if not isinstance(raw_project_ids, list):
        return False
    project_ids = {str(entry).strip() for entry in raw_project_ids if str(entry).strip()}
    return normalized_project_id in project_ids


def applicable_field_contexts(
    client: AtlassianHttpClient,
    field_id: str,
    *,
    project_id: str,
) -> list[dict[str, Any]]:
    contexts = field_context_entries(client, field_id)
    return [
        context
        for context in contexts
        if field_context_applies_to_project(context, project_id=project_id)
    ]


def field_option_values(
    client: AtlassianHttpClient,
    field_id: str,
    *,
    context_id: str,
) -> list[str]:
    values: set[str] = set()
    normalized_context_id = context_id.strip()
    if not normalized_context_id:
        raise AtlassianPlatformError("field_option_values exige context_id nao vazio.")
    start_at = 0
    while True:
        options_payload = client.request_json(
            "jira",
            f"/rest/api/3/field/{field_id}/context/{normalized_context_id}/option",
            params={
                "onlyOptions": "true",
                "maxResults": "100",
                "startAt": str(start_at),
            },
        )
        entries = options_payload.get("values", [])
        if not isinstance(entries, list):
            raise AtlassianPlatformError(
                "Jira field options retornou values em formato inesperado."
            )
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            value = str(entry.get("value", "")).strip()
            if value:
                values.add(value)
        if options_payload.get("isLast", True):
            break
        start_at += int(options_payload.get("maxResults", 100) or 100)
    return sorted(values)


def current_custom_field_option_gaps(
    client: AtlassianHttpClient,
    model: dict[str, Any],
    *,
    role_ids: set[str],
    project_id: str = "",
    role_labels_by_id: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    active_fields = active_custom_fields(model, role_ids=role_ids)
    field_catalog = resolve_named_fields(
        client,
        [
            str(field.get("name", "")).strip()
            for field in active_fields
            if str(field.get("name", "")).strip()
        ],
    )
    gaps: list[dict[str, Any]] = []
    for field in active_fields:
        field_name = str(field.get("name", "")).strip()
        if not field_name:
            continue
        desired_options = configured_custom_field_options(
            field,
            role_ids=role_ids,
            role_labels_by_id=role_labels_by_id,
        )
        if not desired_options:
            continue
        field_entry = field_catalog.get(field_name) or {}
        field_id = str(field_entry.get("id", "")).strip()
        if not field_id:
            continue
        contexts = applicable_field_contexts(client, field_id, project_id=project_id)
        if not contexts:
            gaps.append(
                {
                    "field": field_name,
                    "field_id": field_id,
                    "context_status": "no-applicable-context",
                    "project_id": project_id.strip(),
                    "missing_options": desired_options,
                    "unexpected_options": [],
                    "desired_option_count": len(desired_options),
                    "current_option_count": 0,
                }
            )
            continue
        desired_set = set(desired_options)
        for context in contexts:
            context_id = str(context.get("id", "")).strip()
            if not context_id:
                continue
            current_options = field_option_values(client, field_id, context_id=context_id)
            current_set = set(current_options)
            missing_options = sorted(desired_set - current_set)
            unexpected_options = sorted(current_set - desired_set)
            if not missing_options and not unexpected_options:
                continue
            gaps.append(
                {
                    "field": field_name,
                    "field_id": field_id,
                    "context_id": context_id,
                    "context_name": str(context.get("name", "")).strip(),
                    "context_status": "applicable",
                    "is_global_context": bool(context.get("isGlobalContext", False)),
                    "missing_options": missing_options,
                    "unexpected_options": unexpected_options,
                    "desired_option_count": len(desired_options),
                    "current_option_count": len(current_options),
                }
            )
    return sorted(gaps, key=lambda item: str(item.get("field", "")))


def model_summary_payload(repo_root: str | Path | None = None) -> dict[str, Any]:
    model_path, model = load_jira_model(repo_root)
    project = model.get("project") or {}
    issue_types = (model.get("issue_types") or {}).get("standard") or []
    workflow = model.get("workflow") or {}
    board = project.get("target_board") or {}
    fields = (model.get("fields") or {}).get("custom_fields") or []
    components = model.get("components") or []
    labels = (model.get("labels") or {}).get("baseline") or []
    dashboards = model.get("dashboards") or []
    return {
        "model_path": str(model_path),
        "project": {
            "key": str(project.get("key", "")).strip(),
            "name": str(project.get("name", "")).strip(),
            "style": str(project.get("style", "")).strip(),
        },
        "board": {
            "name": str(board.get("name", "")).strip(),
            "type": str(board.get("type", "")).strip(),
            "columns": [str(entry.get("name", "")).strip() for entry in board.get("columns", [])],
            "optional_columns": [
                str(entry.get("name", "")).strip() for entry in board.get("optional_columns", [])
            ],
            "required_scopes": ensure_string_list(
                board.get("board_api_scopes", []),
                "config/ai/jira-model.yaml project.target_board.board_api_scopes",
            ),
        },
        "workflow_statuses": [
            str(entry.get("name", "")).strip() for entry in workflow.get("statuses", [])
        ],
        "issue_types": ensure_string_list(
            issue_types,
            "config/ai/jira-model.yaml issue_types.standard",
        ),
        "custom_fields": [str(entry.get("name", "")).strip() for entry in fields],
        "components": ensure_string_list(
            components,
            "config/ai/jira-model.yaml components",
        ),
        "labels": ensure_string_list(
            labels,
            "config/ai/jira-model.yaml labels.baseline",
        ),
        "dashboards": [str(entry.get("name", "")).strip() for entry in dashboards],
    }


def current_jira_state_payload(repo_root: str | Path | None = None) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    client = AtlassianHttpClient(resolved)

    project = client.request_json("jira", f"/rest/api/3/project/{resolved.jira_project_key}")
    statuses_payload = client.request_json(
        "jira",
        f"/rest/api/3/project/{resolved.jira_project_key}/statuses",
    )
    components_payload = client.request_json(
        "jira",
        f"/rest/api/3/project/{resolved.jira_project_key}/components",
    )
    status_names = sorted(
        {
            str(status.get("name", "")).strip()
            for issue_type in statuses_payload
            for status in issue_type.get("statuses", [])
            if str(status.get("name", "")).strip()
        }
    )
    issue_type_names = sorted(
        {
            str(issue_type.get("name", "")).strip()
            for issue_type in project.get("issueTypes", [])
            if str(issue_type.get("name", "")).strip()
        }
    )
    component_names = sorted(
        str(component.get("name", "")).strip()
        for component in components_payload
        if str(component.get("name", "")).strip()
    )
    field_names = sorted(current_fields_by_name(client))

    board_payload: dict[str, Any]
    try:
        boards = client.request_json(
            "jira",
            "/rest/agile/1.0/board",
            params={
                "projectKeyOrId": resolved.jira_project_key,
                "type": "kanban",
                "maxResults": "50",
            },
        )
    except AtlassianPlatformError as exc:
        board_payload = {
            "status": "error",
            "error": str(exc),
            "boards": [],
        }
    else:
        board_payload = {
            "status": "ok",
            "boards": [
                {
                    "id": board.get("id"),
                    "name": board.get("name"),
                    "type": board.get("type"),
                }
                for board in boards.get("values", [])
            ],
        }

    return {
        "project": {
            "id": str(project.get("id", "")).strip(),
            "key": str(project.get("key", "")).strip(),
            "name": str(project.get("name", "")).strip(),
            "style": str(project.get("style", "")).strip(),
            "simplified": bool(project.get("simplified", False)),
        },
        "issue_types": issue_type_names,
        "statuses": status_names,
        "components": component_names,
        "fields": field_names,
        "board": board_payload,
    }


def live_delta_payload(repo_root: str | Path | None = None) -> dict[str, Any]:
    summary = model_summary_payload(repo_root)
    current = current_jira_state_payload(repo_root)
    _, model = load_jira_model(repo_root)
    control_plane = load_ai_control_plane(repo_root)
    role_ids = set(control_plane.enabled_roles())
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    client = AtlassianHttpClient(resolved)

    desired_statuses = set(summary["workflow_statuses"])
    current_statuses = set(current["statuses"])
    desired_fields = set(active_custom_field_names(model, role_ids=role_ids))
    inactive_fields = sorted(set(summary["custom_fields"]) - desired_fields)

    desired_issue_types = set(summary["issue_types"])
    desired_components = set(summary["components"])
    current_issue_types = set(current["issue_types"])
    current_components = set(current["components"])
    current_fields = set(current["fields"])
    option_gaps = current_custom_field_option_gaps(
        client,
        model,
        role_ids=role_ids,
        project_id=str((current.get("project") or {}).get("id", "")).strip(),
        role_labels_by_id=control_plane.enabled_role_visible_names_by_id(),
    )

    return {
        "project": current["project"],
        "desired": summary,
        "current": current,
        "delta": {
            "missing_statuses": sorted(desired_statuses - current_statuses),
            "unexpected_statuses": sorted(current_statuses - desired_statuses),
            "missing_issue_types": sorted(desired_issue_types - current_issue_types),
            "unexpected_issue_types": sorted(current_issue_types - desired_issue_types),
            "missing_components": sorted(desired_components - current_components),
            "missing_custom_fields": sorted(desired_fields - current_fields),
            "inactive_custom_fields": inactive_fields,
            "custom_field_option_gaps": option_gaps,
            "missing_custom_field_options": option_gaps,
        },
        "board_access": current["board"],
    }
