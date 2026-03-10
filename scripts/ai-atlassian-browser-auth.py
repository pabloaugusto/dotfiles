#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_browser_auth_lib import (  # noqa: E402
    AtlassianBrowserAuthError,
    bootstrap_browser_auth,
    browser_auth_status,
)


def run_bootstrap(args: argparse.Namespace) -> None:
    payload = bootstrap_browser_auth(
        repo_root=args.repo_root,
        storage_state_path=args.storage_state_path,
        evidence_dir=args.evidence_dir,
        target_url=args.target_url,
        timeout_seconds=args.timeout_seconds,
        browser_name=args.browser,
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_status(args: argparse.Namespace) -> None:
    payload = browser_auth_status(
        repo_root=args.repo_root,
        storage_state_path=args.storage_state_path,
        evidence_dir=args.evidence_dir,
    )
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap e status da autenticacao Atlassian via Playwright."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    bootstrap = sub.add_parser("bootstrap")
    bootstrap.add_argument("--repo-root", default="")
    bootstrap.add_argument("--storage-state-path", default="")
    bootstrap.add_argument("--evidence-dir", default="")
    bootstrap.add_argument("--target-url", default="")
    bootstrap.add_argument("--timeout-seconds", type=int, default=180)
    bootstrap.add_argument("--browser", default="chromium")
    bootstrap.set_defaults(func=run_bootstrap)

    status = sub.add_parser("status")
    status.add_argument("--repo-root", default="")
    status.add_argument("--storage-state-path", default="")
    status.add_argument("--evidence-dir", default="")
    status.set_defaults(func=run_status)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AtlassianBrowserAuthError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
