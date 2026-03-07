#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_dispatch_lib import (
    DEFAULT_DECISIONS,
    DEFAULT_INTAKE_OUT,
    DEFAULT_ROUTE_OUT,
    DEFAULT_TRACKER,
    build_intake_payload,
    normalize_paths,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Registrar intake com preflight de WIP e roteamento opcional."
    )
    parser.add_argument("--message", required=True)
    parser.add_argument("--paths", default="")
    parser.add_argument("--risk", default="medium")
    parser.add_argument("--route", default="0")
    parser.add_argument("--pending-action", default="")
    parser.add_argument("--worklog-file", default=str(DEFAULT_TRACKER))
    parser.add_argument("--worklog-id", default="")
    parser.add_argument("--decisions-file", default=str(DEFAULT_DECISIONS))
    parser.add_argument("--out", default=str(DEFAULT_INTAKE_OUT))
    parser.add_argument("--route-out", default=str(DEFAULT_ROUTE_OUT))
    args = parser.parse_args()

    payload = build_intake_payload(
        message=args.message,
        paths=normalize_paths(args.paths),
        risk=args.risk,
        route=args.route in {"1", "true", "True", "yes"},
        pending_action=args.pending_action,
        tracker_file=Path(args.worklog_file),
        worklog_id=args.worklog_id,
        decisions_file=Path(args.decisions_file),
    )
    write_json(Path(args.out), payload)
    if payload.get("route_payload"):
        write_json(Path(args.route_out), payload["route_payload"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
