from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path("docs/AI-STARTUP-GOVERNANCE-MANIFEST.md")
CHAT_CONTRACTS_REGISTER_PATH = Path("docs/AI-CHAT-CONTRACTS-REGISTER.md")
DEFAULT_REPORT_PATH = Path(".cache/ai/startup-session.md")

PENDING_MARKERS = (
    "<!-- ai-chat-contracts:pending:start -->",
    "<!-- ai-chat-contracts:pending:end -->",
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class ChatContractEntry:
    contract_id: str
    summary: str
    evidence: str
    owner: str
    destination: str
    status: str


def _read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_textual_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    return True


def _resolve_recursive_directory(repo_root: Path, relative_dir: str) -> list[str]:
    directory = (repo_root / relative_dir).resolve()
    if not directory.is_dir():
        return []
    resolved: list[str] = []
    for candidate in sorted(directory.rglob("*")):
        if _is_textual_file(candidate):
            resolved.append(candidate.relative_to(repo_root).as_posix())
    return resolved


def _resolve_ai_docs(repo_root: Path, relative_dir: str) -> list[str]:
    directory = (repo_root / relative_dir).resolve()
    if not directory.is_dir():
        return []
    resolved: list[str] = []
    for candidate in sorted(directory.rglob("AI-*")):
        if _is_textual_file(candidate):
            resolved.append(candidate.relative_to(repo_root).as_posix())
    return resolved


def resolve_startup_manifest_paths(repo_root: Path) -> list[str]:
    manifest_path = (repo_root / MANIFEST_PATH).resolve()
    content = _read_utf8(manifest_path)
    resolved: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        match = MARKDOWN_LINK_RE.search(line)
        if match is None:
            continue
        target = match.group(1).strip()
        candidate = (manifest_path.parent / target).resolve()
        relative_target = candidate.relative_to(repo_root).as_posix()
        if "todos os arquivos `AI-*` em" in line:
            resolved.update(_resolve_ai_docs(repo_root, relative_target))
            continue
        if "todos os arquivos em" in line:
            resolved.update(_resolve_recursive_directory(repo_root, relative_target))
            continue
        if _is_textual_file(candidate):
            resolved.add(relative_target)
    return sorted(resolved)


def _table_rows_between(content: str, start_marker: str, end_marker: str) -> list[list[str]]:
    if start_marker not in content or end_marker not in content:
        return []
    section = content.split(start_marker, 1)[1].split(end_marker, 1)[0]
    rows: list[list[str]] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        values = [item.strip() for item in line.strip("|").split("|")]
        if values and values[0] == "ID":
            continue
        rows.append(values)
    return rows


def load_pending_chat_contracts(repo_root: Path) -> list[ChatContractEntry]:
    register_path = (repo_root / CHAT_CONTRACTS_REGISTER_PATH).resolve()
    content = _read_utf8(register_path)
    entries: list[ChatContractEntry] = []
    for row in _table_rows_between(content, *PENDING_MARKERS):
        if len(row) != 6:
            continue
        entries.append(
            ChatContractEntry(
                contract_id=row[0],
                summary=row[1],
                evidence=row[2],
                owner=row[3],
                destination=row[4],
                status=row[5],
            )
        )
    return entries


def startup_session_payload(repo_root: Path) -> dict[str, Any]:
    resolved_paths = resolve_startup_manifest_paths(repo_root)
    pending_contracts = load_pending_chat_contracts(repo_root)
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "manifest_path": MANIFEST_PATH.as_posix(),
        "chat_contracts_register_path": CHAT_CONTRACTS_REGISTER_PATH.as_posix(),
        "resolved_paths": resolved_paths,
        "resolved_count": len(resolved_paths),
        "pending_chat_contracts": [asdict(entry) for entry in pending_contracts],
        "pending_chat_contract_count": len(pending_contracts),
        "default_report_path": DEFAULT_REPORT_PATH.as_posix(),
    }


def render_startup_session_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# AI Startup Session Report",
        "",
        f"- Gerado em: `{payload['generated_at']}`",
        f"- Manifest canonico: `{payload['manifest_path']}`",
        f"- Registro de contratos do chat: `{payload['chat_contracts_register_path']}`",
        f"- Total de arquivos textuais resolvidos: `{payload['resolved_count']}`",
        f"- Total de contratos do chat ainda pendentes: `{payload['pending_chat_contract_count']}`",
        "",
        "## Arquivos canonicos resolvidos",
        "",
    ]
    for relative in payload["resolved_paths"]:
        lines.append(f"- `{relative}`")
    lines.extend(["", "## Contratos do chat ainda pendentes", ""])
    pending = payload["pending_chat_contracts"]
    if not pending:
        lines.append("- nenhum contrato pendente registrado")
    else:
        lines.extend(
            [
                "| ID | Contrato resumido | Work item dono | Destino perene esperado |",
                "| --- | --- | --- | --- |",
            ]
        )
        for entry in pending:
            lines.append(
                f"| {entry['contract_id']} | {entry['summary']} | {entry['owner']} | {entry['destination']} |"
            )
    lines.extend(
        [
            "",
            "## Acoes obrigatorias da sessao",
            "",
            "- reler integralmente todos os arquivos resolvidos antes de operar",
            "- avisar o usuario se a tabela de contratos pendentes nao estiver vazia",
            "- cruzar branch, worktree e work item antes de decidir commit, PR ou redistribuicao",
        ]
    )
    return "\n".join(lines) + "\n"


def write_startup_session_report(repo_root: Path, *, out_path: Path | None = None) -> dict[str, Any]:
    payload = startup_session_payload(repo_root)
    report_path = (repo_root / (out_path or DEFAULT_REPORT_PATH)).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = render_startup_session_markdown(payload)
    report_path.write_text(report_text, encoding="utf-8")
    payload["report_path"] = report_path.relative_to(repo_root).as_posix()
    return payload


def payload_as_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
