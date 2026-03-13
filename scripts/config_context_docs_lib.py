from __future__ import annotations

from pathlib import Path

from scripts.ai_control_plane_lib import load_ai_control_plane
from scripts.config_context_lib import (
    load_context_manifest,
    manifest_domain_paths,
    resolve_repo_root,
)

CONFIG_REFERENCE_MARKERS = (
    "<!-- config-context:generated:start -->",
    "<!-- config-context:generated:end -->",
)
AGENTS_CATALOG_MARKERS = (
    "<!-- ai-agents:generated-identity:start -->",
    "<!-- ai-agents:generated-identity:end -->",
)


def _replace_block(content: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"Marcadores ausentes ou invalidos: {start_marker} / {end_marker}")
    start += len(start_marker)
    return content[:start] + "\n" + replacement.rstrip() + "\n" + content[end:]


def _format_domain_list(domain_paths: dict[str, str]) -> str:
    items = [
        f"`{domain_name}` -> [{relative_path}](../{relative_path})"
        for domain_name, relative_path in sorted(domain_paths.items())
    ]
    return "<br>".join(items)


def render_config_reference_table(repo_root: str | Path | None = None) -> str:
    resolved_root = resolve_repo_root(repo_root)
    root_manifest_path, root_manifest = load_context_manifest(resolved_root, context="root")
    app_manifest_path, app_manifest = load_context_manifest(resolved_root, context="app")
    ai_manifest_path, ai_manifest = load_context_manifest(resolved_root, context="ai")
    rows = [
        (
            "Projeto / defaults globais",
            root_manifest_path.relative_to(resolved_root).as_posix(),
            _format_domain_list(manifest_domain_paths(root_manifest)),
            "Source of truth para locale, idioma, moeda, calendario, timezone e precedencia global.",
        ),
        (
            "Runtime",
            app_manifest_path.relative_to(resolved_root).as_posix(),
            _format_domain_list(manifest_domain_paths(app_manifest)),
            "Config do produto dotfiles e comportamento real do workstation.",
        ),
        (
            "IA",
            ai_manifest_path.relative_to(resolved_root).as_posix(),
            _format_domain_list(manifest_domain_paths(ai_manifest)),
            "Config declarativa da camada de IA, startup, identidade, prompts e orchestration.",
        ),
    ]
    regionalization = root_manifest.get("regionalization") or {}
    regionalization_summary = (
        f"Locale `{regionalization.get('locale', '')}`, "
        f"idioma `{regionalization.get('language', '')}`, "
        f"moeda `{regionalization.get('currency', '')}`, "
        f"timezone `{regionalization.get('timezone_name', '')}`"
    )
    lines = [
        "",
        "| Contexto | Manifesto canonico | Dominios iniciais | Observacao |",
        "| --- | --- | --- | --- |",
    ]
    for context_name, manifest, domains, note in rows:
        lines.append(f"| {context_name} | [`{manifest}`](../{manifest}) | {domains} | {note} |")
    lines.extend(
        [
            "",
            f"Default global de regionalizacao: {regionalization_summary}.",
            "Registry complementar de superficies temporais: [`config/time-surfaces.yaml`](../config/time-surfaces.yaml).",
            "Toolchain Python permanece em [`pyproject.toml`](../pyproject.toml) e nao entra como hub generico.",
        ]
    )
    return "\n".join(lines).strip()


def render_agent_identity_table(repo_root: str | Path | None = None) -> str:
    resolved_root = resolve_repo_root(repo_root)
    control_plane = load_ai_control_plane(resolved_root)
    role_entries: list[tuple[str, str, str, str, str]] = []
    for role_id, entry in sorted(control_plane.effective_roles_payload().items()):
        display_name = control_plane.formal_name_for_agent(role_id) or "-"
        chat_alias = control_plane.chat_alias_for_agent(role_id) or "-"
        visible_name = control_plane.visible_name_for_agent(role_id) or role_id
        enabled = "true" if bool(entry.get("enabled", False)) else "false"
        role_entries.append((role_id, visible_name, display_name, chat_alias, enabled))

    lines = [
        "",
        "| Role tecnica | Nome visivel efetivo | `display_name` | `chat_alias` | Habilitado |",
        "| --- | --- | --- | --- | --- |",
    ]
    for role_id, visible_name, display_name, chat_alias, enabled in role_entries:
        lines.append(
            f"| `{role_id}` | {visible_name} | {display_name} | {chat_alias} | `{enabled}` |"
        )
    lines.extend(
        [
            "",
            "Config canonica:",
            "- manifesto da camada IA: [`.agents/config/config.toml`](../.agents/config/config.toml)",
            "- identidade declarativa: [`.agents/config/agents.toml`](../.agents/config/agents.toml)",
            "- runtime visivel de chat/Jira: [`.agents/config/communication.toml`](../.agents/config/communication.toml)",
            "- ponte legada temporaria: [`.agents/config.toml`](../.agents/config.toml)",
        ]
    )
    return "\n".join(lines).strip()


def update_generated_sections(repo_root: str | Path | None = None) -> list[Path]:
    resolved_root = resolve_repo_root(repo_root)
    touched: list[Path] = []
    replacements = [
        (
            resolved_root / "docs" / "config-reference.md",
            CONFIG_REFERENCE_MARKERS,
            render_config_reference_table(resolved_root),
        ),
        (
            resolved_root / "docs" / "AI-AGENTS-CATALOG.md",
            AGENTS_CATALOG_MARKERS,
            render_agent_identity_table(resolved_root),
        ),
    ]
    for path, markers, replacement in replacements:
        original = path.read_text(encoding="utf-8")
        updated = _replace_block(original, markers[0], markers[1], replacement)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            touched.append(path)
    return touched


def generated_reference_docs(repo_root: str | Path | None = None) -> dict[str, str]:
    resolved_root = resolve_repo_root(repo_root)
    return {
        "docs/config-reference.md": render_config_reference_table(resolved_root),
        "docs/AI-AGENTS-CATALOG.md": render_agent_identity_table(resolved_root),
    }
