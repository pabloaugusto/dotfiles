from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    load_ai_control_plane,
    resolve_atlassian_platform,
)
from scripts.ai_jira_model_lib import load_jira_model
from scripts.atlassian_platform_lib import AtlassianHttpClient, AtlassianPlatformError

FIELD_TYPE_MAP = {
    "single_select": {
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
        "supports_options": True,
    },
    "multi_select": {
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:multiselect",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
        "supports_options": True,
    },
    "url": {
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:url",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher",
        "supports_options": False,
    },
    "paragraph": {
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "supports_options": False,
    },
    "checkbox": {
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
        "supports_options": True,
        "default_options": ["required"],
    },
}

STATUS_CATEGORY_MAP = {
    "to do": "TODO",
    "in progress": "IN_PROGRESS",
    "done": "DONE",
}


def normalize_status_name(name: str) -> str:
    return " ".join(name.strip().split()).casefold()


def workflow_status_reference(workflow_name: str, status_name: str) -> str:
    seed = f"jira-workflow:{normalize_status_name(workflow_name)}:{normalize_status_name(status_name)}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def enabled_roles(repo_root: str | Path | None = None) -> set[str]:
    control_plane = load_ai_control_plane(repo_root)
    return set(control_plane.enabled_roles())


def active_custom_fields(model: dict[str, Any], *, role_ids: set[str]) -> list[dict[str, Any]]:
    fields = ((model.get("fields") or {}).get("custom_fields") or [])
    if not isinstance(fields, list):
        raise AiControlPlaneError("config/ai/jira-model.yaml fields.custom_fields precisa ser lista.")
    result: list[dict[str, Any]] = []
    for entry in fields:
        if not isinstance(entry, dict):
            raise AiControlPlaneError("fields.custom_fields aceita apenas mapas.")
        enabled_when_role = str(entry.get("enabled_when_role", "")).strip()
        if enabled_when_role and enabled_when_role not in role_ids:
            continue
        result.append(entry)
    return result


def configured_custom_field_options(
    field: dict[str, Any],
    spec: dict[str, Any],
    *,
    role_ids: set[str],
) -> list[str]:
    options_source = str(field.get("options_source", "")).strip()
    if options_source == "enabled_roles":
        return sorted(role_ids)
    raw_options = field.get("options")
    if isinstance(raw_options, list):
        return [str(option).strip() for option in raw_options if str(option).strip()]
    default_options = spec.get("default_options")
    if isinstance(default_options, list):
        return [str(option).strip() for option in default_options if str(option).strip()]
    return []


def workflow_status_entries(
    model: dict[str, Any],
    current_statuses: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    workflow = model.get("workflow") or {}
    workflow_name = str(workflow.get("name", "")).strip()
    if not workflow_name:
        raise AiControlPlaneError("workflow.name e obrigatorio em config/ai/jira-model.yaml.")
    statuses = workflow.get("statuses") or []
    payload: list[dict[str, Any]] = []
    status_references: dict[str, str] = {}
    for entry in statuses:
        if not isinstance(entry, dict):
            raise AiControlPlaneError("workflow.statuses aceita apenas mapas.")
        name = str(entry.get("name", "")).strip()
        if not name:
            continue
        normalized_name = normalize_status_name(name)
        category_key = STATUS_CATEGORY_MAP[str(entry.get("category", "")).strip().lower()]
        existing = current_statuses.get(name) or current_statuses.get(normalized_name)
        status_name = str((existing or {}).get("name") or name).strip()
        status_reference = str((existing or {}).get("id", "")).strip() or workflow_status_reference(
            workflow_name,
            status_name,
        )
        status_payload = {
            "name": status_name,
            "statusCategory": category_key,
            "statusReference": status_reference,
            "description": str(entry.get("description", "")).strip(),
        }
        if existing and existing.get("id"):
            status_payload["id"] = str(existing["id"])
        payload.append(status_payload)
        status_references[normalized_name] = status_reference
    return payload, status_references


def workflow_layout_entries(status_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    x_axis = 0.0
    for entry in status_entries:
        result.append(
            {
                "statusReference": entry["statusReference"],
                "layout": {"x": x_axis, "y": 0.0},
                "properties": {},
            }
        )
        x_axis += 220.0
    return result


def transition_payload(
    transition_id: int,
    from_status: str,
    to_status: str,
    *,
    status_references: dict[str, str],
) -> dict[str, Any]:
    return {
        "id": str(transition_id),
        "name": f"Move to {to_status}",
        "description": "",
        "type": "DIRECTED",
        "toStatusReference": status_references[normalize_status_name(to_status)],
        "links": [
            {
                "fromStatusReference": status_references[normalize_status_name(from_status)],
                "fromPort": 0,
                "toPort": 1,
            }
        ],
        "properties": {},
        "validators": [],
        "actions": [],
        "triggers": [],
    }


def default_workflow_transition_specs() -> list[dict[str, Any]]:
    return [
        {"from": "Backlog", "to": "Refinement"},
        {"from": "Refinement", "to": "Ready"},
        {"from": "Ready", "to": "Doing"},
        {"from": "Doing", "to": "Paused"},
        {"from": "Paused", "to": "Doing"},
        {"from": "Doing", "to": "Testing"},
        {"from": "Testing", "to": "Review"},
        {"from": "Review", "to": "Done"},
        {"from": "Testing", "to": "Changes Requested"},
        {"from": "Review", "to": "Changes Requested"},
        {"from": "Changes Requested", "to": "Doing"},
    ]


def workflow_transition_entries(
    workflow: dict[str, Any],
    *,
    status_references: dict[str, str],
) -> list[dict[str, Any]]:
    raw_transitions = workflow.get("transitions") or default_workflow_transition_specs()
    if not isinstance(raw_transitions, list):
        raise AiControlPlaneError("workflow.transitions precisa ser lista.")
    payload: list[dict[str, Any]] = []
    for index, entry in enumerate(raw_transitions, start=1):
        if not isinstance(entry, dict):
            raise AiControlPlaneError("workflow.transitions aceita apenas mapas.")
        from_status = str(entry.get("from", "")).strip()
        to_status = str(entry.get("to", "")).strip()
        if not from_status or not to_status:
            raise AiControlPlaneError("Cada transicao precisa de from e to.")
        transition_id = int(entry.get("id") or (index * 10 + 1))
        payload.append(
            transition_payload(
                transition_id,
                from_status,
                to_status,
                status_references=status_references,
            )
        )
    return payload


def workflow_create_payload(
    model: dict[str, Any],
    *,
    current_statuses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    workflow = model.get("workflow") or {}
    workflow_name = str(workflow.get("name", "")).strip()
    if not workflow_name:
        raise AiControlPlaneError("workflow.name e obrigatorio em config/ai/jira-model.yaml.")
    status_entries, status_references = workflow_status_entries(model, current_statuses)
    transitions = [
        {
            "id": "1",
            "name": "Create",
            "description": "",
            "type": "INITIAL",
            "toStatusReference": status_references[normalize_status_name("Backlog")],
            "links": [],
            "properties": {},
            "validators": [],
            "actions": [],
            "triggers": [],
        },
        *workflow_transition_entries(
            workflow,
            status_references=status_references,
        ),
    ]
    return {
        "scope": {"type": "GLOBAL"},
        "statuses": status_entries,
        "workflows": [
            {
                "name": workflow_name,
                "description": str(workflow.get("description", "")).strip(),
                "startPointLayout": {"x": -120.0, "y": 0.0},
                "statuses": workflow_layout_entries(status_entries),
                "transitions": transitions,
            }
        ],
    }


def workflow_validation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "payload": payload,
        "validationOptions": {
            "levels": ["ERROR", "WARNING"],
        },
    }


def workflow_update_validation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "payload": payload,
        "validationOptions": {
            "levels": ["ERROR", "WARNING"],
        },
    }


def workflow_transition_signature(transition: dict[str, Any]) -> tuple[Any, ...]:
    links = transition.get("links") or []
    normalized_links = []
    for entry in links:
        if not isinstance(entry, dict):
            continue
        normalized_links.append(
            (
                str(entry.get("fromStatusReference", "")).strip(),
                int(entry.get("fromPort", 0)),
                int(entry.get("toPort", 0)),
            )
        )
    return (
        str(transition.get("id", "")).strip(),
        str(transition.get("name", "")).strip(),
        str(transition.get("type", "")).strip(),
        str(transition.get("toStatusReference", "")).strip(),
        tuple(sorted(normalized_links)),
    )


def workflow_status_layout_signature(status: dict[str, Any]) -> tuple[Any, ...]:
    layout = status.get("layout") or {}
    properties = status.get("properties") or {}
    return (
        str(status.get("statusReference", "")).strip(),
        float(layout.get("x", 0.0)),
        float(layout.get("y", 0.0)),
        tuple(sorted((str(key), str(value)) for key, value in properties.items())),
    )


def current_workflow_detail_by_name(
    client: AtlassianHttpClient,
    workflow_name: str,
) -> dict[str, Any] | None:
    payload = client.request_json(
        "jira",
        "/rest/api/3/workflows/search",
        params={
            "workflowName": workflow_name,
            "expand": "usage,values.transitions",
        },
    )
    values = payload.get("values", [])
    if not isinstance(values, list):
        return None
    for entry in values:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).strip()
        if name == workflow_name:
            return entry
    return None


def workflow_requires_update(existing_workflow: dict[str, Any], desired_payload: dict[str, Any]) -> bool:
    workflows = desired_payload.get("workflows", [])
    if not isinstance(workflows, list) or not workflows:
        raise AiControlPlaneError("Payload de workflow invalido para comparacao de drift.")
    desired_workflow = workflows[0]
    existing_statuses = existing_workflow.get("statuses") or []
    desired_statuses = desired_workflow.get("statuses") or []
    if {
        workflow_status_layout_signature(entry)
        for entry in existing_statuses
        if isinstance(entry, dict)
    } != {
        workflow_status_layout_signature(entry)
        for entry in desired_statuses
        if isinstance(entry, dict)
    }:
        return True
    existing_transitions = existing_workflow.get("transitions") or []
    desired_transitions = desired_workflow.get("transitions") or []
    if {
        workflow_transition_signature(entry)
        for entry in existing_transitions
        if isinstance(entry, dict)
    } != {
        workflow_transition_signature(entry)
        for entry in desired_transitions
        if isinstance(entry, dict)
    }:
        return True
    current_description = str(existing_workflow.get("description", "")).strip()
    desired_description = str(desired_workflow.get("description", "")).strip()
    return current_description != desired_description


def workflow_update_payload(
    model: dict[str, Any],
    *,
    current_statuses: dict[str, dict[str, Any]],
    existing_workflow: dict[str, Any],
) -> dict[str, Any]:
    create_payload = workflow_create_payload(model, current_statuses=current_statuses)
    desired_workflow = create_payload["workflows"][0]
    workflow_id = str(existing_workflow.get("id", "")).strip()
    version = existing_workflow.get("version")
    if not workflow_id or not isinstance(version, dict):
        raise AtlassianPlatformError("Workflow existente nao retornou id/version para update.")
    return {
        "statuses": create_payload["statuses"],
        "workflows": [
            {
                "id": workflow_id,
                "description": desired_workflow.get("description", ""),
                "startPointLayout": desired_workflow.get("startPointLayout", {}),
                "statuses": desired_workflow.get("statuses", []),
                "transitions": desired_workflow.get("transitions", []),
                "version": version,
            }
        ],
    }


def wait_for_workflow_convergence(
    client: AtlassianHttpClient,
    workflow_name: str,
    desired_workflow_payload: dict[str, Any],
    *,
    attempts: int = 5,
    sleep_seconds: float = 1.0,
) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    for index in range(attempts):
        latest = current_workflow_detail_by_name(client, workflow_name)
        if latest is not None and not workflow_requires_update(latest, desired_workflow_payload):
            return latest
        if index < attempts - 1:
            time.sleep(sleep_seconds)
    return latest


def current_project_statuses(client: AtlassianHttpClient, project_key: str) -> dict[str, dict[str, Any]]:
    payload = client.request_json("jira", f"/rest/api/3/project/{project_key}/statuses")
    result: dict[str, dict[str, Any]] = {}
    for issue_type in payload:
        if not isinstance(issue_type, dict):
            continue
        for status in issue_type.get("statuses", []):
            if not isinstance(status, dict):
                continue
            name = str(status.get("name", "")).strip()
            normalized_name = normalize_status_name(name)
            if not normalized_name or normalized_name in result:
                continue
            result[normalized_name] = {
                "id": str(status.get("id", "")).strip(),
                "name": name,
                "statusCategory": str(((status.get("statusCategory") or {}).get("name")) or "").strip(),
                "source": "project",
            }
    return result


def current_accessible_statuses(client: AtlassianHttpClient) -> dict[str, dict[str, Any]]:
    payload = client.request_json("jira", "/rest/api/3/status")
    if not isinstance(payload, list):
        raise AtlassianPlatformError("Jira status retornou payload inesperado.")
    result: dict[str, dict[str, Any]] = {}
    for status in payload:
        if not isinstance(status, dict):
            continue
        name = str(status.get("name", "")).strip()
        normalized_name = normalize_status_name(name)
        if not normalized_name or normalized_name in result:
            continue
        result[normalized_name] = {
            "id": str(status.get("id", "")).strip(),
            "name": name,
            "statusCategory": str(((status.get("statusCategory") or {}).get("name")) or "").strip(),
            "source": "accessible",
        }
    return result


def current_status_catalog(client: AtlassianHttpClient, project_key: str) -> dict[str, dict[str, Any]]:
    statuses = current_accessible_statuses(client)
    statuses.update(current_project_statuses(client, project_key))
    return statuses


def current_fields_by_name(client: AtlassianHttpClient) -> dict[str, dict[str, Any]]:
    start_at = 0
    result: dict[str, dict[str, Any]] = {}
    while True:
        payload = client.request_json(
            "jira",
            "/rest/api/3/field/search",
            params={"startAt": str(start_at), "maxResults": "100"},
        )
        values = payload.get("values", [])
        if not isinstance(values, list):
            break
        for entry in values:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "")).strip()
            if not name or name in result:
                continue
            result[name] = entry
        if payload.get("isLast", True):
            break
        start_at += int(payload.get("maxResults", 100))
    return result


def current_dashboards_by_name(client: AtlassianHttpClient) -> dict[str, dict[str, Any]]:
    payload = client.request_json("jira", "/rest/api/3/dashboard/search", params={"maxResults": "100"})
    result: dict[str, dict[str, Any]] = {}
    for entry in payload.get("values", []):
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).strip()
        if not name:
            continue
        result[name] = entry
    return result


def current_workflows_by_name(client: AtlassianHttpClient) -> dict[str, dict[str, Any]]:
    payload = client.request_json("jira", "/rest/api/3/workflow/search", params={"maxResults": "100"})
    result: dict[str, dict[str, Any]] = {}
    for entry in payload.get("values", []):
        if not isinstance(entry, dict):
            continue
        workflow_id = entry.get("id")
        name = ""
        if isinstance(workflow_id, dict):
            name = str(workflow_id.get("name", "")).strip()
        if not name:
            name = str(entry.get("name", "")).strip()
        if not name:
            continue
        result[name] = entry
    return result


def current_workflow_schemes_by_name(client: AtlassianHttpClient) -> dict[str, dict[str, Any]]:
    payload = client.request_json("jira", "/rest/api/3/workflowscheme", params={"maxResults": "100"})
    result: dict[str, dict[str, Any]] = {}
    for entry in payload.get("values", []):
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).strip()
        if not name:
            continue
        result[name] = entry
    return result


def current_project_payload(client: AtlassianHttpClient, project_key: str) -> dict[str, Any]:
    payload = client.request_json("jira", f"/rest/api/3/project/{project_key}")
    if not isinstance(payload, dict):
        raise AtlassianPlatformError("Projeto Jira retornou payload inesperado.")
    return payload


def current_workflow_scheme_association(client: AtlassianHttpClient, project_id: str) -> dict[str, Any] | None:
    payload = client.request_json(
        "jira",
        "/rest/api/3/workflowscheme/project",
        params={"projectId": project_id},
    )
    values = payload.get("values", [])
    if not isinstance(values, list) or not values:
        return None
    first = values[0]
    return first if isinstance(first, dict) else None


def project_has_issues(client: AtlassianHttpClient, project_key: str) -> bool:
    payload = client.request_json(
        "jira",
        "/rest/api/3/search/jql",
        params={
            "jql": f'project = "{project_key}" ORDER BY created DESC',
            "maxResults": "1",
            "fields": "summary",
        },
    )
    issues = payload.get("issues", [])
    return isinstance(issues, list) and len(issues) > 0


def ensure_field_options(client: AtlassianHttpClient, field_id: str, options: list[str]) -> dict[str, Any]:
    contexts_payload = client.request_json("jira", f"/rest/api/3/field/{field_id}/context")
    contexts = contexts_payload.get("values", [])
    if not isinstance(contexts, list) or not contexts:
        created = client.request_json(
            "jira",
            f"/rest/api/3/field/{field_id}/context",
            method="POST",
            payload={"name": "DOT Default Context", "description": "", "projectIds": [], "issueTypeIds": []},
        )
        context_id = str(created.get("id", "")).strip()
    else:
        context_id = str((contexts[0] or {}).get("id", "")).strip()
    if not context_id:
        raise AtlassianPlatformError(f"Nao foi possivel resolver contexto para o field {field_id}.")

    existing_payload = client.request_json(
        "jira",
        f"/rest/api/3/field/{field_id}/context/{context_id}/option",
        params={"onlyOptions": "true", "maxResults": "200"},
    )
    existing_values = {
        str(entry.get("value", "")).strip()
        for entry in existing_payload.get("values", [])
        if isinstance(entry, dict)
    }
    missing = [option for option in options if option not in existing_values]
    if missing:
        client.request_json(
            "jira",
            f"/rest/api/3/field/{field_id}/context/{context_id}/option",
            method="POST",
            payload={"options": [{"value": option, "disabled": False} for option in missing]},
        )
    return {"context_id": context_id, "created_options": missing}


def field_screens(client: AtlassianHttpClient, field_id: str) -> list[dict[str, Any]]:
    payload = client.request_json("jira", f"/rest/api/3/field/{field_id}/screens")
    values = payload.get("values", [])
    if not isinstance(values, list):
        raise AtlassianPlatformError("Jira field screens retornou values em formato inesperado.")
    return [entry for entry in values if isinstance(entry, dict)]


def ensure_field_on_default_screen(client: AtlassianHttpClient, field_id: str) -> bool:
    if field_screens(client, field_id):
        return False
    client.request_json("jira", f"/rest/api/3/screens/addToDefault/{field_id}", method="POST")
    return True


def build_apply_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    model_path, model = load_jira_model(control_plane.repo_root)
    client = AtlassianHttpClient(resolved)

    project = current_project_payload(client, resolved.jira_project_key)
    project_id = str(project.get("id", "")).strip()
    statuses = current_status_catalog(client, resolved.jira_project_key)
    workflows = current_workflows_by_name(client)
    workflow_schemes = current_workflow_schemes_by_name(client)
    fields = current_fields_by_name(client)
    dashboards = current_dashboards_by_name(client)
    role_ids = set(control_plane.enabled_roles())

    workflow = model.get("workflow") or {}
    workflow_name = str(workflow.get("name", "")).strip()
    scheme_name = str(workflow.get("scheme_name", "")).strip()
    active_fields = active_custom_fields(model, role_ids=role_ids)
    desired_workflow_payload = workflow_create_payload(model, current_statuses=statuses)
    live_workflow = current_workflow_detail_by_name(client, workflow_name)

    return {
        "model_path": str(model_path),
        "project": {
            "id": project_id,
            "key": resolved.jira_project_key,
            "name": str(project.get("name", "")).strip(),
            "has_issues": project_has_issues(client, resolved.jira_project_key),
        },
        "workflow": {
            "name": workflow_name,
            "exists": workflow_name in workflows,
            "scheme_name": scheme_name,
            "scheme_exists": scheme_name in workflow_schemes,
            "requires_update": (
                workflow_name in workflows
                and live_workflow is not None
                and workflow_requires_update(live_workflow, desired_workflow_payload)
            ),
            "payload": desired_workflow_payload,
        },
        "custom_fields": {
            "active_names": [str(entry.get("name", "")).strip() for entry in active_fields],
            "missing_names": [
                str(entry.get("name", "")).strip()
                for entry in active_fields
                if str(entry.get("name", "")).strip() not in fields
            ],
            "detached_from_screens": [
                str(entry.get("name", "")).strip()
                for entry in active_fields
                if str(entry.get("name", "")).strip() in fields
                and str((fields[str(entry.get("name", "")).strip()] or {}).get("id", "")).strip()
                and not field_screens(
                    client,
                    str((fields[str(entry.get("name", "")).strip()] or {}).get("id", "")).strip(),
                )
            ],
        },
        "dashboards": {
            "desired_names": [
                str(entry.get("name", "")).strip()
                for entry in (model.get("dashboards") or [])
                if isinstance(entry, dict) and str(entry.get("name", "")).strip()
            ],
            "missing_names": [
                str(entry.get("name", "")).strip()
                for entry in (model.get("dashboards") or [])
                if isinstance(entry, dict)
                and str(entry.get("name", "")).strip()
                and str(entry.get("name", "")).strip() not in dashboards
            ],
        },
        "board": {
            "name": str(((model.get("project") or {}).get("target_board") or {}).get("name", "")).strip(),
            "status": "deferred-until-agile-api-is-green",
        },
    }


def apply_jira_model(repo_root: str | Path | None = None) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    model_path, model = load_jira_model(control_plane.repo_root)
    client = AtlassianHttpClient(resolved)

    project = current_project_payload(client, resolved.jira_project_key)
    project_id = str(project.get("id", "")).strip()
    if not project_id:
        raise AtlassianPlatformError("Nao foi possivel resolver o project id do Jira.")
    has_issues = project_has_issues(client, resolved.jira_project_key)

    statuses = current_status_catalog(client, resolved.jira_project_key)
    workflows = current_workflows_by_name(client)
    workflow_schemes = current_workflow_schemes_by_name(client)
    fields = current_fields_by_name(client)
    dashboards = current_dashboards_by_name(client)
    role_ids = set(control_plane.enabled_roles())

    workflow = model.get("workflow") or {}
    workflow_name = str(workflow.get("name", "")).strip()
    scheme_name = str(workflow.get("scheme_name", "")).strip()
    desired_workflow_payload = workflow_create_payload(model, current_statuses=statuses)
    live_workflow = current_workflow_detail_by_name(client, workflow_name) if workflow_name in workflows else None
    results: dict[str, Any] = {
        "model_path": str(model_path),
        "project": {"id": project_id, "key": resolved.jira_project_key, "has_issues": has_issues},
        "workflow": {
            "name": workflow_name,
            "created": False,
            "validated": False,
            "updated": False,
            "update_validated": False,
        },
        "workflow_scheme": {"name": scheme_name, "created": False, "assigned": False},
        "custom_fields": {"created": [], "options_updated": [], "added_to_default_screen": []},
        "dashboards": {"created": []},
        "board": {"status": "deferred-until-agile-api-is-green"},
    }

    if workflow_name not in workflows:
        client.request_json(
            "jira",
            "/rest/api/3/workflows/create/validation",
            method="POST",
            payload=workflow_validation_payload(desired_workflow_payload),
        )
        results["workflow"]["validated"] = True
        client.request_json(
            "jira",
            "/rest/api/3/workflows/create",
            method="POST",
            payload=desired_workflow_payload,
        )
        results["workflow"]["created"] = True
        workflows = current_workflows_by_name(client)
        live_workflow = current_workflow_detail_by_name(client, workflow_name)

    if workflow_name not in workflows:
        raise AtlassianPlatformError(f"Workflow {workflow_name!r} nao apareceu apos a criacao.")

    live_workflow = wait_for_workflow_convergence(
        client,
        workflow_name,
        desired_workflow_payload,
    )
    if live_workflow is None:
        raise AtlassianPlatformError(f"Nao foi possivel carregar o workflow publicado {workflow_name!r}.")

    if workflow_requires_update(live_workflow, desired_workflow_payload):
        update_payload = workflow_update_payload(
            model,
            current_statuses=statuses,
            existing_workflow=live_workflow,
        )
        client.request_json(
            "jira",
            "/rest/api/3/workflows/update/validation",
            method="POST",
            payload=workflow_update_validation_payload(update_payload),
        )
        results["workflow"]["update_validated"] = True
        client.request_json(
            "jira",
            "/rest/api/3/workflows/update",
            method="POST",
            payload=update_payload,
        )
        results["workflow"]["updated"] = True
        live_workflow = wait_for_workflow_convergence(
            client,
            workflow_name,
            desired_workflow_payload,
        )
        if live_workflow is None or workflow_requires_update(live_workflow, desired_workflow_payload):
            raise AtlassianPlatformError(
                f"Workflow {workflow_name!r} permaneceu em drift apos o update."
            )

    scheme = workflow_schemes.get(scheme_name)
    if scheme is None:
        scheme = client.request_json(
            "jira",
            "/rest/api/3/workflowscheme",
            method="POST",
            payload={
                "name": scheme_name,
                "description": "Workflow scheme canonico do piloto AI control plane.",
                "defaultWorkflow": workflow_name,
            },
        )
        workflow_schemes = current_workflow_schemes_by_name(client)
        results["workflow_scheme"]["created"] = True

    scheme = workflow_schemes.get(scheme_name) or scheme
    scheme_id = str((scheme or {}).get("id", "")).strip()
    if not scheme_id:
        raise AtlassianPlatformError(f"Nao foi possivel resolver o workflow scheme {scheme_name!r}.")

    association = current_workflow_scheme_association(client, project_id)
    workflow_scheme = (association or {}).get("workflowScheme") or {}
    current_scheme_id = str((workflow_scheme or {}).get("id", "")).strip()
    if current_scheme_id != scheme_id:
        if has_issues:
            raise AtlassianPlatformError(
                "O projeto ja possui issues; o switch com mapeamento de statuses ainda nao foi automatizado."
            )
        client.request_json(
            "jira",
            "/rest/api/3/workflowscheme/project",
            method="PUT",
            payload={"projectId": project_id, "workflowSchemeId": scheme_id},
        )
        results["workflow_scheme"]["assigned"] = True

    active_fields = active_custom_fields(model, role_ids=role_ids)
    for field in active_fields:
        field_name = str(field.get("name", "")).strip()
        if not field_name or field_name in fields:
            continue
        field_kind = str(field.get("type", "")).strip()
        spec = FIELD_TYPE_MAP.get(field_kind)
        if spec is None:
            raise AiControlPlaneError(f"Tipo de custom field nao suportado: {field_kind}")
        payload = {
            "name": field_name,
            "description": "",
            "type": spec["type"],
            "searcherKey": spec["searcherKey"],
        }
        client.request_json("jira", "/rest/api/3/field", method="POST", payload=payload)
        results["custom_fields"]["created"].append(field_name)
        fields = current_fields_by_name(client)
    for field in active_fields:
        field_name = str(field.get("name", "")).strip()
        field_kind = str(field.get("type", "")).strip()
        spec = FIELD_TYPE_MAP.get(field_kind)
        if not field_name or spec is None or not spec.get("supports_options"):
            continue
        field_entry = fields.get(field_name) or {}
        field_id = str((field_entry or {}).get("id", "")).strip()
        if not field_id:
            continue
        configured_options = configured_custom_field_options(
            field,
            spec,
            role_ids=role_ids,
        )
        ensure_result = ensure_field_options(
            client,
            field_id,
            configured_options,
        )
        results["custom_fields"]["options_updated"].append(
            {
                "field": field_name,
                "context_id": ensure_result["context_id"],
                "created_options": ensure_result["created_options"],
            }
        )
    for field in active_fields:
        field_name = str(field.get("name", "")).strip()
        field_entry = fields.get(field_name) or {}
        field_id = str((field_entry or {}).get("id", "")).strip()
        if not field_name or not field_id:
            continue
        if ensure_field_on_default_screen(client, field_id):
            results["custom_fields"]["added_to_default_screen"].append(field_name)

    for dashboard in model.get("dashboards") or []:
        if not isinstance(dashboard, dict):
            continue
        dashboard_name = str(dashboard.get("name", "")).strip()
        if not dashboard_name or dashboard_name in dashboards:
            continue
        client.request_json(
            "jira",
            "/rest/api/3/dashboard",
            method="POST",
            payload={
                "name": dashboard_name,
                "description": "Dashboard canonico do piloto AI control plane.",
                "sharePermissions": [{"type": "authenticated"}],
                "editPermissions": [],
            },
        )
        results["dashboards"]["created"].append(dashboard_name)
        dashboards = current_dashboards_by_name(client)

    return results
