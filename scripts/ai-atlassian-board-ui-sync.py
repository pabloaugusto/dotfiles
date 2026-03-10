#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_board_ui_sync_lib import (  # noqa: E402
    AtlassianBoardUiSyncError,
    sync_jira_board_ui,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sincroniza o layout do Jira board pela UI via Playwright autenticado."
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--settings-url", required=True)
    parser.add_argument("--storage-state-path", default="")
    parser.add_argument("--evidence-dir", default="")
    parser.add_argument("--rename-column", action="append", dest="rename_columns")
    parser.add_argument("--add-column", action="append", dest="add_columns")
    parser.add_argument("--card-field", action="append", dest="card_fields")
    parser.add_argument("--remove-status", action="append", dest="remove_statuses")
    parser.add_argument("--map-status", action="append", dest="map_statuses")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--browser", default="chromium")
    parser.add_argument("--headed", action="store_true")
    return parser


def main() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):  # pragma: no branch - compat runtime local
        reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = sync_jira_board_ui(
            repo_root=args.repo_root,
            settings_url=args.settings_url,
            storage_state_path=args.storage_state_path,
            evidence_dir=args.evidence_dir,
            rename_columns=args.rename_columns or [],
            add_columns=args.add_columns or [],
            card_fields=args.card_fields or [],
            remove_statuses=args.remove_statuses or [],
            map_statuses=args.map_statuses or [],
            timeout_seconds=args.timeout_seconds,
            browser_name=args.browser,
            headless=not args.headed,
        )
    except AtlassianBoardUiSyncError as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
