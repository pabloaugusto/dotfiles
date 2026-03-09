from __future__ import annotations

import unittest
from email.message import Message
from io import BytesIO
from pathlib import Path
from typing import cast
from unittest.mock import patch
from urllib.error import HTTPError

from scripts.ai_control_plane_lib import ResolvedAtlassianPlatform
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    ConfluenceAdapter,
    JiraAdapter,
    adf_text_document,
    build_basic_auth_header,
    jira_board_probe_matrix,
    probe_http_endpoint,
    render_structured_comment,
)


class FakeAtlassianHttpClient:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def request_json(
        self,
        product: str,
        path: str,
        *,
        method: str = "GET",
        params: dict[str, str] | None = None,
        payload: object | None = None,
        raw_body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> object:
        self.calls.append(
            {
                "product": product,
                "path": path,
                "method": method,
                "params": params,
                "payload": payload,
                "raw_body": raw_body,
                "extra_headers": extra_headers,
            }
        )
        return self.responses.pop(0)


class AtlassianPlatformTests(unittest.TestCase):
    def test_build_basic_auth_header_uses_basic_scheme(self) -> None:
        header = build_basic_auth_header("bot@example.com", "secret-token")
        self.assertTrue(header.startswith("Basic "))
        self.assertNotIn("secret-token", header)

    def test_http_client_builds_expected_urls_for_site_mode(self) -> None:
        client = AtlassianHttpClient(
            ResolvedAtlassianPlatform(
                enabled=True,
                provider="atlassian-cloud",
                auth_mode="basic-api-token",
                site_url="https://example.atlassian.net",
                email="bot@example.com",
                token="secret-token",
                service_account="",
                cloud_id="",
                jira_enabled=True,
                jira_project_key="DOT",
                confluence_enabled=True,
                confluence_space_key="DOT",
            )
        )
        self.assertEqual(
            client.build_url("jira", "/rest/api/3/myself"),
            "https://example.atlassian.net/rest/api/3/myself",
        )
        self.assertEqual(
            client.build_url("confluence", "wiki/api/v2/spaces", {"keys": "DOT", "limit": "1"}),
            "https://example.atlassian.net/wiki/api/v2/spaces?keys=DOT&limit=1",
        )

    def test_http_client_builds_gateway_urls_for_service_account_mode(self) -> None:
        client = AtlassianHttpClient(
            ResolvedAtlassianPlatform(
                enabled=True,
                provider="atlassian-cloud",
                auth_mode="service-account-api-token",
                site_url="https://example.atlassian.net",
                email="",
                token="secret-token",
                service_account="dotfiles-ai-atlassian",
                cloud_id="cloud-123",
                jira_enabled=True,
                jira_project_key="DOT",
                confluence_enabled=True,
                confluence_space_key="DOT",
            )
        )
        self.assertEqual(
            client.build_url("jira", "/rest/api/3/myself"),
            "https://api.atlassian.com/ex/jira/cloud-123/rest/api/3/myself",
        )
        self.assertEqual(
            client.build_url("confluence", "/wiki/api/v2/spaces"),
            "https://api.atlassian.com/ex/confluence/cloud-123/wiki/api/v2/spaces",
        )
        self.assertEqual(
            client.auth_headers()["Authorization"],
            "Bearer secret-token",
        )

    def test_adf_text_document_builds_minimal_doc(self) -> None:
        self.assertEqual(
            adf_text_document("Texto"),
            {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Texto"}],
                    }
                ],
            },
        )

    def test_render_structured_comment_formats_multiline_evidence(self) -> None:
        rendered = render_structured_comment(
            {
                "agent": "ai-qa",
                "interaction_type": "test-success",
                "status": "Testing",
                "contexto": [
                    "Suite executada no ambiente alvo.",
                    "Sem regressao observada.",
                ],
                "evidencias": [
                    "task test:python",
                    "https://example.invalid/pipeline/123",
                ],
                "proximo_passo": "Encaminhar para Review.",
            }
        )

        self.assertIn("Agent: ai-qa", rendered)
        self.assertIn("Interaction Type: test-success", rendered)
        self.assertIn("Contexto:", rendered)
        self.assertIn("- Suite executada no ambiente alvo.", rendered)
        self.assertIn("Evidencias:", rendered)
        self.assertIn("- https://example.invalid/pipeline/123", rendered)

    def test_probe_http_endpoint_returns_success_payload(self) -> None:
        class FakeResponse:
            status = 200

            def __enter__(self) -> FakeResponse:
                return self

            def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
                return False

            def read(self) -> bytes:
                return b'{"ok":true}'

        with patch("scripts.atlassian_platform_lib.urlopen", return_value=FakeResponse()):
            payload = probe_http_endpoint("https://example.invalid", {"Accept": "application/json"})

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status_code"], 200)
        self.assertIn('"ok":true', payload["detail"])

    def test_jira_board_probe_matrix_keeps_gateway_bearer_as_primary_mode(self) -> None:
        resolved = ResolvedAtlassianPlatform(
            enabled=True,
            provider="atlassian-cloud",
            auth_mode="service-account-api-token",
            site_url="https://example.atlassian.net",
            email="bot@example.com",
            token="secret-token",
            service_account="dotfiles-ai-atlassian",
            cloud_id="cloud-123",
            jira_enabled=True,
            jira_project_key="DOT",
            confluence_enabled=True,
            confluence_space_key="DOT",
        )
        headers = Message()
        bearer_scope_mismatch = HTTPError(
            url="https://api.atlassian.com/ex/jira/cloud-123/rest/agile/1.0/board?maxResults=1",
            code=401,
            msg="Unauthorized",
            hdrs=headers,
            fp=BytesIO(b'{"code":401,"message":"Unauthorized; scope does not match"}'),
        )
        basic_unauthorized = HTTPError(
            url="https://api.atlassian.com/ex/jira/cloud-123/rest/agile/1.0/board?maxResults=1",
            code=401,
            msg="Unauthorized",
            hdrs=headers,
            fp=BytesIO(b'{"code":401,"message":"Unauthorized"}'),
        )
        site_basic = HTTPError(
            url="https://example.atlassian.net/rest/agile/1.0/board?maxResults=1",
            code=401,
            msg="Unauthorized",
            hdrs=headers,
            fp=BytesIO(b"Client must be authenticated to access this resource."),
        )
        site_bearer = HTTPError(
            url="https://example.atlassian.net/rest/agile/1.0/board?maxResults=1",
            code=403,
            msg="Forbidden",
            hdrs=headers,
            fp=BytesIO(b'{"error":"Failed to parse Connect Session Auth Token"}'),
        )

        with patch(
            "scripts.atlassian_platform_lib.urlopen",
            side_effect=[bearer_scope_mismatch, basic_unauthorized, site_basic, site_bearer],
        ):
            payload = jira_board_probe_matrix(resolved)

        self.assertEqual(
            payload["gateway_bearer"]["detail"],
            '{"code":401,"message":"Unauthorized; scope does not match"}',
        )
        self.assertEqual(payload["gateway_basic"]["status_code"], 401)
        self.assertEqual(payload["site_basic"]["status_code"], 401)
        self.assertEqual(payload["site_bearer"]["status_code"], 403)

    def test_jira_create_issue_posts_expected_payload(self) -> None:
        client = FakeAtlassianHttpClient([{"id": "10001", "key": "DOT-1"}])
        adapter = JiraAdapter(client)  # type: ignore[arg-type]
        payload = adapter.create_issue(
            project_key="DOT",
            issue_type="Task",
            summary="Bootstrap Jira",
            description="Criar projeto piloto",
            labels=["governance", "bootstrap"],
        )
        self.assertEqual(payload["key"], "DOT-1")
        self.assertEqual(client.calls[0]["product"], "jira")
        self.assertEqual(client.calls[0]["path"], "/rest/api/3/issue")
        self.assertEqual(client.calls[0]["method"], "POST")
        self.assertEqual(
            client.calls[0]["payload"],
            {
                "fields": {
                    "project": {"key": "DOT"},
                    "issuetype": {"name": "Task"},
                    "summary": "Bootstrap Jira",
                    "description": adf_text_document("Criar projeto piloto"),
                    "labels": ["governance", "bootstrap"],
                }
            },
        )

    def test_confluence_create_page_uses_space_id_from_lookup(self) -> None:
        client = FakeAtlassianHttpClient(
            [
                {
                    "results": [
                        {
                            "id": "254541826",
                            "key": "DO",
                            "name": "dotfiles",
                            "type": "global",
                            "currentActiveAlias": "DOT",
                        }
                    ],
                    "_links": {},
                },
                {"id": "98765", "title": "Bootstrap"},
            ]
        )
        adapter = ConfluenceAdapter(client)  # type: ignore[arg-type]
        payload = adapter.create_page(
            space_key="DOT",
            title="Bootstrap",
            storage_value="<p>Teste</p>",
        )
        self.assertEqual(payload["id"], "98765")
        self.assertEqual(client.calls[0]["path"], "/wiki/api/v2/spaces")
        self.assertEqual(client.calls[0]["params"], {"keys": "DOT", "limit": "1"})
        self.assertEqual(client.calls[1]["product"], "confluence")
        self.assertEqual(client.calls[1]["path"], "/wiki/api/v2/pages")
        self.assertEqual(
            client.calls[1]["payload"],
            {
                "spaceId": "254541826",
                "status": "current",
                "title": "Bootstrap",
                "body": {
                    "representation": "storage",
                    "value": "<p>Teste</p>",
                },
            },
        )

    def test_jira_update_issue_fields_posts_fields_payload(self) -> None:
        client = FakeAtlassianHttpClient([{}])
        adapter = JiraAdapter(client)  # type: ignore[arg-type]

        adapter.update_issue_fields("DOT-1", {"summary": "Resumo atualizado"})

        self.assertEqual(client.calls[0]["path"], "/rest/api/3/issue/DOT-1")
        self.assertEqual(client.calls[0]["method"], "PUT")
        self.assertEqual(client.calls[0]["payload"], {"fields": {"summary": "Resumo atualizado"}})

    def test_jira_find_issue_by_summary_escapes_windows_backslashes(self) -> None:
        client = FakeAtlassianHttpClient([{"issues": []}])
        adapter = JiraAdapter(client)  # type: ignore[arg-type]

        adapter.find_issue_by_summary(
            project_key="DOT",
            summary=r"[BUG] Corrigir ACL de C:\Users\pablo\.ssh\config",
            issue_types=["Task"],
        )

        params = client.calls[0]["params"]
        self.assertIsInstance(params, dict)
        typed_params = cast(dict[str, str], params)
        self.assertIn(r"C:\\Users\\pablo\\.ssh\\config", typed_params["jql"])

    def test_jira_add_attachment_uses_multipart_with_no_check_header(self) -> None:
        client = FakeAtlassianHttpClient([[{"id": "10000", "filename": "artifact.zip"}]])
        adapter = JiraAdapter(client)  # type: ignore[arg-type]
        temp_file = Path("tests/fixtures/atlassian-attachment.txt")
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_text("payload", encoding="utf-8")
        try:
            payload = adapter.add_attachment("DOT-1", temp_file)
        finally:
            temp_file.unlink(missing_ok=True)

        self.assertEqual(payload[0]["filename"], "artifact.zip")
        self.assertEqual(client.calls[0]["path"], "/rest/api/3/issue/DOT-1/attachments")
        self.assertEqual(client.calls[0]["method"], "POST")
        self.assertIsNone(client.calls[0]["payload"])
        self.assertIsNotNone(client.calls[0]["raw_body"])
        headers = client.calls[0]["extra_headers"]
        self.assertIsInstance(headers, dict)
        typed_headers = cast(dict[str, str], headers)
        self.assertEqual(typed_headers["X-Atlassian-Token"], "no-check")
        self.assertIn("multipart/form-data; boundary=", typed_headers["Content-Type"])

    def test_confluence_update_page_increments_version(self) -> None:
        client = FakeAtlassianHttpClient(
            [
                {
                    "id": "123",
                    "spaceId": "254541826",
                    "version": {"number": 7},
                },
                {"id": "123", "title": "Bootstrap"},
            ]
        )
        adapter = ConfluenceAdapter(client)  # type: ignore[arg-type]

        payload = adapter.update_page(
            page_id="123",
            title="Bootstrap",
            storage_value="<p>Atualizado</p>",
            version_message="sync",
        )

        self.assertEqual(payload["id"], "123")
        self.assertEqual(client.calls[0]["path"], "/wiki/api/v2/pages/123")
        self.assertEqual(client.calls[0]["params"], {"body-format": "storage"})
        self.assertEqual(client.calls[1]["method"], "PUT")
        self.assertEqual(
            client.calls[1]["payload"],
            {
                "id": "123",
                "status": "current",
                "title": "Bootstrap",
                "body": {
                    "representation": "storage",
                    "value": "<p>Atualizado</p>",
                },
                "version": {
                    "number": 8,
                    "message": "sync",
                },
                "spaceId": "254541826",
            },
        )


if __name__ == "__main__":
    unittest.main()
