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
from scripts.ai_sync_foundation_lib import (
    drain_sync_events,
    record_sync_event,
    sync_check_payload,
    sync_status_payload,
)
from scripts.atlassian_platform_lib import connectivity_payload


def run_show(args: argparse.Namespace) -> None:
    payload = summary_payload(args.repo_root)
    try:
        payload["sync"] = sync_check_payload(args.repo_root)
    except AiControlPlaneError as exc:
        payload["sync"] = {
            "ok": False,
            "error": str(exc),
        }
    print(json.dumps(payload, ensure_ascii=False))


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


def run_sync_check(args: argparse.Namespace) -> None:
    print(json.dumps(sync_check_payload(args.repo_root), ensure_ascii=False))


def run_sync_status(args: argparse.Namespace) -> None:
    print(json.dumps(sync_status_payload(args.repo_root), ensure_ascii=False))


def run_sync_record(args: argparse.Namespace) -> None:
    try:
        payload = json.loads(args.payload_json)
    except json.JSONDecodeError as exc:
        raise AiControlPlaneError("--payload-json precisa conter JSON valido.") from exc
    result = record_sync_event(
        args.repo_root,
        artifact_key=args.artifact_key,
        record_key=args.record_key,
        payload=payload,
        execution_status=args.execution_status,
        effectiveness_status=args.effectiveness_status,
        occurred_at=args.occurred_at,
    )
    print(json.dumps(result, ensure_ascii=False))


def run_sync_drain(args: argparse.Namespace) -> None:
    payload = drain_sync_events(
        args.repo_root,
        artifact_key=args.artifact_key,
        apply=args.apply,
        max_events=args.max_events,
    )
    print(json.dumps(payload, ensure_ascii=False))
    if bool(payload.get("errors")):
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

    sync_check = sub.add_parser("sync-check")
    sync_check.add_argument("--repo-root", default="")
    sync_check.set_defaults(func=run_sync_check)

    sync_status = sub.add_parser("sync-status")
    sync_status.add_argument("--repo-root", default="")
    sync_status.set_defaults(func=run_sync_status)

    sync_record = sub.add_parser("sync-record")
    sync_record.add_argument("--repo-root", default="")
    sync_record.add_argument("--artifact-key", required=True)
    sync_record.add_argument("--record-key", required=True)
    sync_record.add_argument("--payload-json", default="{}")
    sync_record.add_argument("--execution-status", default="success")
    sync_record.add_argument("--effectiveness-status", default="effective")
    sync_record.add_argument("--occurred-at", default="")
    sync_record.set_defaults(func=run_sync_record)

    sync_drain = sub.add_parser("sync-drain")
    sync_drain.add_argument("--repo-root", default="")
    sync_drain.add_argument("--artifact-key", default="")
    sync_drain.add_argument("--apply", action="store_true")
    sync_drain.add_argument("--max-events", type=int, default=0)
    sync_drain.set_defaults(func=run_sync_drain)
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
