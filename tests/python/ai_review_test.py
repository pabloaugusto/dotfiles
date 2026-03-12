from __future__ import annotations

import pathlib
import tempfile
import unittest

from scripts.ai_review_lib import check_review_gate, record_review, required_specialist_reviewers

ROOT = pathlib.Path(__file__).resolve().parents[2]


def write_ai_runtime(repo_root: pathlib.Path) -> None:
    config_dir = repo_root / "config" / "ai"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "agents.yaml").write_text(
        """version: 1
roles:
  python-reviewer:
    enabled: true
    required: false
    category: quality
    display_name: Revisor Python
""",
        encoding="utf-8",
    )
    (config_dir / "agent-enablement.yaml").write_text(
        """version: 1
defaults:
  registry_agents_enabled_by_default: true
roles:
  python-reviewer:
    enabled: true
registry_agents: {}
""",
        encoding="utf-8",
    )
    (config_dir / "agent-operations.yaml").write_text(
        "version: 1\nroles:\n  python-reviewer: {}\n",
        encoding="utf-8",
    )
    (config_dir / "contracts.yaml").write_text(
        "version: 1\nworkflow:\n  always_enabled_columns: [Backlog, Doing, Review, Done]\n",
        encoding="utf-8",
    )
    (config_dir / "platforms.yaml").write_text(
        "version: 1\nplatforms:\n  atlassian:\n    enabled: false\n",
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
  python-reviewer:
    status: consultive
    chat_alias: Revisor Python
    chat_owner_supported: true
    owner_mode: consultive
    surfaces: [jira, chat, review]
    process_scopes: [review]
    runtime_artifacts:
      - config/ai/agent-runtime.yaml
registry_agents: {}
""",
        encoding="utf-8",
    )


class AiReviewTests(unittest.TestCase):
    def test_required_specialist_reviewers_detects_python_scope(self) -> None:
        reviewers = required_specialist_reviewers(
            repo_root=ROOT,
            intent="Refatorar validador Python da camada de IA",
            risk="medium",
            paths=["scripts/validate-ai-assets.py"],
        )
        self.assertIn("python-reviewer", reviewers)

    def test_check_review_gate_fails_without_required_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            review_file = pathlib.Path(tmp) / "reviews.md"
            result = check_review_gate(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                repo_root=ROOT,
                intent="Refatorar validador Python da camada de IA",
                risk="medium",
                paths=["scripts/validate-ai-assets.py"],
            )
            self.assertFalse(result["ok"])
            self.assertIn("python-reviewer", " ".join(result["errors"]))

    def test_check_review_gate_passes_with_approved_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            review_file = pathlib.Path(tmp) / "reviews.md"
            record_review(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                reviewer="python-reviewer",
                status="aprovado",
                summary="Parecer favoravel apos revisar corretude e testes.",
                paths=["scripts/validate-ai-assets.py"],
                evidence="task test:unit:python:windows",
            )
            result = check_review_gate(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                repo_root=ROOT,
                intent="Refatorar validador Python da camada de IA",
                risk="medium",
                paths=["scripts/validate-ai-assets.py"],
            )
            self.assertTrue(result["ok"])

    def test_check_review_gate_blocks_rejected_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            review_file = pathlib.Path(tmp) / "reviews.md"
            record_review(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                reviewer="python-reviewer",
                status="reprovado",
                summary="Encontrado risco funcional em path canonico.",
                paths=["scripts/validate-ai-assets.py"],
                evidence="task lint:python",
            )
            result = check_review_gate(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                repo_root=ROOT,
                intent="Refatorar validador Python da camada de IA",
                risk="medium",
                paths=["scripts/validate-ai-assets.py"],
            )
            self.assertFalse(result["ok"])
            self.assertIn("reprovado", " ".join(result["errors"]))

    def test_check_review_gate_blocks_when_approval_does_not_cover_new_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            review_file = pathlib.Path(tmp) / "reviews.md"
            record_review(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                reviewer="python-reviewer",
                status="aprovado",
                summary="Parecer favoravel inicial.",
                paths=["scripts/validate-ai-assets.py"],
                evidence="task test:unit:python:windows",
            )
            result = check_review_gate(
                review_path=review_file,
                worklog_id="WIP-TEST-REVIEW",
                repo_root=ROOT,
                intent="Refatorar validadores Python da camada de IA",
                risk="medium",
                paths=[
                    "scripts/validate-ai-assets.py",
                    "scripts/ai_review_lib.py",
                ],
            )
            self.assertFalse(result["ok"])
            self.assertIn("scripts/ai_review_lib.py", " ".join(result["errors"]))

    def test_record_review_writes_visible_alias_and_gate_still_matches_role_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            write_ai_runtime(repo)
            review_file = repo / "docs" / "AI-REVIEW-LEDGER.md"
            record_review(
                review_path=review_file,
                worklog_id="WIP-TEST-ALIAS-REVIEW",
                reviewer="python-reviewer",
                status="aprovado",
                summary="Parecer favoravel com alias-first.",
                paths=["scripts/validate-ai-assets.py"],
                evidence="task test:unit:python",
            )

            rendered = review_file.read_text(encoding="utf-8")
            result = check_review_gate(
                review_path=review_file,
                worklog_id="WIP-TEST-ALIAS-REVIEW",
                repo_root=ROOT,
                intent="Refatorar validador Python da camada de IA",
                risk="medium",
                paths=["scripts/validate-ai-assets.py"],
            )

            self.assertIn("Revisor Python", rendered)
            self.assertNotIn("| python-reviewer |", rendered)
            self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
