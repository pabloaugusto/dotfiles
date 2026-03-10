#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_seed_lib import sync_confluence_docs
from scripts.ai_control_plane_lib import AiControlPlaneError


def parse_issue_keys(raw_value: str) -> list[str]:
    return [entry.strip() for entry in raw_value.split(",") if entry.strip()]


def run_sync(args: argparse.Namespace) -> None:
    payload = sync_confluence_docs(
        args.repo_root,
        issue_keys=parse_issue_keys(args.issue_keys),
    )
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sincroniza a documentacao oficial do control plane no Confluence."
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--issue-keys", default="")
    parser.set_defaults(func=run_sync)
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
