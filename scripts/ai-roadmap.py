#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_roadmap_lib import (
    ensure_decisions_file,
    ensure_roadmap_file,
    refresh_roadmap,
    register_roadmap_decision,
)


def run_ensure(args: argparse.Namespace) -> None:
    roadmap = Path(args.roadmap_file)
    decisions = Path(args.decisions_file)
    ensure_roadmap_file(roadmap)
    ensure_decisions_file(decisions)
    refresh_roadmap(roadmap_path=roadmap, decisions_path=decisions)
    print(
        json.dumps(
            {"roadmap_file": str(roadmap), "decisions_file": str(decisions), "status": "ensured"},
            ensure_ascii=False,
        )
    )


def run_refresh(args: argparse.Namespace) -> None:
    payload = refresh_roadmap(
        roadmap_path=Path(args.roadmap_file),
        decisions_path=Path(args.decisions_file),
        cycle=args.cycle or "",
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_register(args: argparse.Namespace) -> None:
    payload = register_roadmap_decision(
        roadmap_path=Path(args.roadmap_file),
        decisions_path=Path(args.decisions_file),
        suggestion=args.suggestion,
        decision=args.decision,
        horizon=args.horizon,
        notes=args.notes,
        suggestion_id=args.suggestion_id,
        roadmap_id=args.roadmap_id,
        cycle=args.cycle or "",
    )
    refresh_roadmap(
        roadmap_path=Path(args.roadmap_file),
        decisions_path=Path(args.decisions_file),
        cycle=args.cycle or "",
    )
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gerencia os artefatos de roadmap do repo.")
    sub = parser.add_subparsers(dest="command", required=True)

    ensure = sub.add_parser("ensure")
    ensure.add_argument("--roadmap-file", default="docs/ROADMAP.md")
    ensure.add_argument("--decisions-file", default="docs/ROADMAP-DECISIONS.md")
    ensure.set_defaults(func=run_ensure)

    refresh = sub.add_parser("refresh")
    refresh.add_argument("--roadmap-file", default="docs/ROADMAP.md")
    refresh.add_argument("--decisions-file", default="docs/ROADMAP-DECISIONS.md")
    refresh.add_argument("--cycle", default="")
    refresh.set_defaults(func=run_refresh)

    register = sub.add_parser("register")
    register.add_argument("--roadmap-file", default="docs/ROADMAP.md")
    register.add_argument("--decisions-file", default="docs/ROADMAP-DECISIONS.md")
    register.add_argument("--suggestion", required=True)
    register.add_argument("--decision", choices=["accepted", "pending", "discarded"], required=True)
    register.add_argument("--horizon", choices=["now", "next", "later"], default="next")
    register.add_argument("--notes", default="")
    register.add_argument("--suggestion-id", default="")
    register.add_argument("--roadmap-id", default="")
    register.add_argument("--cycle", default="")
    register.set_defaults(func=run_register)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
