from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

BACKLOG_START = "<!-- roadmap:backlog:start -->"
BACKLOG_END = "<!-- roadmap:backlog:end -->"
PRIORITY_START = "<!-- roadmap:priority:start -->"
PRIORITY_END = "<!-- roadmap:priority:end -->"
NOW_START = "<!-- roadmap:now:start -->"
NOW_END = "<!-- roadmap:now:end -->"
NEXT_START = "<!-- roadmap:next:start -->"
NEXT_END = "<!-- roadmap:next:end -->"
LATER_START = "<!-- roadmap:later:start -->"
LATER_END = "<!-- roadmap:later:end -->"
PENDING_START = "<!-- roadmap:pending:start -->"
PENDING_END = "<!-- roadmap:pending:end -->"
SUGGESTIONS_START = "<!-- roadmap:suggestions:start -->"
SUGGESTIONS_END = "<!-- roadmap:suggestions:end -->"
CYCLES_START = "<!-- roadmap:cycles:start -->"
CYCLES_END = "<!-- roadmap:cycles:end -->"
AUTOLOG_START = "<!-- roadmap:autolog:start -->"
AUTOLOG_END = "<!-- roadmap:autolog:end -->"

BACKLOG_HEADERS = [
    "ID",
    "Iniciativa",
    "R",
    "I",
    "C",
    "E",
    "BV",
    "TC",
    "RR",
    "JS",
    "Status",
]
SUGGESTION_HEADERS = ["ID", "Descricao", "Status", "RM", "Captura", "Atualizacao"]

LIST_MARKERS = {
    "now": (NOW_START, NOW_END),
    "next": (NEXT_START, NEXT_END),
    "later": (LATER_START, LATER_END),
    "pending": (PENDING_START, PENDING_END),
}

DECISION_TO_STATUS = {
    "accepted": "aceita",
    "pending": "pendente",
    "discarded": "descartada",
}
ALLOWED_DECISIONS = set(DECISION_TO_STATUS)
ALLOWED_HORIZONS = {"now", "next", "later"}
ALLOWED_SUGGESTION_STATUSES = {"pendente", "aceita", "descartada", "aplicar_depois"}
INACTIVE_BACKLOG_STATUSES = {
    "done",
    "concluido",
    "concluida",
    "cancelado",
    "cancelada",
    "descartado",
    "descartada",
}


@dataclass(frozen=True)
class RoadmapItem:
    item_id: str
    initiative: str
    reach: float
    impact: float
    confidence: float
    effort: float
    business_value: float
    time_criticality: float
    risk_reduction: float
    job_size: float
    status: str

    @property
    def rice(self) -> float:
        if self.effort <= 0:
            return 0.0
        return (self.reach * self.impact * self.confidence) / self.effort

    @property
    def wsjf(self) -> float:
        if self.job_size <= 0:
            return 0.0
        return (self.business_value + self.time_criticality + self.risk_reduction) / self.job_size

    @property
    def is_active(self) -> bool:
        return normalize_text(self.status) not in INACTIVE_BACKLOG_STATUSES


def now_human_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def today_utc_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def current_cycle_utc() -> str:
    now = datetime.now(timezone.utc)
    quarter = ((now.month - 1) // 3) + 1
    return f"{now.year}-Q{quarter}"


def write_text_lf(path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalized)


def normalize_text(value: str) -> str:
    plain = value or ""
    plain = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", plain)
    plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", plain)
    plain = plain.replace("`", "")
    return " ".join(plain.strip().lower().split())


def normalize_cell(value: str, *, max_len: int = 220) -> str:
    compact = " ".join((value or "").split()).replace("|", "/")
    if not compact:
        return "-"
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3].rstrip() + "..."


def semantic_entry_key(value: str) -> str:
    base = (value or "").split("| notas=", 1)[0].strip()
    normalized = normalize_text(base)
    if normalized.endswith("..."):
        return normalized[:-3].rstrip()
    return normalized


def semantic_entries_match(left: str, right: str) -> bool:
    left_key = semantic_entry_key(left)
    right_key = semantic_entry_key(right)
    if not left_key or not right_key:
        return False
    return (
        left_key == right_key
        or left_key.startswith(right_key)
        or right_key.startswith(left_key)
        or left_key in right_key
        or right_key in left_key
    )


def parse_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise ValueError(f"Linha de tabela invalida: {line}")
    return [cell.strip() for cell in stripped.strip("|").split("|")]


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


def parse_list_section(section: str) -> list[str]:
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()
        if item and item != "(sem itens)":
            items.append(item)
    return items


def render_list_section(items: list[str]) -> str:
    if not items:
        return "- (sem itens)"
    return "\n".join(f"- {item}" for item in items)


def roadmap_template() -> str:
    updated_at = now_human_utc()
    cycle = current_cycle_utc()
    return f"""# Roadmap do Repositorio

Atualizado em: {updated_at}
Ciclo ativo: {cycle}

Planejamento incremental para qualidade, testes, bootstrap e governanca do repo.

## Guardrails

- Toda sugestao aceita deve gerar rastreabilidade no mesmo ciclo.
- Pendencias mantidas devem aparecer em `docs/AI-WIP-TRACKER.md` e no roadmap.
- Priorizacao automatica ajuda a ordenar, mas a decisao final continua humana.

## Backlog Mestre

Edite apenas a tabela entre os marcadores abaixo.

<!-- roadmap:backlog:start -->
| ID | Iniciativa | R | I | C | E | BV | TC | RR | JS | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RM-001 | Harness Linux para bootstrap e relink | 400 | 2.6 | 0.8 | 8 | 8 | 7 | 6 | 5 | proposed |
| RM-002 | Harness Windows real em CI | 380 | 2.8 | 0.7 | 13 | 9 | 8 | 7 | 8 | proposed |
| RM-003 | Governanca de worklog e roadmap com enforcement | 320 | 2.4 | 0.85 | 5 | 9 | 7 | 8 | 4 | in_progress |
<!-- roadmap:backlog:end -->

## Priorizacao Automatica

Atualizada por `task ai:roadmap:refresh`.

<!-- roadmap:priority:start -->
Execute `task ai:roadmap:refresh` para gerar a priorizacao inicial.
<!-- roadmap:priority:end -->

## Horizonte de Entrega

### Now

<!-- roadmap:now:start -->
- (sem itens)
<!-- roadmap:now:end -->

### Next

<!-- roadmap:next:start -->
- (sem itens)
<!-- roadmap:next:end -->

### Later

<!-- roadmap:later:start -->
- (sem itens)
<!-- roadmap:later:end -->

## Sugestoes pendentes de decisao

<!-- roadmap:pending:start -->
- (sem itens)
<!-- roadmap:pending:end -->

## Riscos e bloqueios

- Registrar riscos ativos, impacto e mitigacao.
"""


def decisions_template() -> str:
    updated_at = now_human_utc()
    cycle = current_cycle_utc()
    return f"""# Decisoes do Roadmap

Atualizado em: {updated_at}
Ciclo ativo: {cycle}

Registro das decisoes humanas por ciclo e governanca de sugestoes.

## Registro de Sugestoes

Use status: `pendente`, `aceita`, `descartada`, `aplicar_depois`.

<!-- roadmap:suggestions:start -->
{render_table(SUGGESTION_HEADERS, [])}
<!-- roadmap:suggestions:end -->

## Historico de Ciclos

<!-- roadmap:cycles:start -->
(sem itens)
<!-- roadmap:cycles:end -->

## Registro automatico

<!-- roadmap:autolog:start -->
- (sem itens)
<!-- roadmap:autolog:end -->
"""


def ensure_roadmap_file(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(path, roadmap_template())


def ensure_decisions_file(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(path, decisions_template())


def apply_metadata(text: str, *, updated_at: str, cycle: str) -> str:
    updated = re.sub(r"(?m)^Atualizado em:.*$", f"Atualizado em: {updated_at}", text)
    if re.search(r"(?m)^Ciclo ativo:.*$", updated):
        return re.sub(r"(?m)^Ciclo ativo:.*$", f"Ciclo ativo: {cycle}", updated)
    return updated


def parse_float(value: str, *, field_name: str, item_id: str) -> float:
    normalized = value.strip().replace(",", ".")
    try:
        return float(normalized)
    except ValueError as exc:
        raise ValueError(f"Valor invalido para {field_name} no item {item_id}: {value}") from exc


def load_roadmap_items(backlog_rows: list[dict[str, str]]) -> list[RoadmapItem]:
    items: list[RoadmapItem] = []
    for row in backlog_rows:
        item_id = row["ID"].strip()
        if not item_id:
            continue
        items.append(
            RoadmapItem(
                item_id=item_id,
                initiative=row["Iniciativa"].strip(),
                reach=parse_float(row["R"], field_name="R", item_id=item_id),
                impact=parse_float(row["I"], field_name="I", item_id=item_id),
                confidence=parse_float(row["C"], field_name="C", item_id=item_id),
                effort=parse_float(row["E"], field_name="E", item_id=item_id),
                business_value=parse_float(row["BV"], field_name="BV", item_id=item_id),
                time_criticality=parse_float(row["TC"], field_name="TC", item_id=item_id),
                risk_reduction=parse_float(row["RR"], field_name="RR", item_id=item_id),
                job_size=parse_float(row["JS"], field_name="JS", item_id=item_id),
                status=row["Status"].strip(),
            )
        )
    return items


def validate_suggestion_rows(rows: list[dict[str, str]]) -> None:
    invalid = [
        row["ID"]
        for row in rows
        if normalize_text(row["Status"]) not in ALLOWED_SUGGESTION_STATUSES
    ]
    if invalid:
        raise ValueError(
            "Status invalidos encontrados em sugestoes de roadmap: " + ", ".join(invalid)
        )


def build_priority_section(
    items: list[RoadmapItem],
    suggestion_rows: list[dict[str, str]],
    *,
    updated_at: str,
) -> str:
    active = [item for item in items if item.is_active]
    if not active:
        return "Sem iniciativas ativas para priorizacao neste ciclo."

    rice_ranked = sorted(active, key=lambda item: item.rice, reverse=True)
    wsjf_ranked = sorted(active, key=lambda item: item.wsjf, reverse=True)

    rice_rank = {item.item_id: idx + 1 for idx, item in enumerate(rice_ranked)}
    wsjf_rank = {item.item_id: idx + 1 for idx, item in enumerate(wsjf_ranked)}
    combined = sorted(active, key=lambda item: rice_rank[item.item_id] + wsjf_rank[item.item_id])

    pending = [row for row in suggestion_rows if normalize_text(row["Status"]) == "pendente"]

    lines = [f"Atualizado em: `{updated_at}`", "", "### Ranking RICE", ""]
    lines.extend(
        [
            "| Rank | ID | Status | RICE |",
            "| --- | --- | --- | --- |",
            *[
                f"| {idx} | {item.item_id} | {item.status} | {item.rice:.2f} |"
                for idx, item in enumerate(rice_ranked, start=1)
            ],
            "",
            "### Ranking WSJF",
            "",
            "| Rank | ID | Status | WSJF |",
            "| --- | --- | --- | --- |",
            *[
                f"| {idx} | {item.item_id} | {item.status} | {item.wsjf:.2f} |"
                for idx, item in enumerate(wsjf_ranked, start=1)
            ],
            "",
            "### Referencia de IDs",
            "",
            *[f"- `{item.item_id}`: {item.initiative}" for item in active],
            "",
            "### Sequencia Recomendada",
            "",
            *[
                f"{idx}. `{item.item_id}` - {item.initiative}"
                for idx, item in enumerate(combined[:5], start=1)
            ],
            "",
            "### Governanca de Sugestoes",
            "",
        ]
    )

    if pending:
        pending_ids = ", ".join(row["ID"] for row in pending)
        lines.extend(
            [
                "Ha sugestoes pendentes sem decisao final neste ciclo.",
                "Pergunta obrigatoria ao usuario:",
                "- descartar as sugestoes pendentes, ou",
                "- manter no roadmap para aplicar depois.",
                f"IDs pendentes: `{pending_ids}`",
            ]
        )
    else:
        lines.append("Sem sugestoes pendentes neste ciclo; itens aceitos ja estao rastreaveis.")

    return "\n".join(lines)


def build_cycle_entry(
    items: list[RoadmapItem],
    suggestion_rows: list[dict[str, str]],
    *,
    updated_at: str,
    cycle: str,
) -> str:
    active = [item for item in items if item.is_active]
    rice_ranked = sorted(active, key=lambda item: item.rice, reverse=True)
    wsjf_ranked = sorted(active, key=lambda item: item.wsjf, reverse=True)
    rice_rank = {item.item_id: idx + 1 for idx, item in enumerate(rice_ranked)}
    wsjf_rank = {item.item_id: idx + 1 for idx, item in enumerate(wsjf_ranked)}
    combined = sorted(active, key=lambda item: rice_rank[item.item_id] + wsjf_rank[item.item_id])
    top = ", ".join(item.item_id for item in combined[:3]) if combined else "(sem itens)"
    pending_ids = (
        ", ".join(
            row["ID"] for row in suggestion_rows if normalize_text(row["Status"]) == "pendente"
        )
        or "(nenhuma)"
    )
    return "\n".join(
        [
            f"### Ciclo {cycle} @ {updated_at}",
            "",
            f"- Top sequencia recomendada: `{top}`",
            "- Decisao final permanece humana.",
            "- Acao de governanca: decidir pendencias antes de novo escopo amplo.",
            f"- Sugestoes pendentes no fechamento: `{pending_ids}`",
        ]
    )


def load_suggestion_rows(path: Path) -> tuple[str, list[dict[str, str]]]:
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, SUGGESTIONS_START, SUGGESTIONS_END, label=str(path))
    return raw, parse_table(section, SUGGESTION_HEADERS, label=str(path))


def save_suggestion_rows(path: Path, raw: str, rows: list[dict[str, str]]) -> str:
    return replace_between(
        raw,
        SUGGESTIONS_START,
        SUGGESTIONS_END,
        render_table(SUGGESTION_HEADERS, rows),
        label=str(path),
    )


def load_marker_lines(raw: str, start: str, end: str, *, label: str) -> list[str]:
    return [
        line.strip()
        for line in extract_between(raw, start, end, label=label).splitlines()
        if line.strip() and line.strip() != "(sem itens)"
    ]


def save_marker_lines(raw: str, start: str, end: str, lines: list[str], *, label: str) -> str:
    content = "\n".join(lines) if lines else "(sem itens)"
    return replace_between(raw, start, end, content, label=label)


def parse_cycle_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []

    for line in lines:
        if line.startswith("### "):
            if current:
                blocks.append("\n".join(current))
            current = [line]
            continue
        if current:
            current.append(line)
            continue
        current = [line]

    if current:
        blocks.append("\n".join(current))

    return blocks


def cycle_block_key(block: str) -> str:
    first_line = block.splitlines()[0].strip() if block.strip() else ""
    match = re.match(r"^###\s+Ciclo\s+(.+?)\s+@", first_line)
    if not match:
        return normalize_text(first_line)
    return normalize_text(match.group(1))


def replace_cycle_block(blocks: list[str], cycle_entry: str, *, cycle: str) -> list[str]:
    cycle_key = normalize_text(cycle)
    filtered = [block for block in blocks if cycle_block_key(block) != cycle_key]
    return [cycle_entry, *filtered]


def next_suggestion_id(rows: list[dict[str, str]]) -> str:
    base = datetime.now(timezone.utc).strftime("SG-%Y%m%d-%H%M%S")
    if base not in {row["ID"] for row in rows}:
        return base
    suffix = 1
    while f"{base}-{suffix:02d}" in {row["ID"] for row in rows}:
        suffix += 1
    return f"{base}-{suffix:02d}"


def upsert_suggestion(
    rows: list[dict[str, str]],
    *,
    suggestion: str,
    decision: str,
    suggestion_id: str = "",
    roadmap_id: str = "",
) -> tuple[list[dict[str, str]], str]:
    normalized_description = normalize_text(suggestion)
    chosen_id = suggestion_id.strip()
    current_date = today_utc_iso()
    status = DECISION_TO_STATUS[decision]
    updated_rows = [dict(row) for row in rows]

    target_index = -1
    for idx, row in enumerate(updated_rows):
        if chosen_id and row["ID"] == chosen_id:
            target_index = idx
            break
        if normalize_text(row["Descricao"]) == normalized_description:
            target_index = idx
            chosen_id = row["ID"]
            break

    if not chosen_id:
        chosen_id = next_suggestion_id(updated_rows)

    if target_index >= 0:
        row = updated_rows[target_index]
        row["Descricao"] = normalize_cell(suggestion, max_len=180)
        row["Status"] = status
        row["RM"] = normalize_cell(roadmap_id, max_len=40) if roadmap_id else row.get("RM", "")
        row["Atualizacao"] = current_date
        updated_rows[target_index] = row
    else:
        updated_rows.insert(
            0,
            {
                "ID": chosen_id,
                "Descricao": normalize_cell(suggestion, max_len=180),
                "Status": status,
                "RM": normalize_cell(roadmap_id, max_len=40) if roadmap_id else "",
                "Captura": current_date,
                "Atualizacao": current_date,
            },
        )

    return updated_rows, chosen_id


def remove_matching_entries(items: list[str], suggestion: str) -> list[str]:
    return [item for item in items if not semantic_entries_match(item, suggestion)]


def add_unique_entry(items: list[str], entry: str) -> list[str]:
    normalized_entry = normalize_text(entry)
    if any(normalized_entry == normalize_text(item) for item in items):
        return items
    return [entry, *items]


def autolog_signature(line: str) -> str:
    match = re.match(
        r"^- .*?\| decisao=(?P<decision>[^|]+) \| horizonte=(?P<horizon>[^|]+) \| item=(?P<item>.*?)(?: \| notas=.*)?$",
        line.strip(),
    )
    if not match:
        return normalize_text(line)
    return "|".join(
        [
            normalize_text(match.group("decision")),
            normalize_text(match.group("horizon")),
            semantic_entry_key(match.group("item")),
        ]
    )


def refresh_roadmap(
    *,
    roadmap_path: Path,
    decisions_path: Path,
    cycle: str = "",
) -> dict[str, object]:
    ensure_roadmap_file(roadmap_path)
    ensure_decisions_file(decisions_path)

    updated_at = now_human_utc()
    cycle_value = cycle.strip() or current_cycle_utc()

    roadmap_raw = apply_metadata(
        roadmap_path.read_text(encoding="utf-8"), updated_at=updated_at, cycle=cycle_value
    )
    decisions_raw = apply_metadata(
        decisions_path.read_text(encoding="utf-8"), updated_at=updated_at, cycle=cycle_value
    )

    backlog_section = extract_between(
        roadmap_raw, BACKLOG_START, BACKLOG_END, label=str(roadmap_path)
    )
    suggestion_section = extract_between(
        decisions_raw, SUGGESTIONS_START, SUGGESTIONS_END, label=str(decisions_path)
    )

    backlog_rows = parse_table(backlog_section, BACKLOG_HEADERS, label=str(roadmap_path))
    suggestion_rows = parse_table(suggestion_section, SUGGESTION_HEADERS, label=str(decisions_path))
    validate_suggestion_rows(suggestion_rows)

    items = load_roadmap_items(backlog_rows)
    priority_block = build_priority_section(items, suggestion_rows, updated_at=updated_at)
    roadmap_raw = replace_between(
        roadmap_raw, PRIORITY_START, PRIORITY_END, priority_block, label=str(roadmap_path)
    )

    cycle_lines = load_marker_lines(
        decisions_raw, CYCLES_START, CYCLES_END, label=str(decisions_path)
    )
    cycle_blocks = parse_cycle_blocks(cycle_lines)
    cycle_entry = build_cycle_entry(
        items, suggestion_rows, updated_at=updated_at, cycle=cycle_value
    )
    cycle_blocks = replace_cycle_block(cycle_blocks, cycle_entry, cycle=cycle_value)
    decisions_raw = save_marker_lines(
        decisions_raw, CYCLES_START, CYCLES_END, cycle_blocks, label=str(decisions_path)
    )

    write_text_lf(roadmap_path, roadmap_raw)
    write_text_lf(decisions_path, decisions_raw)

    return {
        "roadmap_file": str(roadmap_path),
        "decisions_file": str(decisions_path),
        "cycle": cycle_value,
        "updated_at": updated_at,
    }


def register_roadmap_decision(
    *,
    roadmap_path: Path,
    decisions_path: Path,
    suggestion: str,
    decision: str,
    horizon: str = "next",
    notes: str = "",
    suggestion_id: str = "",
    roadmap_id: str = "",
    cycle: str = "",
) -> dict[str, object]:
    normalized_decision = decision.strip().lower()
    normalized_horizon = horizon.strip().lower() or "next"
    if normalized_decision not in ALLOWED_DECISIONS:
        raise ValueError("Decisao invalida. Use: accepted, pending ou discarded.")
    if normalized_horizon not in ALLOWED_HORIZONS:
        raise ValueError("Horizonte invalido. Use: now, next ou later.")

    ensure_roadmap_file(roadmap_path)
    ensure_decisions_file(decisions_path)

    updated_at = now_human_utc()
    cycle_value = cycle.strip() or current_cycle_utc()
    clean_suggestion = normalize_cell(suggestion, max_len=180)
    note_suffix = f" | notas={normalize_cell(notes, max_len=140)}" if notes.strip() else ""
    roadmap_entry = f"{clean_suggestion}{note_suffix}"

    roadmap_raw = apply_metadata(
        roadmap_path.read_text(encoding="utf-8"), updated_at=updated_at, cycle=cycle_value
    )
    for marker_start, marker_end in LIST_MARKERS.values():
        section = parse_list_section(
            extract_between(roadmap_raw, marker_start, marker_end, label=str(roadmap_path))
        )
        cleaned = remove_matching_entries(section, clean_suggestion)
        roadmap_raw = replace_between(
            roadmap_raw,
            marker_start,
            marker_end,
            render_list_section(cleaned),
            label=str(roadmap_path),
        )

    target_section = "pending" if normalized_decision == "pending" else normalized_horizon
    if normalized_decision != "discarded":
        marker_start, marker_end = LIST_MARKERS[target_section]
        section = parse_list_section(
            extract_between(roadmap_raw, marker_start, marker_end, label=str(roadmap_path))
        )
        section = add_unique_entry(section, roadmap_entry)
        roadmap_raw = replace_between(
            roadmap_raw,
            marker_start,
            marker_end,
            render_list_section(section),
            label=str(roadmap_path),
        )

    decisions_raw, suggestion_rows = load_suggestion_rows(decisions_path)
    decisions_raw = apply_metadata(decisions_raw, updated_at=updated_at, cycle=cycle_value)
    suggestion_rows, chosen_id = upsert_suggestion(
        suggestion_rows,
        suggestion=clean_suggestion,
        decision=normalized_decision,
        suggestion_id=suggestion_id,
        roadmap_id=roadmap_id,
    )
    decisions_raw = save_suggestion_rows(decisions_path, decisions_raw, suggestion_rows)

    autolog_lines = load_marker_lines(
        decisions_raw, AUTOLOG_START, AUTOLOG_END, label=str(decisions_path)
    )
    autolog_line = (
        f"- {updated_at} | decisao={normalized_decision} | horizonte={normalized_horizon} "
        f"| item={clean_suggestion}{note_suffix}"
    )
    signature = autolog_signature(autolog_line)
    autolog_lines = [line for line in autolog_lines if autolog_signature(line) != signature]
    autolog_lines = [autolog_line, *autolog_lines]
    decisions_raw = save_marker_lines(
        decisions_raw, AUTOLOG_START, AUTOLOG_END, autolog_lines, label=str(decisions_path)
    )

    write_text_lf(roadmap_path, roadmap_raw)
    write_text_lf(decisions_path, decisions_raw)

    return {
        "roadmap_file": str(roadmap_path),
        "decisions_file": str(decisions_path),
        "cycle": cycle_value,
        "updated_at": updated_at,
        "suggestion_id": chosen_id,
        "decision": normalized_decision,
        "horizon": normalized_horizon,
    }
