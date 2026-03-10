from __future__ import annotations

import pathlib
import tempfile
import textwrap
import unittest

from scripts.ai_jira_model_lib import load_jira_model, model_summary_payload


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


if __name__ == "__main__":
    unittest.main()
