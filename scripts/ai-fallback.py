#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_fallback_governance_lib import (
    FallbackGovernanceError,
    capture_fallback_record,
    fallback_status_payload,
    resolve_fallback_record,
)


def resolve_repo_path(repo_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (repo_root / candidate).resolve()


def run_status(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).resolve()
    payload = fallback_status_payload(
        repo_root,
        ledger_path=resolve_repo_path(repo_root, args.ledger_file),
        tracker_path=resolve_repo_path(repo_root, args.tracker_file),
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_capture(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).resolve()
    payload = capture_fallback_record(
        repo_root,
        tracker_relative=args.tracker,
        local_reference=args.local_reference,
        summary=args.summary,
        next_step=args.next_step,
        jira_issue=args.jira_issue,
        allow_when_jira_available=args.allow_while_jira_up == 1,
        ledger_path=resolve_repo_path(repo_root, args.ledger_file),
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_resolve(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).resolve()
    payload = resolve_fallback_record(
        repo_root,
        tracker_relative=args.tracker,
        local_reference=args.local_reference,
        outcome=args.outcome,
        result=args.result,
        jira_issue=args.jira_issue,
        summary=args.summary,
        agent=args.agent,
        sync_jira=args.sync_jira == 1,
        ledger_path=resolve_repo_path(repo_root, args.ledger_file),
    )
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Governanca do fallback local entre Jira primario e trackers contingenciais."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--repo-root", default=".")
    status.add_argument("--ledger-file", default="docs/AI-FALLBACK-LEDGER.md")
    status.add_argument("--tracker-file", default="docs/AI-WIP-TRACKER.md")
    status.set_defaults(func=run_status)

    capture = sub.add_parser("capture")
    capture.add_argument("--repo-root", default=".")
    capture.add_argument("--ledger-file", default="docs/AI-FALLBACK-LEDGER.md")
    capture.add_argument("--tracker", required=True)
    capture.add_argument("--local-reference", required=True)
    capture.add_argument("--summary", required=True)
    capture.add_argument("--next-step", required=True)
    capture.add_argument("--jira-issue", default="")
    capture.add_argument("--allow-while-jira-up", type=int, choices=[0, 1], default=0)
    capture.set_defaults(func=run_capture)

    resolve = sub.add_parser("resolve")
    resolve.add_argument("--repo-root", default=".")
    resolve.add_argument("--ledger-file", default="docs/AI-FALLBACK-LEDGER.md")
    resolve.add_argument("--tracker", required=True)
    resolve.add_argument("--local-reference", required=True)
    resolve.add_argument("--outcome", required=True, choices=["drained", "reconciled", "obsolete"])
    resolve.add_argument("--result", default="")
    resolve.add_argument("--summary", default="")
    resolve.add_argument("--jira-issue", default="")
    resolve.add_argument("--agent", default="ai-product-owner")
    resolve.add_argument("--sync-jira", type=int, choices=[0, 1], default=1)
    resolve.set_defaults(func=run_resolve)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except FallbackGovernanceError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
