#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_browser_validate_lib import (  # noqa: E402
    AtlassianBrowserValidationError,
    validate_browser_page,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validador browser de paginas Atlassian usando storageState do Playwright."
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--storage-state-path", default="")
    parser.add_argument("--evidence-dir", default="")
    parser.add_argument("--expected-title-contains", default="")
    parser.add_argument("--expected-text", action="append", dest="expected_texts")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--browser", default="chromium")
    parser.add_argument("--headed", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = validate_browser_page(
            repo_root=args.repo_root,
            target_url=args.target_url,
            storage_state_path=args.storage_state_path,
            evidence_dir=args.evidence_dir,
            expected_title_contains=args.expected_title_contains,
            expected_texts=args.expected_texts or [],
            timeout_seconds=args.timeout_seconds,
            browser_name=args.browser,
            headless=not args.headed,
        )
    except AtlassianBrowserValidationError as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
