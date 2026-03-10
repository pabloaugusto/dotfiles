from __future__ import annotations

import pathlib
import tempfile
import textwrap
import unittest

from scripts.ai_jira_model_lib import load_jira_model, model_summary_payload
from scripts.ai_control_plane_lib import load_yaml_map


def write_jira_model(repo_root: pathlib.Path) -> None:
    config_dir = repo_root / "config" / "ai"
    config_dir.mkdir(parents=True)
    (config_dir / "jira-model.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            project:
              key: DOT
              name: dotfiles
              style: company-managed-software
              target_board:
                name: DOT - Autonomous Engineering
                type: kanban
                board_api_scopes:
                  - read:board-scope:jira-software
                columns:
                  - name: Backlog
                    statuses: [Backlog]
                  - name: Ready
                    statuses: [Ready]
                optional_columns:
                  - name: SEO Review
                    enabled_when_role: ai-seo-specialist
                    statuses: [SEO Review]
            issue_types:
              standard:
                - Epic
                - Task
            workflow:
              statuses:
                - name: Backlog
                  category: To Do
                - name: Ready
                  category: To Do
            fields:
              custom_fields:
                - name: Work Kind
                  type: single_select
                - name: Current Agent Role
                  type: single_select
            components:
              - ai-control-plane
              - documentation-governance
            labels:
              baseline:
                - atlassian-ia
                - docs
            dashboards:
              - name: DOT - Autonomous Engineering Overview
            """
        ),
        encoding="utf-8",
    )


class AiJiraModelTests(unittest.TestCase):
    def test_load_jira_model_reads_repo_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_jira_model(repo_root)
            model_path, model = load_jira_model(repo_root)
        self.assertTrue(str(model_path).endswith("config\\ai\\jira-model.yaml"))
        self.assertEqual(model["project"]["key"], "DOT")

    def test_model_summary_payload_extracts_core_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_jira_model(repo_root)
            payload = model_summary_payload(repo_root)
        self.assertEqual(payload["project"]["key"], "DOT")
        self.assertEqual(payload["board"]["columns"], ["Backlog", "Ready"])
        self.assertEqual(payload["custom_fields"], ["Work Kind", "Current Agent Role"])
        self.assertEqual(payload["components"], ["ai-control-plane", "documentation-governance"])

    def test_repo_model_keeps_product_owner_priority_and_timeline_rules(self) -> None:
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        _, jira_model = load_jira_model(repo_root)
        execution_rules = ((jira_model.get("workflow") or {}).get("execution_rules")) or []
        self.assertIn("ordered-lists-must-remain-prioritized", execution_rules)
        self.assertIn("new-demand-must-enter-the-right-priority-position", execution_rules)
        self.assertIn("product-owner-must-maintain-start-and-due-dates-for-non-subtasks", execution_rules)

        agent_operations = load_yaml_map(repo_root / "config" / "ai" / "agent-operations.yaml")
        product_owner = ((agent_operations.get("roles") or {}).get("ai-product-owner")) or {}
        jira_payload = product_owner.get("jira") or {}
        primary_actions = jira_payload.get("primary_issue_actions") or []
        operating_steps = product_owner.get("operating_steps") or []

        self.assertIn("manter backlog, refinement e ready ordenados por prioridade real", primary_actions)
        self.assertIn(
            "manter timeline, start date e due date atualizados para itens acima de subtarefa",
            primary_actions,
        )
        self.assertIn(
            "posicionar o item novo no ponto correto da prioridade do backlog e das filas ordenadas do board",
            operating_steps,
        )
        self.assertIn(
            "revisar se Start date e Due date precisam ser estimados ou recalculados",
            operating_steps,
        )


if __name__ == "__main__":
    unittest.main()
