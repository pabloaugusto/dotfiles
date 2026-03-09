from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from scripts.ai_agent_execution_lib import (
    AgentExecutionError,
    clear_context,
    default_context_path,
    load_context,
    record_activity,
)


class FakeJira:
    def __init__(self) -> None:
        self.client = self
        self.status = "Ready"
        self.summary = "Instrumentar execucao local por agente e issue"
        self.logged: list[dict[str, object]] = []
        self.transitions_taken: list[str] = []
        self.comments: list[dict[str, object]] = []
        self.updated_fields: list[dict[str, object]] = []

    def get_issue(self, issue_key: str, *, fields: list[str] | None = None) -> dict[str, object]:
        payload_fields: dict[str, object] = {}
        if fields and "summary" in fields:
            payload_fields["summary"] = self.summary
        if fields and "status" in fields:
            payload_fields["status"] = {"name": self.status}
        return {"key": issue_key, "fields": payload_fields}

    def get_transitions(self, issue_key: str) -> list[dict[str, object]]:
        transitions_map: dict[str, list[dict[str, object]]] = {
            "Ready": [{"id": "1", "to": {"name": "Doing"}}],
            "Doing": [
                {"id": "2", "to": {"name": "Testing"}},
                {"id": "3", "to": {"name": "Paused"}},
                {"id": "4", "to": {"name": "Done"}},
            ],
            "Testing": [{"id": "5", "to": {"name": "Review"}}],
            "Review": [{"id": "6", "to": {"name": "Done"}}],
            "Paused": [{"id": "7", "to": {"name": "Doing"}}],
            "Done": [],
        }
        if self.status in transitions_map:
            return transitions_map[self.status]
        return []

    def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, object]:
        self.transitions_taken.append(transition_id)
        status_map = {
            "1": "Doing",
            "2": "Testing",
            "3": "Paused",
            "4": "Done",
            "5": "Review",
            "6": "Done",
            "7": "Doing",
        }
        self.status = status_map[transition_id]
        return {}

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
        if path == "/rest/api/3/field/search":
            return {
                "isLast": True,
                "values": [
                    {"name": "Current Agent Role", "id": "customfield_10001"},
                    {"name": "Next Required Role", "id": "customfield_10002"},
                ],
            }
        if path.endswith("/comment") and method == "GET":
            return {"comments": self.comments}
        raise AssertionError(f"request_json inesperado: {method} {path}")

    def add_comment(self, issue_key: str, body_text: str) -> dict[str, object]:
        payload: dict[str, Any] = {
            "id": str(len(self.comments) + 1),
            "body": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": body_text}],
                    }
                ],
            },
        }
        self.comments.append(payload)
        self.logged.append({"issue_key": issue_key, "body_text": body_text})
        return payload

    def update_issue_fields(self, issue_key: str, fields: dict[str, object]) -> dict[str, object]:
        self.updated_fields.append({"issue_key": issue_key, "fields": fields})
        return {"ok": True}

    def site_url(self) -> str:
        return "https://example.atlassian.net"


class FakeJiraStatusDrift(FakeJira):
    def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, object]:
        self.transitions_taken.append(transition_id)
        return {}


class AgentExecutionTests(unittest.TestCase):
    def test_start_records_local_context_and_transitions_issue(self) -> None:
        fake_jira = FakeJira()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira), patch(
                "scripts.ai_agent_execution_lib.current_branch",
                return_value="feat/DOT-101-agent-issue-instrumentation",
            ):
                payload = record_activity(
                    repo_root=repo,
                    issue_key="DOT-101",
                    agent="ai-developer-automation",
                    interaction_type="progress-update",
                    status="doing",
                    contexto=["rodada iniciada"],
                    evidencias=["worktree dedicada"],
                    proximo_passo="continuar",
                    current_agent_role="ai-developer-automation",
                    next_required_role="ai-tech-lead",
                )

        self.assertEqual(fake_jira.status, "Doing")
        self.assertEqual(fake_jira.transitions_taken, ["1"])
        context = payload["context"]
        self.assertIsInstance(context, dict)
        self.assertEqual(context["issue_key"], "DOT-101")
        self.assertEqual(context["agent"], "ai-developer-automation")
        self.assertEqual(context["status"], "doing")

    def test_handoff_clears_local_context_after_logging(self) -> None:
        fake_jira = FakeJira()
        fake_jira.status = "Doing"
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira), patch(
                "scripts.ai_agent_execution_lib.current_branch",
                return_value="feat/DOT-101-agent-issue-instrumentation",
            ):
                record_activity(
                    repo_root=repo,
                    issue_key="DOT-101",
                    agent="ai-developer-automation",
                    interaction_type="progress-update",
                    status="doing",
                    current_agent_role="ai-developer-automation",
                    next_required_role="ai-tech-lead",
                )
                payload = record_activity(
                    repo_root=repo,
                    agent="ai-developer-automation",
                    interaction_type="handoff",
                    status="doing",
                    next_required_role="ai-tech-lead",
                    clear_after=True,
                )

                self.assertIsNone(payload["context"])
                self.assertIsNone(load_context(repo))

    def test_done_clears_context_and_transitions_to_done(self) -> None:
        fake_jira = FakeJira()
        fake_jira.status = "Review"
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira), patch(
                "scripts.ai_agent_execution_lib.current_branch",
                return_value="feat/DOT-101-agent-issue-instrumentation",
            ):
                context_path = default_context_path(repo)
                context_path.parent.mkdir(parents=True, exist_ok=True)
                context_path.write_text(
                    json.dumps(
                        {
                            "issue_key": "DOT-101",
                            "issue_summary": fake_jira.summary,
                            "issue_url": "https://example.atlassian.net/browse/DOT-101",
                            "agent": "ai-reviewer-automation",
                            "status": "review",
                            "current_agent_role": "ai-reviewer-automation",
                            "next_required_role": "ai-engineering-manager",
                            "branch": "feat/DOT-101-agent-issue-instrumentation",
                            "worktree_root": str(repo),
                            "started_at": "2026-03-09T00:00:00-03:00",
                            "updated_at": "2026-03-09T00:10:00-03:00",
                        }
                    ),
                    encoding="utf-8",
                )

                payload = record_activity(
                    repo_root=repo,
                    agent="ai-engineering-manager",
                    interaction_type="closure",
                    status="done",
                    clear_after=True,
                )

        self.assertEqual(fake_jira.status, "Done")
        self.assertEqual(fake_jira.transitions_taken, ["6"])
        self.assertIsNone(payload["context"])

    def test_requires_issue_and_agent_when_no_context_exists(self) -> None:
        fake_jira = FakeJira()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira):
                with self.assertRaises(AgentExecutionError):
                    record_activity(
                        repo_root=repo,
                        interaction_type="progress-update",
                        status="doing",
                    )

    def test_fails_when_jira_status_remains_divergent_after_transition(self) -> None:
        fake_jira = FakeJiraStatusDrift()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira), patch(
                "scripts.ai_agent_execution_lib.current_branch",
                return_value="feat/DOT-101-agent-issue-instrumentation",
            ):
                with self.assertRaises(AgentExecutionError):
                    record_activity(
                        repo_root=repo,
                        issue_key="DOT-101",
                        agent="ai-developer-automation",
                        interaction_type="progress-update",
                        status="doing",
                    )

    def test_clear_context_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            clear_context(repo)
            self.assertIsNone(load_context(repo))


if __name__ == "__main__":
    unittest.main()
