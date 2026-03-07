from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from scripts.ai_contract_paths import ROOT
from scripts.ai_dispatch_lib import build_route_payload
from scripts.ai_lessons_lib import (
    extract_between,
    normalize_cell,
    now_human_utc,
    parse_table,
    render_table,
    replace_between,
    write_text_lf,
)

RECORDS_START = "<!-- ai-review:records:start -->"
RECORDS_END = "<!-- ai-review:records:end -->"
RECORD_HEADERS = [
    "Data/Hora UTC",
    "Worklog ID",
    "Revisor",
    "Status",
    "Arquivos",
    "Resumo",
    "Evidencia",
]
ALLOWED_REVIEW_STATUSES = {"aprovado", "reprovado"}
SPECIALIST_REVIEWERS = {
    "python-reviewer",
    "powershell-reviewer",
    "automation-reviewer",
}


def review_template() -> str:
    return """# AI Review Ledger

Atualizado em: {updated_at}

Registro operacional dos pareceres de revisao especializada por `worklog`.

## Regras operacionais

- Toda mudanca de codigo ou automacao que toque Python, PowerShell, shell,
  workflows, `Taskfile.yml` ou Docker exige parecer explicito do revisor
  especializado correspondente antes de fechar o `worklog`.
- O parecer vale por `worklog` + `revisor`.
- Apenas o registro mais recente de cada `worklog` + `revisor` conta como fonte
  de verdade.
- `reprovado` bloqueia o `done` ate existir um novo parecer `aprovado`.
- Se nao houver familia de arquivo coberta pelo gate especializado, o ledger nao
  bloqueia o fechamento.

## Status validos

- `aprovado`
- `reprovado`

## Artefatos relacionados

- [`AGENTS.md`](../AGENTS.md)
- [`LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md)
- [`docs/AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md)
- [`ROADMAP.md`](../ROADMAP.md)
- [`scripts/ai-review.py`](../scripts/ai-review.py)
- [`scripts/ai_review_lib.py`](../scripts/ai_review_lib.py)

## Registros

<!-- ai-review:records:start -->
| Data/Hora UTC | Worklog ID | Revisor | Status | Arquivos | Resumo | Evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - |
<!-- ai-review:records:end -->
""".format(updated_at=now_human_utc())


def ensure_review_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(path, review_template())


def load_reviews(path: Path) -> list[dict[str, str]]:
    ensure_review_file(path)
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, RECORDS_START, RECORDS_END, label=str(path))
    return parse_table(section, RECORD_HEADERS, label=str(path))


def save_reviews(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_review_file(path)
    raw = path.read_text(encoding="utf-8")
    updated = replace_between(
        raw,
        RECORDS_START,
        RECORDS_END,
        render_table(RECORD_HEADERS, rows),
        label=str(path),
    )
    write_text_lf(path, updated)


def normalize_path_list(paths: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in paths:
        candidate = (raw or "").strip().replace("\\", "/")
        if not candidate or candidate in normalized:
            continue
        normalized.append(candidate)
    return normalized


def parse_paths_csv(raw_paths: str) -> list[str]:
    return normalize_path_list([chunk.strip() for chunk in (raw_paths or "").split(",")])


def collect_dirty_paths(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--porcelain"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return []

    dirty_paths: list[str] = []
    for raw_line in completed.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        path_part = line[3:] if len(line) > 3 else line
        if " -> " in path_part:
            path_part = path_part.split(" -> ", maxsplit=1)[1]
        dirty_paths.append(path_part)
    return normalize_path_list(dirty_paths)


def required_specialist_reviewers(
    *,
    repo_root: Path,
    intent: str,
    risk: str,
    paths: list[str],
) -> list[str]:
    try:
        payload = build_route_payload(
            intent=intent or "Revisao especializada obrigatoria",
            paths=paths,
            risk=risk or "medium",
            repo_root=repo_root,
        )
    except FileNotFoundError:
        return []
    required_agents = payload["task_card"]["required_agents"]
    return [agent for agent in required_agents if agent in SPECIALIST_REVIEWERS]


def record_review(
    *,
    review_path: Path,
    worklog_id: str,
    reviewer: str,
    status: str,
    summary: str,
    paths: list[str],
    evidence: str = "",
) -> dict[str, Any]:
    normalized_status = (status or "").strip().lower()
    if normalized_status not in ALLOWED_REVIEW_STATUSES:
        raise ValueError("Status de review invalido. Use aprovado ou reprovado.")
    if reviewer not in SPECIALIST_REVIEWERS:
        raise ValueError("Revisor especializado invalido para este ledger.")

    rows = [
        row
        for row in load_reviews(review_path)
        if not (row["Worklog ID"] == worklog_id and row["Revisor"] == reviewer)
    ]
    rows.insert(
        0,
        {
            "Data/Hora UTC": now_human_utc(),
            "Worklog ID": normalize_cell(worklog_id, max_len=80),
            "Revisor": reviewer,
            "Status": normalized_status,
            "Arquivos": normalize_cell(", ".join(normalize_path_list(paths)), max_len=1000),
            "Resumo": normalize_cell(summary, max_len=220),
            "Evidencia": normalize_cell(evidence, max_len=220),
        },
    )
    save_reviews(review_path, rows)
    return {
        "worklog_id": worklog_id,
        "reviewer": reviewer,
        "status": normalized_status,
        "paths": normalize_path_list(paths),
    }


def latest_reviews_for_worklog(
    review_path: Path,
    *,
    worklog_id: str,
) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in load_reviews(review_path):
        if row["Worklog ID"] != worklog_id:
            continue
        reviewer = row["Revisor"]
        if reviewer in latest:
            continue
        latest[reviewer] = row
    return latest


def check_review_gate(
    *,
    review_path: Path,
    worklog_id: str,
    repo_root: Path = ROOT,
    intent: str = "",
    risk: str = "medium",
    paths: list[str] | None = None,
) -> dict[str, Any]:
    effective_paths = normalize_path_list(paths or []) or collect_dirty_paths(repo_root)
    required = required_specialist_reviewers(
        repo_root=repo_root,
        intent=intent,
        risk=risk,
        paths=effective_paths,
    )
    if not required:
        return {
            "ok": True,
            "required_reviewers": [],
            "paths": effective_paths,
            "errors": [],
        }

    review_map = latest_reviews_for_worklog(review_path, worklog_id=worklog_id)
    reviewer_paths: dict[str, list[str]] = {reviewer: [] for reviewer in required}
    for candidate_path in effective_paths:
        for reviewer in required_specialist_reviewers(
            repo_root=repo_root,
            intent=intent,
            risk=risk,
            paths=[candidate_path],
        ):
            if reviewer in reviewer_paths and candidate_path not in reviewer_paths[reviewer]:
                reviewer_paths[reviewer].append(candidate_path)
    errors: list[str] = []
    for reviewer in required:
        row = review_map.get(reviewer)
        if row is None:
            errors.append(
                f"Parecer especializado ausente para {reviewer} no worklog {worklog_id}."
            )
            continue
        if row["Status"] == "reprovado":
            errors.append(
                f"Parecer especializado reprovado para {reviewer} no worklog {worklog_id}: {row['Resumo']}"
            )
            continue
        if row["Status"] != "aprovado":
            errors.append(
                f"Status invalido de review para {reviewer} no worklog {worklog_id}: {row['Status']}"
            )
            continue
        recorded_paths = parse_paths_csv("" if row["Arquivos"] == "-" else row["Arquivos"])
        missing_paths = [
            candidate_path
            for candidate_path in reviewer_paths.get(reviewer, [])
            if candidate_path not in recorded_paths
        ]
        if missing_paths:
            errors.append(
                f"Parecer aprovado de {reviewer} nao cobre os paths atuais do worklog {worklog_id}: "
                + ", ".join(missing_paths)
            )

    return {
        "ok": not errors,
        "required_reviewers": required,
        "paths": effective_paths,
        "errors": errors,
    }
