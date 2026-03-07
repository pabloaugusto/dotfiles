from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

CATALOG_START = "<!-- ai-lessons:catalog:start -->"
CATALOG_END = "<!-- ai-lessons:catalog:end -->"
REVIEWS_START = "<!-- ai-lessons:reviews:start -->"
REVIEWS_END = "<!-- ai-lessons:reviews:end -->"
REVIEW_HEADERS = [
    "Data/Hora UTC",
    "Worklog ID",
    "Decisao",
    "Resumo",
    "Licoes",
    "Evidencia",
]
DONE_START = "<!-- ai-worklog:done:start -->"
DONE_END = "<!-- ai-worklog:done:end -->"
DONE_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Concluido UTC",
    "Resultado",
]
REVIEW_DECISIONS = {"capturada", "sem_nova_licao"}


def now_human_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def write_text_lf(path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalized)


def normalize_cell(value: str, *, max_len: int = 220) -> str:
    compact = " ".join((value or "").split()).replace("|", "/")
    if not compact:
        return "-"
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3].rstrip() + "..."


def parse_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise ValueError(f"Linha de tabela invalida: {line}")
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def render_table(headers: list[str], rows: list[dict[str, str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    if rows:
        for row in rows:
            lines.append("| " + " | ".join(row.get(header, "-") for header in headers) + " |")
    else:
        lines.append("| " + " | ".join(["(sem itens)"] + ["-"] * (len(headers) - 1)) + " |")
    return "\n".join(lines)


def extract_between(text: str, start: str, end: str, *, label: str) -> str:
    start_idx = text.find(start)
    if start_idx < 0:
        raise ValueError(f"Marcador ausente ({start}) em {label}")
    end_idx = text.find(end, start_idx + len(start))
    if end_idx < 0:
        raise ValueError(f"Marcador ausente ({end}) em {label}")
    return text[start_idx + len(start) : end_idx]


def replace_between(text: str, start: str, end: str, replacement: str, *, label: str) -> str:
    start_idx = text.find(start)
    if start_idx < 0:
        raise ValueError(f"Marcador ausente ({start}) em {label}")
    end_idx = text.find(end, start_idx + len(start))
    if end_idx < 0:
        raise ValueError(f"Marcador ausente ({end}) em {label}")
    return text[: start_idx + len(start)] + "\n" + replacement.strip("\n") + "\n" + text[end_idx:]


def parse_table(section: str, headers: list[str], *, label: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if not lines:
        return []
    if parse_row(lines[0]) != headers:
        raise ValueError(f"Cabecalho inesperado em {label}")
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        values = parse_row(line)
        if values[0] == "(sem itens)":
            continue
        rows.append({headers[idx]: values[idx] for idx in range(len(headers))})
    return rows


def lesson_template() -> str:
    return f"""# Licoes Aprendidas

Historico incremental das regras operacionais que nao devem depender de memoria de chat.

## Leitura obrigatoria

- A cada novo comando do usuario, a IA deve ler:
  - `AGENTS.md`
  - `LICOES-APRENDIDAS.md`
- Em caso de conflito entre regra normativa e licao operacional, prevalece o `AGENTS.md`.

## Criterio de registro de novas licoes

- Registrar somente quando houver ganho real de eficiencia, qualidade, resiliencia ou precisao.
- Priorizar recorrencias, incidentes relevantes, workarounds comprovados e decisoes que reduzam drift.
- Cada licao deve ser curta, verificavel e acionavel.

## Formato recomendado de entrada

- `ID`: identificador curto, por exemplo `LA-004`
- `Contexto`: onde o problema apareceu
- `Regra`: comportamento que passa a ser obrigatorio
- `Solucao validada`: o que efetivamente resolveu
- `Prevencao`: como evitar a regressao
- `Validacao`: comandos, testes ou gates usados

## Curadoria e manutencao

- Evitar duplicacoes; consolidar licoes equivalentes.
- Promover para `AGENTS.md` apenas regras estaveis e amplas.
- Manter aqui os detalhes operacionais e a memoria incremental das rodadas.

## Catalogo de licoes

<!-- ai-lessons:catalog:start -->
<!-- ai-lessons:catalog:end -->

## Revisoes de rodadas

Toda finalizacao de worklog deve registrar se houve nova licao.

<!-- ai-lessons:reviews:start -->
{render_table(REVIEW_HEADERS, [])}
<!-- ai-lessons:reviews:end -->
"""


def ensure_lessons_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(path, lesson_template())


def load_reviews(path: Path) -> list[dict[str, str]]:
    ensure_lessons_file(path)
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, REVIEWS_START, REVIEWS_END, label=str(path))
    return parse_table(section, REVIEW_HEADERS, label=str(path))


def save_reviews(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_lessons_file(path)
    raw = path.read_text(encoding="utf-8")
    updated = replace_between(
        raw, REVIEWS_START, REVIEWS_END, render_table(REVIEW_HEADERS, rows), label=str(path)
    )
    write_text_lf(path, updated)


def list_catalog_ids(path: Path) -> list[str]:
    ensure_lessons_file(path)
    raw = path.read_text(encoding="utf-8")
    catalog = extract_between(raw, CATALOG_START, CATALOG_END, label=str(path))
    return re.findall(r"(?m)^## (LA-\d+) - ", catalog)


def next_lesson_id(path: Path) -> str:
    numeric_ids = []
    for lesson_id in list_catalog_ids(path):
        try:
            numeric_ids.append(int(lesson_id.split("-", 1)[1]))
        except ValueError:
            continue
    next_number = (max(numeric_ids) if numeric_ids else 0) + 1
    return f"LA-{next_number:03d}"


def add_lesson(
    *,
    path: Path,
    lesson_id: str,
    title: str,
    context: str,
    rule: str,
    validated_solution: str,
    prevention: str,
    validation: str,
    related_worklog: str = "",
    source_repos: list[str] | None = None,
) -> None:
    ensure_lessons_file(path)
    raw = path.read_text(encoding="utf-8")
    catalog = extract_between(raw, CATALOG_START, CATALOG_END, label=str(path)).strip()
    existing_ids = set(list_catalog_ids(path))
    if lesson_id in existing_ids:
        raise ValueError(f"Licao ja existente: {lesson_id}")
    source_text = ""
    if source_repos:
        source_text = f"\n- Fontes relacionadas: {', '.join(source_repos)}"
    worklog_text = ""
    if related_worklog:
        worklog_text = f"\n- Worklog relacionado: `{related_worklog}`"
    block = (
        f"## {lesson_id} - {title}\n\n"
        f"- Contexto: {context}\n"
        f"- Regra: {rule}\n"
        f"- Solucao validada: {validated_solution}\n"
        f"- Prevencao: {prevention}\n"
        f"- Validacao: {validation}"
        f"{worklog_text}"
        f"{source_text}\n"
    )
    new_catalog = block if not catalog else catalog + "\n\n" + block
    updated = replace_between(raw, CATALOG_START, CATALOG_END, new_catalog, label=str(path))
    write_text_lf(path, updated)


def normalize_lesson_ids(raw_ids: str) -> list[str]:
    values = [item.strip() for item in raw_ids.split(",") if item.strip()]
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return deduped


def upsert_review(
    *,
    path: Path,
    worklog_id: str,
    decision: str,
    summary: str,
    lesson_ids: list[str] | None = None,
    evidence: str = "",
) -> None:
    ensure_lessons_file(path)
    validate_review_request(
        path=path, decision=decision, summary=summary, lesson_ids=lesson_ids or []
    )
    rows = [row for row in load_reviews(path) if row["Worklog ID"] != worklog_id]
    rows.insert(
        0,
        {
            "Data/Hora UTC": now_human_utc(),
            "Worklog ID": normalize_cell(worklog_id, max_len=80),
            "Decisao": decision.strip(),
            "Resumo": normalize_cell(summary, max_len=220),
            "Licoes": ", ".join(lesson_ids or []) if lesson_ids else "-",
            "Evidencia": normalize_cell(evidence, max_len=220),
        },
    )
    save_reviews(path, rows)


def validate_review_request(
    *, path: Path, decision: str, summary: str, lesson_ids: list[str]
) -> None:
    ensure_lessons_file(path)
    decision_value = (decision or "").strip()
    if decision_value not in REVIEW_DECISIONS:
        raise ValueError("Decisao de licoes invalida. Use capturada ou sem_nova_licao.")
    if normalize_cell(summary, max_len=220) == "-":
        raise ValueError("Resumo de revisao de licoes nao pode ser vazio.")
    if decision_value == "capturada" and not lesson_ids:
        raise ValueError("Informe pelo menos uma licao quando a decisao for capturada.")
    catalog_ids = set(list_catalog_ids(path))
    missing_ids = [item for item in lesson_ids if item not in catalog_ids]
    if missing_ids:
        raise ValueError("Licoes inexistentes para a revisao: " + ", ".join(missing_ids))


def load_done_worklog_ids(tracker_path: Path) -> list[str]:
    raw = tracker_path.read_text(encoding="utf-8")
    done_section = extract_between(raw, DONE_START, DONE_END, label=str(tracker_path))
    rows = parse_table(done_section, DONE_HEADERS, label=str(tracker_path))
    return [row["ID"] for row in rows]


def check_reviews(*, tracker_path: Path, lessons_path: Path) -> list[str]:
    ensure_lessons_file(lessons_path)
    failures: list[str] = []
    done_ids = load_done_worklog_ids(tracker_path)
    reviews = load_reviews(lessons_path)
    review_map = {row["Worklog ID"]: row for row in reviews}
    catalog_ids = set(list_catalog_ids(lessons_path))

    for worklog_id in done_ids:
        if worklog_id not in review_map:
            failures.append(f"Worklog concluido sem revisao de licoes: {worklog_id}")
            continue
        row = review_map[worklog_id]
        decision = row["Decisao"]
        summary = row["Resumo"]
        if decision not in REVIEW_DECISIONS:
            failures.append(f"Decisao de licoes invalida para {worklog_id}: {decision}")
        if summary in {"", "-"}:
            failures.append(f"Resumo de revisao ausente para {worklog_id}")
        lesson_ids = normalize_lesson_ids("" if row["Licoes"] == "-" else row["Licoes"])
        if decision == "capturada" and not lesson_ids:
            failures.append(f"Worklog {worklog_id} marcou capturada sem licoes vinculadas")
        for lesson_id in lesson_ids:
            if lesson_id not in catalog_ids:
                failures.append(f"Worklog {worklog_id} referencia licao inexistente: {lesson_id}")

    return failures


def sync_reviews(path: Path) -> None:
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in load_reviews(path):
        worklog_id = row["Worklog ID"]
        if worklog_id in seen:
            continue
        deduped.append(row)
        seen.add(worklog_id)
    save_reviews(path, deduped)
