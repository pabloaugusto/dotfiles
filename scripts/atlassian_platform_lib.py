from __future__ import annotations

import base64
import json
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    ResolvedAtlassianPlatform,
    load_ai_control_plane,
    resolve_atlassian_platform,
    summary_payload,
)


class AtlassianPlatformError(AiControlPlaneError):
    """Raised when Atlassian platform operations fail."""


STRUCTURED_COMMENT_FIELDS = (
    ("Agente", "agent"),
    ("Tipo de interacao", "interaction_type"),
    ("Status atual", "status"),
    ("Contexto", "contexto"),
    ("Evidencias", "evidencias"),
    ("Proximo passo", "proximo_passo"),
)

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s<>)\]]+")
ISSUE_KEY_RE = re.compile(r"(?<![A-Z0-9-])([A-Z][A-Z0-9]+-\d+)(?![A-Z0-9-])")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
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


def build_basic_auth_header(email: str, token: str) -> str:
    payload = f"{email}:{token}".encode()
    encoded = base64.b64encode(payload).decode("ascii")
    return f"Basic {encoded}"


def _text_node(text: str, *, link_url: str = "") -> dict[str, Any]:
    node: dict[str, Any] = {
        "type": "text",
        "text": text,
    }
    if link_url:
        node["marks"] = [
            {
                "type": "link",
                "attrs": {"href": link_url},
            }
        ]
    return node


def _strip_trailing_url_punctuation(url: str) -> tuple[str, str]:
    trimmed = url
    trailing = ""
    while trimmed and trimmed[-1] in ".,;:)]":
        trailing = trimmed[-1] + trailing
        trimmed = trimmed[:-1]
    return trimmed, trailing


def _append_plain_node(nodes: list[dict[str, Any]], text: str) -> None:
    if not text:
        return
    nodes.append(_text_node(text))


def _append_link_node(nodes: list[dict[str, Any]], text: str, url: str) -> None:
    if not text:
        return
    nodes.append(_text_node(text, link_url=url))


def adf_inline_content(text: str, *, site_url: str = "") -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(text):
        markdown_match = MARKDOWN_LINK_RE.search(text, cursor)
        url_match = URL_RE.search(text, cursor)
        issue_match = ISSUE_KEY_RE.search(text, cursor) if site_url.strip() else None
        matches = [match for match in (markdown_match, url_match, issue_match) if match is not None]
        if not matches:
            _append_plain_node(nodes, text[cursor:])
            break
        match = min(matches, key=lambda item: item.start())
        if match.start() > cursor:
            _append_plain_node(nodes, text[cursor : match.start()])
        if match.re is MARKDOWN_LINK_RE:
            label = match.group(1)
            url = match.group(2)
            _append_link_node(nodes, label, url)
        elif match.re is URL_RE:
            raw_url = match.group(0)
            normalized_url, trailing = _strip_trailing_url_punctuation(raw_url)
            _append_link_node(nodes, normalized_url, normalized_url)
            _append_plain_node(nodes, trailing)
        else:
            issue_key = match.group(1)
            _append_link_node(
                nodes,
                issue_key,
                f"{site_url.rstrip('/')}/browse/{issue_key}",
            )
        cursor = match.end()
    return nodes


def adf_text_document(text: str, *, site_url: str = "") -> dict[str, Any]:
    normalized = text.strip()
    if not normalized:
        return {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": []}],
        }

    content: list[dict[str, Any]] = []
    bullet_items: list[str] = []

    def flush_bullets() -> None:
        nonlocal bullet_items
        if not bullet_items:
            return
        content.append(
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": adf_inline_content(item, site_url=site_url),
                            }
                        ],
                    }
                    for item in bullet_items
                ],
            }
        )
        bullet_items = []

    for raw_line in normalized.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            flush_bullets()
            continue
        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            flush_bullets()
            level = min(6, len(heading_match.group(1)))
            heading_text = heading_match.group(2).strip()
            content.append(
                {
                    "type": "heading",
                    "attrs": {"level": level},
                    "content": adf_inline_content(heading_text, site_url=site_url),
                }
            )
            continue
        if stripped.startswith("- "):
            bullet_items.append(stripped[2:].strip())
            continue
        flush_bullets()
        content.append(
            {
                "type": "paragraph",
                "content": adf_inline_content(stripped, site_url=site_url),
            }
        )
    flush_bullets()
    if not content:
        content = [{"type": "paragraph", "content": []}]
    return {
        "type": "doc",
        "version": 1,
        "content": content,
    }


def adf_to_text(node: Any) -> str:
    if isinstance(node, dict):
        node_type = str(node.get("type", "")).strip()
        content = node.get("content")
        if node_type == "text":
            return str(node.get("text", ""))
        if node_type == "hardBreak":
            return "\n"
        if node_type in {"paragraph", "heading"}:
            parts = [adf_to_text(item) for item in content or []]
            return "".join(parts).strip()
        if node_type == "doc":
            parts = [adf_to_text(item).strip() for item in content or []]
            return "\n".join(part for part in parts if part)
        if node_type == "bulletList":
            lines: list[str] = []
            for item in content or []:
                item_text = adf_to_text(item).strip()
                if item_text:
                    lines.append(f"- {item_text}")
            return "\n".join(lines)
        if node_type == "listItem":
            parts = [adf_to_text(item).strip() for item in content or []]
            return "\n".join(part for part in parts if part)
        if isinstance(content, list):
            parts = [adf_to_text(item) for item in content]
            return "\n".join(part for part in parts if part.strip())
        return ""
    if isinstance(node, list):
        parts = [adf_to_text(item).strip() for item in node]
        return "\n".join(part for part in parts if part)
    return ""


def flatten_adf_text(node: Any) -> str:
    return normalize_text_for_dedup(adf_to_text(node))


def normalize_text_for_dedup(text: str) -> str:
    return " ".join(text.split())


def canonicalize_workflow_status(value: Any) -> str:
    normalized = normalize_text_for_dedup(str(value or "")).casefold()
    return WORKFLOW_STATUS_ALIASES.get(normalized, normalized)


def _comment_values(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, str):
        normalized = raw_value.strip()
        return [normalized] if normalized else []
    if isinstance(raw_value, list):
        values: list[str] = []
        for entry in raw_value:
            normalized = str(entry).strip()
            if normalized:
                values.append(normalized)
        return values
    normalized = str(raw_value).strip()
    return [normalized] if normalized else []


def render_structured_comment(activity: dict[str, Any]) -> str:
    lines: list[str] = []
    header_fields = STRUCTURED_COMMENT_FIELDS[:3]
    detail_fields = STRUCTURED_COMMENT_FIELDS[3:]

    for label, key in header_fields:
        values = _comment_values(activity.get(key, activity.get(label)))
        if key == "status" and values:
            values = [canonicalize_workflow_status(values[0]) or values[0]]
        value = values[0] if values else "n/a"
        lines.append(f"{label}: {value}")

    for label, key in detail_fields:
        values = _comment_values(activity.get(key, activity.get(label)))
        lines.append("")
        lines.append(f"## {label}")
        if not values:
            lines.append("- n/a")
            continue
        lines.extend(f"- {value}" for value in values)
    return "\n".join(lines)


def field_entry_requires_adf(field_entry: dict[str, Any] | None) -> bool:
    if not isinstance(field_entry, dict):
        return False
    schema = field_entry.get("schema")
    if not isinstance(schema, dict):
        return False
    custom_key = str(schema.get("custom", "")).strip()
    return custom_key == "com.atlassian.jira.plugin.system.customfieldtypes:textarea"


class AtlassianHttpClient:
    def __init__(self, resolved: ResolvedAtlassianPlatform) -> None:
        self.resolved = resolved

    def build_url(
        self,
        product: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url_for(product)}{normalized_path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        return url

    def base_url_for(self, product: str) -> str:
        normalized_product = product.strip().lower()
        if self.resolved.auth_mode == "service-account-api-token":
            if not self.resolved.cloud_id:
                raise AtlassianPlatformError(
                    "cloud_id e obrigatorio para auth_mode=service-account-api-token."
                )
            if normalized_product == "jira":
                return f"https://api.atlassian.com/ex/jira/{self.resolved.cloud_id}"
            if normalized_product == "confluence":
                return f"https://api.atlassian.com/ex/confluence/{self.resolved.cloud_id}"
            raise AtlassianPlatformError(f"Produto Atlassian nao suportado: {product}")
        return self.resolved.site_url

    def auth_headers(self) -> dict[str, str]:
        if self.resolved.auth_mode == "service-account-api-token":
            return {
                "Authorization": f"Bearer {self.resolved.token}",
                "Accept": "application/json",
            }
        return {
            "Authorization": build_basic_auth_header(
                self.resolved.email,
                self.resolved.token,
            ),
            "Accept": "application/json",
        }

    def request_json(
        self,
        product: str,
        path: str,
        *,
        method: str = "GET",
        params: dict[str, str] | None = None,
        payload: Any | None = None,
        raw_body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        if payload is not None and raw_body is not None:
            raise AtlassianPlatformError(
                "request_json aceita payload JSON ou raw_body, nunca ambos."
            )
        body = raw_body
        headers = self.auth_headers()
        if extra_headers:
            headers.update(extra_headers)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            self.build_url(product, path, params),
            headers=headers,
            method=method,
            data=body,
        )
        try:
            with urlopen(request, timeout=30) as response:
                text = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise AtlassianPlatformError(
                f"Atlassian API {exc.code} em {path}: {detail[:300] or exc.reason}"
            ) from exc
        except URLError as exc:
            raise AtlassianPlatformError(
                f"Falha de conectividade com Atlassian em {path}: {exc.reason}"
            ) from exc
        try:
            return json.loads(text or "{}")
        except json.JSONDecodeError as exc:
            raise AtlassianPlatformError(
                f"Resposta JSON invalida recebida de Atlassian em {path}."
            ) from exc


def probe_http_endpoint(url: str, headers: dict[str, str]) -> dict[str, Any]:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace").strip()
            return {
                "status_code": response.status,
                "ok": 200 <= response.status < 300,
                "detail": body[:300],
            }
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        return {
            "status_code": exc.code,
            "ok": False,
            "detail": detail[:300] or str(exc.reason),
        }
    except URLError as exc:
        return {
            "status_code": 0,
            "ok": False,
            "detail": f"URLError: {exc.reason}",
        }


def jira_board_probe_matrix(resolved: ResolvedAtlassianPlatform) -> dict[str, dict[str, Any]]:
    board_path = "/rest/agile/1.0/board?maxResults=1"
    gateway_url = f"https://api.atlassian.com/ex/jira/{resolved.cloud_id}{board_path}"
    site_url = f"{resolved.site_url.rstrip('/')}{board_path}"
    return {
        "gateway_bearer": probe_http_endpoint(
            gateway_url,
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {resolved.token}",
            },
        ),
        "gateway_basic": probe_http_endpoint(
            gateway_url,
            {
                "Accept": "application/json",
                "Authorization": build_basic_auth_header(resolved.email, resolved.token),
            },
        ),
        "site_basic": probe_http_endpoint(
            site_url,
            {
                "Accept": "application/json",
                "Authorization": build_basic_auth_header(resolved.email, resolved.token),
            },
        ),
        "site_bearer": probe_http_endpoint(
            site_url,
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {resolved.token}",
            },
        ),
    }


class JiraAdapter:
    def __init__(self, client: AtlassianHttpClient) -> None:
        self.client = client
        self._field_catalog_by_name: dict[str, dict[str, Any]] | None = None

    def current_user(self) -> dict[str, Any]:
        payload = self.client.request_json("jira", "/rest/api/3/myself")
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira /myself retornou payload inesperado.")
        return payload

    def get_project(self, project_key: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/project/{quote(project_key, safe='')}",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira project retornou payload inesperado.")
        return payload

    def site_url(self) -> str:
        resolved = getattr(self.client, "resolved", None)
        if resolved is None:
            return ""
        return str(getattr(resolved, "site_url", "")).strip()

    def get_issue(
        self,
        issue_key: str,
        *,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] | None = None
        if fields:
            params = {"fields": ",".join(fields)}
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}",
            params=params,
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira issue retornou payload inesperado.")
        return payload

    def get_issue_editmeta(self, issue_key: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/editmeta",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira editmeta retornou payload inesperado.")
        return payload

    def editable_field_ids(self, issue_key: str) -> set[str]:
        payload = self.get_issue_editmeta(issue_key)
        fields = payload.get("fields")
        if not isinstance(fields, dict):
            raise AtlassianPlatformError("Jira editmeta retornou fields em formato inesperado.")
        return {
            str(field_id).strip()
            for field_id in fields
            if str(field_id).strip()
        }

    def search_issues(
        self,
        jql: str,
        *,
        fields: list[str] | None = None,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        params = {
            "jql": jql.strip(),
            "maxResults": str(max_results),
        }
        if fields:
            params["fields"] = ",".join(fields)
        payload = self.client.request_json(
            "jira",
            "/rest/api/3/search/jql",
            params=params,
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira search retornou payload inesperado.")
        issues = payload.get("issues")
        if not isinstance(issues, list):
            raise AtlassianPlatformError("Jira search retornou issues em formato inesperado.")
        return [entry for entry in issues if isinstance(entry, dict)]

    def find_issue_by_summary(
        self,
        *,
        project_key: str,
        summary: str,
        issue_types: list[str] | None = None,
    ) -> dict[str, Any] | None:
        escaped_summary = summary.replace("\\", "\\\\").replace('"', '\\"').strip()
        issue_type_clause = ""
        if issue_types:
            quoted = ", ".join(f'"{item.strip()}"' for item in issue_types if item.strip())
            if quoted:
                issue_type_clause = f" AND issuetype IN ({quoted})"
        jql = (
            f'project = "{project_key.strip()}"'
            f'{issue_type_clause} AND summary ~ "\\"{escaped_summary}\\""'
            " ORDER BY created DESC"
        )
        issues = self.search_issues(
            jql,
            fields=["summary", "status", "issuetype"],
            max_results=10,
        )
        normalized = summary.strip()
        for issue in issues:
            fields = issue.get("fields")
            if not isinstance(fields, dict):
                continue
            if str(fields.get("summary", "")).strip() == normalized:
                return issue
        return None

    def create_issue(
        self,
        *,
        project_key: str,
        issue_type: str,
        summary: str,
        description: str,
        labels: list[str] | None = None,
        extra_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type},
            "summary": summary.strip(),
            "description": adf_text_document(description, site_url=self.site_url()),
            **({"labels": labels} if labels else {}),
        }
        if extra_fields:
            fields.update(extra_fields)
        payload = self.client.request_json(
            "jira",
            "/rest/api/3/issue",
            method="POST",
            payload={"fields": fields},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira create_issue retornou payload inesperado.")
        return payload

    def add_comment(self, issue_key: str, body_text: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/comment",
            method="POST",
            payload={"body": adf_text_document(body_text, site_url=self.site_url())},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira add_comment retornou payload inesperado.")
        return payload

    def list_comments(self, issue_key: str, *, max_results: int = 200) -> list[dict[str, Any]]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/comment",
            params={"maxResults": str(max_results)},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira list_comments retornou payload inesperado.")
        comments = payload.get("comments")
        if not isinstance(comments, list):
            raise AtlassianPlatformError(
                "Jira list_comments retornou comments em formato inesperado."
            )
        return [entry for entry in comments if isinstance(entry, dict)]

    def update_comment(self, issue_key: str, comment_id: str, body_text: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/comment/{quote(comment_id, safe='')}",
            method="PUT",
            payload={"body": adf_text_document(body_text, site_url=self.site_url())},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira update_comment retornou payload inesperado.")
        return payload

    def delete_comment(self, issue_key: str, comment_id: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/comment/{quote(comment_id, safe='')}",
            method="DELETE",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira delete_comment retornou payload inesperado.")
        return payload

    def ensure_comment(self, issue_key: str, body_text: str) -> tuple[dict[str, Any], bool]:
        normalized = normalize_text_for_dedup(body_text)
        for comment in self.list_comments(issue_key):
            body = comment.get("body")
            if normalize_text_for_dedup(flatten_adf_text(body)) == normalized:
                return comment, False
        return self.add_comment(issue_key, body_text), True

    def set_agent_roles(
        self,
        issue_key: str,
        *,
        current_agent_role: str = "",
        next_required_role: str = "",
    ) -> dict[str, Any]:
        current_field_id = self.field_id_by_name("Current Agent Role")
        next_field_id = self.field_id_by_name("Next Required Role")
        fields: dict[str, Any] = {}
        if current_field_id:
            fields[current_field_id] = (
                {"value": current_agent_role.strip()} if current_agent_role.strip() else None
            )
        if next_field_id:
            fields[next_field_id] = (
                {"value": next_required_role.strip()} if next_required_role.strip() else None
            )
        if not fields:
            return {}
        return self.update_issue_fields(issue_key, fields)

    def log_issue_activity(
        self,
        issue_key: str,
        *,
        agent: str,
        interaction_type: str,
        status: str,
        contexto: list[str] | None = None,
        evidencias: list[str] | None = None,
        proximo_passo: str = "",
        current_agent_role: str = "",
        next_required_role: str = "",
        sync_roles: bool = True,
    ) -> dict[str, Any]:
        rendered = render_structured_comment(
            {
                "agent": agent,
                "interaction_type": interaction_type,
                "status": status,
                "contexto": contexto or [],
                "evidencias": evidencias or [],
                "proximo_passo": proximo_passo,
            }
        )
        comment, created = self.ensure_comment(issue_key, rendered)
        role_result: dict[str, Any] = {}
        if sync_roles:
            role_result = self.set_agent_roles(
                issue_key,
                current_agent_role=current_agent_role,
                next_required_role=next_required_role,
            )
        return {
            "comment": comment,
            "comment_created": created,
            "status": canonicalize_workflow_status(status),
            "current_agent_role": current_agent_role.strip(),
            "next_required_role": next_required_role.strip(),
            "role_sync": role_result,
        }

    def update_issue_fields(self, issue_key: str, fields: dict[str, Any]) -> dict[str, Any]:
        normalized_fields = dict(fields)
        catalog = self.field_catalog_by_name()
        field_entries_by_id = {
            str(entry.get("id", "")).strip(): entry
            for entry in catalog.values()
            if isinstance(entry, dict) and str(entry.get("id", "")).strip()
        }
        for field_key, raw_value in list(normalized_fields.items()):
            if not isinstance(raw_value, str):
                continue
            normalized_key = str(field_key).strip()
            if normalized_key == "description" or field_entry_requires_adf(
                field_entries_by_id.get(normalized_key)
            ):
                normalized_fields[field_key] = adf_text_document(
                    raw_value,
                    site_url=self.site_url(),
                )
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}",
            method="PUT",
            payload={"fields": normalized_fields},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira update_issue_fields retornou payload inesperado.")
        return payload

    def field_catalog_by_name(self, *, refresh: bool = False) -> dict[str, dict[str, Any]]:
        if self._field_catalog_by_name is not None and not refresh:
            return dict(self._field_catalog_by_name)
        start_at = 0
        catalog: dict[str, dict[str, Any]] = {}
        while True:
            payload = self.client.request_json(
                "jira",
                "/rest/api/3/field/search",
                params={"startAt": str(start_at), "maxResults": "100"},
            )
            if not isinstance(payload, dict):
                raise AtlassianPlatformError("Jira field search retornou payload inesperado.")
            values = payload.get("values")
            if not isinstance(values, list):
                raise AtlassianPlatformError(
                    "Jira field search retornou values em formato inesperado."
                )
            for entry in values:
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("name", "")).strip()
                if not name or name in catalog:
                    continue
                catalog[name] = entry
            if payload.get("isLast", True):
                break
            start_at += int(payload.get("maxResults", 100) or 100)
        self._field_catalog_by_name = dict(catalog)
        return dict(catalog)

    def field_id_by_name(self, field_name: str, *, refresh: bool = False) -> str:
        normalized_name = field_name.strip()
        if not normalized_name:
            raise AtlassianPlatformError("field_id_by_name exige um nome de field nao vazio.")
        catalog = self.field_catalog_by_name(refresh=refresh)
        entry = catalog.get(normalized_name)
        if not isinstance(entry, dict):
            raise AtlassianPlatformError(
                f"Jira field search nao encontrou o field {normalized_name!r}."
            )
        field_id = str(entry.get("id", "")).strip()
        if not field_id:
            raise AtlassianPlatformError(
                f"Jira field search retornou id vazio para {normalized_name!r}."
            )
        return field_id

    def field_screens(self, field_id: str) -> list[dict[str, Any]]:
        normalized_field_id = field_id.strip()
        if not normalized_field_id:
            raise AtlassianPlatformError("field_screens exige um field_id nao vazio.")
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/field/{quote(normalized_field_id, safe='')}/screens",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira field screens retornou payload inesperado.")
        values = payload.get("values")
        if not isinstance(values, list):
            raise AtlassianPlatformError(
                "Jira field screens retornou values em formato inesperado."
            )
        return [entry for entry in values if isinstance(entry, dict)]

    def add_field_to_default_screen(self, field_id: str) -> dict[str, Any]:
        normalized_field_id = field_id.strip()
        if not normalized_field_id:
            raise AtlassianPlatformError(
                "add_field_to_default_screen exige um field_id nao vazio."
            )
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/screens/addToDefault/{quote(normalized_field_id, safe='')}",
            method="POST",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError(
                "Jira add_field_to_default_screen retornou payload inesperado."
            )
        return payload

    def list_screen_tabs(self, screen_id: str) -> list[dict[str, Any]]:
        normalized_screen_id = screen_id.strip()
        if not normalized_screen_id:
            raise AtlassianPlatformError("list_screen_tabs exige um screen_id nao vazio.")
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/screens/{quote(normalized_screen_id, safe='')}/tabs",
        )
        if not isinstance(payload, list):
            raise AtlassianPlatformError("Jira screen tabs retornou payload inesperado.")
        return [entry for entry in payload if isinstance(entry, dict)]

    def list_screen_fields(self, screen_id: str, tab_id: str) -> list[dict[str, Any]]:
        normalized_screen_id = screen_id.strip()
        normalized_tab_id = tab_id.strip()
        if not normalized_screen_id or not normalized_tab_id:
            raise AtlassianPlatformError(
                "list_screen_fields exige screen_id e tab_id nao vazios."
            )
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/screens/{quote(normalized_screen_id, safe='')}/tabs/{quote(normalized_tab_id, safe='')}/fields",
        )
        if not isinstance(payload, list):
            raise AtlassianPlatformError("Jira screen fields retornou payload inesperado.")
        return [entry for entry in payload if isinstance(entry, dict)]

    def add_field_to_screen_tab(
        self,
        screen_id: str,
        tab_id: str,
        field_id: str,
    ) -> dict[str, Any]:
        normalized_screen_id = screen_id.strip()
        normalized_tab_id = tab_id.strip()
        normalized_field_id = field_id.strip()
        if not normalized_screen_id or not normalized_tab_id or not normalized_field_id:
            raise AtlassianPlatformError(
                "add_field_to_screen_tab exige screen_id, tab_id e field_id nao vazios."
            )
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/screens/{quote(normalized_screen_id, safe='')}/tabs/{quote(normalized_tab_id, safe='')}/fields",
            method="POST",
            payload={"fieldId": normalized_field_id},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError(
                "Jira add_field_to_screen_tab retornou payload inesperado."
            )
        return payload

    def ensure_issue_fields_editable(
        self,
        issue_key: str,
        field_names: list[str],
        *,
        fallback_screen_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        resolved_fields: dict[str, str] = {}
        for field_name in field_names:
            normalized_name = str(field_name).strip()
            if not normalized_name:
                continue
            resolved_fields[normalized_name] = self.field_id_by_name(normalized_name)

        initial_editable = self.editable_field_ids(issue_key)
        missing_fields = {
            name: field_id
            for name, field_id in resolved_fields.items()
            if field_id not in initial_editable
        }
        result: dict[str, Any] = {
            "issue_key": issue_key,
            "field_ids": dict(resolved_fields),
            "initial_missing": dict(missing_fields),
            "added_to_default_screen": [],
            "added_to_tabs": [],
            "remaining_missing": {},
        }
        if not missing_fields:
            return result

        for field_name, field_id in list(missing_fields.items()):
            if self.field_screens(field_id):
                continue
            self.add_field_to_default_screen(field_id)
            result["added_to_default_screen"].append(field_name)

        editable_after_default = self.editable_field_ids(issue_key)
        missing_fields = {
            name: field_id
            for name, field_id in resolved_fields.items()
            if field_id not in editable_after_default
        }
        if missing_fields and fallback_screen_ids:
            for screen_id in fallback_screen_ids:
                normalized_screen_id = str(screen_id).strip()
                if not normalized_screen_id:
                    continue
                tabs = self.list_screen_tabs(normalized_screen_id)
                if not tabs:
                    continue
                first_tab_id = str((tabs[0] or {}).get("id", "")).strip()
                if not first_tab_id:
                    continue
                existing_field_ids = {
                    str(entry.get("id", "")).strip()
                    for entry in self.list_screen_fields(normalized_screen_id, first_tab_id)
                    if str(entry.get("id", "")).strip()
                }
                for field_name, field_id in list(missing_fields.items()):
                    if field_id in existing_field_ids:
                        continue
                    self.add_field_to_screen_tab(normalized_screen_id, first_tab_id, field_id)
                    result["added_to_tabs"].append(
                        {
                            "field": field_name,
                            "screen_id": normalized_screen_id,
                            "tab_id": first_tab_id,
                        }
                    )
                    existing_field_ids.add(field_id)

        final_editable = self.editable_field_ids(issue_key)
        result["remaining_missing"] = {
            name: field_id
            for name, field_id in resolved_fields.items()
            if field_id not in final_editable
        }
        return result

    def update_issue_fields_by_name(
        self,
        issue_key: str,
        fields_by_name: dict[str, Any],
    ) -> dict[str, Any]:
        normalized_fields: dict[str, Any] = {}
        catalog = self.field_catalog_by_name()
        for field_name, value in fields_by_name.items():
            normalized_name = str(field_name).strip()
            if not normalized_name:
                continue
            field_id = self.field_id_by_name(normalized_name)
            normalized_value = value
            field_entry = catalog.get(normalized_name)
            if (
                field_id == "description"
                or field_entry_requires_adf(field_entry)
            ) and isinstance(normalized_value, str):
                normalized_value = adf_text_document(
                    normalized_value,
                    site_url=self.site_url(),
                )
            normalized_fields[field_id] = normalized_value
        editable_field_ids = self.editable_field_ids(issue_key)
        non_editable = {
            field_name: field_id
            for field_name, field_id in (
                (str(field_name).strip(), self.field_id_by_name(str(field_name).strip()))
                for field_name in fields_by_name
                if str(field_name).strip()
            )
            if field_id not in editable_field_ids
        }
        if non_editable:
            details = ", ".join(
                f"{field_name} ({field_id})" for field_name, field_id in sorted(non_editable.items())
            )
            raise AtlassianPlatformError(
                "Jira recusou campos fora do editmeta desta issue. "
                f"Campos nao editaveis em {issue_key}: {details}."
            )
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}",
            method="PUT",
            payload={"fields": normalized_fields},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError(
                "Jira update_issue_fields_by_name retornou payload inesperado."
            )
        return payload

    def add_attachment(self, issue_key: str, file_path: str | Path) -> list[dict[str, Any]]:
        resolved_file = Path(file_path).resolve()
        if not resolved_file.is_file():
            raise AtlassianPlatformError(f"Attachment Jira nao encontrado: {resolved_file}")
        boundary = f"----dotfiles-atlassian-{uuid.uuid4().hex}"
        content_type = mimetypes.guess_type(resolved_file.name)[0] or "application/octet-stream"
        file_bytes = resolved_file.read_bytes()
        body = b"".join(
            [
                f"--{boundary}\r\n".encode(),
                (
                    'Content-Disposition: form-data; name="file"; '
                    f'filename="{resolved_file.name}"\r\n'
                ).encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                file_bytes,
                b"\r\n",
                f"--{boundary}--\r\n".encode(),
            ]
        )
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/attachments",
            method="POST",
            raw_body=body,
            extra_headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "X-Atlassian-Token": "no-check",
            },
        )
        if not isinstance(payload, list):
            raise AtlassianPlatformError("Jira add_attachment retornou payload inesperado.")
        return [entry for entry in payload if isinstance(entry, dict)]

    def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/transitions",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira get_transitions retornou payload inesperado.")
        transitions = payload.get("transitions")
        if not isinstance(transitions, list):
            raise AtlassianPlatformError(
                "Jira get_transitions retornou transitions em formato inesperado."
            )
        return [entry for entry in transitions if isinstance(entry, dict)]

    def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/transitions",
            method="POST",
            payload={"transition": {"id": transition_id}},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira transition_issue retornou payload inesperado.")
        return payload

    def ensure_issue_link(
        self,
        issue_key: str,
        target_issue_key: str,
        *,
        link_type: str = "Relates",
    ) -> bool:
        if issue_key.strip().upper() == target_issue_key.strip().upper():
            return False
        issue = self.get_issue(issue_key, fields=["issuelinks"])
        fields = issue.get("fields") or {}
        for entry in fields.get("issuelinks") or []:
            if not isinstance(entry, dict):
                continue
            type_payload = entry.get("type") or {}
            current_type = str(type_payload.get("name", "")).strip()
            linked_issue = entry.get("outwardIssue") or entry.get("inwardIssue") or {}
            linked_key = str(linked_issue.get("key", "")).strip().upper()
            if linked_key == target_issue_key.strip().upper() and current_type == link_type:
                return False
        self.client.request_json(
            "jira",
            "/rest/api/3/issueLink",
            method="POST",
            payload={
                "type": {"name": link_type},
                "inwardIssue": {"key": issue_key},
                "outwardIssue": {"key": target_issue_key},
            },
        )
        return True

    def list_issue_links(self, issue_key: str) -> list[dict[str, Any]]:
        issue = self.get_issue(issue_key, fields=["issuelinks"])
        fields = issue.get("fields") or {}
        issue_links = fields.get("issuelinks")
        if not isinstance(issue_links, list):
            raise AtlassianPlatformError(
                "Jira list_issue_links retornou issuelinks em formato inesperado."
            )
        return [entry for entry in issue_links if isinstance(entry, dict)]

    def delete_issue_link(self, link_id: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issueLink/{quote(link_id, safe='')}",
            method="DELETE",
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira delete_issue_link retornou payload inesperado.")
        return payload

    def list_issue_link_types(self) -> list[dict[str, Any]]:
        payload = self.client.request_json("jira", "/rest/api/3/issueLinkType")
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira issueLinkType retornou payload inesperado.")
        link_types = payload.get("issueLinkTypes")
        if not isinstance(link_types, list):
            raise AtlassianPlatformError(
                "Jira issueLinkType retornou issueLinkTypes em formato inesperado."
            )
        return [entry for entry in link_types if isinstance(entry, dict)]


class ConfluenceAdapter:
    def __init__(self, client: AtlassianHttpClient) -> None:
        self.client = client

    def get_space(self, space_key: str) -> dict[str, Any]:
        normalized_key = space_key.strip()
        payload = self.client.request_json(
            "confluence",
            "/wiki/api/v2/spaces",
            params={
                "keys": normalized_key,
                "limit": "1",
            },
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Confluence spaces retornou payload inesperado.")
        results = payload.get("results")
        if not isinstance(results, list):
            raise AtlassianPlatformError(
                "Confluence spaces retornou results em formato inesperado."
            )
        for entry in results:
            if not isinstance(entry, dict):
                continue
            key = str(entry.get("key", "")).strip().upper()
            active_alias = str(entry.get("currentActiveAlias", "")).strip().upper()
            if key == normalized_key.upper() or active_alias == normalized_key.upper():
                return entry
        if len(results) == 1 and isinstance(results[0], dict):
            return results[0]
        raise AtlassianPlatformError(
            f"Confluence nao retornou space para a key {normalized_key!r}."
        )

    def list_pages(
        self,
        *,
        space_key: str,
        title: str = "",
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        space = self.get_space(space_key)
        space_id = str(space.get("id", "")).strip()
        if not space_id:
            raise AtlassianPlatformError("Confluence list_pages exige um space com id resolvido.")
        params = {
            "space-id": space_id,
            "limit": str(limit),
        }
        if title.strip():
            params["title"] = title.strip()
        payload = self.client.request_json(
            "confluence",
            "/wiki/api/v2/pages",
            params=params,
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Confluence pages retornou payload inesperado.")
        results = payload.get("results")
        if not isinstance(results, list):
            raise AtlassianPlatformError("Confluence pages retornou results em formato inesperado.")
        return [entry for entry in results if isinstance(entry, dict)]

    def find_page_by_title(self, *, space_key: str, title: str) -> dict[str, Any] | None:
        normalized = title.strip()
        for entry in self.list_pages(space_key=space_key, title=normalized, limit=10):
            if str(entry.get("title", "")).strip() == normalized:
                return entry
        return None

    def create_page(
        self,
        *,
        space_key: str,
        title: str,
        storage_value: str,
        parent_page_id: str = "",
    ) -> dict[str, Any]:
        space = self.get_space(space_key)
        space_id = str(space.get("id", "")).strip()
        if not space_id:
            raise AtlassianPlatformError("Confluence create_page exige um space com id resolvido.")
        page_payload: dict[str, Any] = {
            "spaceId": space_id,
            "status": "current",
            "title": title.strip(),
            "body": {
                "representation": "storage",
                "value": storage_value,
            },
        }
        if parent_page_id.strip():
            page_payload["parentId"] = parent_page_id.strip()
        payload = self.client.request_json(
            "confluence",
            "/wiki/api/v2/pages",
            method="POST",
            payload=page_payload,
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Confluence create_page retornou payload inesperado.")
        return payload

    def get_page(self, page_id: str, *, body_format: str = "storage") -> dict[str, Any]:
        payload = self.client.request_json(
            "confluence",
            f"/wiki/api/v2/pages/{quote(page_id, safe='')}",
            params={"body-format": body_format},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Confluence get_page retornou payload inesperado.")
        return payload

    def update_page(
        self,
        *,
        page_id: str,
        title: str,
        storage_value: str,
        parent_page_id: str = "",
        version_message: str = "",
    ) -> dict[str, Any]:
        current = self.get_page(page_id, body_format="storage")
        version_payload = current.get("version") or {}
        current_version = int(version_payload.get("number") or 0)
        payload: dict[str, Any] = {
            "id": page_id,
            "status": "current",
            "title": title.strip(),
            "body": {
                "representation": "storage",
                "value": storage_value,
            },
            "version": {
                "number": current_version + 1,
                "message": version_message.strip(),
            },
        }
        space_id = str(current.get("spaceId", "")).strip()
        if space_id:
            payload["spaceId"] = space_id
        if parent_page_id.strip():
            payload["parentId"] = parent_page_id.strip()
        updated = self.client.request_json(
            "confluence",
            f"/wiki/api/v2/pages/{quote(page_id, safe='')}",
            method="PUT",
            payload=payload,
        )
        if not isinstance(updated, dict):
            raise AtlassianPlatformError("Confluence update_page retornou payload inesperado.")
        return updated


def connectivity_payload(
    repo_root: str | Path | None = None,
    *,
    site_url_override: str = "",
) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
        site_url_override=site_url_override,
    )
    client = AtlassianHttpClient(resolved)
    jira = JiraAdapter(client)
    confluence = ConfluenceAdapter(client)

    jira_payload: dict[str, Any] = {
        "enabled": resolved.jira_enabled,
    }
    if resolved.auth_mode == "service-account-api-token":
        jira_payload["current_user"] = {
            "account_id": "",
            "display_name": resolved.service_account,
            "email_address": "",
            "active": True,
            "lookup_mode": "skipped-for-scoped-service-account-token",
        }
    else:
        current_user = jira.current_user()
        jira_payload["current_user"] = {
            "account_id": str(current_user.get("accountId", "")).strip(),
            "display_name": str(current_user.get("displayName", "")).strip(),
            "email_address": str(current_user.get("emailAddress", "")).strip(),
            "active": bool(current_user.get("active", False)),
            "lookup_mode": "jira-myself",
        }
    confluence_payload: dict[str, Any] = {
        "enabled": resolved.confluence_enabled,
    }
    payload: dict[str, Any] = {
        "control_plane": summary_payload(control_plane=control_plane),
        "atlassian": {
            "enabled": resolved.enabled,
            "provider": resolved.provider,
            "auth_mode": resolved.auth_mode,
            "site_url": resolved.site_url,
            "jira_api_base_url": client.base_url_for("jira"),
            "confluence_api_base_url": client.base_url_for("confluence"),
            "cloud_id": resolved.cloud_id,
            "service_account": resolved.service_account,
        },
        "jira": jira_payload,
        "confluence": confluence_payload,
    }

    jira_ok = not resolved.jira_enabled
    if resolved.jira_enabled:
        try:
            project = jira.get_project(resolved.jira_project_key)
        except AtlassianPlatformError as exc:
            jira_payload["status"] = "error"
            jira_payload["error"] = str(exc)
        else:
            jira_payload["status"] = "ok"
            jira_payload["project"] = {
                "key": str(project.get("key", "")).strip(),
                "name": str(project.get("name", "")).strip(),
                "project_type": str(project.get("projectTypeKey", "")).strip(),
            }
            if resolved.auth_mode == "service-account-api-token" and resolved.cloud_id:
                probes = jira_board_probe_matrix(resolved)
                jira_payload["board_api"] = {
                    "status": (
                        "ok"
                        if any(entry.get("ok", False) for entry in probes.values())
                        else "error"
                    ),
                    "probes": probes,
                }
            jira_ok = True

    confluence_ok = not resolved.confluence_enabled
    if resolved.confluence_enabled:
        try:
            space = confluence.get_space(resolved.confluence_space_key)
        except AtlassianPlatformError as exc:
            confluence_payload["status"] = "error"
            confluence_payload["error"] = str(exc)
        else:
            confluence_payload["status"] = "ok"
            confluence_payload["space"] = {
                "key": str(space.get("key", "")).strip(),
                "name": str(space.get("name", "")).strip(),
                "type": str(space.get("type", "")).strip(),
            }
            confluence_ok = True

    payload["overall_ok"] = jira_ok and confluence_ok

    return payload
