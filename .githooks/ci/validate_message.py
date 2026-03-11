#!/usr/bin/env python3
"""Validador de mensagem para commit subject e PR title."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import conventional_emoji  # noqa: E402


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("message", help="Mensagem a validar.")
    parser.add_argument("--context", default="message", help="Contexto da validacao.")
    parser.add_argument("--branch", default="", help="Branch contextual para enforcement.")
    parser.add_argument(
        "--paths-json",
        default="",
        help="Lista JSON de paths para enforcement contextual.",
    )
    args = parser.parse_args(argv)

    try:
        paths = conventional_emoji.parse_paths_json(args.paths_json)
    except ValueError as exc:
        print(f"INVALID ({args.context})", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    required_scope = conventional_emoji.required_scope_for_paths_and_branch(
        paths, args.branch
    )
    result = conventional_emoji.validate_message(
        args.message,
        require_emoji=True,
        require_issue_key=True,
        required_scope=required_scope,
    )
    if result.ok:
        print(f"OK ({args.context})")
        return 0

    print(f"INVALID ({args.context})", file=sys.stderr)
    if result.error:
        print(result.error, file=sys.stderr)
    print("\nMensagem recebida:", file=sys.stderr)
    print(args.message, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
