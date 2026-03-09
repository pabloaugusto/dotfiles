from __future__ import annotations

import base64
import json
import mimetypes
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
    ("Agent", "agent"),
    ("Interaction Type", "interaction_type"),
    ("Status", "status"),
    ("Contexto", "contexto"),
    ("Evidencias", "evidencias"),
    ("Proximo passo", "proximo_passo"),
)


def build_basic_auth_header(email: str, token: str) -> str:
    payload = f"{email}:{token}".encode()
    encoded = base64.b64encode(payload).decode("ascii")
    return f"Basic {encoded}"


def adf_text_document(text: str) -> dict[str, Any]:
    normalized = text.strip()
    paragraph_node: dict[str, Any] = {
        "type": "paragraph",
        "content": [],
    }
    if normalized:
        paragraph_node["content"] = [
            {
                "type": "text",
                "text": normalized,
            }
        ]
    return {
        "type": "doc",
        "version": 1,
        "content": [paragraph_node],
    }


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
    for label, key in STRUCTURED_COMMENT_FIELDS:
        values = _comment_values(activity.get(key, activity.get(label)))
        if not values:
            lines.append(f"{label}: n/a")
            continue
        if len(values) == 1:
            lines.append(f"{label}: {values[0]}")
            continue
        lines.append(f"{label}:")
        lines.extend(f"- {value}" for value in values)
    return "\n".join(lines)


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
            raise AtlassianPlatformError("request_json aceita payload JSON ou raw_body, nunca ambos.")
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
    ) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            "/rest/api/3/issue",
            method="POST",
            payload={
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"name": issue_type},
                    "summary": summary.strip(),
                    "description": adf_text_document(description),
                    **({"labels": labels} if labels else {}),
                }
            },
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira create_issue retornou payload inesperado.")
        return payload

    def add_comment(self, issue_key: str, body_text: str) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}/comment",
            method="POST",
            payload={"body": adf_text_document(body_text)},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira add_comment retornou payload inesperado.")
        return payload

    def update_issue_fields(self, issue_key: str, fields: dict[str, Any]) -> dict[str, Any]:
        payload = self.client.request_json(
            "jira",
            f"/rest/api/3/issue/{quote(issue_key, safe='')}",
            method="PUT",
            payload={"fields": fields},
        )
        if not isinstance(payload, dict):
            raise AtlassianPlatformError("Jira update_issue_fields retornou payload inesperado.")
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
                    "Content-Disposition: form-data; name=\"file\"; "
                    f"filename=\"{resolved_file.name}\"\r\n"
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
