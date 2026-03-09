#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_openapi_lib import spec_catalog_payload, vendor_openapi_specs
from scripts.ai_control_plane_lib import AiControlPlaneError


def run_show(args: argparse.Namespace) -> None:
    print(json.dumps(spec_catalog_payload(args.repo_root), ensure_ascii=False))


def run_vendor(args: argparse.Namespace) -> None:
    print(json.dumps(vendor_openapi_specs(args.repo_root), ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cataloga e vendoriza specs OpenAPI oficiais da Atlassian."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show")
    show.add_argument("--repo-root", default="")
    show.set_defaults(func=run_show)

    vendor = sub.add_parser("vendor")
    vendor.add_argument("--repo-root", default="")
    vendor.set_defaults(func=run_vendor)

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
