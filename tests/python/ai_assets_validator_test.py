from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate-ai-assets.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_ai_assets", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("Nao foi possivel carregar validate-ai-assets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateAiAssetsTests(unittest.TestCase):
    def test_validator_exports_new_governance_contracts(self) -> None:
        module = load_validator_module()
        self.assertIn("LICOES-APRENDIDAS.md", module.REQUIRED_FILES)
        self.assertIn(".agents/README.md", module.REQUIRED_FILES)
        self.assertIn(".agents/config.toml", module.REQUIRED_FILES)
        self.assertIn(".codex/README.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-AGENTS-CATALOG.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-ORTHOGRAPHY-LEDGER.md", module.REQUIRED_FILES)
        self.assertIn("docs/AI-SOURCE-AUDIT.md", module.REQUIRED_FILES)
        self.assertIn("docs/TASKS.md", module.REQUIRED_FILES)
        self.assertIn("docs/WORKFLOWS.md", module.REQUIRED_FILES)
        self.assertIn("config/ai/platforms.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/platforms.local.yaml.tpl", module.REQUIRED_FILES)
        self.assertIn("config/ai/agents.yaml", module.REQUIRED_FILES)
        self.assertIn("config/ai/contracts.yaml", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-route.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai-control-plane.py", module.REQUIRED_FILES)
        self.assertIn("scripts/ai_control_plane_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/atlassian_platform_lib.py", module.REQUIRED_FILES)
        self.assertIn("scripts/cspell-governance.py", module.REQUIRED_FILES)
        self.assertIn("scripts/validate_workflow_task_sync.py", module.REQUIRED_FILES)
        self.assertIn("## Validacao recomendada", module.REQUIRED_AGENT_HEADINGS)
        self.assertIn("## Regras", module.REQUIRED_SKILL_HEADINGS)
        self.assertIn("## Entregas esperadas", module.REQUIRED_SKILL_HEADINGS)
        self.assertIn("Nunca operar por amostragem", module.AGENTS_REQUIRED_SNIPPETS)
        self.assertIn(
            "Nenhum `done` e valido sem revisar `LICOES-APRENDIDAS.md`",
            module.AGENTS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### Camada 2.2. Orquestracao, rules e evals",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "### Fronteira entre `.agents/` e adaptadores de assistente",
            module.OPERATING_MODEL_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "## LA-007 - Integracoes criticas exigem guardiao proprio",
            module.LESSONS_REQUIRED_SNIPPETS,
        )
        self.assertIn(
            "$task-routing-and-decomposition",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-SKILLS-CATALOG.md"],
        )
        self.assertIn(
            "$dotfiles-orthography-review",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-SKILLS-CATALOG.md"],
        )
        self.assertIn(
            "pascoalete",
            module.CATALOG_REQUIRED_SNIPPETS["docs/AI-AGENTS-CATALOG.md"],
        )
        self.assertIn(
            "### `ai:atlassian:check`",
            module.CATALOG_REQUIRED_SNIPPETS["docs/TASKS.md"],
        )

    def test_validator_passes_on_current_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("AI assets OK.", completed.stdout)


if __name__ == "__main__":
    unittest.main()
