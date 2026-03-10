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
from scripts.atlassian_platform_lib import AtlassianHttpClient, AtlassianPlatformError

DEFAULT_JIRA_MODEL_PATH = Path("config/ai/jira-model.yaml")


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
    fields_payload = client.request_json(
        "jira",
        "/rest/api/3/field/search",
        params={"maxResults": "200"},
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
    field_names = sorted(
        str(field.get("name", "")).strip()
        for field in fields_payload.get("values", [])
        if str(field.get("name", "")).strip()
    )

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

    desired_statuses = set(summary["workflow_statuses"])
    desired_issue_types = set(summary["issue_types"])
    desired_components = set(summary["components"])
    desired_fields = set(summary["custom_fields"])

    current_statuses = set(current["statuses"])
    current_issue_types = set(current["issue_types"])
    current_components = set(current["components"])
    current_fields = set(current["fields"])

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
        },
        "board_access": current["board"],
    }
