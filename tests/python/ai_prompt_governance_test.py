from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ai-prompt-governance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ai_prompt_governance", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("Nao foi possivel carregar ai-prompt-governance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeJira:
    def __init__(self, issues: dict[str, dict[str, object]]) -> None:
        self.issues = issues
        self.updated: list[tuple[str, dict[str, object]]] = []

    def get_issue(self, issue_key: str, *, fields: list[str] | None = None) -> dict[str, object]:
        payload = self.issues[issue_key]
        selected = dict(payload)
        if fields is not None:
            selected = {name: payload.get(name) for name in fields}
        return {"key": issue_key, "fields": selected}

    def update_issue_fields(self, issue_key: str, fields: dict[str, object]) -> dict[str, object]:
        issue_fields = self.issues[issue_key]
        issue_fields.update(fields)
        self.updated.append((issue_key, dict(fields)))
        return {}


class PromptGovernanceTests(unittest.TestCase):
    def test_load_prompt_issue_contracts_reads_owner_issue_rules(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = pathlib.Path(temp_dir)
            meta_root = repo_root / ".agents" / "prompts" / "formal" / "sample-pack"
            meta_root.mkdir(parents=True)
            (meta_root / "meta.yaml").write_text(
                "\n".join(
                    [
                        "id: sample-pack",
                        "task_id: prompt/sample-pack",
                        "owner_issue: DOT-999",
                        "jira:",
                        '  summary_prefix: "PROMPT:"',
                        "  required_labels:",
                        "    - prompt",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            contracts = module.load_prompt_issue_contracts(repo_root)

        self.assertEqual(len(contracts), 1)
        self.assertEqual(contracts[0].pack_id, "sample-pack")
        self.assertEqual(contracts[0].task_id, "prompt/sample-pack")
        self.assertEqual(contracts[0].owner_issue, "DOT-999")
        self.assertEqual(contracts[0].summary_prefix, "PROMPT:")
        self.assertEqual(contracts[0].required_labels, ("prompt",))

    def test_sync_contracts_prefixes_summary_and_adds_prompt_label(self) -> None:
        module = load_module()
        fake_jira = FakeJira(
            {
                "DOT-179": {
                    "summary": "Formalizar arquitetura agnostica",
                    "labels": ["governance"],
                }
            }
        )
        contract = module.PromptIssueContract(
            pack_id="agnostic-sync-outbox-foundation",
            task_id="prompt/agnostic-sync-outbox-foundation",
            owner_issue="DOT-179",
            summary_prefix="PROMPT:",
            required_labels=("prompt",),
        )
        with (
            mock.patch.object(module, "resolve_jira", return_value=fake_jira),
            mock.patch.object(module, "load_prompt_issue_contracts", return_value=[contract]),
        ):
            payload = module.sync_contracts(ROOT)

        self.assertTrue(payload["ok"])
        self.assertEqual(
            fake_jira.updated,
            [
                (
                    "DOT-179",
                    {
                        "summary": "PROMPT: Formalizar arquitetura agnostica",
                        "labels": ["governance", "prompt"],
                    },
                )
            ],
        )

    def test_check_contracts_fails_when_prompt_contract_is_missing(self) -> None:
        module = load_module()
        fake_jira = FakeJira(
            {
                "DOT-178": {
                    "summary": "Formalizar PEA",
                    "labels": [],
                }
            }
        )
        contract = module.PromptIssueContract(
            pack_id="pea-startup-governance",
            task_id="prompt/pea-startup-governance",
            owner_issue="DOT-178",
            summary_prefix="PROMPT:",
            required_labels=("prompt",),
        )
        with (
            mock.patch.object(module, "resolve_jira", return_value=fake_jira),
            mock.patch.object(module, "load_prompt_issue_contracts", return_value=[contract]),
        ):
            payload = module.check_contracts(ROOT)

        self.assertFalse(payload["ok"])
        self.assertEqual(len(payload["contracts"]), 1)
        self.assertTrue(payload["contracts"][0]["needs_summary_update"])
        self.assertEqual(payload["contracts"][0]["missing_labels"], ["prompt"])


if __name__ == "__main__":
    unittest.main()
