#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_agent_execution_lib import resolve_jira

PROMPTS_ROOT = Path(".agents/prompts/formal")
DEFAULT_SUMMARY_PREFIX = "PROMPT:"
DEFAULT_REQUIRED_LABEL = "prompt"


@dataclass(frozen=True)
class PromptIssueContract:
    pack_id: str
    task_id: str
    owner_issue: str
    summary_prefix: str
    required_labels: tuple[str, ...]


def load_prompt_issue_contracts(repo_root: Path) -> list[PromptIssueContract]:
    prompts_root = (repo_root / PROMPTS_ROOT).resolve()
    if not prompts_root.is_dir():
        raise RuntimeError("Pasta de prompt packs formais ausente.")

    contracts: list[PromptIssueContract] = []
    for pack_root in sorted(
        (item for item in prompts_root.iterdir() if item.is_dir()), key=lambda item: item.name
    ):
        meta_path = pack_root / "meta.yaml"
        if not meta_path.is_file():
            continue
        payload = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise RuntimeError(f"meta.yaml invalido em {meta_path.as_posix()}")
        owner_issue = str(payload.get("owner_issue", "") or "").strip().upper()
        if not owner_issue:
            continue
        jira_payload = payload.get("jira") or {}
        if not isinstance(jira_payload, dict):
            jira_payload = {}
        required_labels_raw = jira_payload.get("required_labels") or []
        required_labels = tuple(
            sorted({str(label).strip() for label in required_labels_raw if str(label).strip()})
        )
        contracts.append(
            PromptIssueContract(
                pack_id=str(payload.get("id", pack_root.name) or pack_root.name).strip(),
                task_id=str(payload.get("task_id", "") or "").strip(),
                owner_issue=owner_issue,
                summary_prefix=str(
                    jira_payload.get("summary_prefix", "") or DEFAULT_SUMMARY_PREFIX
                ).strip()
                or DEFAULT_SUMMARY_PREFIX,
                required_labels=required_labels or (DEFAULT_REQUIRED_LABEL,),
            )
        )
    return contracts


def normalize_prompt_summary(summary: str, prefix: str) -> str:
    normalized_prefix = str(prefix or DEFAULT_SUMMARY_PREFIX).strip() or DEFAULT_SUMMARY_PREFIX
    raw = str(summary or "").strip()
    if not raw:
        return normalized_prefix
    base = re.sub(rf"^(?:{re.escape(normalized_prefix)}\s*)+", "", raw).strip()
    return f"{normalized_prefix} {base}".strip()


def merge_labels(existing_labels: list[str], required_labels: tuple[str, ...]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for label in list(existing_labels) + list(required_labels):
        normalized = str(label).strip()
        if not normalized:
            continue
        folded = normalized.casefold()
        if folded in seen:
            continue
        seen.add(folded)
        merged.append(normalized)
    return merged


def issue_contract_delta(jira: Any, contract: PromptIssueContract) -> dict[str, Any]:
    issue = jira.get_issue(contract.owner_issue, fields=["summary", "labels"])
    fields = issue.get("fields") or {}
    if not isinstance(fields, dict):
        raise RuntimeError(f"Issue Jira invalida para {contract.owner_issue}")
    current_summary = str(fields.get("summary", "") or "").strip()
    current_labels_raw = fields.get("labels") or []
    if not isinstance(current_labels_raw, list):
        current_labels_raw = []
    current_labels = [str(label).strip() for label in current_labels_raw if str(label).strip()]
    expected_summary = normalize_prompt_summary(current_summary, contract.summary_prefix)
    expected_labels = merge_labels(current_labels, contract.required_labels)
    missing_labels = [
        label
        for label in contract.required_labels
        if label.casefold() not in {existing.casefold() for existing in current_labels}
    ]
    return {
        "pack_id": contract.pack_id,
        "task_id": contract.task_id,
        "issue_key": contract.owner_issue,
        "current_summary": current_summary,
        "expected_summary": expected_summary,
        "current_labels": current_labels,
        "expected_labels": expected_labels,
        "missing_labels": missing_labels,
        "needs_summary_update": current_summary != expected_summary,
        "needs_label_update": bool(missing_labels),
    }


def check_contracts(repo_root: Path) -> dict[str, Any]:
    jira = resolve_jira(repo_root)
    contracts = load_prompt_issue_contracts(repo_root)
    results = [issue_contract_delta(jira, contract) for contract in contracts]
    return {
        "repo_root": str(repo_root),
        "contracts": results,
        "ok": all(
            not item["needs_summary_update"] and not item["missing_labels"] for item in results
        ),
    }


def sync_contracts(repo_root: Path) -> dict[str, Any]:
    jira = resolve_jira(repo_root)
    contracts = load_prompt_issue_contracts(repo_root)
    results: list[dict[str, Any]] = []
    for contract in contracts:
        delta = issue_contract_delta(jira, contract)
        fields: dict[str, Any] = {}
        if delta["needs_summary_update"]:
            fields["summary"] = delta["expected_summary"]
        if delta["missing_labels"]:
            fields["labels"] = delta["expected_labels"]
        if fields:
            jira.update_issue_fields(contract.owner_issue, fields)
        refreshed = issue_contract_delta(jira, contract)
        refreshed["applied_fields"] = fields
        results.append(refreshed)
    return {
        "repo_root": str(repo_root),
        "contracts": results,
        "ok": all(
            not item["needs_summary_update"] and not item["missing_labels"] for item in results
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida e sincroniza a governanca Jira dos prompt packs formais."
    )
    parser.add_argument("command", choices=("check", "sync"))
    parser.add_argument("--repo-root", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    payload = check_contracts(repo_root) if args.command == "check" else sync_contracts(repo_root)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
