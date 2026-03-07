#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_lessons_lib import (
    check_reviews,
    ensure_lessons_file,
    normalize_lesson_ids,
    upsert_review,
    validate_review_request,
)
from scripts.ai_roadmap_lib import (
    ensure_decisions_file as ensure_governed_decisions_file,
)
from scripts.ai_roadmap_lib import (
    ensure_roadmap_file,
    refresh_roadmap,
    register_roadmap_decision,
)

DOING_START = "<!-- ai-worklog:doing:start -->"
DOING_END = "<!-- ai-worklog:doing:end -->"
DONE_START = "<!-- ai-worklog:done:start -->"
DONE_END = "<!-- ai-worklog:done:end -->"
LOG_START = "<!-- ai-worklog:log:start -->"
LOG_END = "<!-- ai-worklog:log:end -->"
SUGGESTIONS_START = "<!-- roadmap:suggestions:start -->"
SUGGESTIONS_END = "<!-- roadmap:suggestions:end -->"
CYCLES_START = "<!-- roadmap:cycles:start -->"
CYCLES_END = "<!-- roadmap:cycles:end -->"

DOING_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Ultima atualizacao UTC",
    "Proximo passo",
    "Bloqueios",
]
DONE_HEADERS = [
    "ID",
    "Tarefa",
    "Branch",
    "Responsavel",
    "Inicio UTC",
    "Concluido UTC",
    "Resultado",
]
LOG_HEADERS = [
    "Data/Hora UTC",
    "ID",
    "Status",
    "Resumo",
    "Proximo passo",
    "Bloqueios",
    "Contexto",
    "Notas",
]
SUGGESTION_HEADERS = ["ID", "Descricao", "Status", "RM", "Captura", "Atualizacao"]
ALLOWED_PENDING_ACTIONS = {"", "concluir_primeiro", "roadmap_pendente"}


def now_human_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def today_utc_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


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


def format_log_line(
    *,
    worklog_id: str,
    status: str,
    summary: str,
    next_step: str,
    blockers: str,
    context: str = "",
    notes: str = "",
) -> str:
    parts = [
        now_human_utc(),
        f"id={normalize_cell(worklog_id, max_len=80)}",
        f"status={normalize_cell(status, max_len=40)}",
        f"resumo={normalize_cell(summary, max_len=220)}",
        f"next={normalize_cell(next_step, max_len=220)}",
        f"blockers={normalize_cell(blockers, max_len=120)}",
    ]
    if context:
        parts.append(f"contexto={normalize_cell(context, max_len=220)}")
    if notes:
        parts.append(f"notas={normalize_cell(notes, max_len=220)}")
    return " | ".join(parts)


def parse_log_id(line: str) -> str:
    for part in [segment.strip() for segment in line.split("|")]:
        if part.startswith("id="):
            return part.split("=", 1)[1].strip()
    return ""


def parse_log_lines(section: str) -> list[str]:
    stripped = section.strip()
    if not stripped:
        return []
    if stripped.startswith("|"):
        rows = parse_table(section, LOG_HEADERS, label="AI-WIP-TRACKER log")
        return [
            format_log_line(
                worklog_id=row["ID"],
                status=row["Status"],
                summary=row["Resumo"],
                next_step=row["Proximo passo"],
                blockers=row["Bloqueios"],
                context="" if row["Contexto"] == "-" else row["Contexto"],
                notes="" if row["Notas"] == "-" else row["Notas"],
            )
            for row in rows
        ]
    return [
        line.strip()
        for line in section.splitlines()
        if line.strip() and line.strip() != "(sem itens)"
    ]


def render_log_table(log_lines: list[str]) -> str:
    rows = []
    for line in log_lines:
        parts = [part.strip() for part in line.split("|") if part.strip()]
        row = {
            "Data/Hora UTC": parts[0] if parts else "-",
            "ID": "-",
            "Status": "-",
            "Resumo": "-",
            "Proximo passo": "-",
            "Bloqueios": "-",
            "Contexto": "-",
            "Notas": "-",
        }
        mapping = {
            "id": "ID",
            "status": "Status",
            "resumo": "Resumo",
            "next": "Proximo passo",
            "blockers": "Bloqueios",
            "contexto": "Contexto",
            "notas": "Notas",
        }
        for part in parts[1:]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            mapped = mapping.get(key.strip().lower())
            if mapped:
                row[mapped] = value.strip()
        rows.append(row)
    return render_table(LOG_HEADERS, rows)


def tracker_template() -> str:
    return f"""# AI WIP Tracker

Atualizado em: {now_human_utc()}

Fonte de verdade operacional para continuidade de tarefas dos agentes de IA.

## Regras operacionais

- Toda solicitacao acionavel deve passar por preflight de pendencias.
- Se houver itens em `Doing`, perguntar ao usuario:
  - concluir pendencias antes (`concluir_primeiro`), ou
  - manter pendencias e registrar no roadmap (`roadmap_pendente`).
- Durante execucao, registrar progresso incremental no ledger.
- O item ativo deve permanecer em `Doing` enquanto a execucao estiver em curso.
- Ultimo passo obrigatorio antes de encerrar demanda: mover item ativo de
  `Doing` para `Done` e remover do log incremental as demandas finalizadas.

## Doing

<!-- ai-worklog:doing:start -->
{render_table(DOING_HEADERS, [])}
<!-- ai-worklog:doing:end -->

## Done

<!-- ai-worklog:done:start -->
{render_table(DONE_HEADERS, [])}
<!-- ai-worklog:done:end -->

## Log incremental - Tarefas nao finalizadas ainda

<!-- ai-worklog:log:start -->
{render_log_table([])}
<!-- ai-worklog:log:end -->
"""


def roadmap_template() -> str:
    return f"""# Decisoes do Roadmap

Registro das decisoes humanas por ciclo e governanca de sugestoes.

## Registro de Sugestoes

Use status: `pendente`, `aceita`, `descartada`, `aplicar_depois`.

<!-- roadmap:suggestions:start -->
{render_table(SUGGESTION_HEADERS, [])}
<!-- roadmap:suggestions:end -->

## Historico de Ciclos

<!-- roadmap:cycles:start -->
<!-- roadmap:cycles:end -->
"""


def ensure_tracker_file(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(path, tracker_template())


def ensure_decisions_file(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(path, roadmap_template())


def load_tracker(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    raw = path.read_text(encoding="utf-8")
    doing = parse_table(
        extract_between(raw, DOING_START, DOING_END, label=str(path)),
        DOING_HEADERS,
        label=str(path),
    )
    done = parse_table(
        extract_between(raw, DONE_START, DONE_END, label=str(path)), DONE_HEADERS, label=str(path)
    )
    log = parse_log_lines(extract_between(raw, LOG_START, LOG_END, label=str(path)))
    return doing, done, log


def save_tracker(
    path: Path, doing: list[dict[str, str]], done: list[dict[str, str]], log: list[str]
) -> None:
    content = tracker_template()
    content = replace_between(
        content, DOING_START, DOING_END, render_table(DOING_HEADERS, doing), label=str(path)
    )
    content = replace_between(
        content, DONE_START, DONE_END, render_table(DONE_HEADERS, done), label=str(path)
    )
    active_ids = {row["ID"] for row in doing}
    filtered = [line for line in log if parse_log_id(line) in active_ids]
    content = replace_between(
        content, LOG_START, LOG_END, render_log_table(filtered), label=str(path)
    )
    write_text_lf(path, content)


def load_suggestions(path: Path) -> tuple[str, list[dict[str, str]]]:
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, SUGGESTIONS_START, SUGGESTIONS_END, label=str(path))
    return raw, parse_table(section, SUGGESTION_HEADERS, label=str(path))


def save_suggestions(path: Path, raw: str, rows: list[dict[str, str]]) -> None:
    updated = replace_between(
        raw,
        SUGGESTIONS_START,
        SUGGESTIONS_END,
        render_table(SUGGESTION_HEADERS, rows),
        label=str(path),
    )
    _ = extract_between(updated, CYCLES_START, CYCLES_END, label=str(path))
    write_text_lf(path, updated)


def resolve_branch() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], check=True, capture_output=True, text=True
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def collect_dirty_paths(repo_root_value: str) -> list[str]:
    repo_root = (repo_root_value or "").strip()
    if not repo_root:
        return []
    try:
        root = Path(repo_root).expanduser().resolve()
        probe = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            return []
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, check=False, capture_output=True, text=True
        )
        if status.returncode != 0:
            return []
    except OSError:
        return []

    dirty_paths: list[str] = []
    for raw_line in status.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        dirty_paths.append(line[3:] if len(line) > 3 else line)
    return dirty_paths


def next_worklog_id(existing_ids: set[str]) -> str:
    base = datetime.now(timezone.utc).strftime("WIP-%Y%m%d-%H%M%S")
    if base not in existing_ids:
        return base
    suffix = 1
    while f"{base}-{suffix:02d}" in existing_ids:
        suffix += 1
    return f"{base}-{suffix:02d}"


def add_suggestions(
    *,
    suggestions: list[dict[str, str]],
    rows: list[dict[str, str]],
    description_overrides: dict[str, str] | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    overrides = description_overrides or {}
    existing_ids = {row["ID"] for row in suggestions}
    added: list[dict[str, str]] = []
    for row in rows:
        worklog_id = row.get("ID", "").strip()
        suggestion_id = f"SG-{worklog_id}"
        if not worklog_id or suggestion_id in existing_ids:
            continue
        description = (
            overrides.get(worklog_id)
            or f"Retomar tarefa pendente {worklog_id}: {row.get('Tarefa', '-')}"
        )
        added.append(
            {
                "ID": suggestion_id,
                "Descricao": normalize_cell(description, max_len=180),
                "Status": "pendente",
                "RM": "",
                "Captura": today_utc_iso(),
                "Atualizacao": today_utc_iso(),
            }
        )
    return ((added + suggestions), added) if added else (suggestions, [])


def run_ensure(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    roadmap = Path(args.roadmap_file)
    decisions = Path(args.decisions_file)
    lessons = Path(args.lessons_file)
    ensure_tracker_file(tracker)
    ensure_roadmap_file(roadmap)
    ensure_governed_decisions_file(decisions)
    ensure_lessons_file(lessons)
    refresh_roadmap(roadmap_path=roadmap, decisions_path=decisions)
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "roadmap_file": str(roadmap),
                "decisions_file": str(decisions),
                "lessons_file": str(lessons),
                "status": "ensured",
            },
            ensure_ascii=False,
        )
    )


def run_list(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    ensure_tracker_file(tracker)
    doing, _, _ = load_tracker(tracker)
    print(
        json.dumps(
            {"tracker_file": str(tracker), "pending_count": len(doing), "items": doing},
            ensure_ascii=False,
        )
    )


def run_preflight(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    ensure_tracker_file(tracker)
    doing, _, _ = load_tracker(tracker)
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "pending_count": len(doing),
                "pending_ids": [row["ID"] for row in doing],
                "must_ask_user": bool(doing and (args.message or "").strip()),
                "resolution_options": ["concluir_primeiro", "roadmap_pendente"] if doing else [],
            },
            ensure_ascii=False,
        )
    )


def run_check(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    ensure_tracker_file(tracker)
    doing, _, _ = load_tracker(tracker)
    pending_action = (args.pending_action or "").strip()
    if pending_action not in ALLOWED_PENDING_ACTIONS:
        raise SystemExit("Acao pendente invalida. Use concluir_primeiro ou roadmap_pendente.")
    dirty_paths = collect_dirty_paths(args.repo_root or "")
    if args.enforce_clean_checkpoint == 1 and not doing and dirty_paths:
        preview = ", ".join(dirty_paths[:8])
        suffix = " ..." if len(dirty_paths) > 8 else ""
        raise SystemExit(
            "Checkpoint commit obrigatorio antes de nova rodada: worktree suja sem item em Doing. "
            "Faca commit do contexto atual antes de seguir. Arquivos pendentes: " + preview + suffix
        )
    if args.strict == 1 and doing and not pending_action:
        raise SystemExit(
            "Existem tarefas em Doing. Defina uma decisao humana explicita: concluir_primeiro ou roadmap_pendente."
        )
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "pending_count": len(doing),
                "pending_ids": [row["ID"] for row in doing],
                "pending_action": pending_action or "(none)",
                "ok": True,
            },
            ensure_ascii=False,
        )
    )


def run_close_gate(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    lessons = Path(args.lessons_file)
    ensure_tracker_file(tracker)
    doing, _, _ = load_tracker(tracker)
    if doing:
        raise SystemExit(
            "Finalizacao bloqueada: existem tarefas em Doing no docs/AI-WIP-TRACKER.md. IDs pendentes: "
            + ", ".join(row["ID"] for row in doing)
        )
    lessons_failures = check_reviews(tracker_path=tracker, lessons_path=lessons)
    if lessons_failures:
        raise SystemExit(
            "Finalizacao bloqueada por governanca de licoes:\n" + "\n".join(lessons_failures)
        )
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "lessons_file": str(lessons),
                "pending_count": 0,
                "status": "close_gate_passed",
            },
            ensure_ascii=False,
        )
    )


def run_branch_check(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    ensure_tracker_file(tracker)
    branch = (args.branch or "").strip() or resolve_branch()
    owner = (args.owner or "").strip()
    doing, _, _ = load_tracker(tracker)
    pending = [
        row
        for row in doing
        if row.get("Branch") == branch and (not owner or row.get("Responsavel") == owner)
    ]
    if pending:
        raise SystemExit(
            "Fechamento da branch bloqueado: existem tarefas em Doing para branch="
            + branch
            + f" owner={owner or '(any)'}. IDs pendentes: "
            + ", ".join(row["ID"] for row in pending)
        )
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "branch": branch,
                "owner": owner or "(any)",
                "pending_count": 0,
                "ok": True,
            },
            ensure_ascii=False,
        )
    )


def run_start(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    ensure_tracker_file(tracker)
    doing, done, log = load_tracker(tracker)
    existing = {row["ID"] for row in doing} | {row["ID"] for row in done}
    worklog_id = (args.worklog_id or "").strip() or next_worklog_id(existing)
    if worklog_id in existing:
        raise SystemExit(f"ID de worklog ja existe: {worklog_id}")
    row = {
        "ID": worklog_id,
        "Tarefa": normalize_cell(args.message),
        "Branch": normalize_cell((args.branch or "").strip() or resolve_branch(), max_len=80),
        "Responsavel": normalize_cell((args.owner or "").strip() or "ai-agent", max_len=60),
        "Inicio UTC": now_human_utc(),
        "Ultima atualizacao UTC": now_human_utc(),
        "Proximo passo": normalize_cell(
            (args.next_step or args.progress or "seguir implementacao").strip()
        ),
        "Bloqueios": normalize_cell((args.blockers or "-").strip(), max_len=120),
    }
    doing.insert(0, row)
    log.append(
        format_log_line(
            worklog_id=worklog_id,
            status="doing",
            summary=row["Tarefa"],
            next_step=row["Proximo passo"],
            blockers=row["Bloqueios"],
            context=args.scope or "",
            notes="inicio da tarefa",
        )
    )
    save_tracker(tracker, doing, done, log)
    print(
        json.dumps(
            {"tracker_file": str(tracker), "worklog_id": worklog_id, "action": "started"},
            ensure_ascii=False,
        )
    )


def run_update(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    ensure_tracker_file(tracker)
    doing, done, log = load_tracker(tracker)
    target = (args.worklog_id or "").strip()
    progress_summary = normalize_cell((args.progress or "").strip())
    updated = None
    for row in doing:
        if row["ID"] != target:
            continue
        row["Ultima atualizacao UTC"] = now_human_utc()
        row["Proximo passo"] = normalize_cell((args.next_step or args.progress).strip())
        row["Bloqueios"] = normalize_cell((args.blockers or "-").strip(), max_len=120)
        if args.message:
            row["Tarefa"] = normalize_cell(args.message)
        if args.branch:
            row["Branch"] = normalize_cell(args.branch, max_len=80)
        if args.owner:
            row["Responsavel"] = normalize_cell(args.owner, max_len=60)
        updated = row
        break
    if updated is None:
        raise SystemExit(f"Worklog ID nao encontrado em Doing: {target}")
    log.append(
        format_log_line(
            worklog_id=target,
            status="doing",
            summary=progress_summary,
            next_step=updated["Proximo passo"],
            blockers=updated["Bloqueios"],
            context=args.scope or "",
            notes="checkpoint incremental",
        )
    )
    save_tracker(tracker, doing, done, log)
    print(
        json.dumps(
            {"tracker_file": str(tracker), "worklog_id": target, "action": "updated"},
            ensure_ascii=False,
        )
    )


def run_done(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    lessons = Path(args.lessons_file)
    ensure_tracker_file(tracker)
    ensure_lessons_file(lessons)
    doing, done, log = load_tracker(tracker)
    target = (args.worklog_id or "").strip()
    current = None
    remaining = []
    for row in doing:
        if row["ID"] == target:
            current = row
        else:
            remaining.append(row)
    if current is None:
        raise SystemExit(f"Worklog ID nao encontrado em Doing: {target}")
    lesson_ids = normalize_lesson_ids(args.lessons_ids or "")
    validate_review_request(
        path=lessons,
        decision=(args.lessons_decision or "").strip(),
        summary=(args.lessons_summary or "").strip(),
        lesson_ids=lesson_ids,
    )
    result = normalize_cell(args.delivery, max_len=180)
    if (args.evidence or "").strip():
        result = normalize_cell(f"{result} / evidencias: {args.evidence.strip()}", max_len=220)
    done.insert(
        0,
        {
            "ID": current["ID"],
            "Tarefa": current["Tarefa"],
            "Branch": current["Branch"],
            "Responsavel": current["Responsavel"],
            "Inicio UTC": current["Inicio UTC"],
            "Concluido UTC": now_human_utc(),
            "Resultado": result,
        },
    )
    save_tracker(tracker, remaining, done, log)
    upsert_review(
        path=lessons,
        worklog_id=target,
        decision=(args.lessons_decision or "").strip(),
        summary=(args.lessons_summary or "").strip(),
        lesson_ids=lesson_ids,
        evidence=(args.lessons_evidence or args.evidence or "").strip(),
    )
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "lessons_file": str(lessons),
                "worklog_id": target,
                "action": "done",
            },
            ensure_ascii=False,
        )
    )


def run_roadmap_pending(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    roadmap = Path(args.roadmap_file)
    decisions = Path(args.decisions_file)
    ensure_tracker_file(tracker)
    ensure_roadmap_file(roadmap)
    ensure_governed_decisions_file(decisions)
    doing, done, log = load_tracker(tracker)
    target = (args.worklog_id or "").strip()
    row = None
    for item in doing:
        if item["ID"] != target:
            continue
        item["Ultima atualizacao UTC"] = now_human_utc()
        item["Proximo passo"] = normalize_cell(
            (args.next_step or "Aguardar priorizacao no roadmap para retomada.").strip()
        )
        item["Bloqueios"] = normalize_cell((args.blockers or "-").strip(), max_len=120)
        row = item
        break
    if row is None:
        raise SystemExit(f"Worklog ID nao encontrado em Doing: {target}")
    log.append(
        format_log_line(
            worklog_id=target,
            status="doing",
            summary=row["Tarefa"],
            next_step=row["Proximo passo"],
            blockers=row["Bloqueios"],
            context=args.context or "resolucao roadmap_pendente",
            notes=args.notes or "opcao=roadmap_pendente",
        )
    )
    save_tracker(tracker, doing, done, log)
    suggestion = (
        args.suggestion or ""
    ).strip() or f"Retomar tarefa pendente {target}: {row['Tarefa']}"
    registered = register_roadmap_decision(
        roadmap_path=roadmap,
        decisions_path=decisions,
        suggestion=suggestion,
        decision="pending",
        horizon="next",
        notes=args.notes or f"worklog={target}",
        suggestion_id=f"SG-{target}",
    )
    refresh_roadmap(roadmap_path=roadmap, decisions_path=decisions)
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "roadmap_file": str(roadmap),
                "decisions_file": str(decisions),
                "worklog_id": target,
                "action": "roadmap_pending",
                "added_ids": [registered["suggestion_id"]],
            },
            ensure_ascii=False,
        )
    )


def run_sync_roadmap(args: argparse.Namespace) -> None:
    tracker = Path(args.file)
    roadmap = Path(args.roadmap_file)
    decisions = Path(args.decisions_file)
    ensure_tracker_file(tracker)
    ensure_roadmap_file(roadmap)
    ensure_governed_decisions_file(decisions)
    doing, _, _ = load_tracker(tracker)
    rows = doing
    if args.worklog_id:
        rows = [row for row in rows if row["ID"] == args.worklog_id]
    if args.limit > 0:
        rows = rows[: args.limit]
    registered_ids: list[str] = []
    for row in rows:
        suggestion = f"Retomar tarefa pendente {row['ID']}: {row['Tarefa']}"
        registered = register_roadmap_decision(
            roadmap_path=roadmap,
            decisions_path=decisions,
            suggestion=suggestion,
            decision="pending",
            horizon="next",
            notes=f"sync-roadmap; worklog={row['ID']}",
            suggestion_id=f"SG-{row['ID']}",
        )
        registered_ids.append(str(registered["suggestion_id"]))
    refresh_roadmap(roadmap_path=roadmap, decisions_path=decisions)
    print(
        json.dumps(
            {
                "tracker_file": str(tracker),
                "roadmap_file": str(roadmap),
                "decisions_file": str(decisions),
                "added_count": len(registered_ids),
                "added_ids": registered_ids,
            },
            ensure_ascii=False,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gerencia AI WIP Tracker com doing/done/log incremental."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ensure = sub.add_parser("ensure")
    ensure.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    ensure.add_argument("--roadmap-file", default="docs/ROADMAP.md")
    ensure.add_argument("--decisions-file", default="docs/ROADMAP-DECISIONS.md")
    ensure.add_argument("--lessons-file", default="LICOES-APRENDIDAS.md")
    ensure.set_defaults(func=run_ensure)

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    list_cmd.set_defaults(func=run_list)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    preflight.add_argument("--message", default="")
    preflight.set_defaults(func=run_preflight)

    check = sub.add_parser("check")
    check.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    check.add_argument("--pending-action", default="")
    check.add_argument("--strict", type=int, choices=[0, 1], default=1)
    check.add_argument("--repo-root", default="")
    check.add_argument("--enforce-clean-checkpoint", type=int, choices=[0, 1], default=1)
    check.set_defaults(func=run_check)

    close_gate = sub.add_parser("close-gate")
    close_gate.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    close_gate.add_argument("--lessons-file", default="LICOES-APRENDIDAS.md")
    close_gate.set_defaults(func=run_close_gate)

    branch_check = sub.add_parser("branch-check")
    branch_check.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    branch_check.add_argument("--branch", default="")
    branch_check.add_argument("--owner", default="")
    branch_check.set_defaults(func=run_branch_check)

    start = sub.add_parser("start")
    start.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    start.add_argument("--message", required=True)
    start.add_argument("--scope", default="")
    start.add_argument("--branch", default="")
    start.add_argument("--owner", default="ai-agent")
    start.add_argument("--next-step", default="")
    start.add_argument("--progress", default="intake registrado")
    start.add_argument("--blockers", default="-")
    start.add_argument("--worklog-id", default="")
    start.set_defaults(func=run_start)

    update = sub.add_parser("update")
    update.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    update.add_argument("--worklog-id", required=True)
    update.add_argument("--progress", required=True)
    update.add_argument("--next-step", default="")
    update.add_argument("--blockers", default="-")
    update.add_argument("--message", default="")
    update.add_argument("--scope", default="")
    update.add_argument("--branch", default="")
    update.add_argument("--owner", default="")
    update.set_defaults(func=run_update)

    done = sub.add_parser("done")
    done.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    done.add_argument("--lessons-file", default="LICOES-APRENDIDAS.md")
    done.add_argument("--worklog-id", required=True)
    done.add_argument("--delivery", required=True)
    done.add_argument("--evidence", default="")
    done.add_argument("--lessons-decision", required=True, choices=["capturada", "sem_nova_licao"])
    done.add_argument("--lessons-summary", required=True)
    done.add_argument("--lessons-ids", default="")
    done.add_argument("--lessons-evidence", default="")
    done.set_defaults(func=run_done)

    roadmap_pending = sub.add_parser("roadmap-pending")
    roadmap_pending.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    roadmap_pending.add_argument("--roadmap-file", default="docs/ROADMAP.md")
    roadmap_pending.add_argument("--worklog-id", required=True)
    roadmap_pending.add_argument("--decisions-file", default="docs/ROADMAP-DECISIONS.md")
    roadmap_pending.add_argument("--suggestion", default="")
    roadmap_pending.add_argument(
        "--next-step", default="Aguardar priorizacao no roadmap para retomada."
    )
    roadmap_pending.add_argument("--blockers", default="-")
    roadmap_pending.add_argument("--context", default="resolucao roadmap_pendente")
    roadmap_pending.add_argument("--notes", default="opcao=roadmap_pendente")
    roadmap_pending.set_defaults(func=run_roadmap_pending)

    sync_roadmap = sub.add_parser("sync-roadmap")
    sync_roadmap.add_argument("--file", default="docs/AI-WIP-TRACKER.md")
    sync_roadmap.add_argument("--roadmap-file", default="docs/ROADMAP.md")
    sync_roadmap.add_argument("--decisions-file", default="docs/ROADMAP-DECISIONS.md")
    sync_roadmap.add_argument("--worklog-id", default="")
    sync_roadmap.add_argument("--limit", type=int, default=0)
    sync_roadmap.set_defaults(func=run_sync_roadmap)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
