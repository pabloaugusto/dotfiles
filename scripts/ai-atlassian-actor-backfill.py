#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_atlassian_actor_backfill_lib import (
    DEFAULT_MAX_ISSUES,
    apply_actor_comment_backfill,
    audit_actor_comment_backfill,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audita e aplica backfill de comentarios Jira para service accounts por agente."
    )
    parser.add_argument("--role", default="ai-product-owner")
    parser.add_argument("--issue-key", action="append", dest="issue_keys")
    parser.add_argument("--max-issues", type=int, default=DEFAULT_MAX_ISSUES)
    parser.add_argument(
        "--include-non-global-authored",
        action="store_true",
        help="Inclui candidatos cujo comentario legado nao foi escrito pela service account global.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica o backfill de fato; sem isso roda apenas auditoria.",
    )
    parser.add_argument(
        "--keep-legacy-comments",
        action="store_true",
        help="Nao remove o comentario legado depois de criar ou reutilizar o comentario da service account propria.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    only_global_authored = not args.include_non_global_authored
    if args.apply:
        payload = apply_actor_comment_backfill(
            role_id=args.role,
            issue_keys=args.issue_keys,
            max_issues=args.max_issues,
            delete_legacy_comments=not args.keep_legacy_comments,
            only_global_authored=only_global_authored,
        )
    else:
        payload = audit_actor_comment_backfill(
            role_id=args.role,
            issue_keys=args.issue_keys,
            max_issues=args.max_issues,
            only_global_authored=only_global_authored,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
