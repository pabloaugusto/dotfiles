"""Executar CSpell com a pilha de dicionarios canonica do repositorio."""

from __future__ import annotations

import subprocess
import sys

from scripts.cspell_governance_lib import build_cspell_command


def main() -> int:
    args = sys.argv[1:] or ["lint", ".", "--config", ".cspell.json", "--gitignore", "--dot"]
    return subprocess.run(build_cspell_command(args), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
