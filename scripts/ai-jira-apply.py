#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_control_plane_lib import AiControlPlaneError
from scripts.ai_jira_apply_lib import apply_jira_model, build_apply_plan


def run_plan(args: argparse.Namespace) -> None:
    print(json.dumps(build_apply_plan(args.repo_root), ensure_ascii=False))


def run_apply(args: argparse.Namespace) -> None:
    print(json.dumps(apply_jira_model(args.repo_root), ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Planeja e aplica o schema Jira do control plane.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("--repo-root", default="")
    plan.set_defaults(func=run_plan)

    apply = sub.add_parser("apply")
    apply.add_argument("--repo-root", default="")
    apply.set_defaults(func=run_apply)
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
