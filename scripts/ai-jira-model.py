#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_control_plane_lib import AiControlPlaneError
from scripts.ai_jira_model_lib import live_delta_payload, model_summary_payload


def run_show(args: argparse.Namespace) -> None:
    print(json.dumps(model_summary_payload(args.repo_root), ensure_ascii=False))


def run_live_delta(args: argparse.Namespace) -> None:
    print(json.dumps(live_delta_payload(args.repo_root), ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exibe o modelo declarativo do Jira e compara com o estado atual do tenant."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show")
    show.add_argument("--repo-root", default="")
    show.set_defaults(func=run_show)

    live_delta = sub.add_parser("live-delta")
    live_delta.add_argument("--repo-root", default="")
    live_delta.set_defaults(func=run_live_delta)
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
