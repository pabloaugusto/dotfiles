"""Executar o `gitleaks` pinado para a plataforma corrente."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.release_tool import ROOT, ensure_tool_binary


def main() -> int:
    binary = ensure_tool_binary("gitleaks")
    result = subprocess.run([str(binary), *sys.argv[1:]], cwd=ROOT, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
