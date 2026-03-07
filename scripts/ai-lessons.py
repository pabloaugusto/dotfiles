#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_lessons_lib import (
    add_lesson,
    check_reviews,
    ensure_lessons_file,
    list_catalog_ids,
    load_reviews,
    next_lesson_id,
    normalize_lesson_ids,
    sync_reviews,
    upsert_review,
)


def run_ensure(args: argparse.Namespace) -> None:
    lessons = Path(args.file)
    ensure_lessons_file(lessons)
    print(json.dumps({"lessons_file": str(lessons), "status": "ensured"}, ensure_ascii=False))


def run_add(args: argparse.Namespace) -> None:
    lessons = Path(args.file)
    ensure_lessons_file(lessons)
    lesson_id = (args.lesson_id or "").strip() or next_lesson_id(lessons)
    source_repos = [item.strip() for item in (args.source_repos or "").split(",") if item.strip()]
    add_lesson(
        path=lessons,
        lesson_id=lesson_id,
        title=args.title.strip(),
        context=args.context.strip(),
        rule=args.rule.strip(),
        validated_solution=args.validated_solution.strip(),
        prevention=args.prevention.strip(),
        validation=args.validation.strip(),
        related_worklog=(args.worklog_id or "").strip(),
        source_repos=source_repos,
    )
    print(json.dumps({"lessons_file": str(lessons), "lesson_id": lesson_id, "action": "added"}, ensure_ascii=False))


def run_review(args: argparse.Namespace) -> None:
    lessons = Path(args.file)
    lesson_ids = normalize_lesson_ids(args.lesson_ids or "")
    upsert_review(
        path=lessons,
        worklog_id=args.worklog_id.strip(),
        decision=args.decision.strip(),
        summary=args.summary.strip(),
        lesson_ids=lesson_ids,
        evidence=(args.evidence or "").strip(),
    )
    print(
        json.dumps(
            {
                "lessons_file": str(lessons),
                "worklog_id": args.worklog_id.strip(),
                "decision": args.decision.strip(),
                "lesson_ids": lesson_ids,
                "action": "reviewed",
            },
            ensure_ascii=False,
        )
    )


def run_check(args: argparse.Namespace) -> None:
    tracker = Path(args.tracker_file)
    lessons = Path(args.file)
    failures = check_reviews(tracker_path=tracker, lessons_path=lessons)
    if failures:
        raise SystemExit("\n".join(failures))
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "lessons_file": str(lessons),
                "reviewed_worklogs": [row["Worklog ID"] for row in load_reviews(lessons)],
                "status": "checked",
            },
            ensure_ascii=False,
        )
    )


def run_sync(args: argparse.Namespace) -> None:
    lessons = Path(args.file)
    sync_reviews(lessons)
    print(
        json.dumps(
            {"lessons_file": str(lessons), "catalog_ids": list_catalog_ids(lessons), "status": "synced"},
            ensure_ascii=False,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gerencia o fluxo formal de licoes aprendidas do repo.")
    sub = parser.add_subparsers(dest="command", required=True)

    ensure = sub.add_parser("ensure")
    ensure.add_argument("--file", default="LICOES-APRENDIDAS.md")
    ensure.set_defaults(func=run_ensure)

    add = sub.add_parser("add")
    add.add_argument("--file", default="LICOES-APRENDIDAS.md")
    add.add_argument("--lesson-id", default="")
    add.add_argument("--title", required=True)
    add.add_argument("--context", required=True)
    add.add_argument("--rule", required=True)
    add.add_argument("--validated-solution", required=True)
    add.add_argument("--prevention", required=True)
    add.add_argument("--validation", required=True)
    add.add_argument("--worklog-id", default="")
    add.add_argument("--source-repos", default="")
    add.set_defaults(func=run_add)

    review = sub.add_parser("review")
    review.add_argument("--file", default="LICOES-APRENDIDAS.md")
    review.add_argument("--worklog-id", required=True)
    review.add_argument("--decision", required=True, choices=["capturada", "sem_nova_licao"])
    review.add_argument("--summary", required=True)
    review.add_argument("--lesson-ids", default="")
    review.add_argument("--evidence", default="")
    review.set_defaults(func=run_review)

    check = sub.add_parser("check")
    check.add_argument("--file", default="LICOES-APRENDIDAS.md")
    check.add_argument("--tracker-file", default="docs/AI-WIP-TRACKER.md")
    check.set_defaults(func=run_check)

    sync = sub.add_parser("sync")
    sync.add_argument("--file", default="LICOES-APRENDIDAS.md")
    sync.set_defaults(func=run_sync)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
