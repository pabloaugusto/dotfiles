from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.ai_control_plane_lib import (
    github_blob_url,
    linkify_repo_relative_paths,
    resolve_repo_root,
)
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
from scripts.atlassian_platform_lib import canonicalize_workflow_status

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
JIRA_SUMMARY_LIMIT = 96
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`]*)`")

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
        "status": canonicalize_workflow_status(status) or str(status).strip(),
        "contexto": [entry for entry in contexto if entry.strip()],
        "evidencias": [entry for entry in evidencias if entry.strip()],
        "proximo_passo": proximo_passo.strip(),
    }


def strip_markdown_syntax(text: str) -> str:
    normalized = MARKDOWN_LINK_RE.sub(lambda match: match.group(1), text)
    normalized = INLINE_CODE_RE.sub(lambda match: match.group(1), normalized)
    normalized = normalized.replace("**", "").replace("__", "")
    return " ".join(normalized.split())


def build_jira_summary(identifier: str, raw_summary: str) -> str:
    del identifier
    normalized = strip_markdown_syntax(raw_summary)
    if not normalized:
        normalized = "Item importado do backlog local"
    if len(normalized) <= JIRA_SUMMARY_LIMIT:
        return normalized
    separators = (": ", " - ", "; ", ", ", " para ", " com ")
    best_candidate = ""
    for separator in separators:
        head, separator_found, _tail = normalized.partition(separator)
        candidate = head.strip() if separator_found else ""
        if 45 <= len(candidate) <= JIRA_SUMMARY_LIMIT:
            best_candidate = candidate
            break
    if best_candidate:
        return best_candidate
    return f"{normalized[: JIRA_SUMMARY_LIMIT - 3].rstrip()}..."


def infer_priority(*, external_id: str, issue_type: str, summary: str, state_hint: str) -> str:
    normalized_id = external_id.strip().upper()
    normalized_summary = strip_markdown_syntax(summary).casefold()
    normalized_state = state_hint.strip().casefold()
    if normalized_state == "doing":
        return "High"
    if normalized_id.startswith("SG-ORTHO"):
        return "Low"
    if issue_type.strip() == "Bug":
        return "High"
    critical_tokens = (
        "auth",
        "board",
        "bootstrap",
        "1password",
        "ssh",
        "sign",
        "secret",
        "security",
        "workflow",
    )
    if any(token in normalized_summary for token in critical_tokens):
        return "High"
    return "Medium"


def infer_components(*, summary: str, origin: str) -> list[str]:
    normalized_summary = strip_markdown_syntax(summary).casefold()
    components = ["ai-control-plane"]
    keyword_map = {
        "documentation-governance": ("doc", "docs", "document", "confluence"),
        "bootstrap": ("bootstrap",),
        "secrets": ("secret", "1password", "ssh", "signing", "token", "credential"),
        "ci": ("ci", "workflow", "pipeline", "github actions"),
        "cross-platform": ("windows", "linux", "wsl", "cross-platform"),
        "developer-experience": ("review", "reviewer", "workspace", "vscode", "developer"),
    }
    for component_name, tokens in keyword_map.items():
        if any(token in normalized_summary for token in tokens):
            components.append(component_name)
    if origin.startswith("wip-") and "documentation-governance" not in components:
        components.append("documentation-governance")
    deduped: list[str] = []
    for entry in components:
        if entry not in deduped:
            deduped.append(entry)
    return deduped


def build_description_sections(sections: list[tuple[str, list[str]]]) -> list[str]:
    lines: list[str] = []
    for title, values in sections:
        filtered = [
            strip_markdown_syntax(value) for value in values if strip_markdown_syntax(value)
        ]
        if not filtered:
            continue
        if lines:
            lines.append("")
        lines.append(f"## {title}")
        lines.extend(f"- {value}" for value in filtered)
    return lines


def build_story_statement(summary: str) -> str:
    normalized = strip_markdown_syntax(summary).strip()
    if not normalized:
        normalized = "evoluir o backlog oficial"
    return (
        "Como time responsavel pelo control plane autonomo, "
        f"queremos {normalized.casefold()}, para manter a entrega clara, rastreavel e priorizavel."
    )


def build_resultado_esperado(issue_type: str, summary: str) -> list[str]:
    normalized = strip_markdown_syntax(summary).strip()
    if issue_type == "Bug":
        return [f"A falha relacionada a '{normalized}' deixa de afetar o fluxo esperado."]
    if issue_type == "Story":
        return [
            f"A historia '{normalized}' fica pronta para entrega e validacao pelos papeis seguintes."
        ]
    return [
        f"O trabalho necessario para '{normalized}' fica concluido com rastreabilidade operacional."
    ]


def build_acceptance_criteria(
    *,
    issue_type: str,
    state_hint: str,
    references_expected: bool = True,
) -> list[str]:
    normalized_issue_type = issue_type.strip()
    normalized_state = state_hint.strip().casefold()
    criteria = [
        "O escopo desta demanda esta claro e consistente com o contexto registrado.",
        "Existe evidencia objetiva do trabalho executado ou n/a explicito quando a prova nao se aplica.",
    ]
    if normalized_issue_type == "Story":
        criteria.insert(
            0,
            "O valor esperado da historia pode ser entendido por uma pessoa leitora sem depender do contexto do chat.",
        )
    if normalized_issue_type == "Bug":
        criteria.insert(
            0,
            "O problema observado pode ser reproduzido antes da correcao e deixa de ocorrer depois da validacao.",
        )
    if normalized_state in {"doing", "done"}:
        criteria.append("O status e o proximo papel no Jira refletem a etapa real do trabalho.")
    else:
        criteria.append("A demanda ficou pronta para refinement sem perder contexto ou prioridade.")
    if references_expected:
        criteria.append(
            "As referencias relevantes ficaram registradas na issue e, quando aplicavel, linkadas ao Confluence."
        )
    return criteria


def build_reference_lines(
    *,
    source_path: Path,
    repo_root: Path,
    external_id: str,
    extras: list[str] | None = None,
) -> list[str]:
    repo_relative_source = source_path.relative_to(repo_root).as_posix()
    lines = [
        f"Artefato de origem no GitHub: {github_blob_url(repo_root, repo_relative_source)}",
        f"Identificador local: {external_id}",
    ]
    for entry in extras or []:
        normalized = linkify_repo_relative_paths(
            strip_markdown_syntax(entry),
            repo_root=repo_root,
        )
        if normalized:
            lines.append(normalized)
    return lines


def build_narrative_description(
    *,
    issue_type: str,
    summary: str,
    contexto: list[str],
    referencias: list[str],
    state_hint: str,
    historia: str = "",
    escopo_tecnico: list[str] | None = None,
    problema_observado: list[str] | None = None,
    impacto: list[str] | None = None,
) -> list[str]:
    sections: list[tuple[str, list[str]]] = []
    normalized_issue_type = issue_type.strip()
    if normalized_issue_type == "Story":
        sections.append(("Historia", [historia or build_story_statement(summary)]))
    if normalized_issue_type == "Bug":
        sections.append(("Problema observado", problema_observado or [summary]))
        if impacto:
            sections.append(("Impacto", impacto))
    sections.append(("Contexto", contexto))
    sections.append(
        ("Resultado esperado", build_resultado_esperado(normalized_issue_type, summary))
    )
    if normalized_issue_type in {"Task", "Sub-task"} and escopo_tecnico:
        sections.append(("Escopo tecnico", escopo_tecnico))
    sections.append(
        (
            "Criterios de aceite",
            build_acceptance_criteria(
                issue_type=normalized_issue_type,
                state_hint=state_hint,
            ),
        )
    )
    sections.append(("Referencias", referencias))
    return build_description_sections(sections)


def roadmap_backlog_records(paths: BackfillPaths) -> list[dict[str, Any]]:
    rows = parse_markdown_table(paths.roadmap, BACKLOG_START, BACKLOG_END, BACKLOG_HEADERS)
    records: list[dict[str, Any]] = []
    for row in rows:
        item_id = row["ID"].strip()
        if not item_id:
            continue
        issue_type = map_roadmap_type_to_issue_type(row["Tipo"])
        records.append(
            {
                "external_id": item_id,
                "origin": "roadmap-backlog",
                "issue_type": issue_type,
                "summary": build_jira_summary(item_id, row["Iniciativa"]),
                "state_hint": row["Status"].strip().lower(),
                "priority": infer_priority(
                    external_id=item_id,
                    issue_type=issue_type,
                    summary=row["Iniciativa"],
                    state_hint=row["Status"],
                ),
                "components": infer_components(
                    summary=row["Iniciativa"],
                    origin="roadmap-backlog",
                ),
                "labels": [
                    "atlassian-ia",
                    "retro-sync",
                    "roadmap",
                    normalize_change_type(row["Tipo"]),
                ],
                "description_lines": build_narrative_description(
                    issue_type=issue_type,
                    summary=row["Iniciativa"],
                    state_hint=row["Status"],
                    historia=(
                        build_story_statement(row["Iniciativa"]) if issue_type == "Story" else ""
                    ),
                    contexto=[
                        "Demanda importada do roadmap local para manter o Jira como backlog oficial do trabalho.",
                        f"Tipo local classificado como {row['Tipo'].strip()}.",
                        f"Estado atual no roadmap local: {row['Status'].strip()}.",
                    ],
                    escopo_tecnico=[
                        "Consolidar o objetivo da demanda com prioridade, plataforma afetada e proximo handoff.",
                        "Usar os sinais de priorizacao abaixo para orientar refinement e ordem de execucao.",
                        f"Reach: {row['R'].strip()} | Impact: {row['I'].strip()} | Confidence: {row['C'].strip()} | Effort: {row['E'].strip()}",
                        f"Business value: {row['BV'].strip()} | Time criticality: {row['TC'].strip()} | Risk reduction: {row['RR'].strip()} | Job size: {row['JS'].strip()}",
                    ],
                    referencias=build_reference_lines(
                        source_path=paths.roadmap,
                        repo_root=paths.repo_root,
                        external_id=item_id,
                        extras=[
                            f"Tipo local: {row['Tipo'].strip()}",
                            "Sinais de priorizacao consolidados no roadmap para este item.",
                        ],
                    ),
                ),
                "seed_activity": build_seed_activity(
                    agent="ai-product-owner",
                    interaction_type="progress-update",
                    status=row["Status"].strip().lower(),
                    contexto=[
                        "Backfill retroativo do backlog local para Jira com titulo sintetizado e descricao orientada a leitura humana.",
                        "Item promovido a partir do roadmap versionado no GitHub.",
                    ],
                    evidencias=[
                        github_blob_url(
                            paths.repo_root,
                            paths.roadmap.relative_to(paths.repo_root).as_posix(),
                        ),
                    ],
                    proximo_passo="Linkar a documentacao correspondente no Confluence, revisar a prioridade final e definir o proximo papel.",
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
        issue_type = map_roadmap_type_to_issue_type(change_type)
        records.append(
            {
                "external_id": suggestion_id,
                "origin": "roadmap-suggestion",
                "issue_type": issue_type,
                "summary": build_jira_summary(suggestion_id, row["Descricao"]),
                "state_hint": "backlog" if status == "aceita" else "triage",
                "priority": infer_priority(
                    external_id=suggestion_id,
                    issue_type=issue_type,
                    summary=row["Descricao"],
                    state_hint=status,
                ),
                "components": infer_components(
                    summary=row["Descricao"],
                    origin="roadmap-suggestion",
                ),
                "labels": [
                    "atlassian-ia",
                    "retro-sync",
                    "roadmap-suggestion",
                    change_type,
                    status,
                ],
                "description_lines": build_narrative_description(
                    issue_type=issue_type,
                    summary=row["Descricao"],
                    state_hint="backlog" if status == "aceita" else "triage",
                    historia=(
                        build_story_statement(row["Descricao"]) if issue_type == "Story" else ""
                    ),
                    contexto=[
                        "Sugestao ou decisao do roadmap promovida para o backlog oficial do Jira.",
                        f"Situacao local no ledger de decisoes: {row['Status'].strip()}.",
                        f"Tipo local classificado como {row['Tipo'].strip()}.",
                    ],
                    escopo_tecnico=[
                        "Validar a necessidade real da demanda, seu encaixe no roadmap e a melhor quebra de execucao.",
                        "Transformar a sugestao em trabalho rastreavel, com links e criterios de aceite suficientes para refinement.",
                    ],
                    referencias=build_reference_lines(
                        source_path=paths.decisions,
                        repo_root=paths.repo_root,
                        external_id=suggestion_id,
                        extras=[
                            f"RM vinculado: {row['RM'].strip() or 'n/a'}",
                            f"Captura: {row['Captura'].strip() or 'n/a'}",
                            f"Atualizacao: {row['Atualizacao'].strip() or 'n/a'}",
                        ],
                    ),
                ),
                "seed_activity": build_seed_activity(
                    agent="ai-product-owner",
                    interaction_type="progress-update",
                    status="backlog",
                    contexto=[
                        "Backfill retroativo de sugestao ou decisao do roadmap para Jira, com descricao preparada para leitura humana.",
                        "Sugestao extraida do ledger de decisoes versionado no GitHub.",
                    ],
                    evidencias=[
                        github_blob_url(
                            paths.repo_root,
                            paths.decisions.relative_to(paths.repo_root).as_posix(),
                        ),
                    ],
                    proximo_passo="Refinar a demanda no Jira, linkar a documentacao correspondente e decidir se a quebra em subtarefas ja e necessaria.",
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
        timeline_lines = [
            f"Branch ativa: {row['Branch'].strip()}",
            f"Responsavel no tracker local: {row['Responsavel'].strip()}",
            f"Inicio tecnico em UTC: {row['Inicio UTC'].strip()}",
        ]
        if done:
            timeline_lines.extend(
                [
                    f"Concluido tecnico em UTC: {row['Concluido UTC'].strip()}",
                    f"Resultado resumido: {row['Resultado'].strip()}",
                ]
            )
        else:
            timeline_lines.extend(
                [
                    f"Ultima atualizacao tecnica em UTC: {row['Ultima atualizacao UTC'].strip()}",
                    f"Proximo passo registrado: {row['Proximo passo'].strip()}",
                    f"Bloqueios registrados: {row['Bloqueios'].strip()}",
                ]
            )
        records.append(
            {
                "external_id": worklog_id,
                "origin": "wip-done" if done else "wip-doing",
                "issue_type": "Task",
                "summary": build_jira_summary(worklog_id, summary),
                "state_hint": state_hint,
                "priority": infer_priority(
                    external_id=worklog_id,
                    issue_type="Task",
                    summary=summary,
                    state_hint=state_hint,
                ),
                "components": infer_components(
                    summary=summary,
                    origin="wip-done" if done else "wip-doing",
                ),
                "labels": [
                    "atlassian-ia",
                    "retro-sync",
                    "worklog",
                    state_hint,
                ],
                "description_lines": build_narrative_description(
                    issue_type="Task",
                    summary=summary,
                    state_hint=state_hint,
                    contexto=[
                        "Registro espelhado do tracker operacional de IA para manter o Jira alinhado ao estado real da execucao.",
                        (
                            "O item ainda esta em andamento e precisa continuar refletindo progresso, bloqueios e proximo passo."
                            if not done
                            else "O item foi concluido localmente e fica registrado no Jira para auditoria e retroativo."
                        ),
                    ],
                    escopo_tecnico=timeline_lines,
                    referencias=build_reference_lines(
                        source_path=paths.wip_tracker,
                        repo_root=paths.repo_root,
                        external_id=worklog_id,
                    ),
                ),
                "seed_activity": build_seed_activity(
                    agent="ai-documentation-sync",
                    interaction_type="progress-update",
                    status=state_hint,
                    contexto=[
                        "Backfill retroativo do worklog local para Jira com estado refletindo a operacao real.",
                        "Registro espelhado do tracker operacional versionado no GitHub, com rastreabilidade cross-surface quando aplicavel.",
                    ],
                    evidencias=[
                        github_blob_url(
                            paths.repo_root,
                            paths.wip_tracker.relative_to(paths.repo_root).as_posix(),
                        ),
                    ],
                    proximo_passo="Confirmar backlinks ou documentation-link quando houver superficie remota elegivel e manter o status do Jira alinhado ao trabalho real.",
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
