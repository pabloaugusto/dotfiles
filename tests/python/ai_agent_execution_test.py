from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from scripts.ai_agent_execution_lib import (
    AgentExecutionError,
    clear_context,
    default_context_path,
    load_context,
    record_activity,
)


def write_runtime(repo_root: Path) -> None:
    config_dir = repo_root / "config" / "ai"
    root_config_dir = repo_root / "config"
    app_config_dir = repo_root / "app" / "config"
    agents_config_dir = repo_root / ".agents" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    app_config_dir.mkdir(parents=True, exist_ok=True)
    agents_config_dir.mkdir(parents=True, exist_ok=True)
    (root_config_dir / "config.toml").write_text(
        """version = 1

[project]
id = "dotfiles"
source_of_truth = "config/config.toml"
default_config_ref_convention = "arquivo::chave"

[contexts]
dev_root = "config"
dev_manifest = "config/config.toml"
runtime_root = "app/config"
runtime_manifest = "app/config/config.toml"
ai_root = ".agents/config"
ai_manifest = ".agents/config/config.toml"

[regionalization]
timezone_name = "America/Sao_Paulo"
locale = "pt-BR"
language = "pt-BR"
currency = "BRL"
calendar_system = "gregorian"

[domains]
dev = "config/dev.toml"
integrations = "config/integrations.toml"
quality = "config/quality.toml"
time_surfaces = "config/time-surfaces.yaml"
schema = "config/schema.json"
""",
        encoding="utf-8",
    )
    (root_config_dir / "dev.toml").write_text("version = 1\n", encoding="utf-8")
    (root_config_dir / "integrations.toml").write_text("version = 1\n", encoding="utf-8")
    (root_config_dir / "quality.toml").write_text("version = 1\n", encoding="utf-8")
    (root_config_dir / "schema.json").write_text("{}", encoding="utf-8")
    (root_config_dir / "time-surfaces.yaml").write_text("surfaces: {}\n", encoding="utf-8")
    (app_config_dir / "config.toml").write_text(
        """version = 1

[context]
kind = "runtime"
source_of_truth = "app/config/config.toml"
inherits_regionalization = "config/config.toml::regionalization"

[domains]
runtime = "app/config/runtime.toml"
bootstrap = "app/config/bootstrap.toml"
links = "app/config/links.toml"
schema = "app/config/schema.json"
""",
        encoding="utf-8",
    )
    (app_config_dir / "runtime.toml").write_text("version = 1\n", encoding="utf-8")
    (app_config_dir / "bootstrap.toml").write_text("version = 1\n", encoding="utf-8")
    (app_config_dir / "links.toml").write_text("version = 1\n", encoding="utf-8")
    (app_config_dir / "schema.json").write_text("{}", encoding="utf-8")
    (agents_config_dir / "config.toml").write_text(
        """version = 1

[context]
kind = "ai"
source_of_truth = ".agents/config/config.toml"
inherits_regionalization = "config/config.toml::regionalization"

[domains]
agents = ".agents/config/agents.toml"
communication = ".agents/config/communication.toml"
startup = ".agents/config/startup.toml"
orchestration = ".agents/config/orchestration.toml"
reviews = ".agents/config/reviews.toml"
prompts = ".agents/config/prompts.toml"
schema = ".agents/config/schema.json"

[compatibility]
bridge_manifest = ".agents/config.toml"
legacy_control_plane_root = "config/ai"
legacy_agents = "config/ai/agents.yaml"
legacy_agent_enablement = "config/ai/agent-enablement.yaml"
legacy_agent_runtime = "config/ai/agent-runtime.yaml"
legacy_agent_operations = "config/ai/agent-operations.yaml"
legacy_contracts = "config/ai/contracts.yaml"
""",
        encoding="utf-8",
    )
    (agents_config_dir / "agents.toml").write_text(
        """version = 1

[source_of_truth]
display_name_registry = ".agents/registry/*.toml::display_name"

[identity]
display_name_source = ".agents/registry/*.toml::display_name"
chat_alias_source = "config/ai/agent-runtime.yaml::roles"
enablement_source = "config/ai/agent-enablement.yaml::roles"
""",
        encoding="utf-8",
    )
    (agents_config_dir / "communication.toml").write_text(
        """version = 1

[chat]
prefix_template = "[{timestamp}] **{visible_name}**"
timestamp_display_pattern = "dd-mm hh:mm"
timestamp_surface = "chat"
timestamp_source = "local_system_clock"
body_starts_on_next_line = true
visible_name_fallback_order = ["chat_alias", "display_name", "technical_id"]
display_name_source = ".agents/config/agents.toml::source_of_truth.display_name_registry"

[jira.fields]
current_agent_role = "Current Agent Role"
next_required_role = "Next Required Role"

[literal_lint]
managed_literals = ["[{timestamp}] **{visible_name}**", "dd-mm hh:mm"]
""",
        encoding="utf-8",
    )
    (agents_config_dir / "startup.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "orchestration.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "reviews.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "prompts.toml").write_text("version = 1\n", encoding="utf-8")
    (agents_config_dir / "schema.json").write_text("{}", encoding="utf-8")
    (repo_root / ".agents" / "config.toml").write_text(
        """version = 1

[config_context]
manifest = ".agents/config/config.toml"
bridge_mode = "legacy-rules-and-identity-contracts"
""",
        encoding="utf-8",
    )
    (config_dir / "agents.yaml").write_text(
        """version: 1
roles:
  ai-developer-automation:
    enabled: true
    required: false
    category: delivery
    display_name: Automation Dev
  ai-tech-lead:
    enabled: true
    required: false
    category: governance
    display_name: Tech Lead
  ai-qa:
    enabled: true
    required: false
    category: quality
    display_name: Testador (QA)
  ai-reviewer-automation:
    enabled: true
    required: false
    category: quality
    display_name: Revisor Automacao
  ai-engineering-manager:
    enabled: true
    required: false
    category: governance
    display_name: Engenheiro
""",
        encoding="utf-8",
    )
    (config_dir / "agent-enablement.yaml").write_text(
        """version: 1
defaults:
  registry_agents_enabled_by_default: true
roles:
  ai-developer-automation:
    enabled: true
  ai-tech-lead:
    enabled: true
  ai-qa:
    enabled: true
  ai-reviewer-automation:
    enabled: true
  ai-engineering-manager:
    enabled: true
registry_agents: {}
""",
        encoding="utf-8",
    )
    (config_dir / "agent-operations.yaml").write_text(
        """version: 1
roles:
  ai-developer-automation: {}
  ai-tech-lead: {}
  ai-qa: {}
  ai-reviewer-automation: {}
  ai-engineering-manager: {}
""",
        encoding="utf-8",
    )
    (config_dir / "contracts.yaml").write_text(
        """version: 1
workflow:
  always_enabled_columns:
    - Backlog
    - Doing
    - Review
    - Done
""",
        encoding="utf-8",
    )
    (config_dir / "platforms.yaml").write_text(
        """version: 1
platforms:
  atlassian:
    enabled: false
""",
        encoding="utf-8",
    )
    (config_dir / "agent-runtime.yaml").write_text(
        """version: 1
policies:
  enabled_role_statuses: [operational, consultive]
  required_role_statuses: [operational, consultive]
  enabled_registry_statuses: [operational, consultive]
  chat_owner_statuses: [operational, consultive]
  chat_name_fallback_order: [chat_alias, display_name, technical_id]
roles:
  ai-developer-automation:
    status: operational
    chat_alias: Automation Dev
    chat_owner_supported: true
    owner_mode: primary
    surfaces: [jira, chat]
    process_scopes: [automation]
    jira_assignee:
      account_id: account-automation
    runtime_artifacts:
      - config/ai/agent-runtime.yaml
  ai-tech-lead:
    status: operational
    chat_alias: Tech Lead
    chat_owner_supported: true
    owner_mode: primary
    surfaces: [jira, chat]
    process_scopes: [handoff]
    runtime_artifacts:
      - config/ai/agent-runtime.yaml
  ai-qa:
    status: operational
    chat_alias: Testador (QA)
    chat_owner_supported: true
    owner_mode: primary
    surfaces: [jira, chat]
    process_scopes: [tests]
    runtime_artifacts:
      - config/ai/agent-runtime.yaml
  ai-reviewer-automation:
    status: consultive
    chat_alias: Revisor Automacao
    chat_owner_supported: true
    owner_mode: consultive
    surfaces: [jira, chat]
    process_scopes: [review]
    runtime_artifacts:
      - config/ai/agent-runtime.yaml
  ai-engineering-manager:
    status: operational
    chat_alias: Engenheiro
    chat_owner_supported: true
    owner_mode: primary
    surfaces: [jira, chat]
    process_scopes: [capacity]
    runtime_artifacts:
      - config/ai/agent-runtime.yaml
registry_agents: {}
""",
        encoding="utf-8",
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


def fake_with_jira_actor(fake_jira: FakeJira):
    role_account_ids = {
        "ai-developer-automation": "account-automation",
        "ai-engineering-manager": "account-eng",
        "ai-qa": "account-qa",
        "ai-reviewer-automation": "account-reviewer",
    }

    def _runner(
        repo_root: Path,
        role_id: str,
        surface: str,
        operation,
        *,
        context_issue_key: str = "",
    ):
        del repo_root, context_issue_key
        account_id = role_account_ids.get(role_id, "")
        if surface != "jira-assignee":
            account_id = role_account_ids.get(role_id, "")
        actor = SimpleNamespace(
            role_id=role_id,
            surface=surface,
            account_id=account_id,
            actor_mode="role-service-account",
            account_id_source="secret",
        )
        return operation(fake_jira, actor), actor

    return _runner


class AgentExecutionTests(unittest.TestCase):
    def test_start_records_local_context_and_transitions_issue(self) -> None:
        fake_jira = FakeJira()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
                patch(
                    "scripts.ai_agent_execution_lib.current_branch",
                    return_value="feat/DOT-101-agent-issue-instrumentation",
                ),
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
        self.assertEqual(context["agent"], "Automation Dev")
        self.assertEqual(context["agent_id"], "ai-developer-automation")
        self.assertEqual(context["status"], "doing")
        self.assertEqual(context["current_agent_role"], "Automation Dev")
        self.assertEqual(context["current_agent_role_id"], "ai-developer-automation")
        self.assertEqual(context["next_required_role"], "Tech Lead")
        self.assertEqual(context["next_required_role_id"], "ai-tech-lead")
        self.assertEqual(payload["jira"]["current_agent_role_display"], "Automation Dev")
        self.assertEqual(payload["jira"]["next_required_role_display"], "Tech Lead")
        self.assertEqual(payload["jira"]["role_sync"]["assignee_status"], "synced")
        self.assertEqual(payload["jira"]["comment_actor_mode"], "role-service-account")
        self.assertEqual(payload["jira"]["role_actor_mode"], "role-service-account")
        last_comment = cast(dict[str, object], fake_jira.logged[-1])
        self.assertIn("Agent: Automation Dev", cast(str, last_comment["body_text"]))
        self.assertNotIn(
            "Agent: ai-developer-automation",
            cast(str, last_comment["body_text"]),
        )
        last_update = cast(dict[str, object], fake_jira.updated_fields[-1])
        last_update_fields = cast(dict[str, object], last_update["fields"])
        self.assertEqual(
            last_update_fields["assignee"],
            {"accountId": "account-automation"},
        )

    def test_start_uses_configured_jira_field_names(self) -> None:
        fake_jira = FakeJira()
        fake_control_plane = SimpleNamespace(
            jira_field_names=lambda: {
                "current_agent_role": "Agente Atual",
                "next_required_role": "Proximo Papel",
            },
            visible_name_for_agent=lambda role_id: {
                "ai-developer-automation": "Automation Dev",
                "ai-tech-lead": "Tech Lead",
            }.get(role_id, role_id),
            formal_name_for_agent=lambda role_id: {
                "ai-developer-automation": "Automation Dev",
                "ai-tech-lead": "Tech Lead",
            }.get(role_id, role_id),
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
                patch(
                    "scripts.ai_agent_execution_lib.current_branch",
                    return_value="feat/DOT-101-agent-issue-instrumentation",
                ),
                patch(
                    "scripts.ai_agent_execution_lib.field_catalog_by_name",
                    return_value={
                        "Agente Atual": "customfield_20001",
                        "Proximo Papel": "customfield_20002",
                    },
                ),
                patch(
                    "scripts.ai_agent_execution_lib.load_ai_control_plane",
                    return_value=fake_control_plane,
                ),
            ):
                record_activity(
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

        last_update = cast(dict[str, object], fake_jira.updated_fields[-1])
        fields = cast(dict[str, object], last_update["fields"])
        self.assertEqual(fields["customfield_20001"], {"value": "Automation Dev"})
        self.assertEqual(fields["customfield_20002"], {"value": "Tech Lead"})

    def test_handoff_clears_local_context_after_logging(self) -> None:
        fake_jira = FakeJira()
        fake_jira.status = "Doing"
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
                patch(
                    "scripts.ai_agent_execution_lib.current_branch",
                    return_value="feat/DOT-101-agent-issue-instrumentation",
                ),
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
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
                patch(
                    "scripts.ai_agent_execution_lib.current_branch",
                    return_value="feat/DOT-101-agent-issue-instrumentation",
                ),
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
        last_comment = cast(dict[str, object], fake_jira.logged[-1])
        self.assertIn("Agent: Engenheiro", cast(str, last_comment["body_text"]))
        self.assertNotIn(
            "Agent: ai-engineering-manager",
            cast(str, last_comment["body_text"]),
        )
        self.assertIsNone(payload["context"])

    def test_load_context_migrates_legacy_schema_to_alias_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_runtime(repo)
            context_path = default_context_path(repo)
            context_path.parent.mkdir(parents=True, exist_ok=True)
            context_path.write_text(
                json.dumps(
                    {
                        "issue_key": "DOT-101",
                        "issue_summary": "Instrumentar execucao local por agente e issue",
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

            context = load_context(repo)

        self.assertIsNotNone(context)
        context = cast(Any, context)
        self.assertEqual(context.agent, "Revisor Automacao")
        self.assertEqual(context.agent_id, "ai-reviewer-automation")
        self.assertEqual(context.current_agent_role, "Revisor Automacao")
        self.assertEqual(context.current_agent_role_id, "ai-reviewer-automation")
        self.assertEqual(context.next_required_role, "Engenheiro")
        self.assertEqual(context.next_required_role_id, "ai-engineering-manager")

    def test_paused_issue_resumes_to_doing_before_advancing(self) -> None:
        fake_jira = FakeJira()
        fake_jira.status = "Paused"
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
                patch(
                    "scripts.ai_agent_execution_lib.current_branch",
                    return_value="feat/DOT-101-agent-issue-instrumentation",
                ),
            ):
                payload = record_activity(
                    repo_root=repo,
                    issue_key="DOT-101",
                    agent="ai-qa",
                    interaction_type="progress-update",
                    status="testing",
                    current_agent_role="ai-qa",
                    next_required_role="ai-reviewer-automation",
                )

        self.assertEqual(fake_jira.status, "Testing")
        self.assertEqual(fake_jira.transitions_taken, ["7", "2"])
        self.assertEqual(payload["jira"]["status"], "testing")

    def test_requires_issue_and_agent_when_no_context_exists(self) -> None:
        fake_jira = FakeJira()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
            ):
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
            write_runtime(repo)
            with (
                patch("scripts.ai_agent_execution_lib.resolve_jira", return_value=fake_jira),
                patch(
                    "scripts.ai_agent_execution_lib.with_jira_actor",
                    side_effect=fake_with_jira_actor(fake_jira),
                ),
                patch(
                    "scripts.ai_agent_execution_lib.current_branch",
                    return_value="feat/DOT-101-agent-issue-instrumentation",
                ),
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

    def test_load_context_rejects_corrupted_json_with_domain_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            context_path = default_context_path(repo)
            context_path.parent.mkdir(parents=True, exist_ok=True)
            context_path.write_text("{", encoding="utf-8")

            with self.assertRaises(AgentExecutionError):
                load_context(repo)


if __name__ == "__main__":
    unittest.main()
