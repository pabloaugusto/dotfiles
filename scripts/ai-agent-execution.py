#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_agent_execution_lib import (
    AgentExecutionError,
    clear_context,
    default_context_path,
    load_context,
    record_activity,
)


def csv_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split("||") if item.strip()]


def run_status(args: argparse.Namespace) -> None:
    context = load_context(args.repo_root)
    payload = {
        "context_path": str(default_context_path(args.repo_root)),
        "context": None if context is None else context.__dict__,
    }
    print(json.dumps(payload, ensure_ascii=False))


def run_clear(args: argparse.Namespace) -> None:
    clear_context(args.repo_root)
    print(json.dumps({"context_path": str(default_context_path(args.repo_root)), "cleared": True}))


def run_start(args: argparse.Namespace) -> None:
    payload = record_activity(
        repo_root=args.repo_root,
        issue_key=args.issue_key,
        agent=args.agent,
        interaction_type=args.interaction_type,
        status=args.status,
        contexto=csv_list(args.contexto),
        evidencias=csv_list(args.evidencias),
        proximo_passo=args.proximo_passo,
        current_agent_role=args.agent,
        next_required_role=args.next_required_role,
        transition_issue=args.transition == 1,
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_progress(args: argparse.Namespace) -> None:
    payload = record_activity(
        repo_root=args.repo_root,
        issue_key=args.issue_key,
        agent=args.agent,
        interaction_type=args.interaction_type,
        status=args.status,
        contexto=csv_list(args.contexto),
        evidencias=csv_list(args.evidencias),
        proximo_passo=args.proximo_passo,
        current_agent_role=args.agent,
        next_required_role=args.next_required_role,
        transition_issue=args.transition == 1,
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_handoff(args: argparse.Namespace) -> None:
    payload = record_activity(
        repo_root=args.repo_root,
        issue_key=args.issue_key,
        agent=args.agent,
        interaction_type="handoff",
        status=args.status,
        contexto=csv_list(args.contexto),
        evidencias=csv_list(args.evidencias),
        proximo_passo=args.proximo_passo,
        current_agent_role="",
        next_required_role=args.next_required_role,
        transition_issue=args.transition == 1,
        clear_after=True,
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_pause(args: argparse.Namespace) -> None:
    payload = record_activity(
        repo_root=args.repo_root,
        issue_key=args.issue_key,
        agent=args.agent,
        interaction_type="blocker" if args.blocker == 1 else "progress-update",
        status="paused",
        contexto=csv_list(args.contexto),
        evidencias=csv_list(args.evidencias),
        proximo_passo=args.proximo_passo,
        current_agent_role="",
        next_required_role=args.next_required_role,
        transition_issue=args.transition == 1,
        clear_after=True,
    )
    print(json.dumps(payload, ensure_ascii=False))


def run_done(args: argparse.Namespace) -> None:
    payload = record_activity(
        repo_root=args.repo_root,
        issue_key=args.issue_key,
        agent=args.agent,
        interaction_type="closure",
        status="done",
        contexto=csv_list(args.contexto),
        evidencias=csv_list(args.evidencias),
        proximo_passo=args.proximo_passo,
        current_agent_role="",
        next_required_role="",
        transition_issue=args.transition == 1,
        clear_after=True,
    )
    print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mantem contexto local ativo por agente/issue e sincroniza a atividade com o Jira."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--repo-root", default="")
        command.add_argument("--issue-key", default="")
        command.add_argument("--agent", default="")
        command.add_argument("--status", default="doing")
        command.add_argument("--contexto", default="")
        command.add_argument("--evidencias", default="")
        command.add_argument("--proximo-passo", default="")
        command.add_argument("--next-required-role", default="")
        command.add_argument("--transition", type=int, choices=[0, 1], default=1)

    status = sub.add_parser("status")
    status.add_argument("--repo-root", default="")
    status.set_defaults(func=run_status)

    clear = sub.add_parser("clear")
    clear.add_argument("--repo-root", default="")
    clear.set_defaults(func=run_clear)

    start = sub.add_parser("start")
    add_common(start)
    start.add_argument("--interaction-type", default="progress-update")
    start.set_defaults(func=run_start)

    progress = sub.add_parser("progress")
    add_common(progress)
    progress.add_argument("--interaction-type", default="progress-update")
    progress.set_defaults(func=run_progress)

    handoff = sub.add_parser("handoff")
    add_common(handoff)
    handoff.set_defaults(func=run_handoff)

    pause = sub.add_parser("pause")
    add_common(pause)
    pause.add_argument("--blocker", type=int, choices=[0, 1], default=1)
    pause.set_defaults(func=run_pause)

    done = sub.add_parser("done")
    add_common(done)
    done.set_defaults(func=run_done)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AgentExecutionError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
