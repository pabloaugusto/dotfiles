#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.cspell_governance_lib import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_DECISIONS_PATH,
    DEFAULT_LEDGER_PATH,
    DEFAULT_PROJECT_WORDS_PATH,
    DEFAULT_ROADMAP_PATH,
    add_project_words,
    find_redundant_project_words,
    load_project_words,
    review_paths,
    run_cspell,
)


def run_check(args: argparse.Namespace) -> int:
    targets = args.targets or ["."]
    result = run_cspell(
        ["lint", *targets, "--config", args.config, "--gitignore", "--dot"]
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def run_dictionary_audit(args: argparse.Namespace) -> int:
    redundant = find_redundant_project_words(
        config_path=Path(args.config),
        project_words_path=Path(args.project_words),
    )
    payload = {"redundant_words": redundant, "count": len(redundant)}
    print(json.dumps(payload, ensure_ascii=False))
    if redundant and not args.fix:
        return 1
    if redundant and args.fix:
        current = load_project_words(Path(args.project_words))
        cleaned = [word for word in current if word not in set(redundant)]
        from scripts.cspell_governance_lib import save_project_words

        save_project_words(cleaned, Path(args.project_words))
    return 0


def run_curate(args: argparse.Namespace) -> int:
    targets = args.targets or ["."]
    result = run_cspell(
        ["lint", *targets, "--config", args.config, "--gitignore", "--dot"]
    )
    from scripts.cspell_governance_lib import parse_unknown_word_findings

    findings = parse_unknown_word_findings((result.stdout or "") + "\n" + (result.stderr or ""))
    unknown_words = sorted({finding.word for finding in findings})
    current_words = load_project_words(Path(args.project_words))
    additions = [word for word in unknown_words if word not in current_words]
    added = 0
    if args.apply and additions:
        added = add_project_words(additions, Path(args.project_words))
    payload = {
        "unknown_words": unknown_words,
        "candidate_additions": additions,
        "added": added,
        "applied": bool(args.apply),
    }
    print(json.dumps(payload, ensure_ascii=False))
    if additions and not args.apply:
        return 1
    return 0


def run_review(args: argparse.Namespace) -> int:
    payload = review_paths(
        worklog_id=args.worklog_id,
        reviewer=args.reviewer,
        paths=[chunk.strip() for chunk in args.paths.split(",") if chunk.strip()],
        ledger_path=Path(args.ledger_file),
        config_path=Path(args.config),
        project_words_path=Path(args.project_words),
        roadmap_path=Path(args.roadmap_file),
        decisions_path=Path(args.decisions_file),
        register_pending=args.register_pending,
        fix_dictionary=args.fix_dictionary,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Governanca ortografica consultiva do repositorio via Pascoalete + CSpell."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check")
    check.add_argument("targets", nargs="*")
    check.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    check.set_defaults(func=run_check)

    dict_audit = sub.add_parser("dictionary-audit")
    dict_audit.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    dict_audit.add_argument("--project-words", default=str(DEFAULT_PROJECT_WORDS_PATH))
    dict_audit.add_argument("--fix", action="store_true")
    dict_audit.set_defaults(func=run_dictionary_audit)

    curate = sub.add_parser("curate")
    curate.add_argument("targets", nargs="*")
    curate.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    curate.add_argument("--project-words", default=str(DEFAULT_PROJECT_WORDS_PATH))
    curate.add_argument("--apply", action="store_true")
    curate.set_defaults(func=run_curate)

    review = sub.add_parser("review")
    review.add_argument("--worklog-id", required=True)
    review.add_argument("--reviewer", default="pascoalete")
    review.add_argument("--paths", required=True)
    review.add_argument("--ledger-file", default=str(DEFAULT_LEDGER_PATH))
    review.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    review.add_argument("--project-words", default=str(DEFAULT_PROJECT_WORDS_PATH))
    review.add_argument("--roadmap-file", default=str(DEFAULT_ROADMAP_PATH))
    review.add_argument("--decisions-file", default=str(DEFAULT_DECISIONS_PATH))
    review.add_argument("--register-pending", action=argparse.BooleanOptionalAction, default=True)
    review.add_argument("--fix-dictionary", action=argparse.BooleanOptionalAction, default=True)
    review.set_defaults(func=run_review)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
