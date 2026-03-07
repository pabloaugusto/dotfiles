#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    "docs/ai-operating-model.md",
    "docs/AI-WIP-TRACKER.md",
    "docs/ROADMAP-DECISIONS.md",
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
]

REQUIRED_AGENT_HEADINGS = [
    "## Objetivo",
    "## Quando usar",
    "## Entradas",
    "## Saidas",
    "## Fluxo",
    "## Guardrails",
    "## Criterios de conclusao",
]


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
    if not match:
        return None
    return match.group(1).strip().strip("'\"")


def require_markers(content: str, markers: list[str], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in content:
            failures.append(f"Marcador obrigatorio ausente em {label}: {marker}")


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

    if agent_yaml.is_file():
        agent_content = agent_yaml.read_text(encoding="utf-8")
        if not re.search(r"(?m)^interface:\s*$", agent_content):
            failures.append(f"interface ausente em {skill_dir.name}/agents/openai.yaml")
        expected_skill_ref = f"${skill_dir.name}"
        default_prompt_re = rf'(?m)^\s*default_prompt:\s*".*{re.escape(expected_skill_ref)}.*"\s*$'
        if not re.search(default_prompt_re, agent_content):
            failures.append(f"default_prompt precisa mencionar {expected_skill_ref} em {skill_dir.name}/agents/openai.yaml")
        short_match = re.search(r'(?m)^\s*short_description:\s*"(?P<value>.+)"\s*$', agent_content)
        if not short_match:
            failures.append(f"short_description ausente em {skill_dir.name}/agents/openai.yaml")
        else:
            short_len = len(short_match.group("value"))
            if short_len < 25 or short_len > 64:
                failures.append(f"short_description fora do intervalo 25-64 em {skill_dir.name}/agents/openai.yaml")


def main(argv: list[str]) -> int:
    repo_root = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        path = repo_root / relative
        if not path.is_file():
            failures.append(f"Arquivo obrigatorio ausente: {relative}")

    tracker_path = repo_root / "docs" / "AI-WIP-TRACKER.md"
    if tracker_path.is_file():
        require_markers(tracker_path.read_text(encoding="utf-8"), TRACKER_MARKERS, "docs/AI-WIP-TRACKER.md", failures)

    decisions_path = repo_root / "docs" / "ROADMAP-DECISIONS.md"
    if decisions_path.is_file():
        require_markers(decisions_path.read_text(encoding="utf-8"), DECISIONS_MARKERS, "docs/ROADMAP-DECISIONS.md", failures)

    skills_root = repo_root / ".codex" / "skills"
    if not skills_root.is_dir():
        failures.append("Pasta obrigatoria ausente: .codex/skills")
    else:
        skill_dirs = sorted([item for item in skills_root.iterdir() if item.is_dir()], key=lambda item: item.name)
        if not skill_dirs:
            failures.append("Nenhuma skill encontrada em .codex/skills")
        for skill_dir in skill_dirs:
            validate_skill_dir(skill_dir, failures)

    agents_root = repo_root / ".agents"
    if not agents_root.is_dir():
        failures.append("Pasta obrigatoria ausente: .agents")
    else:
        cards = sorted(agents_root.glob("*.md"))
        if not cards:
            failures.append("Nenhum cartao de agente encontrado em .agents")
        for card in cards:
            content = card.read_text(encoding="utf-8")
            for heading in REQUIRED_AGENT_HEADINGS:
                if heading not in content:
                    failures.append(f"Heading obrigatorio ausente em .agents/{card.name}: {heading}")

    if failures:
        print("Falhas encontradas na camada de IA:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1

    print("AI assets OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
