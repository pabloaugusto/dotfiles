#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_review_lib import (
    ROOT,
    check_review_gate,
    ensure_review_file,
    parse_paths_csv,
    record_review,
    required_specialist_reviewers,
)


def run_ensure(args: argparse.Namespace) -> None:
    review_path = Path(args.review_file)
    ensure_review_file(review_path)
    print(json.dumps({"review_file": str(review_path), "status": "ensured"}, ensure_ascii=False))


def run_required(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else ROOT
    paths = parse_paths_csv(args.paths)
    reviewers = required_specialist_reviewers(
        repo_root=repo_root,
        intent=args.intent,
        risk=args.risk,
        paths=paths,
    )
    print(
        json.dumps(
            {"repo_root": str(repo_root), "paths": paths, "required_reviewers": reviewers},
            ensure_ascii=False,
        )
    )


def run_record(args: argparse.Namespace) -> None:
    result = record_review(
        review_path=Path(args.review_file),
        worklog_id=args.worklog_id,
        reviewer=args.reviewer,
        status=args.status,
        summary=args.summary,
        paths=parse_paths_csv(args.paths),
        evidence=args.evidence,
    )
    print(json.dumps(result, ensure_ascii=False))


def run_check(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else ROOT
    result = check_review_gate(
        review_path=Path(args.review_file),
        worklog_id=args.worklog_id,
        repo_root=repo_root,
        intent=args.intent,
        risk=args.risk,
        paths=parse_paths_csv(args.paths),
    )
    if not result["ok"]:
        raise SystemExit(
            "Revisao especializada bloqueou o fechamento:\n- "
            + "\n- ".join(result["errors"])
        )
    print(json.dumps(result, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gerencia o ledger de revisao especializada.")
    sub = parser.add_subparsers(dest="command", required=True)

    ensure = sub.add_parser("ensure")
    ensure.add_argument("--review-file", default="docs/AI-REVIEW-LEDGER.md")
    ensure.set_defaults(func=run_ensure)

    required = sub.add_parser("required")
    required.add_argument("--repo-root", default=str(ROOT))
    required.add_argument("--paths", default="")
    required.add_argument("--intent", default="Revisao especializada obrigatoria")
    required.add_argument("--risk", default="medium")
    required.set_defaults(func=run_required)

    record = sub.add_parser("record")
    record.add_argument("--review-file", default="docs/AI-REVIEW-LEDGER.md")
    record.add_argument("--worklog-id", required=True)
    record.add_argument("--reviewer", required=True)
    record.add_argument("--status", required=True, choices=["aprovado", "reprovado"])
    record.add_argument("--summary", required=True)
    record.add_argument("--paths", default="")
    record.add_argument("--evidence", default="")
    record.set_defaults(func=run_record)

    check = sub.add_parser("check")
    check.add_argument("--review-file", default="docs/AI-REVIEW-LEDGER.md")
    check.add_argument("--worklog-id", required=True)
    check.add_argument("--repo-root", default=str(ROOT))
    check.add_argument("--paths", default="")
    check.add_argument("--intent", default="Revisao especializada obrigatoria")
    check.add_argument("--risk", default="medium")
    check.set_defaults(func=run_check)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
