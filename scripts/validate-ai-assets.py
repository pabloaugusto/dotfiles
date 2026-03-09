#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_contract_paths import (
    cards_root,
    config_path,
    evals_root,
    legacy_codex_readme,
    legacy_codex_root,
    orchestration_root,
    registry_root,
    rules_root,
    skills_root,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for Python < 3.11
    tomllib = None  # type: ignore[assignment]


REQUIRED_FILES = [
    "AGENTS.md",
    "LICOES-APRENDIDAS.md",
    "docs/AI-AGENTS-CATALOG.md",
    "docs/AI-DELEGATION-FLOW.md",
    "docs/AI-GOVERNANCE-AND-REGRESSION.md",
    "docs/AI-ORTHOGRAPHY-LEDGER.md",
    "docs/AI-REVIEW-LEDGER.md",
    "docs/AI-SKILLS-CATALOG.md",
    "docs/AI-SOURCE-AUDIT.md",
    "docs/ai-operating-model.md",
    "docs/AI-WIP-TRACKER.md",
    "ROADMAP.md",
    "docs/ROADMAP-DECISIONS.md",
    "docs/TASKS.md",
    "docs/WORKFLOWS.md",
    "config/ai/platforms.yaml",
    "config/ai/platforms.local.yaml.tpl",
    "config/ai/agents.yaml",
    "config/ai/contracts.yaml",
    ".agents/README.md",
    ".agents/config.toml",
    ".codex/README.md",
    ".agents/orchestration/capability-matrix.yaml",
    ".agents/orchestration/routing-policy.yaml",
    ".agents/orchestration/task-card.schema.json",
    ".agents/orchestration/delegation-plan.schema.json",
    ".agents/rules/default.rules",
    ".agents/rules/ci.rules",
    ".agents/rules/security.rules",
    ".agents/evals/scenarios/smoke.md",
    ".agents/evals/scenarios/regression.md",
    ".agents/evals/scenarios/security.md",
    ".agents/evals/datasets/routing.jsonl",
    ".agents/evals/datasets/governance.jsonl",
    "scripts/ai-lessons.py",
    "scripts/ai_lessons_lib.py",
    "scripts/ai-worklog.py",
    "scripts/ai-chat-intake.py",
    "scripts/ai-route.py",
    "scripts/ai-delegate.py",
    "scripts/ai-eval-smoke.py",
    "scripts/ai-review.py",
    "scripts/ai_review_lib.py",
    "scripts/ai-control-plane.py",
    "scripts/ai_control_plane_lib.py",
    "scripts/atlassian_platform_lib.py",
    "scripts/run-ai-atlassian-check.ps1",
    "scripts/cspell-governance.py",
    "scripts/cspell_governance_lib.py",
    "scripts/validate_workflow_task_sync.py",
    "scripts/validate-ai-assets.ps1",
]

TRACKER_MARKERS = [
    "<!-- ai-worklog:doing:start -->",
    "<!-- ai-worklog:doing:end -->",
    "<!-- ai-worklog:done:start -->",
    "<!-- ai-worklog:done:end -->",
    "<!-- ai-worklog:log:start -->",
    "<!-- ai-worklog:log:end -->",
]

DECISIONS_MARKERS = [
    "<!-- roadmap:suggestions:start -->",
    "<!-- roadmap:suggestions:end -->",
    "<!-- roadmap:cycles:start -->",
    "<!-- roadmap:cycles:end -->",
    "<!-- roadmap:autolog:start -->",
    "<!-- roadmap:autolog:end -->",
]

ROADMAP_MARKERS = [
    "<!-- roadmap:backlog:start -->",
    "<!-- roadmap:backlog:end -->",
    "<!-- roadmap:priority:start -->",
    "<!-- roadmap:priority:end -->",
    "<!-- roadmap:now:start -->",
    "<!-- roadmap:now:end -->",
    "<!-- roadmap:next:start -->",
    "<!-- roadmap:next:end -->",
    "<!-- roadmap:later:start -->",
    "<!-- roadmap:later:end -->",
    "<!-- roadmap:pending:start -->",
    "<!-- roadmap:pending:end -->",
]

LESSONS_MARKERS = [
    "<!-- ai-lessons:catalog:start -->",
    "<!-- ai-lessons:catalog:end -->",
    "<!-- ai-lessons:reviews:start -->",
    "<!-- ai-lessons:reviews:end -->",
]

REQUIRED_AGENT_HEADINGS = [
    "## Objetivo",
    "## Quando usar",
    "## Skill principal",
    "## Entradas",
    "## Saidas",
    "## Fluxo",
    "## Guardrails",
    "## Validacao recomendada",
    "## Criterios de conclusao",
]

REQUIRED_SKILL_HEADINGS = [
    "## Objetivo",
    "## Fluxo",
    "## Regras",
    "## Entregas esperadas",
    "## Validacao",
    "## Referencias",
]

AGENTS_REQUIRED_SNIPPETS = [
    "Nunca operar por amostragem",
    "docs/AI-SOURCE-AUDIT.md",
    "Manter o item ativo em `Doing` durante toda a execucao relevante",
    "Nenhum `done` e valido sem revisar `LICOES-APRENDIDAS.md`",
    "Acionar os gates paralelos obrigatorios de arquitetura/modernizacao",
]

OPERATING_MODEL_REQUIRED_SNIPPETS = [
    "### 5. Auditoria exaustiva antes de reuso cross-repo",
    "### Fronteira entre `.agents/` e adaptadores de assistente",
    "### Camada 2.1. Registry declarativo do repo",
    "### Camada 2.2. Orquestracao, rules e evals",
]

LESSONS_REQUIRED_SNIPPETS = [
    "## LA-001 - Auditoria exaustiva antes de importacao cross-repo",
    "## LA-004 - Toda finalizacao de worklog exige revisao explicita de licoes",
    "## LA-006 - Arquitetura e modernizacao precisam de um gate paralelo permanente",
    "## LA-007 - Integracoes criticas exigem guardiao proprio",
]

SOURCE_AUDIT_REQUIRED_SNIPPETS = [
    "## Escopo da auditoria",
    "## Repositorios auditados",
    "## Inventario consolidado por dominio",
    "## Gaps no repo atual",
    "## Decisoes de importacao",
    "## Fronteira entre",
    "## Regra operacional permanente",
]

CATALOG_REQUIRED_SNIPPETS = {
    "docs/AI-AGENTS-CATALOG.md": [
        "architecture-modernization-authority",
        "critical-integrations-guardian",
        "lessons-governance-curator",
        "pascoalete",
        "python-reviewer",
        "powershell-reviewer",
        "automation-reviewer",
    ],
    "docs/AI-SKILLS-CATALOG.md": [
        "$dotfiles-architecture-modernization",
        "$dotfiles-critical-integrations",
        "$dotfiles-lessons-governance",
        "$dotfiles-orthography-review",
        "$task-routing-and-decomposition",
        "$dotfiles-python-review",
        "$dotfiles-powershell-review",
        "$dotfiles-automation-review",
    ],
    "docs/AI-DELEGATION-FLOW.md": [
        "architecture-modernization-authority",
        "critical-integrations-guardian",
        "lessons-governance-curator",
        "pascoalete",
        "orchestrator",
        "python-reviewer",
        "powershell-reviewer",
        "automation-reviewer",
    ],
    "docs/AI-GOVERNANCE-AND-REGRESSION.md": [
        "task ai:lessons:check",
        "task ai:review:check",
        "task spell:review",
        "architecture-modernization-authority",
        "critical-integrations-guardian",
        "task ai:eval:smoke",
        "task ci:workflow:sync:check",
        "pascoalete",
        "python-reviewer",
        "powershell-reviewer",
        "automation-reviewer",
    ],
    "docs/TASKS.md": [
        "### `ai:chat:intake`",
        "### `ai:route`",
        "### `ai:delegate`",
        "### `ai:review:record`",
        "### `ai:review:check`",
        "### `ai:control-plane:show`",
        "### `ai:atlassian:check`",
        "### `spell:review:windows`",
        "### `spell:dictionary:audit:windows`",
        "### `ci:workflow:sync:check`",
    ],
    "docs/WORKFLOWS.md": [
        "### `ai-governance.yml`",
        "### `bootstrap-integration.yml`",
        "### `pr-validate.yml`",
        "spell:review",
    ],
}

REQUIRED_REGISTRY_AGENT_KEYS = [
    "id",
    "tier",
    "purpose",
    "default_skills",
    "triggers",
    "output_contract",
    "handoff_to",
]

REQUIRED_AI_CONFIG_SECTIONS = ["skills", "agents", "orchestration", "rules", "evals"]


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
    if not match:
        return None
    return match.group(1).strip().strip("'\"")


def normalize_contract_text(value: str) -> str:
    normalized = value or ""
    normalized = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", normalized)
    normalized = normalized.replace("`", "")
    return " ".join(normalized.split())


def require_markers(content: str, markers: list[str], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in content:
            failures.append(f"Marcador obrigatorio ausente em {label}: {marker}")


def require_snippets(content: str, snippets: list[str], label: str, failures: list[str]) -> None:
    normalized_content = normalize_contract_text(content)
    for snippet in snippets:
        if normalize_contract_text(snippet) not in normalized_content:
            failures.append(f"Trecho obrigatorio ausente em {label}: {snippet}")


def validate_skill_dir(skill_dir: Path, failures: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    agent_yaml = skill_dir / "agents" / "openai.yaml"
    references_dir = skill_dir / "references"

    if not skill_md.is_file():
        failures.append(f"SKILL.md ausente em {skill_dir.name}")
        return
    if not agent_yaml.is_file():
        failures.append(f"agents/openai.yaml ausente em {skill_dir.name}")
    if not references_dir.is_dir():
        failures.append(f"references/ ausente em {skill_dir.name}")

    skill_content = skill_md.read_text(encoding="utf-8")
    if "TODO" in skill_content:
        failures.append(f"Placeholder TODO encontrado em {skill_dir.name}/SKILL.md")

    frontmatter_match = re.match(r"(?s)\A---\r?\n(?P<front>.*?)\r?\n---", skill_content)
    if not frontmatter_match:
        failures.append(f"Frontmatter invalido em {skill_dir.name}/SKILL.md")
        return

    frontmatter = frontmatter_match.group("front")
    skill_name = frontmatter_value(frontmatter, "name")
    description = frontmatter_value(frontmatter, "description")

    if not skill_name:
        failures.append(f"name ausente em {skill_dir.name}/SKILL.md")
    elif skill_name != skill_dir.name:
        failures.append(f"name '{skill_name}' difere da pasta '{skill_dir.name}'")
    elif not re.match(r"^[a-z0-9-]+$", skill_name):
        failures.append(f"name invalido em {skill_dir.name}/SKILL.md")

    if not description:
        failures.append(f"description ausente em {skill_dir.name}/SKILL.md")

    for heading in REQUIRED_SKILL_HEADINGS:
        if heading not in skill_content:
            failures.append(f"Heading obrigatorio ausente em {skill_dir.name}/SKILL.md: {heading}")

    if agent_yaml.is_file():
        agent_content = agent_yaml.read_text(encoding="utf-8")
        if not re.search(r"(?m)^interface:\s*$", agent_content):
            failures.append(f"interface ausente em {skill_dir.name}/agents/openai.yaml")
        expected_skill_ref = f"${skill_dir.name}"
        default_prompt_re = rf'(?m)^\s*default_prompt:\s*".*{re.escape(expected_skill_ref)}.*"\s*$'
        if not re.search(default_prompt_re, agent_content):
            failures.append(
                f"default_prompt precisa mencionar {expected_skill_ref} em {skill_dir.name}/agents/openai.yaml"
            )
        short_match = re.search(r'(?m)^\s*short_description:\s*"(?P<value>.+)"\s*$', agent_content)
        if not short_match:
            failures.append(f"short_description ausente em {skill_dir.name}/agents/openai.yaml")
        else:
            short_len = len(short_match.group("value"))
            if short_len < 25 or short_len > 64:
                failures.append(
                    f"short_description fora do intervalo 25-64 em {skill_dir.name}/agents/openai.yaml"
                )


def validate_registry_agent(agent_file: Path, skill_names: set[str], failures: list[str]) -> None:
    try:
        payload = parse_toml_text(agent_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        failures.append(f"TOML invalido em {agent_file.as_posix()}: {exc}")
        return
    for key in REQUIRED_REGISTRY_AGENT_KEYS:
        if key not in payload:
            failures.append(f"Chave obrigatoria ausente em {agent_file.as_posix()}: {key}")
    for list_key in ("default_skills", "triggers", "handoff_to"):
        value = payload.get(list_key)
        if value is not None and not isinstance(value, list):
            failures.append(f"{list_key} deve ser lista em {agent_file.as_posix()}")
    default_skills = payload.get("default_skills", [])
    if isinstance(default_skills, list):
        for skill_name in default_skills:
            if isinstance(skill_name, str) and skill_name not in skill_names:
                failures.append(
                    f"default_skill inexistente em {agent_file.as_posix()}: {skill_name}"
                )


def validate_ai_config(repo_root: Path, failures: list[str]) -> None:
    config_file = config_path(repo_root)
    try:
        payload = parse_toml_text(config_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        failures.append(f"TOML invalido em .agents/config.toml: {exc}")
        return
    for section in REQUIRED_AI_CONFIG_SECTIONS:
        if section not in payload:
            failures.append(f"Secao obrigatoria ausente em .agents/config.toml: [{section}]")
    for section_name in ("orchestration", "rules", "evals"):
        section = payload.get(section_name, {})
        if not isinstance(section, dict):
            continue
        for value in section.values():
            if isinstance(value, str) and not (repo_root / value).exists():
                failures.append(f"Referencia ausente em .agents/config.toml: {value}")
    skills_section = payload.get("skills", {})
    if isinstance(skills_section, dict):
        for skill_name in skills_section.get("required", []):
            if (
                isinstance(skill_name, str)
                and not (skills_root(repo_root) / skill_name / "SKILL.md").exists()
            ):
                failures.append(f"Skill requerida ausente em .agents/config.toml: {skill_name}")
        for skill_name in skills_section.get("mandatory_parallel", []):
            if (
                isinstance(skill_name, str)
                and not (skills_root(repo_root) / skill_name / "SKILL.md").exists()
            ):
                failures.append(
                    f"Skill de gate paralelo ausente em .agents/config.toml: {skill_name}"
                )
    agents_section = payload.get("agents", {})
    if isinstance(agents_section, dict):
        for agent_name in agents_section.get("required", []):
            if (
                isinstance(agent_name, str)
                and not (registry_root(repo_root) / f"{agent_name}.toml").exists()
            ):
                failures.append(f"Agente requerido ausente em .agents/config.toml: {agent_name}")
        for agent_name in agents_section.get("mandatory_global", []):
            if (
                isinstance(agent_name, str)
                and not (registry_root(repo_root) / f"{agent_name}.toml").exists()
            ):
                failures.append(
                    f"Agente mandatory_global ausente em .agents/config.toml: {agent_name}"
                )
        for agent_name in agents_section.get("mandatory_platform", []):
            if (
                isinstance(agent_name, str)
                and not (registry_root(repo_root) / f"{agent_name}.toml").exists()
            ):
                failures.append(
                    f"Agente mandatory_platform ausente em .agents/config.toml: {agent_name}"
                )


def validate_legacy_codex_stub(repo_root: Path, failures: list[str]) -> None:
    legacy_root = legacy_codex_root(repo_root)
    readme_path = legacy_codex_readme(repo_root)

    if not readme_path.is_file():
        failures.append("Arquivo obrigatorio ausente: .codex/README.md")
        return

    unexpected = []
    if legacy_root.exists():
        for child in legacy_root.iterdir():
            if child.name == "README.md":
                continue
            if child.is_dir() and not any(child.iterdir()):
                continue
            unexpected.append(child.name)
    if unexpected:
        failures.append(
            ".codex deve conter apenas README.md de compatibilidade; entradas extras encontradas: "
            + ", ".join(sorted(unexpected))
        )


def validate_json_schema(path: Path, failures: list[str]) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"JSON invalido em {path.as_posix()}: {exc}")


def validate_jsonl(path: Path, failures: list[str]) -> None:
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            json.loads(stripped)
        except json.JSONDecodeError as exc:
            failures.append(f"JSONL invalido em {path.as_posix()} linha {index}: {exc}")


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


def parse_basic_toml(text: str) -> dict[str, object]:
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
            if not section_name:
                raise ValueError("Secao TOML vazia")
            section = data.setdefault(section_name, {})
            if not isinstance(section, dict):
                raise ValueError(f"Secao duplicada com tipo invalido: {section_name}")
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


def parse_toml_text(text: str) -> dict[str, object]:
    if tomllib is not None:
        try:
            return tomllib.loads(text)
        except Exception as exc:  # pragma: no cover - delegated to stdlib parser
            raise ValueError(str(exc)) from exc
    return parse_basic_toml(text)


def validate_agent_card(card: Path, skill_names: set[str], failures: list[str]) -> None:
    content = card.read_text(encoding="utf-8")
    for heading in REQUIRED_AGENT_HEADINGS:
        if heading not in content:
            failures.append(f"Heading obrigatorio ausente em .agents/cards/{card.name}: {heading}")

    skill_refs = re.findall(r"(?m)^-\s+`\$(.+?)`", content)
    if not skill_refs:
        failures.append(f"Skill principal ausente ou invalida em .agents/cards/{card.name}")
        return
    for skill_ref in skill_refs:
        if skill_ref not in skill_names:
            failures.append(
                f"Skill referenciada e inexistente em .agents/cards/{card.name}: {skill_ref}"
            )


def main(argv: list[str]) -> int:
    repo_root = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        path = repo_root / relative
        if not path.is_file():
            failures.append(f"Arquivo obrigatorio ausente: {relative}")

    tracker_path = repo_root / "docs" / "AI-WIP-TRACKER.md"
    if tracker_path.is_file():
        require_markers(
            tracker_path.read_text(encoding="utf-8"),
            TRACKER_MARKERS,
            "docs/AI-WIP-TRACKER.md",
            failures,
        )

    roadmap_path = repo_root / "ROADMAP.md"
    if roadmap_path.is_file():
        require_markers(
            roadmap_path.read_text(encoding="utf-8"), ROADMAP_MARKERS, "ROADMAP.md", failures
        )

    decisions_path = repo_root / "docs" / "ROADMAP-DECISIONS.md"
    if decisions_path.is_file():
        require_markers(
            decisions_path.read_text(encoding="utf-8"),
            DECISIONS_MARKERS,
            "docs/ROADMAP-DECISIONS.md",
            failures,
        )

    lessons_path = repo_root / "LICOES-APRENDIDAS.md"
    if lessons_path.is_file():
        lessons_content = lessons_path.read_text(encoding="utf-8")
        require_markers(lessons_content, LESSONS_MARKERS, "LICOES-APRENDIDAS.md", failures)
        require_snippets(
            lessons_content, LESSONS_REQUIRED_SNIPPETS, "LICOES-APRENDIDAS.md", failures
        )

    agents_contract_path = repo_root / "AGENTS.md"
    if agents_contract_path.is_file():
        require_snippets(
            agents_contract_path.read_text(encoding="utf-8"),
            AGENTS_REQUIRED_SNIPPETS,
            "AGENTS.md",
            failures,
        )

    operating_model_path = repo_root / "docs" / "ai-operating-model.md"
    if operating_model_path.is_file():
        require_snippets(
            operating_model_path.read_text(encoding="utf-8"),
            OPERATING_MODEL_REQUIRED_SNIPPETS,
            "docs/ai-operating-model.md",
            failures,
        )

    source_audit_path = repo_root / "docs" / "AI-SOURCE-AUDIT.md"
    if source_audit_path.is_file():
        require_snippets(
            source_audit_path.read_text(encoding="utf-8"),
            SOURCE_AUDIT_REQUIRED_SNIPPETS,
            "docs/AI-SOURCE-AUDIT.md",
            failures,
        )

    for relative, snippets in CATALOG_REQUIRED_SNIPPETS.items():
        path = repo_root / relative
        if path.is_file():
            require_snippets(path.read_text(encoding="utf-8"), snippets, relative, failures)

    skills_dir = skills_root(repo_root)
    if not skills_dir.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/skills")
    else:
        skill_dirs = sorted(
            [item for item in skills_dir.iterdir() if item.is_dir()], key=lambda item: item.name
        )
        if not skill_dirs:
            failures.append("Nenhuma skill encontrada em .agents/skills")
        skill_names = {item.name for item in skill_dirs}
        for skill_dir in skill_dirs:
            validate_skill_dir(skill_dir, failures)
    skill_names = locals().get("skill_names", set())

    registry_dir = registry_root(repo_root)
    if not registry_dir.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/registry")
    else:
        agent_files = sorted(registry_dir.glob("*.toml"))
        if not agent_files:
            failures.append("Nenhum agente declarativo encontrado em .agents/registry")
        for agent_file in agent_files:
            validate_registry_agent(agent_file, skill_names, failures)

    validate_ai_config(repo_root, failures)
    validate_legacy_codex_stub(repo_root, failures)

    for schema_path in (
        orchestration_root(repo_root) / "task-card.schema.json",
        orchestration_root(repo_root) / "delegation-plan.schema.json",
    ):
        if schema_path.is_file():
            validate_json_schema(schema_path, failures)

    for dataset_path in (
        evals_root(repo_root) / "datasets" / "routing.jsonl",
        evals_root(repo_root) / "datasets" / "governance.jsonl",
    ):
        if dataset_path.is_file():
            validate_jsonl(dataset_path, failures)

    for rule_path in (
        rules_root(repo_root) / "default.rules",
        rules_root(repo_root) / "ci.rules",
        rules_root(repo_root) / "security.rules",
    ):
        if rule_path.is_file():
            content = rule_path.read_text(encoding="utf-8")
            if "rule " not in content or "must:" not in content:
                failures.append(f"Formato minimo ausente em {rule_path.as_posix()}")

    cards_dir = cards_root(repo_root)
    if not cards_dir.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents/cards")
    else:
        cards = sorted(cards_dir.glob("*.md"))
        if not cards:
            failures.append("Nenhum cartao de agente encontrado em .agents/cards")
        for card in cards:
            validate_agent_card(card, skill_names, failures)

    if failures:
        print("Falhas encontradas na camada de IA:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1

    print("AI assets OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
