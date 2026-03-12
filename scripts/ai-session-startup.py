#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_session_startup_lib import (
    DEFAULT_REPORT_PATH,
    DEFAULT_READINESS_PATH,
    payload_as_json,
    startup_session_payload,
    write_startup_session_report,
)


def run_show(args: argparse.Namespace) -> None:
    payload = startup_session_payload(args.repo_root, pending_action=args.pending_action)
    print(payload_as_json(payload))


def run_report(args: argparse.Namespace) -> None:
    payload = write_startup_session_report(
        args.repo_root,
        out_path=args.out,
        ready_out=args.ready_out,
        pending_action=args.pending_action,
    )
    print(payload_as_json(payload))


def run_enforce(args: argparse.Namespace) -> None:
    payload = write_startup_session_report(
        args.repo_root,
        out_path=args.out,
        ready_out=args.ready_out,
        pending_action=args.pending_action,
    )
    print(payload_as_json(payload))
    startup_governor_status = payload.get("startup_governor_status", {})
    if not startup_governor_status.get("clearance_granted", False):
        blockers = startup_governor_status.get("blocking_findings", [])
        message = "; ".join(str(item) for item in blockers) or "startup clearance bloqueada"
        raise SystemExit(message)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera relatorio declarativo de startup/restart da sessao de IA."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show")
    show.add_argument("--repo-root", type=Path, default=Path(""))
    show.add_argument(
        "--pending-action",
        choices=["concluir_primeiro", "roadmap_pendente"],
        default="",
    )
    show.set_defaults(func=run_show)

    report = sub.add_parser("report")
    report.add_argument("--repo-root", type=Path, default=Path(""))
    report.add_argument("--out", type=Path, default=DEFAULT_REPORT_PATH)
    report.add_argument("--ready-out", type=Path, default=DEFAULT_READINESS_PATH)
    report.add_argument(
        "--pending-action",
        choices=["concluir_primeiro", "roadmap_pendente"],
        default="",
    )
    report.set_defaults(func=run_report)

    enforce = sub.add_parser("enforce")
    enforce.add_argument("--repo-root", type=Path, default=Path(""))
    enforce.add_argument("--out", type=Path, default=DEFAULT_REPORT_PATH)
    enforce.add_argument("--ready-out", type=Path, default=DEFAULT_READINESS_PATH)
    enforce.add_argument(
        "--pending-action",
        choices=["concluir_primeiro", "roadmap_pendente"],
        default="",
    )
    enforce.set_defaults(func=run_enforce)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = (
        args.repo_root.resolve() if str(args.repo_root) else Path(__file__).resolve().parents[1]
    )
    args.repo_root = repo_root
    args.func(args)


if __name__ == "__main__":
    main()
