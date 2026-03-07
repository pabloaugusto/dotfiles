"""Executar CSpell com dicionarios tecnicos padronizados do repo."""

from __future__ import annotations

import subprocess
import sys

PACKAGES = [
    "cspell@8.19.4",
    "@cspell/dict-pt-br",
    "@cspell/dict-python",
    "@cspell/dict-bash",
    "@cspell/dict-shell",
    "@cspell/dict-software-terms",
    "@cspell/dict-fullstack",
    "@cspell/dict-k8s",
    "@cspell/dict-docker",
    "@cspell/dict-companies",
    "@cspell/dict-fonts",
    "@cspell/dict-sql",
    "@cspell/dict-powershell",
    "@cspell/dict-git",
    "@cspell/dict-filetypes",
    "@cspell/dict-google",
]


def main() -> int:
    args = sys.argv[1:] or ["lint", ".", "--config", ".cspell.json", "--gitignore", "--dot"]
    command = ["uvx", "--from", "nodejs-wheel", "npm", "exec", "--yes"]
    for package in PACKAGES:
        command.extend(["--package", package])
    command.extend(["--", "cspell", *args])
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
