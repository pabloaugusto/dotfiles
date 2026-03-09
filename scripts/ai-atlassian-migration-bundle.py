#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_migration_bundle_lib import build_migration_bundle
from scripts.ai_control_plane_lib import AiControlPlaneError


def run_bundle(args: argparse.Namespace) -> None:
    print(
        json.dumps(
            build_migration_bundle(args.repo_root, output_root=args.output_root),
            ensure_ascii=False,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera bundle auditavel da migracao repo -> Jira/Confluence."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    bundle = sub.add_parser("bundle")
    bundle.add_argument("--repo-root", default="")
    bundle.add_argument("--output-root", default="")
    bundle.set_defaults(func=run_bundle)
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
