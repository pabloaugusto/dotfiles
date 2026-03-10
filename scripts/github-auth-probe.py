from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.github_auth_probe_lib import GitHubAuthProbeError, probe_github_auth


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnostica a autenticacao efetiva do GitHub CLI para este repo."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Raiz do repositorio onde o probe deve executar.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        payload = probe_github_auth(repo_root)
    except GitHubAuthProbeError as exc:
        print(json.dumps({"status": "error", "detail": str(exc)}, ensure_ascii=True))
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
