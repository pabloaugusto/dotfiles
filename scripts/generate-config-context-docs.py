#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.config_context_docs_lib import update_generated_sections


def main(argv: list[str]) -> int:
    repo_root = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parents[1]
    touched = update_generated_sections(repo_root)
    if touched:
        for path in touched:
            print(path.relative_to(repo_root).as_posix())
    else:
        print("no-op")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
