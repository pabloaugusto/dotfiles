#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.git_signing_lib import (
    GitSigningError,
    apply_automation_mode,
    apply_human_mode,
    ensure_github_signing_key,
    status_payload,
)


def run_status(args: argparse.Namespace) -> None:
    print(json.dumps(status_payload(args.repo_root), ensure_ascii=False))


def run_use_automation(args: argparse.Namespace) -> None:
    payload = apply_automation_mode(
        args.repo_root,
        public_key_ref=args.public_key_ref,
        public_key=args.public_key,
        ensure_github=args.ensure_github == 1,
        title=args.title,
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_use_human(args: argparse.Namespace) -> None:
    print(json.dumps(apply_human_mode(args.repo_root), ensure_ascii=False))


def run_ensure_github(args: argparse.Namespace) -> None:
    payload = ensure_github_signing_key(
        Path(args.repo_root).resolve() if args.repo_root else None or Path.cwd(),
        public_key_ref=args.public_key_ref,
        public_key=args.public_key,
        title=args.title,
    )
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Orquestra o modo de assinatura Git humano x automacao para a worktree atual."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--repo-root", default="")
    status.set_defaults(func=run_status)

    automation = sub.add_parser("use-automation")
    automation.add_argument("--repo-root", default="")
    automation.add_argument("--public-key-ref", default="")
    automation.add_argument("--public-key", default="")
    automation.add_argument("--ensure-github", type=int, choices=[0, 1], default=0)
    automation.add_argument("--title", default="")
    automation.set_defaults(func=run_use_automation)

    human = sub.add_parser("use-human")
    human.add_argument("--repo-root", default="")
    human.set_defaults(func=run_use_human)

    github = sub.add_parser("ensure-github-signing-key")
    github.add_argument("--repo-root", default="")
    github.add_argument("--public-key-ref", default="")
    github.add_argument("--public-key", default="")
    github.add_argument("--title", default="")
    github.set_defaults(func=run_ensure_github)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except GitSigningError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
