from __future__ import annotations

import os
import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ai_agent_execution_lib import (
    ensure_comment,
    issue_url,
    render_structured_comment,
    resolve_jira,
)

LEDGER_PATH = Path("docs/AI-FALLBACK-LEDGER.md")
TRACKER_PATH = Path("docs/AI-WIP-TRACKER.md")
DECISIONS_PATH = Path("docs/ROADMAP-DECISIONS.md")
ALLOWED_TRACKERS = {
    TRACKER_PATH.as_posix(),
    DECISIONS_PATH.as_posix(),
}

ACTIVE_START = "<!-- ai-fallback:active:start -->"
ACTIVE_END = "<!-- ai-fallback:active:end -->"
RESOLVED_START = "<!-- ai-fallback:resolved:start -->"
RESOLVED_END = "<!-- ai-fallback:resolved:end -->"
TRACKER_DOING_START = "<!-- ai-worklog:doing:start -->"
TRACKER_DOING_END = "<!-- ai-worklog:doing:end -->"

ACTIVE_HEADERS = [
    "Capturado UTC",
    "Atualizado UTC",
    "Tracker",
    "Referencia local",
    "Estado",
    "Jira",
    "Resumo",
    "Proximo passo",
]
RESOLVED_HEADERS = [
    "Capturado UTC",
    "Resolvido UTC",
    "Tracker",
    "Referencia local",
    "Estado",
    "Jira",
    "Resumo",
    "Resultado",
]
TRACKER_DOING_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Ultima atualizacao UTC",
    "Proximo passo",
    "Bloqueios",
]

MARKDOWN_LINK_RE = re.compile(r"^\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)$")


class FallbackGovernanceError(RuntimeError):
    pass


def now_human_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


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


def write_text_lf(path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalized)


def ledger_template() -> str:
    return f"""# AI Fallback Ledger

Atualizado em: {now_human_utc()}

Registro canonico do uso excepcional dos trackers locais quando o `Jira` nao
consegue sustentar o fluxo primario.

## Regras operacionais

- O modo normal do repo e `primary`: o `Jira` segue como fonte primaria e o
  fallback local nao pode virar ledger concorrente por inercia.
- O modo `degraded` so pode ser usado quando houver indisponibilidade real do
  `Jira` ou falha objetiva da sincronizacao primaria.
- Toda degradacao real deve gerar um registro ativo neste ledger antes de
  transformar [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md) ou
  [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) em fallback operacional.
- Quando o `Jira` voltar, a sessao entra em `recovery` ate que cada registro
  ativo seja classificado como `drained`, `reconciled` ou `obsolete`.
- `drained` significa que o contexto local foi drenado de volta para o `Jira`.
- `reconciled` significa que o `Jira` voltou com contexto equivalente, sem
  precisar copiar tudo literalmente do fallback local.
- `obsolete` significa que o registro local deixou de representar backlog vivo
  e foi encerrado sem sincronizacao adicional.

## Registros ativos

<!-- ai-fallback:active:start -->
{render_table(ACTIVE_HEADERS, [])}
<!-- ai-fallback:active:end -->

## Registros resolvidos

<!-- ai-fallback:resolved:start -->
{render_table(RESOLVED_HEADERS, [])}
<!-- ai-fallback:resolved:end -->
"""


def ensure_fallback_ledger_file(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(path, ledger_template())


def load_fallback_ledger(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    raw = path.read_text(encoding="utf-8")
    active = parse_table(
        extract_between(raw, ACTIVE_START, ACTIVE_END, label=str(path)),
        ACTIVE_HEADERS,
        label=str(path),
    )
    resolved = parse_table(
        extract_between(raw, RESOLVED_START, RESOLVED_END, label=str(path)),
        RESOLVED_HEADERS,
        label=str(path),
    )
    return active, resolved


def save_fallback_ledger(
    path: Path, active: list[dict[str, str]], resolved: list[dict[str, str]]
) -> None:
    content = ledger_template()
    content = replace_between(
        content,
        ACTIVE_START,
        ACTIVE_END,
        render_table(ACTIVE_HEADERS, active),
        label=str(path),
    )
    content = replace_between(
        content,
        RESOLVED_START,
        RESOLVED_END,
        render_table(RESOLVED_HEADERS, resolved),
        label=str(path),
    )
    write_text_lf(path, content)


def markdown_link(label: str, target: str) -> str:
    return f"[{label}]({target})"


def cell_label(value: str) -> str:
    match = MARKDOWN_LINK_RE.match((value or "").strip())
    if match:
        return match.group("label").strip()
    return (value or "").strip()


def relative_doc_target(base_file: Path, target_file: Path) -> str:
    return Path(os.path.relpath(target_file, start=base_file.parent)).as_posix()


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def validate_tracker_reference(tracker_relative: str) -> str:
    normalized = tracker_relative.strip().replace("\\", "/")
    if normalized not in ALLOWED_TRACKERS:
        allowed = ", ".join(sorted(ALLOWED_TRACKERS))
        raise FallbackGovernanceError(
            f"Tracker invalido para fallback: {normalized!r}. Permitidos: {allowed}."
        )
    return normalized


def format_tracker_cell(repo_root: Path, ledger_path: Path, tracker_relative: str) -> str:
    tracker_path = (repo_root / tracker_relative).resolve()
    return markdown_link(
        tracker_relative,
        relative_doc_target(ledger_path, tracker_path),
    )


def format_jira_cell(repo_root: Path, issue_key: str) -> str:
    normalized = (issue_key or "").strip().upper()
    if not normalized:
        return "-"
    try:
        jira = resolve_jira(repo_root)
        return markdown_link(normalized, issue_url(jira, normalized))
    except Exception:
        return normalized


def tracker_doing_count(path: Path) -> int:
    if not path.exists():
        return 0
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, TRACKER_DOING_START, TRACKER_DOING_END, label=str(path))
    rows = parse_table(section, TRACKER_DOING_HEADERS, label=str(path))
    return len(rows)


def find_active_record(
    active: list[dict[str, str]], *, tracker_relative: str, local_reference: str
) -> dict[str, str] | None:
    normalized_tracker = tracker_relative.strip()
    normalized_ref = local_reference.strip()
    for row in active:
        if cell_label(row.get("Tracker", "")) != normalized_tracker:
            continue
        if row.get("Referencia local", "").strip() != normalized_ref:
            continue
        return row
    return None


def probe_jira_availability(repo_root: Path) -> tuple[bool, str]:
    try:
        jira = resolve_jira(repo_root)
        project_key = str(getattr(jira.client.resolved, "jira_project_key", "")).strip()
        if not project_key:
            raise FallbackGovernanceError("Projeto Jira nao resolvido no control plane.")
        _ = jira.get_project(project_key)
    except Exception as exc:
        return False, normalize_cell(str(exc), max_len=180)
    return True, "project-probe-ok"


def fallback_status_payload(
    repo_root: Path,
    *,
    ledger_path: Path | None = None,
    tracker_path: Path | None = None,
    jira_probe: Callable[[Path], tuple[bool, str]] = probe_jira_availability,
) -> dict[str, Any]:
    resolved_ledger_path = (ledger_path or (repo_root / LEDGER_PATH)).resolve()
    resolved_tracker_path = (tracker_path or (repo_root / TRACKER_PATH)).resolve()
    ensure_fallback_ledger_file(resolved_ledger_path)
    active, resolved = load_fallback_ledger(resolved_ledger_path)
    jira_available, jira_reason = jira_probe(repo_root)
    tracker_pending = tracker_doing_count(resolved_tracker_path)
    if not jira_available:
        mode = "degraded"
        guidance = (
            "Registrar capturas no ledger de fallback antes de operar localmente como contingencia."
        )
    elif active:
        mode = "recovery"
        guidance = (
            "Drenar ou reconciliar cada registro ativo com `task ai:fallback:resolve` antes "
            "de tratar o fallback local como vazio."
        )
    else:
        mode = "primary"
        guidance = (
            "Manter o Jira como fonte primaria e usar o fallback local apenas para continuidade, "
            "nao como ledger concorrente."
        )
    return {
        "mode": mode,
        "jira_available": jira_available,
        "jira_reason": jira_reason,
        "active_fallback_count": len(active),
        "resolved_fallback_count": len(resolved),
        "tracker_doing_count": tracker_pending,
        "active_records": [
            {
                "tracker": cell_label(row.get("Tracker", "")),
                "local_reference": row.get("Referencia local", "").strip(),
                "state": row.get("Estado", "").strip(),
                "jira_issue": cell_label(row.get("Jira", "")) if row.get("Jira") != "-" else "",
                "summary": row.get("Resumo", "").strip(),
            }
            for row in active
        ],
        "guidance": guidance,
        "ledger_path": display_path(resolved_ledger_path, repo_root),
        "tracker_path": display_path(resolved_tracker_path, repo_root),
    }


def capture_fallback_record(
    repo_root: Path,
    *,
    tracker_relative: str,
    local_reference: str,
    summary: str,
    next_step: str,
    jira_issue: str = "",
    allow_when_jira_available: bool = False,
    ledger_path: Path | None = None,
    jira_probe: Callable[[Path], tuple[bool, str]] = probe_jira_availability,
) -> dict[str, Any]:
    normalized_tracker = validate_tracker_reference(tracker_relative)
    normalized_ref = local_reference.strip()
    if not normalized_tracker or not normalized_ref:
        raise FallbackGovernanceError("Tracker e referencia local sao obrigatorios.")
    jira_available, jira_reason = jira_probe(repo_root)
    if jira_available and not allow_when_jira_available:
        raise FallbackGovernanceError(
            "Fallback local bloqueado: o Jira esta disponivel. Use --allow-while-jira-up 1 "
            "somente quando houver falha primaria objetiva diferente da indisponibilidade total."
        )
    resolved_ledger_path = (ledger_path or (repo_root / LEDGER_PATH)).resolve()
    ensure_fallback_ledger_file(resolved_ledger_path)
    active, resolved = load_fallback_ledger(resolved_ledger_path)
    current = find_active_record(
        active, tracker_relative=normalized_tracker, local_reference=normalized_ref
    )
    timestamp = now_human_utc()
    if current is None:
        row = {
            "Capturado UTC": timestamp,
            "Atualizado UTC": timestamp,
            "Tracker": format_tracker_cell(repo_root, resolved_ledger_path, normalized_tracker),
            "Referencia local": normalized_ref,
            "Estado": "captured",
            "Jira": format_jira_cell(repo_root, jira_issue),
            "Resumo": normalize_cell(summary, max_len=180),
            "Proximo passo": normalize_cell(next_step, max_len=180),
        }
        active.insert(0, row)
    else:
        current["Atualizado UTC"] = timestamp
        current["Estado"] = "captured"
        current["Jira"] = format_jira_cell(repo_root, jira_issue or cell_label(current["Jira"]))
        current["Resumo"] = normalize_cell(summary, max_len=180)
        current["Proximo passo"] = normalize_cell(next_step, max_len=180)
    save_fallback_ledger(resolved_ledger_path, active, resolved)
    return {
        "action": "captured",
        "mode": "degraded" if not jira_available else "forced-degraded",
        "jira_reason": jira_reason,
        "tracker": normalized_tracker,
        "local_reference": normalized_ref,
        "ledger_path": display_path(resolved_ledger_path, repo_root),
    }


def build_fallback_sync_comment(
    *,
    tracker_relative: str,
    local_reference: str,
    outcome: str,
    result: str,
    ledger_reference: str,
    agent: str,
) -> str:
    return render_structured_comment(
        agent=agent,
        interaction_type="fallback-sync",
        status="done",
        contexto=[
            "O fallback local precisou assumir rastreabilidade temporaria enquanto a fonte primaria nao estava operacional.",
            f"Tracker local: {tracker_relative}",
            f"Referencia local: {local_reference}",
            f"Resultado da reconciliacao: {outcome}",
        ],
        evidencias=[
            ledger_reference,
            tracker_relative,
            f"resultado={outcome}",
        ],
        proximo_passo=result
        or "Fluxo primario no Jira retomado; o registro local deixou de estar pendente.",
    )


def resolve_fallback_record(
    repo_root: Path,
    *,
    tracker_relative: str,
    local_reference: str,
    outcome: str,
    result: str,
    jira_issue: str = "",
    summary: str = "",
    agent: str = "ai-product-owner",
    sync_jira: bool = True,
    ledger_path: Path | None = None,
    jira_resolver: Callable[[Path], Any] = resolve_jira,
) -> dict[str, Any]:
    normalized_tracker = validate_tracker_reference(tracker_relative)
    normalized_ref = local_reference.strip()
    normalized_outcome = outcome.strip().lower()
    if normalized_outcome not in {"drained", "reconciled", "obsolete"}:
        raise FallbackGovernanceError("Resultado invalido. Use drained, reconciled ou obsolete.")
    resolved_ledger_path = (ledger_path or (repo_root / LEDGER_PATH)).resolve()
    ensure_fallback_ledger_file(resolved_ledger_path)
    active, resolved = load_fallback_ledger(resolved_ledger_path)
    current = find_active_record(
        active, tracker_relative=normalized_tracker, local_reference=normalized_ref
    )
    if current is None:
        raise FallbackGovernanceError(
            "Registro ativo de fallback nao encontrado para tracker/ref informados."
        )
    active = [
        row
        for row in active
        if not (
            cell_label(row.get("Tracker", "")) == normalized_tracker
            and row.get("Referencia local", "").strip() == normalized_ref
        )
    ]
    effective_issue = (jira_issue or cell_label(current.get("Jira", ""))).strip().upper()
    effective_summary = normalize_cell(summary or current.get("Resumo", ""), max_len=180)
    effective_result = normalize_cell(
        result
        or {
            "drained": "Registro local drenado de volta para o Jira e removido da fila de recovery.",
            "reconciled": "Registro local reconciliado com o Jira sem backlog vivo remanescente no fallback.",
            "obsolete": "Registro local marcado como obsoleto porque ja nao representava backlog vivo.",
        }[normalized_outcome],
        max_len=220,
    )

    comment_id = ""
    if sync_jira and normalized_outcome in {"drained", "reconciled"}:
        if not effective_issue:
            raise FallbackGovernanceError(
                "Jira issue obrigatoria para drained/reconciled quando sync_jira estiver ativo."
            )
        jira = jira_resolver(repo_root)
        comment = ensure_comment(
            jira,
            effective_issue,
            build_fallback_sync_comment(
                tracker_relative=normalized_tracker,
                local_reference=normalized_ref,
                outcome=normalized_outcome,
                result=effective_result,
                ledger_reference=display_path(resolved_ledger_path, repo_root),
                agent=agent,
            ),
        )
        comment_id = str(comment.get("id", "")).strip()

    resolved.insert(
        0,
        {
            "Capturado UTC": current.get("Capturado UTC", "-"),
            "Resolvido UTC": now_human_utc(),
            "Tracker": format_tracker_cell(repo_root, resolved_ledger_path, normalized_tracker),
            "Referencia local": normalized_ref,
            "Estado": normalized_outcome,
            "Jira": format_jira_cell(repo_root, effective_issue),
            "Resumo": effective_summary,
            "Resultado": effective_result,
        },
    )
    save_fallback_ledger(resolved_ledger_path, active, resolved)
    return {
        "action": "resolved",
        "outcome": normalized_outcome,
        "tracker": normalized_tracker,
        "local_reference": normalized_ref,
        "jira_issue": effective_issue,
        "jira_comment_id": comment_id,
        "ledger_path": display_path(resolved_ledger_path, repo_root),
    }
