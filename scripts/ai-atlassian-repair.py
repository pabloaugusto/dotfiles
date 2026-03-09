#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_repair_lib import repair_generated_atlassian
from scripts.ai_control_plane_lib import AiControlPlaneError


def run_apply(args: argparse.Namespace) -> None:
    print(json.dumps(repair_generated_atlassian(args.repo_root), ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repara descricoes, comentarios e paginas geradas no Jira/Confluence."
    )
    parser.add_argument("--repo-root", default="")
    parser.set_defaults(func=run_apply)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AiControlPlaneError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
