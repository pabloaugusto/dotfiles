#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts.ai_contract_paths import evals_root
except ModuleNotFoundError:  # pragma: no cover - execucao direta do script
    from ai_contract_paths import evals_root
from ai_dispatch_lib import ROOT, build_route_payload


def load_jsonl(path: Path) -> list[dict]:
    cases: list[dict] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Dataset invalido em {path}:{line_number}")
        cases.append(payload)
    return cases


def run_routing_cases() -> list[str]:
    dataset = evals_root(ROOT) / "datasets" / "routing.jsonl"
    errors: list[str] = []
    for index, case in enumerate(load_jsonl(dataset), start=1):
        payload = build_route_payload(
            intent=str(case.get("intent", "")),
            paths=[str(item) for item in case.get("paths", [])],
            risk=str(case.get("risk", "medium")),
        )
        task_card = payload["task_card"]
        plan = payload["delegation_plan"]
        for agent in [str(item) for item in case.get("expected_agents", [])]:
            if agent not in task_card["required_agents"]:
                errors.append(f"routing:{index} agente esperado ausente: {agent}")
        expected_primary = str(case.get("expected_primary", "")).strip()
        if expected_primary and expected_primary not in plan["primary_agents"]:
            errors.append(f"routing:{index} primary esperado ausente: {expected_primary}")
        for gate in [str(item) for item in case.get("expected_mandatory_gates", [])]:
            if gate not in plan["mandatory_gates"]:
                errors.append(f"routing:{index} mandatory gate esperado ausente: {gate}")
        for task in [str(item) for item in case.get("expected_validation", [])]:
            if task not in plan["validation"]:
                errors.append(f"routing:{index} validacao esperada ausente: {task}")
    return errors


def run_governance_cases() -> list[str]:
    dataset = evals_root(ROOT) / "datasets" / "governance.jsonl"
    errors: list[str] = []
    for index, case in enumerate(load_jsonl(dataset), start=1):
        decision = str(case.get("decision", "")).strip()
        lesson_ids = case.get("required_lesson_ids", [])
        if decision not in {"capturada", "sem_nova_licao"}:
            errors.append(f"governance:{index} decision invalida: {decision}")
        if not isinstance(lesson_ids, list):
            errors.append(f"governance:{index} required_lesson_ids deve ser lista")
            continue
        if decision == "capturada" and not lesson_ids:
            errors.append(f"governance:{index} capturada exige ao menos uma licao")
    return errors


def main() -> int:
    errors = run_routing_cases() + run_governance_cases()
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print("[OK] Smoke eval de IA passou.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
