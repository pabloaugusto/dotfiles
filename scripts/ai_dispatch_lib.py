from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_contract_paths import orchestration_root, registry_root, skills_root

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACKER = ROOT / "docs" / "AI-WIP-TRACKER.md"
DEFAULT_DECISIONS = ROOT / "docs" / "ROADMAP-DECISIONS.md"
DEFAULT_ROUTE_OUT = ROOT / ".cache" / "ai" / "route-output.json"
DEFAULT_INTAKE_OUT = ROOT / ".cache" / "ai" / "chat-intake.json"
DEFAULT_DELEGATION_OUT = ROOT / ".cache" / "ai" / "delegation-plan.md"
RISK_LEVELS = {"low", "medium", "high"}
PENDING_ACTION_GUIDANCE = {
    "concluir_primeiro": (
        "concluir o item em curso ou puxar apenas o work item minimo que o destrava "
        "diretamente"
    ),
    "roadmap_pendente": (
        "registrar a retomada no roadmap somente quando a rodada atual realmente nao "
        "vai continuar agora"
    ),
}
PYTHON_REVIEW_PATHS = ["scripts/*.py", "tests/python/*", ".githooks/ci/*.py", "pyproject.toml"]
POWERSHELL_REVIEW_PATHS = [
    "bootstrap/*.ps1",
    "bootstrap/**/*.ps1",
    "df/powershell/*.ps1",
    "df/powershell/**/*.ps1",
    "scripts/*.ps1",
    "scripts/**/*.ps1",
    "tests/powershell/*.ps1",
    "tests/powershell/**/*.ps1",
]
AUTOMATION_REVIEW_PATHS = [
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    "Taskfile.yml",
    "Dockerfile",
    "docker/**",
    "scripts/*.sh",
    "scripts/**/*.sh",
    "bootstrap/*.sh",
    "bootstrap/**/*.sh",
    "tests/bash/*",
    ".githooks/*",
]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML invalido em {path}")
    return payload


def load_toml(path: Path) -> dict:
    if tomllib is None:  # pragma: no cover
        return parse_basic_toml(path.read_text(encoding="utf-8"))
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"TOML invalido em {path}")
    return payload


def parse_basic_toml_value(raw: str) -> object:
    stripped = raw.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
    if stripped.startswith('"') and stripped.endswith('"'):
        return stripped[1:-1]
    if stripped.startswith("'") and stripped.endswith("'"):
        return stripped[1:-1]
    if stripped.isdigit():
        return int(stripped)
    return stripped


def parse_basic_toml(text: str) -> dict:
    data: dict[str, object] = {}
    current: dict[str, object] = data
    pending_key = ""
    pending_value_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if pending_key:
            pending_value_lines.append(line)
            if "]" in line:
                current[pending_key] = parse_basic_toml_value(" ".join(pending_value_lines))
                pending_key = ""
                pending_value_lines = []
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            section = data.setdefault(section_name, {})
            if not isinstance(section, dict):
                raise ValueError(f"Secao TOML invalida: {section_name}")
            current = section
            continue
        if "=" not in line:
            raise ValueError(f"Linha TOML invalida: {raw_line}")
        key, value = line.split("=", 1)
        normalized_key = key.strip()
        normalized_value = value.strip()
        if normalized_value.startswith("[") and not normalized_value.endswith("]"):
            pending_key = normalized_key
            pending_value_lines = [normalized_value]
            continue
        current[normalized_key] = parse_basic_toml_value(normalized_value)
    if pending_key:
        raise ValueError(f"Array TOML nao finalizado para a chave: {pending_key}")
    return data


def normalize_text(value: str) -> str:
    return " ".join(value.replace("|", "/").split())


def normalize_keyword_text(value: str) -> str:
    lowered = value.lower().replace("-", " ").replace("_", " ")
    lowered = re.sub(r"[^a-z0-9\u00c0-\u024f]+", " ", lowered)
    return " ".join(lowered.split())


def normalize_paths(raw: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        items = [item for item in raw if isinstance(item, str)]
    else:
        items = [item.strip() for item in re.split(r"[,\n]+", raw) if item.strip()]

    normalized: list[str] = []
    for item in items:
        path = item.strip().replace("\\", "/")
        if path.startswith("./"):
            path = path[2:]
        normalized.append(path)
    return normalized


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def path_matches(patterns: list[str], paths: list[str]) -> bool:
    for pattern in patterns:
        normalized_pattern = pattern.replace("\\", "/")
        for path in paths:
            if fnmatch.fnmatch(path, normalized_pattern) or normalized_pattern == path:
                return True
    return False


def keyword_matches(keywords: list[str], intent: str) -> bool:
    normalized_intent = normalize_keyword_text(intent)
    padded_intent = f" {normalized_intent} "
    tokens = set(normalized_intent.split())
    for keyword in keywords:
        normalized_keyword = normalize_keyword_text(str(keyword))
        if not normalized_keyword:
            continue
        if " " in normalized_keyword:
            if f" {normalized_keyword} " in padded_intent:
                return True
            continue
        if normalized_keyword in tokens:
            return True
    return False


def infer_risk(intent: str, fallback: str = "medium") -> tuple[str, str]:
    normalized_fallback = fallback if fallback in RISK_LEVELS else "medium"
    normalized = normalize_keyword_text(intent)
    high_keywords = {
        "auth",
        "secret",
        "secrets",
        "security",
        "sops",
        "age",
        "1password",
        "op",
        "ssh agent",
        "signing",
        "gh",
        "bootstrap",
    }
    medium_keywords = {
        "workflow",
        "ci",
        "taskfile",
        "wsl",
        "relink",
        "refresh",
        "roadmap",
        "lessons",
    }

    if any(keyword in normalized for keyword in high_keywords):
        return "high", "inferred"
    if any(keyword in normalized for keyword in medium_keywords):
        return "medium", "inferred"
    return normalized_fallback, "input" if fallback in RISK_LEVELS else "default"


def load_agent_defaults(repo_root: Path) -> dict[str, list[str]]:
    defaults: dict[str, list[str]] = {}
    for agent_file in sorted(registry_root(repo_root).glob("*.toml")):
        payload = load_toml(agent_file)
        agent_id = payload.get("id")
        default_skills = payload.get("default_skills", [])
        if isinstance(agent_id, str) and isinstance(default_skills, list):
            defaults[agent_id] = [value for value in default_skills if isinstance(value, str)]
    return defaults


def load_skill_names(repo_root: Path) -> set[str]:
    return {path.parent.name for path in skills_root(repo_root).glob("*/SKILL.md")}


def load_capability_matrix(repo_root: Path) -> dict[str, list[str]]:
    matrix = load_yaml(orchestration_root(repo_root) / "capability-matrix.yaml")
    defaults: dict[str, list[str]] = {}
    for entry in matrix.get("agents", []):
        if not isinstance(entry, dict):
            continue
        agent_id = entry.get("id")
        skills = entry.get("default_skills", [])
        if isinstance(agent_id, str) and isinstance(skills, list):
            defaults.setdefault(agent_id, [])
            defaults[agent_id].extend(value for value in skills if isinstance(value, str))
    return {key: dedupe(value) for key, value in defaults.items()}


def load_rules(
    policy: dict, intent: str, paths: list[str]
) -> tuple[list[str], list[str], list[dict]]:
    matched_gates: list[str] = []
    matched_conditions: list[str] = []
    matched_routes: list[dict] = []

    for gate in policy.get("conditional_mandatory_gates", []):
        if not isinstance(gate, dict):
            continue
        labels = []
        matched = False
        path_patterns = gate.get("when_any_path_matches", [])
        if isinstance(path_patterns, list) and path_matches(path_patterns, paths):
            matched = True
            labels.append("paths")
        keywords = gate.get("when_any_keyword_matches", [])
        if isinstance(keywords, list) and keyword_matches(keywords, intent):
            matched = True
            labels.append("keywords")
        if not matched:
            continue
        matched_conditions.append("+".join(labels) or "conditional")
        agents = gate.get("agents", [])
        if isinstance(agents, list):
            matched_gates.extend(str(agent) for agent in agents)

    for route in policy.get("routes", []):
        if not isinstance(route, dict):
            continue
        match = route.get("match", {})
        if not isinstance(match, dict):
            continue
        route_hit = False
        if isinstance(match.get("paths"), list) and path_matches(match["paths"], paths):
            route_hit = True
        if isinstance(match.get("keywords"), list) and keyword_matches(match["keywords"], intent):
            route_hit = True
        if route_hit:
            matched_routes.append(route)
    return dedupe(matched_gates), dedupe(matched_conditions), matched_routes


def build_validation_plan(paths: list[str], intent: str) -> list[str]:
    validations = [
        "task ai:validate",
        "task ai:lessons:check",
        "task ai:worklog:close:gate",
        "task ai:eval:smoke",
    ]

    if path_matches(["bootstrap/**", "df/**"], paths) or keyword_matches(
        ["bootstrap", "relink", "refresh", "symlink", "checkEnv"], intent
    ):
        validations.extend(["task test:integration", "task ci:lint", "task env:check"])

    if path_matches(
        [
            ".github/workflows/**",
            "Taskfile.yml",
            "docs/TASKS.md",
            "docs/WORKFLOWS.md",
            "scripts/validate_workflow_task_sync.py",
        ],
        paths,
    ) or keyword_matches(["workflow", "taskfile", "ci", "catalogo"], intent):
        validations.append("task ci:workflow:sync:check")

    if path_matches([".agents/**", ".codex/README.md", "docs/**", "scripts/**"], paths):
        validations.append("task test:unit:python")

    if path_matches(PYTHON_REVIEW_PATHS, paths):
        validations.extend(
            [
                "task lint:python",
                "task format:python:check",
                "task type:check",
                "task test:unit:python",
            ]
        )

    if path_matches(POWERSHELL_REVIEW_PATHS, paths):
        validations.extend(["task ci:lint", "task test:unit:powershell"])

    if path_matches(AUTOMATION_REVIEW_PATHS, paths):
        validations.extend(
            [
                "task ci:lint",
                "task lint:yaml",
                "task validate:actions",
                "task ci:workflow:sync:check",
            ]
        )

    return dedupe(validations)


def build_route_payload(
    *,
    intent: str,
    paths: list[str],
    risk: str,
    repo_root: Path = ROOT,
) -> dict:
    normalized_intent = normalize_text(intent)
    normalized_paths = normalize_paths(paths)
    normalized_risk = risk if risk in RISK_LEVELS else "medium"

    policy = load_yaml(orchestration_root(repo_root) / "routing-policy.yaml")
    agent_defaults = load_agent_defaults(repo_root)
    matrix_defaults = load_capability_matrix(repo_root)
    skill_names = load_skill_names(repo_root)

    for agent_id, skills in matrix_defaults.items():
        agent_defaults.setdefault(agent_id, [])
        agent_defaults[agent_id].extend(skills)
        agent_defaults[agent_id] = dedupe(agent_defaults[agent_id])

    matched_gates, matched_conditions, matched_routes = load_rules(
        policy, normalized_intent, normalized_paths
    )
    mandatory_gates = dedupe(
        [str(agent) for agent in policy.get("global_mandatory_gates", [])] + matched_gates
    )

    primary_agents: list[str] = []
    support_agents: list[str] = []
    matched_route_ids: list[str] = []
    for route in matched_routes:
        route_id = route.get("id")
        if isinstance(route_id, str):
            matched_route_ids.append(route_id)
        if isinstance(route.get("primary"), list):
            primary_agents.extend(str(agent) for agent in route["primary"])
        if isinstance(route.get("support"), list):
            support_agents.extend(str(agent) for agent in route["support"])

    if not primary_agents:
        fallback = (
            "orchestrator" if "orchestrator" in agent_defaults else "repo-governance-authority"
        )
        primary_agents.append(fallback)
        if fallback == "orchestrator":
            support_agents.extend(
                ["repo-governance-authority", "architecture-modernization-authority"]
            )

    required_agents = dedupe(mandatory_gates + primary_agents + support_agents)
    required_skills: list[str] = []
    for agent in required_agents:
        required_skills.extend(agent_defaults.get(agent, []))
    required_skills = [skill for skill in dedupe(required_skills) if skill in skill_names]

    notes = "; ".join(
        [
            f"rotas={', '.join(matched_route_ids) if matched_route_ids else 'fallback'}",
            f"condicoes={', '.join(matched_conditions) if matched_conditions else 'nenhuma'}",
        ]
    )

    return {
        "task_card": {
            "intent": normalized_intent,
            "risk": normalized_risk,
            "paths": normalized_paths,
            "required_agents": required_agents,
            "required_skills": required_skills,
            "notes": notes,
        },
        "delegation_plan": {
            "primary_agents": dedupe(primary_agents),
            "support_agents": dedupe(support_agents),
            "mandatory_gates": mandatory_gates,
            "validation": build_validation_plan(normalized_paths, normalized_intent),
            "roadmap_followups": [],
        },
        "matched_routes": matched_route_ids,
        "matched_conditions": matched_conditions,
        "used_fallback": not bool(matched_routes),
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def current_branch(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def run_worklog(*, repo_root: Path, args: list[str], expect_json: bool = True) -> dict | str:
    command = [sys.executable, str(repo_root / "scripts" / "ai-worklog.py"), *args]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Falha ao executar ai-worklog.py:\n"
            f"cmd={' '.join(command)}\n"
            f"stdout={completed.stdout}\n"
            f"stderr={completed.stderr}"
        )
    if not expect_json:
        return completed.stdout
    return json.loads(completed.stdout.strip() or "{}")


def build_intake_payload(
    *,
    message: str,
    paths: list[str],
    risk: str,
    route: bool,
    pending_action: str,
    tracker_file: Path,
    worklog_id: str,
    decisions_file: Path,
    repo_root: Path = ROOT,
) -> dict:
    if not normalize_text(message):
        raise ValueError("message vazio")
    if pending_action not in {"", "concluir_primeiro", "roadmap_pendente"}:
        raise ValueError("pending_action invalido")

    inferred_risk, risk_source = infer_risk(message, fallback=risk)
    preflight = run_worklog(
        repo_root=repo_root,
        args=[
            "check",
            "--file",
            str(tracker_file),
            "--pending-action",
            pending_action,
            "--strict",
            "1",
        ],
    )

    current_worklog_id = worklog_id
    sync_action = "none"
    if pending_action == "roadmap_pendente" and preflight.get("pending_count", 0):
        if current_worklog_id:
            run_worklog(
                repo_root=repo_root,
                args=[
                    "roadmap-pending",
                    "--file",
                    str(tracker_file),
                    "--worklog-id",
                    current_worklog_id,
                    "--decisions-file",
                    str(decisions_file),
                    "--suggestion",
                    normalize_text(message),
                ],
            )
            sync_action = "roadmap_pending_updated"
        else:
            run_worklog(
                repo_root=repo_root,
                args=["sync-roadmap", "--file", str(tracker_file)],
            )
            sync_action = "roadmap_synced"

    if current_worklog_id:
        run_worklog(
            repo_root=repo_root,
            args=[
                "update",
                "--file",
                str(tracker_file),
                "--worklog-id",
                current_worklog_id,
                "--progress",
                "retomada via ai-chat-intake",
                "--message",
                normalize_text(message),
                "--scope",
                ",".join(paths),
            ],
        )
    else:
        started = run_worklog(
            repo_root=repo_root,
            args=[
                "start",
                "--file",
                str(tracker_file),
                "--message",
                normalize_text(message),
                "--scope",
                ",".join(paths),
                "--branch",
                current_branch(repo_root),
                "--progress",
                "intake registrado",
            ],
        )
        current_worklog_id = str(started.get("worklog_id", "")).strip()

    route_payload = None
    if route:
        route_payload = build_route_payload(
            intent=message, paths=paths, risk=inferred_risk, repo_root=repo_root
        )

    return {
        "message": normalize_text(message),
        "paths": normalize_paths(paths),
        "risk": inferred_risk,
        "risk_source": risk_source,
        "pending_action": pending_action or "-",
        "pending_action_guidance": PENDING_ACTION_GUIDANCE if pending_action else {},
        "preflight": preflight,
        "worklog_id": current_worklog_id,
        "tracker_file": str(tracker_file),
        "decisions_file": str(decisions_file),
        "sync_action": sync_action,
        "route_enabled": route,
        "route_payload": route_payload,
    }


def render_delegation_markdown(payload: dict) -> str:
    route_payload = payload.get("route_payload")
    if not isinstance(route_payload, dict):
        raise ValueError("route_payload ausente para gerar delegation plan")

    task_card = route_payload["task_card"]
    plan = route_payload["delegation_plan"]
    lines = [
        "# Delegation Plan",
        "",
        "## Intake",
        "",
        f"- Mensagem: {payload['message']}",
        f"- Worklog: `{payload['worklog_id']}`",
        f"- Risco: `{payload['risk']}`",
        f"- Acao de pendencia: `{payload['pending_action']}`",
        (
            "- Semantica da acao: "
            + payload.get("pending_action_guidance", {}).get(payload.get("pending_action"), "-")
        ),
        "",
        "## Task Card",
        "",
        f"- Intent: {task_card['intent']}",
        f"- Paths: `{', '.join(task_card['paths']) if task_card['paths'] else '(sem paths)'}`",
        f"- Required agents: `{', '.join(task_card['required_agents'])}`",
        f"- Required skills: `{', '.join(task_card['required_skills'])}`",
        f"- Notes: {task_card['notes']}",
        "",
        "## Delegation Plan",
        "",
        f"- Primary agents: `{', '.join(plan['primary_agents'])}`",
        f"- Support agents: `{', '.join(plan['support_agents']) if plan['support_agents'] else '(nenhum)'}`",
        f"- Mandatory gates: `{', '.join(plan['mandatory_gates'])}`",
        "",
        "## Validation",
        "",
    ]
    for task in plan["validation"]:
        lines.append(f"- `{task}`")
    lines.extend(
        [
            "",
            "## Route Metadata",
            "",
            f"- Matched routes: `{', '.join(route_payload.get('matched_routes', [])) or 'fallback'}`",
            f"- Matched conditions: `{', '.join(route_payload.get('matched_conditions', [])) or 'nenhuma'}`",
            f"- Used fallback: `{route_payload.get('used_fallback', False)}`",
        ]
    )
    return "\n".join(lines) + "\n"
