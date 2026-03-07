#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_dispatch_lib import (
    DEFAULT_ROUTE_OUT,
    RISK_LEVELS,
    build_route_payload,
    normalize_paths,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerar roteamento declarativo de IA.")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--paths", default="")
    parser.add_argument("--risk", default="medium")
    parser.add_argument("--out", default=str(DEFAULT_ROUTE_OUT))
    args = parser.parse_args()

    if args.risk not in RISK_LEVELS:
        raise SystemExit("--risk deve ser low, medium ou high")

    payload = build_route_payload(
        intent=args.intent, paths=normalize_paths(args.paths), risk=args.risk
    )
    write_json(Path(args.out), payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
