#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.secrets_rotation_lib import (  # noqa: E402
    SecretsRotationError,
    plan_payload,
    preflight_payload,
    validate_payload,
)


def run_preflight(args: argparse.Namespace) -> None:
    payload = preflight_payload(repo_root=args.repo_root, config_path=args.config_path)
    print(json.dumps(payload, ensure_ascii=False))


def run_plan(args: argparse.Namespace) -> None:
    payload = plan_payload(repo_root=args.repo_root, config_path=args.config_path)
    print(json.dumps(payload, ensure_ascii=False))


def run_validate(args: argparse.Namespace) -> None:
    payload = validate_payload(repo_root=args.repo_root, config_path=args.config_path)
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight, plano e validacao nao-destrutiva da trilha de rotacao de secrets."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, runner in {
        "preflight": run_preflight,
        "plan": run_plan,
        "validate": run_validate,
    }.items():
        command = sub.add_parser(name)
        command.add_argument("--repo-root", default="")
        command.add_argument("--config-path", default="")
        command.set_defaults(func=runner)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except SecretsRotationError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
