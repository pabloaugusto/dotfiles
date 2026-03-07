from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class AiEvalSmokeTests(unittest.TestCase):
    def test_smoke_eval_passes_on_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "ai-eval-smoke.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=f"{completed.stdout}\n{completed.stderr}")
        self.assertIn("[OK] Smoke eval de IA passou.", completed.stdout)


if __name__ == "__main__":
    unittest.main()
