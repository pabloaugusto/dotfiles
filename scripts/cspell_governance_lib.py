from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from scripts.ai_contract_paths import ROOT
from scripts.ai_lessons_lib import (
    extract_between,
    normalize_cell,
    now_human_utc,
    parse_table,
    render_table,
    replace_between,
    write_text_lf,
)
from scripts.ai_roadmap_lib import register_roadmap_decision

PACKAGES = [
    "cspell@8.19.4",
    "@cspell/dict-pt-br",
    "@cspell/dict-python",
    "@cspell/dict-bash",
    "@cspell/dict-shell",
    "@cspell/dict-software-terms",
    "@cspell/dict-fullstack",
    "@cspell/dict-k8s",
    "@cspell/dict-docker",
    "@cspell/dict-companies",
    "@cspell/dict-fonts",
    "@cspell/dict-sql",
    "@cspell/dict-powershell",
    "@cspell/dict-git",
    "@cspell/dict-filetypes",
    "@cspell/dict-google",
    "@cspell/dict-markdown",
    "@cspell/dict-node",
    "@cspell/dict-npm",
]

DEFAULT_CONFIG_PATH = ROOT / ".cspell.json"
DEFAULT_PROJECT_WORDS_PATH = ROOT / ".cspell" / "project-words.txt"
DEFAULT_LEDGER_PATH = ROOT / "docs" / "AI-ORTHOGRAPHY-LEDGER.md"
DEFAULT_ROADMAP_PATH = ROOT / "ROADMAP.md"
DEFAULT_DECISIONS_PATH = ROOT / "docs" / "ROADMAP-DECISIONS.md"

RECORDS_START = "<!-- ai-orthography:records:start -->"
RECORDS_END = "<!-- ai-orthography:records:end -->"
RECORD_HEADERS = [
    "Data/Hora UTC",
    "Worklog ID",
    "Revisor",
    "Status",
    "Arquivo",
    "Achados",
    "Evidencia",
]
ALLOWED_REVIEW_STATUSES = {"aprovado", "reprovado"}

UNKNOWN_WORD_RE = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+):(?P<column>\d+)\s+-\s+Unknown word \((?P<word>[^)]+)\)",
    re.MULTILINE,
)


@dataclass(frozen=True)
class OrthographyFinding:
    path: str
    line: int
    column: int
    word: str


def orthography_ledger_template() -> str:
    updated_at = now_human_utc()
    return f"""# AI Orthography Ledger

Atualizado em: {updated_at}

Registro consultivo do agente Pascoalete para ortografia e higiene vocabular.

## Regras operacionais

- O parecer ortografico e consultivo: nao bloqueia PR, branch, commit, worktree,
  deploy, release ou `done` tecnico.
- Toda mudanca versionada pode receber parecer de Pascoalete; quando houver
  falha nao corrigida, o problema deve virar pendencia rastreavel no backlog
  vigente.
- O dicionario local em [`.cspell/project-words.txt`](../.cspell/project-words.txt)
  nao deve repetir palavras ja cobertas pelos dicionarios importados.
- A fonte de verdade da configuracao do `cspell` e [`.cspell.json`](../.cspell.json).

## Registros

<!-- ai-orthography:records:start -->
| Data/Hora UTC | Worklog ID | Revisor | Status | Arquivo | Achados | Evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - |
<!-- ai-orthography:records:end -->
"""


def ensure_orthography_ledger(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(path, orthography_ledger_template())


def load_orthography_rows(path: Path) -> list[dict[str, str]]:
    ensure_orthography_ledger(path)
    raw = path.read_text(encoding="utf-8")
    section = extract_between(raw, RECORDS_START, RECORDS_END, label=str(path))
    return parse_table(section, RECORD_HEADERS, label=str(path))


def save_orthography_rows(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_orthography_ledger(path)
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


def build_cspell_command(args: list[str]) -> list[str]:
    command = ["uvx", "--from", "nodejs-wheel", "npm", "exec", "--yes"]
    for package in PACKAGES:
        command.extend(["--package", package])
    command.extend(["--", "cspell", *args])
    return command


def run_cspell(args: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        build_cspell_command(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_unknown_word_findings(output: str) -> list[OrthographyFinding]:
    findings: list[OrthographyFinding] = []
    for match in UNKNOWN_WORD_RE.finditer(output or ""):
        findings.append(
            OrthographyFinding(
                path=match.group("path").replace("\\", "/"),
                line=int(match.group("line")),
                column=int(match.group("column")),
                word=match.group("word"),
            )
        )
    return findings


def load_cspell_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["__config_source__"] = str(path.resolve())
    return payload


def local_dictionary_names(config: dict[str, Any], *, project_words_path: Path) -> set[str]:
    names: set[str] = set()
    target = project_words_path.resolve()
    config_root = DEFAULT_CONFIG_PATH.parent
    config_source = config.get("__config_source__")
    if isinstance(config_source, str):
        config_root = Path(config_source).resolve().parent
    for definition in config.get("dictionaryDefinitions", []):
        if not isinstance(definition, dict):
            continue
        raw_path = definition.get("path")
        name = definition.get("name")
        if not isinstance(raw_path, str) or not isinstance(name, str):
            continue
        definition_path = (config_root / raw_path).resolve()
        if definition_path == target:
            names.add(name)
    return names


def build_external_only_config(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    project_words_path: Path = DEFAULT_PROJECT_WORDS_PATH,
) -> dict[str, Any]:
    config = load_cspell_config(config_path)
    local_names = local_dictionary_names(config, project_words_path=project_words_path)
    if local_names:
        config["dictionaryDefinitions"] = [
            definition
            for definition in config.get("dictionaryDefinitions", [])
            if not (
                isinstance(definition, dict)
                and isinstance(definition.get("name"), str)
                and definition["name"] in local_names
            )
        ]
        config["dictionaries"] = [
            dictionary
            for dictionary in config.get("dictionaries", [])
            if dictionary not in local_names
        ]
    return config


def check_word_with_config(
    *,
    word: str,
    config_payload: dict[str, Any],
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> bool:
    active_runner = runner or (lambda args: run_cspell(args))
    with tempfile.TemporaryDirectory(prefix="cspell-governance-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        text_path = temp_dir / "probe.txt"
        config_path = temp_dir / "cspell.json"
        text_path.write_text(word + "\n", encoding="utf-8")
        config_path.write_text(json.dumps(config_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        result = active_runner(
            ["lint", str(text_path), "--config", str(config_path), "--no-progress", "--no-summary"]
        )
        return result.returncode == 0


def load_project_words(path: Path = DEFAULT_PROJECT_WORDS_PATH) -> list[str]:
    if not path.exists():
        return []
    words = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [word for word in words if word]


def save_project_words(words: list[str], path: Path = DEFAULT_PROJECT_WORDS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    deduped = sorted({word.strip() for word in words if word.strip()}, key=str.casefold)
    write_text_lf(path, "\n".join(deduped) + ("\n" if deduped else ""))


def find_redundant_project_words(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    project_words_path: Path = DEFAULT_PROJECT_WORDS_PATH,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> list[str]:
    external_config = build_external_only_config(
        config_path=config_path, project_words_path=project_words_path
    )
    redundant: list[str] = []
    for word in load_project_words(project_words_path):
        if check_word_with_config(word=word, config_payload=external_config, runner=runner):
            redundant.append(word)
    return redundant


def remove_project_words(words_to_remove: list[str], path: Path = DEFAULT_PROJECT_WORDS_PATH) -> int:
    current = load_project_words(path)
    next_words = [word for word in current if word not in set(words_to_remove)]
    if next_words == current:
        return 0
    save_project_words(next_words, path)
    return len(current) - len(next_words)


def add_project_words(words_to_add: list[str], path: Path = DEFAULT_PROJECT_WORDS_PATH) -> int:
    current = load_project_words(path)
    merged = current + [word for word in words_to_add if word not in current]
    save_project_words(merged, path)
    return len(set(merged)) - len(set(current))


def findings_by_path(findings: list[OrthographyFinding]) -> dict[str, list[OrthographyFinding]]:
    grouped: dict[str, list[OrthographyFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.path, []).append(finding)
    return grouped


def summarize_findings(findings: list[OrthographyFinding], *, limit: int = 8) -> str:
    if not findings:
        return "sem achados"
    words = [finding.word for finding in findings]
    listed = ", ".join(words[:limit])
    if len(words) > limit:
        listed += f" (+{len(words) - limit})"
    return normalize_cell(listed, max_len=220)


def record_orthography_review(
    *,
    ledger_path: Path,
    worklog_id: str,
    reviewer: str,
    file_path: str,
    status: str,
    findings: list[OrthographyFinding],
    evidence: str = "",
) -> None:
    normalized_status = status.strip().lower()
    if normalized_status not in ALLOWED_REVIEW_STATUSES:
        raise ValueError("Status ortografico invalido. Use aprovado ou reprovado.")

    normalized_file = file_path.replace("\\", "/").strip()
    rows = [
        row
        for row in load_orthography_rows(ledger_path)
        if not (
            row["Worklog ID"] == worklog_id
            and row["Revisor"] == reviewer
            and row["Arquivo"] == normalized_file
        )
    ]
    rows.insert(
        0,
        {
            "Data/Hora UTC": now_human_utc(),
            "Worklog ID": normalize_cell(worklog_id, max_len=80),
            "Revisor": reviewer,
            "Status": normalized_status,
            "Arquivo": normalize_cell(normalized_file, max_len=220),
            "Achados": summarize_findings(findings),
            "Evidencia": normalize_cell(evidence, max_len=220),
        },
    )
    save_orthography_rows(ledger_path, rows)


def orthography_suggestion_id(worklog_id: str) -> str:
    return f"SG-ORTHO-{re.sub(r'[^A-Za-z0-9-]+', '-', worklog_id.strip()).strip('-')}"


def register_orthography_backlog(
    *,
    worklog_id: str,
    failing_paths: list[str],
    roadmap_path: Path = DEFAULT_ROADMAP_PATH,
    decisions_path: Path = DEFAULT_DECISIONS_PATH,
) -> str:
    suggestion = (
        f"Corrigir pendencias ortograficas remanescentes do worklog `{worklog_id}` "
        f"em {', '.join(failing_paths[:5])}"
    )
    if len(failing_paths) > 5:
        suggestion += f" e mais {len(failing_paths) - 5} arquivo(s)"
    payload = register_roadmap_decision(
        roadmap_path=roadmap_path,
        decisions_path=decisions_path,
        suggestion=suggestion,
        decision="accepted",
        horizon="next",
        change_type="fix",
        notes=(
            "Pendencia automatica criada por Pascoalete apos review consultivo "
            "reprovado sem correcao automatica."
        ),
        suggestion_id=orthography_suggestion_id(worklog_id),
    )
    return str(payload["suggestion_id"])


def clear_orthography_backlog(
    *,
    worklog_id: str,
    roadmap_path: Path = DEFAULT_ROADMAP_PATH,
    decisions_path: Path = DEFAULT_DECISIONS_PATH,
) -> str:
    payload = register_roadmap_decision(
        roadmap_path=roadmap_path,
        decisions_path=decisions_path,
        suggestion=(
            f"Corrigir pendencias ortograficas remanescentes do worklog `{worklog_id}`"
        ),
        decision="discarded",
        horizon="next",
        change_type="fix",
        notes="Pendencia ortografica descartada automaticamente porque o escopo atual ficou limpo.",
        suggestion_id=orthography_suggestion_id(worklog_id),
    )
    return str(payload["suggestion_id"])


def review_paths(
    *,
    worklog_id: str,
    reviewer: str,
    paths: list[str],
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    config_path: Path = DEFAULT_CONFIG_PATH,
    project_words_path: Path = DEFAULT_PROJECT_WORDS_PATH,
    roadmap_path: Path = DEFAULT_ROADMAP_PATH,
    decisions_path: Path = DEFAULT_DECISIONS_PATH,
    register_pending: bool = True,
    fix_dictionary: bool = True,
) -> dict[str, Any]:
    normalized_paths = [path for path in normalize_path_list(paths) if (ROOT / path).exists()]
    redundant_words = find_redundant_project_words(
        config_path=config_path, project_words_path=project_words_path
    )
    removed = 0
    if fix_dictionary and redundant_words:
        removed = remove_project_words(redundant_words, project_words_path)

    lint_args = ["lint", *normalized_paths, "--config", str(config_path), "--gitignore", "--dot"]
    lint_result = run_cspell(lint_args)
    findings = parse_unknown_word_findings((lint_result.stdout or "") + "\n" + (lint_result.stderr or ""))
    grouped = findings_by_path(findings)

    reviewed_paths = normalized_paths or ["."]
    for file_path in reviewed_paths:
        file_findings = grouped.get(file_path, [])
        status = "reprovado" if file_findings else "aprovado"
        evidence = "task spell:check"
        if removed:
            evidence += f"; dicionario higienizado ({removed} removida(s))"
        record_orthography_review(
            ledger_path=ledger_path,
            worklog_id=worklog_id,
            reviewer=reviewer,
            file_path=file_path,
            status=status,
            findings=file_findings,
            evidence=evidence,
        )

    backlog_id = ""
    failing_paths = sorted(grouped)
    if failing_paths and register_pending and worklog_id.strip():
        backlog_id = register_orthography_backlog(
            worklog_id=worklog_id,
            failing_paths=failing_paths,
            roadmap_path=roadmap_path,
            decisions_path=decisions_path,
        )
    elif not failing_paths and worklog_id.strip():
        backlog_id = clear_orthography_backlog(
            worklog_id=worklog_id,
            roadmap_path=roadmap_path,
            decisions_path=decisions_path,
        )

    return {
        "ok": not failing_paths,
        "reviewer": reviewer,
        "paths": reviewed_paths,
        "findings": [
            {
                "path": finding.path,
                "line": finding.line,
                "column": finding.column,
                "word": finding.word,
            }
            for finding in findings
        ],
        "redundant_words": redundant_words,
        "removed_redundant_words": removed,
        "backlog_id": backlog_id,
    }
