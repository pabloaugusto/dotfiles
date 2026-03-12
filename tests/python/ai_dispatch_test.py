from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from scripts.ai_dispatch_lib import build_route_payload

ROOT = pathlib.Path(__file__).resolve().parents[2]


class AiDispatchTests(unittest.TestCase):
    def test_route_payload_includes_bootstrap_and_guardrails(self) -> None:
        payload = build_route_payload(
            intent="Recriar relink do bootstrap do Windows",
            paths=["app/bootstrap/bootstrap-windows.ps1"],
            risk="high",
        )
        self.assertIn("bootstrap-operator", payload["task_card"]["required_agents"])
        self.assertIn("critical-integrations-guardian", payload["task_card"]["required_agents"])
        self.assertIn("powershell-reviewer", payload["task_card"]["required_agents"])
        self.assertIn(
            "architecture-modernization-authority", payload["task_card"]["required_agents"]
        )
        self.assertIn("task test:unit:powershell", payload["delegation_plan"]["validation"])
        self.assertIn("task ci:lint", payload["delegation_plan"]["validation"])
        self.assertIn("task env:check", payload["delegation_plan"]["validation"])

    def test_route_payload_requires_python_reviewer(self) -> None:
        payload = build_route_payload(
            intent="Refatorar validador Python da camada de IA",
            paths=["scripts/validate-ai-assets.py"],
            risk="medium",
        )
        self.assertIn("python-reviewer", payload["task_card"]["required_agents"])
        self.assertIn(
            "repo-governance-authority",
            payload["delegation_plan"]["primary_agents"],
        )
        self.assertIn("task lint:python", payload["delegation_plan"]["validation"])
        self.assertIn("task type:check", payload["delegation_plan"]["validation"])
        self.assertIn("task test:unit:python", payload["delegation_plan"]["validation"])

    def test_route_payload_requires_automation_reviewer(self) -> None:
        payload = build_route_payload(
            intent="Ajustar workflow e Taskfile do CI",
            paths=[".github/workflows/ai-governance.yml", "Taskfile.yml"],
            risk="medium",
        )
        self.assertIn("automation-reviewer", payload["task_card"]["required_agents"])
        self.assertIn("task validate:actions", payload["delegation_plan"]["validation"])
        self.assertIn("task lint:yaml", payload["delegation_plan"]["validation"])
        self.assertIn("task ci:workflow:sync:check", payload["delegation_plan"]["validation"])

    def test_route_payload_uses_orchestrator_fallback(self) -> None:
        payload = build_route_payload(
            intent="Planejar e decompor backlog tecnico amplo",
            paths=["ROADMAP.md"],
            risk="medium",
        )
        self.assertIn("orchestrator", payload["delegation_plan"]["primary_agents"])

    def test_chat_intake_registers_worklog_and_route_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tracker = pathlib.Path(tmp) / "tracker.md"
            decisions = pathlib.Path(tmp) / "decisions.md"
            out = pathlib.Path(tmp) / "intake.json"
            route_out = pathlib.Path(tmp) / "route.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "ai-chat-intake.py"),
                    "--message",
                    "Ajustar governanca de IA e docs",
                    "--paths",
                    "AGENTS.md,docs/AI-DELEGATION-FLOW.md",
                    "--route",
                    "1",
                    "--pending-action",
                    "concluir_primeiro",
                    "--worklog-file",
                    str(tracker),
                    "--decisions-file",
                    str(decisions),
                    "--out",
                    str(out),
                    "--route-out",
                    str(route_out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=f"{completed.stdout}\n{completed.stderr}")
            payload = json.loads(out.read_text(encoding="utf-8"))
            routed = json.loads(route_out.read_text(encoding="utf-8"))
            self.assertTrue(payload["worklog_id"].startswith("WIP-"))
            self.assertTrue(payload["route_enabled"])
            self.assertIn(
                "destrava diretamente",
                payload["pending_action_guidance"]["concluir_primeiro"],
            )
            self.assertIn("repo-governance-authority", routed["task_card"]["required_agents"])


if __name__ == "__main__":
    unittest.main()
