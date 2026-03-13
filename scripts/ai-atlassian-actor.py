#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_actor_lib import (
    actor_runtime_state,
    resolve_atlassian_actor,
    resolve_global_atlassian_actor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve e audita a identidade Atlassian efetiva de um agente."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve = subparsers.add_parser("resolve", help="Resolve a identidade efetiva de um agente.")
    resolve.add_argument("--role", required=True)
    resolve.add_argument("--surface", required=True)
    resolve.add_argument("--context-issue-key", default="")
    resolve.add_argument(
        "--global-only",
        action="store_true",
        help="Resolve apenas o fallback global para a surface informada.",
    )

    subparsers.add_parser("state", help="Mostra o estado acumulado das resolucoes desta worktree.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "state":
        print(json.dumps(actor_runtime_state(None), ensure_ascii=False, indent=2))
        return
    if args.global_only:
        payload = resolve_global_atlassian_actor(None, args.role, args.surface).to_public_dict()
    else:
        payload = resolve_atlassian_actor(
            None,
            args.role,
            args.surface,
            context_issue_key=args.context_issue_key,
        )
        payload = payload.to_public_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
