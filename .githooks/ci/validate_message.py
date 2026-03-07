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
    args = parser.parse_args(argv)

    result = conventional_emoji.validate_message(args.message, require_emoji=True)
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
