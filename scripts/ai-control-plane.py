#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    service_account_ratelimit_payload,
    summary_payload,
)
from scripts.atlassian_platform_lib import connectivity_payload


def run_show(args: argparse.Namespace) -> None:
    print(json.dumps(summary_payload(args.repo_root), ensure_ascii=False))


def run_atlassian_check(args: argparse.Namespace) -> None:
    payload = connectivity_payload(
        args.repo_root,
        site_url_override=args.site_url,
    )
    print(json.dumps(payload, ensure_ascii=False))
    if not bool(payload.get("overall_ok", False)):
        raise SystemExit(1)


def run_op_ratelimit(args: argparse.Namespace) -> None:
    payload = service_account_ratelimit_payload(args.repo_root, force_refresh=args.refresh)
    print(json.dumps(payload, ensure_ascii=False))
    if bool(payload.get("account_read_write_exhausted", False)):
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspeciona a control plane de IA e valida a conectividade Atlassian."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show")
    show.add_argument("--repo-root", default="")
    show.set_defaults(func=run_show)

    atlassian_check = sub.add_parser("atlassian-check")
    atlassian_check.add_argument("--repo-root", default="")
    atlassian_check.add_argument("--site-url", default="")
    atlassian_check.set_defaults(func=run_atlassian_check)

    op_ratelimit = sub.add_parser("op-ratelimit")
    op_ratelimit.add_argument("--repo-root", default="")
    op_ratelimit.add_argument("--refresh", action="store_true")
    op_ratelimit.set_defaults(func=run_op_ratelimit)
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
