from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.ai_control_plane_lib import resolve_repo_root
from scripts.ai_roadmap_lib import (
    BACKLOG_END,
    BACKLOG_HEADERS,
    BACKLOG_START,
    SUGGESTION_HEADERS,
    SUGGESTIONS_END,
    SUGGESTIONS_START,
    extract_between,
    normalize_change_type,
    parse_table,
    today_utc_iso,
)

WIP_DOING_START = "<!-- ai-worklog:doing:start -->"
WIP_DOING_END = "<!-- ai-worklog:doing:end -->"
WIP_DONE_START = "<!-- ai-worklog:done:start -->"
WIP_DONE_END = "<!-- ai-worklog:done:end -->"
WIP_DOING_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Ultima atualizacao UTC",
    "Proximo passo",
    "Bloqueios",
]
WIP_DONE_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Concluido UTC",
    "Resultado",
]
JIRA_SUMMARY_LIMIT = 255

# O tracker local ainda serializa datas tecnicas em UTC. O backfill apenas
# espelha esse contrato atual; a normalizacao para locale de exibicao precisa
# acontecer de forma centralizada no worklog e nos ledgers, nao apenas aqui.


@dataclass(frozen=True)
class BackfillPaths:
    repo_root: Path
    roadmap: Path
    decisions: Path
    wip_tracker: Path
    atlassian_docs_dir: Path


def load_backfill_paths(repo_root: str | Path | None = None) -> BackfillPaths:
    resolved_repo_root = resolve_repo_root(repo_root)
    return BackfillPaths(
        repo_root=resolved_repo_root,
        roadmap=resolved_repo_root / "ROADMAP.md",
        decisions=resolved_repo_root / "docs" / "ROADMAP-DECISIONS.md",
        wip_tracker=resolved_repo_root / "docs" / "AI-WIP-TRACKER.md",
        atlassian_docs_dir=resolved_repo_root / "docs" / "atlassian-ia",
    )


def map_roadmap_type_to_issue_type(change_type: str) -> str:
    normalized = normalize_change_type(change_type)
    if normalized == "fix":
        return "Bug"
    if normalized in {"feat", "research"}:
        return "Story"
    return "Task"


def parse_markdown_table(
    path: Path, start: str, end: str, headers: list[str]
) -> list[dict[str, str]]:
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, start, end, label=str(path))
    return parse_table(section, headers, label=str(path))


def build_seed_activity(
    *,
    agent: str,
    interaction_type: str,
    status: str,
    contexto: list[str],
    evidencias: list[str],
    proximo_passo: str,
) -> dict[str, Any]:
    return {
        "agent": agent,
        "interaction_type": interaction_type,
        "status": status,
        "contexto": [entry for entry in contexto if entry.strip()],
        "evidencias": [entry for entry in evidencias if entry.strip()],
        "proximo_passo": proximo_passo.strip(),
    }


def build_jira_summary(identifier: str, raw_summary: str) -> str:
    prefix = f"[{identifier.strip()}] "
    normalized = " ".join(raw_summary.strip().split())
    limit = JIRA_SUMMARY_LIMIT
    if len(prefix) >= limit:
        return prefix[:limit]
    candidate = f"{prefix}{normalized}"
    if len(candidate) <= limit:
        return candidate
    available = limit - len(prefix)
    if available <= 3:
        return candidate[:limit]
    return f"{prefix}{normalized[: available - 3].rstrip()}..."


def roadmap_backlog_records(paths: BackfillPaths) -> list[dict[str, Any]]:
    rows = parse_markdown_table(paths.roadmap, BACKLOG_START, BACKLOG_END, BACKLOG_HEADERS)
    records: list[dict[str, Any]] = []
    for row in rows:
        item_id = row["ID"].strip()
        if not item_id:
            continue
        records.append(
            {
                "external_id": item_id,
                "origin": "roadmap-backlog",
                "issue_type": map_roadmap_type_to_issue_type(row["Tipo"]),
                "summary": build_jira_summary(item_id, row["Iniciativa"]),
                "state_hint": row["Status"].strip().lower(),
                "labels": [
                    "atlassian-ia",
                    "retro-sync",
                    "roadmap",
                    normalize_change_type(row["Tipo"]),
                ],
                "description_lines": [
                    f"Origem: {paths.roadmap.relative_to(paths.repo_root)}",
                    f"ID local: {item_id}",
                    f"Tipo local: {row['Tipo'].strip()}",
                    f"Status local: {row['Status'].strip()}",
                    "Metricas:",
                    f"- Reach: {row['R'].strip()}",
                    f"- Impact: {row['I'].strip()}",
                    f"- Confidence: {row['C'].strip()}",
                    f"- Effort: {row['E'].strip()}",
                    f"- BV: {row['BV'].strip()}",
                    f"- TC: {row['TC'].strip()}",
                    f"- RR: {row['RR'].strip()}",
                    f"- JS: {row['JS'].strip()}",
                ],
                "seed_activity": build_seed_activity(
                    agent="ai-product-owner",
                    interaction_type="progress-update",
                    status=row["Status"].strip(),
                    contexto=[
                        "Backfill retroativo do backlog local para Jira.",
                        f"Item promovido a partir de {paths.roadmap.relative_to(paths.repo_root)}.",
                    ],
                    evidencias=[
                        str(paths.roadmap.relative_to(paths.repo_root)),
                    ],
                    proximo_passo="Linkar pagina correspondente no Confluence e definir o proximo papel.",
                ),
            }
        )
    return records


def roadmap_suggestion_records(paths: BackfillPaths) -> list[dict[str, Any]]:
    rows = parse_markdown_table(
        paths.decisions,
        SUGGESTIONS_START,
        SUGGESTIONS_END,
        SUGGESTION_HEADERS,
    )
    records: list[dict[str, Any]] = []
    for row in rows:
        suggestion_id = row["ID"].strip()
        if not suggestion_id:
            continue
        status = row["Status"].strip().lower()
        if status not in {"aceita", "pendente"}:
            continue
        change_type = normalize_change_type(row["Tipo"])
        records.append(
            {
                "external_id": suggestion_id,
                "origin": "roadmap-suggestion",
                "issue_type": map_roadmap_type_to_issue_type(change_type),
                "summary": build_jira_summary(suggestion_id, row["Descricao"]),
                "state_hint": "backlog" if status == "aceita" else "triage",
                "labels": [
                    "atlassian-ia",
                    "retro-sync",
                    "roadmap-suggestion",
                    change_type,
                    status,
                ],
                "description_lines": [
                    f"Origem: {paths.decisions.relative_to(paths.repo_root)}",
                    f"ID local: {suggestion_id}",
                    f"Tipo local: {row['Tipo'].strip()}",
                    f"Status local: {row['Status'].strip()}",
                    f"RM vinculado: {row['RM'].strip() or '-'}",
                    f"Captura: {row['Captura'].strip() or '-'}",
                    f"Atualizacao: {row['Atualizacao'].strip() or '-'}",
                ],
                "seed_activity": build_seed_activity(
                    agent="ai-product-owner",
                    interaction_type="progress-update",
                    status=row["Status"].strip(),
                    contexto=[
                        "Backfill retroativo de sugestao ou decisao do roadmap para Jira.",
                        f"Sugestao extraida de {paths.decisions.relative_to(paths.repo_root)}.",
                    ],
                    evidencias=[
                        str(paths.decisions.relative_to(paths.repo_root)),
                    ],
                    proximo_passo="Validar triagem no Jira e linkar documentacao correspondente.",
                ),
            }
        )
    return records


def worklog_records(paths: BackfillPaths, *, done: bool) -> list[dict[str, Any]]:
    start = WIP_DONE_START if done else WIP_DOING_START
    end = WIP_DONE_END if done else WIP_DOING_END
    headers = WIP_DONE_HEADERS if done else WIP_DOING_HEADERS
    rows = parse_markdown_table(paths.wip_tracker, start, end, headers)
    records: list[dict[str, Any]] = []
    for row in rows:
        worklog_id = row["ID"].strip()
        if not worklog_id:
            continue
        summary = row["Tarefa"].strip()
        state_hint = "done" if done else "doing"
        description_lines = [
            f"Origem: {paths.wip_tracker.relative_to(paths.repo_root)}",
            f"Worklog local: {worklog_id}",
            f"Branch: {row['Branch'].strip()}",
            f"Responsavel: {row['Responsavel'].strip()}",
            f"Inicio UTC: {row['Inicio UTC'].strip()}",
        ]
        if done:
            description_lines.extend(
                [
                    f"Concluido UTC: {row['Concluido UTC'].strip()}",
                    "Resultado:",
                    row["Resultado"].strip(),
                ]
            )
        else:
            description_lines.extend(
                [
                    f"Ultima atualizacao UTC: {row['Ultima atualizacao UTC'].strip()}",
                    f"Proximo passo: {row['Proximo passo'].strip()}",
                    f"Bloqueios: {row['Bloqueios'].strip()}",
                ]
            )
        records.append(
            {
                "external_id": worklog_id,
                "origin": "wip-done" if done else "wip-doing",
                "issue_type": "Task",
                "summary": build_jira_summary(worklog_id, summary),
                "state_hint": state_hint,
                "labels": [
                    "atlassian-ia",
                    "retro-sync",
                    "worklog",
                    state_hint,
                ],
                "description_lines": description_lines,
                "seed_activity": build_seed_activity(
                    agent="ai-documentation-agent",
                    interaction_type="progress-update",
                    status=state_hint,
                    contexto=[
                        "Backfill retroativo do worklog local para Jira.",
                        f"Registro espelhado de {paths.wip_tracker.relative_to(paths.repo_root)}.",
                    ],
                    evidencias=[
                        str(paths.wip_tracker.relative_to(paths.repo_root)),
                    ],
                    proximo_passo="Confirmar vinculo com a pagina correspondente no Confluence.",
                ),
            }
        )
    return records


def confluence_snapshot_pages(paths: BackfillPaths) -> list[dict[str, Any]]:
    source_paths = [
        paths.repo_root / "ROADMAP.md",
        paths.repo_root / "docs" / "ROADMAP-DECISIONS.md",
        paths.repo_root / "docs" / "AI-WIP-TRACKER.md",
    ]
    source_paths.extend(sorted(paths.atlassian_docs_dir.glob("*.md")))
    pages: list[dict[str, Any]] = []
    for source_path in source_paths:
        relative = source_path.relative_to(paths.repo_root)
        pages.append(
            {
                "title": f"SYNC :: {relative.as_posix()}",
                "source_path": relative.as_posix(),
            }
        )
    return pages


def build_backfill_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    paths = load_backfill_paths(repo_root)
    backlog = roadmap_backlog_records(paths)
    suggestions = roadmap_suggestion_records(paths)
    doing = worklog_records(paths, done=False)
    done = worklog_records(paths, done=True)
    pages = confluence_snapshot_pages(paths)
    return {
        "metadata": {
            "generated_on": today_utc_iso(),
            "repo_root": str(paths.repo_root),
            "timestamp_policy": {
                "source_tracker_timezone": "UTC",
                "jira_export_policy": "preserve-source-audit-timestamps",
                "display_locale_policy": "pending-central-normalization",
            },
        },
        "jira": {
            "roadmap_backlog": backlog,
            "roadmap_suggestions": suggestions,
            "worklog_doing": doing,
            "worklog_done": done,
            "counts": {
                "roadmap_backlog": len(backlog),
                "roadmap_suggestions": len(suggestions),
                "worklog_doing": len(doing),
                "worklog_done": len(done),
                "total_records": len(backlog) + len(suggestions) + len(doing) + len(done),
            },
        },
        "confluence": {
            "snapshot_pages": pages,
            "count": len(pages),
        },
    }
