from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

try:
    import markdown as markdown_lib
except ModuleNotFoundError:  # pragma: no cover - fallback local para unit tests sem dependencia opcional
    markdown_lib = None

from scripts.ai_atlassian_backfill_lib import build_backfill_plan
from scripts.ai_atlassian_actor_lib import (
    confluence_adapter_for_role,
    global_confluence_adapter,
    global_jira_adapter,
    with_jira_actor,
)
from scripts.ai_atlassian_migration_bundle_lib import build_migration_bundle
from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    github_blob_url,
    linkify_repo_relative_paths,
    load_ai_control_plane,
    load_yaml_map,
    resolve_atlassian_platform,
    resolve_repo_root,
    resolve_tracked_repo_files,
)
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    AtlassianPlatformError,
    ConfluenceAdapter,
    JiraAdapter,
    adf_to_text,
    canonicalize_workflow_status,
    render_structured_comment,
)

DEFAULT_CONFLUENCE_MODEL_PATH = Path("config/ai/confluence-model.yaml")
DEFAULT_JIRA_MODEL_PATH = Path("config/ai/jira-model.yaml")
MIGRATION_ISSUE_SUMMARY = "Migrar backlog e documentacao para Jira e Confluence"
MIGRATION_ISSUE_LABELS = [
    "atlassian-ia",
    "migration",
    "retro-sync",
    "control-plane",
]
MIGRATION_REPO_REFERENCES = (
    (
        "Plano vivo da migracao",
        "docs/atlassian-ia/2026-03-07-parecer-e-plano-inicial.md",
    ),
    (
        "Contrato do migration bundle",
        "docs/atlassian-ia/artifacts/migration-bundle.md",
    ),
    (
        "Padrao de escrita das issues",
        "docs/atlassian-ia/artifacts/jira-writing-standards.md",
    ),
    (
        "Estrategia GitHub Jira Confluence",
        "docs/atlassian-ia/2026-03-08-github-jira-confluence-traceability.md",
    ),
)
WORKFLOW_ORDER = [
    ("backlog", ["backlog"]),
    ("refinement", ["refinement"]),
    ("ready", ["ready"]),
    ("doing", ["doing", "doing".upper()]),
    ("paused", ["paused"]),
    ("testing", ["testing", "testing".upper()]),
    ("review", ["review"]),
    ("done", ["done"]),
]
WORKFLOW_TRANSITION_GRAPH = {
    "backlog": ["refinement"],
    "refinement": ["ready"],
    "ready": ["doing"],
    "doing": ["testing", "paused"],
    "paused": ["doing"],
    "testing": ["review"],
    "review": ["done"],
    "done": [],
}
LEGACY_EXTERNAL_ID_RE = re.compile(r"^\[(?P<external_id>[^\]]+)\]\s+")
MARKDOWN_LINK_TARGET_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class SeedArtifacts:
    migration_issue_key: str
    migration_issue_url: str
    bundle_zip_path: Path
    bundle_attachment_urls: list[str]
    confluence_pages: dict[str, dict[str, str]]
    seeded_issues: list[dict[str, str]]


def build_seed_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    _, jira_model = load_jira_model(control_plane.repo_root)
    _, confluence_model = load_confluence_model(control_plane.repo_root)
    backfill = build_backfill_plan(control_plane.repo_root)
    page_entries = flatten_page_tree(confluence_model)
    jira_records = []
    jira_records.extend(backfill["jira"]["roadmap_backlog"])
    jira_records.extend(backfill["jira"]["roadmap_suggestions"])
    jira_records.extend(backfill["jira"]["worklog_doing"])
    jira_records.extend(backfill["jira"]["worklog_done"])
    return {
        "metadata": {
            "model_id": "ai-control-plane-atlassian-pilot",
            "project_key": resolved.jira_project_key,
            "space_key": resolved.confluence_space_key,
            "migration_issue_summary": MIGRATION_ISSUE_SUMMARY,
        },
        "preconditions": {
            "jira_schema_applied": True,
            "confluence_schema_artifacts_ready": True,
            "board_layout_confirmed": jira_board_layout_confirmed(jira_model),
            "board_layout_status": (
                "confirmed"
                if jira_board_layout_confirmed(jira_model)
                else "blocked-until-board-layout-confirmed"
            ),
            "board_api_gap": "read:project:jira-missing-or-not-effective",
        },
        "jira": {
            "total_records": len(jira_records),
            "records": [
                {
                    "external_id": str(entry["external_id"]).strip(),
                    "issue_type": str(entry["issue_type"]).strip(),
                    "summary": str(entry["summary"]).strip(),
                    "state_hint": str(entry["state_hint"]).strip(),
                    "origin": str(entry["origin"]).strip(),
                }
                for entry in jira_records
            ],
        },
        "confluence": {
            "total_pages": len(page_entries),
            "pages": page_entries,
        },
    }


def load_confluence_model(repo_root: str | Path | None = None) -> tuple[Path, dict[str, Any]]:
    resolved_repo_root = resolve_repo_root(repo_root)
    model_path = resolved_repo_root / DEFAULT_CONFLUENCE_MODEL_PATH
    return model_path, load_yaml_map(model_path)


def load_jira_model(repo_root: str | Path | None = None) -> tuple[Path, dict[str, Any]]:
    resolved_repo_root = resolve_repo_root(repo_root)
    model_path = resolved_repo_root / DEFAULT_JIRA_MODEL_PATH
    return model_path, load_yaml_map(model_path)


def jira_board_layout_confirmed(model: dict[str, Any]) -> bool:
    project = model.get("project") or {}
    if not isinstance(project, dict):
        raise AiControlPlaneError("config/ai/jira-model.yaml project precisa ser mapa.")
    target_board = project.get("target_board") or {}
    if not isinstance(target_board, dict):
        raise AiControlPlaneError(
            "config/ai/jira-model.yaml project.target_board precisa ser mapa."
        )
    return bool(target_board.get("layout_confirmed", False))


def page_url(site_url: str, space_key: str, page_id: str) -> str:
    return f"{site_url.rstrip('/')}/wiki/spaces/{space_key}/pages/{page_id}"


def issue_url(site_url: str, issue_key: str) -> str:
    return f"{site_url.rstrip('/')}/browse/{issue_key}"


def normalize_status_label(name: str) -> str:
    return " ".join(name.strip().split()).casefold()


def logical_status_from_name(name: str) -> str:
    normalized = normalize_status_label(name)
    for logical, candidates in WORKFLOW_ORDER:
        candidate_set = {normalize_status_label(value) for value in candidates}
        if normalized in candidate_set:
            return logical
    return ""


def workflow_transition_path(
    current_logical_status: str,
    target_logical_status: str,
) -> list[str]:
    current = current_logical_status.strip().casefold()
    target = target_logical_status.strip().casefold()
    if not current or not target:
        return []
    if current == target:
        return [current]
    if current not in WORKFLOW_TRANSITION_GRAPH or target not in WORKFLOW_TRANSITION_GRAPH:
        return []

    queue: list[list[str]] = [[current]]
    visited = {current}
    while queue:
        path = queue.pop(0)
        node = path[-1]
        for neighbor in WORKFLOW_TRANSITION_GRAPH.get(node, []):
            if neighbor in visited:
                continue
            next_path = [*path, neighbor]
            if neighbor == target:
                return next_path
            visited.add(neighbor)
            queue.append(next_path)
    return []


def state_hint_to_logical_status(state_hint: str) -> str:
    normalized = state_hint.strip().lower()
    if normalized in {"done", "aceita"}:
        return "done"
    if normalized in {"doing", "in progress", "executando"}:
        return "doing"
    if normalized in {"paused", "on hold", "pausado"}:
        return "paused"
    if normalized in {"triage", "pendente"}:
        return "backlog"
    return "backlog"


def build_issue_description(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines if line.strip())


def build_migration_issue_description(
    repo_root: Path,
    *,
    bundle_attachment_name: str,
) -> str:
    reference_lines = [
        f"- [{label}]({github_blob_url(repo_root, repo_path)})"
        for label, repo_path in MIGRATION_REPO_REFERENCES
    ]
    reference_lines.append(f"- Bundle auditavel anexado nesta issue: {bundle_attachment_name}")
    reference_lines.append(
        "- Paginas oficiais do Confluence vinculadas por comentarios estruturados nesta propria issue."
    )
    return build_issue_description(
        [
            "## Contexto",
            "- Esta issue concentra a migracao inicial do backlog e da documentacao oficial para Jira e Confluence.",
            "- Ela tambem funciona como ancora auditavel para bundles, comentarios estruturados e checkpoints da transicao.",
            "",
            "## Resultado esperado",
            "- O tenant reflete o backlog retroativo, a documentacao oficial e as evidencias centrais desta trilha.",
            "",
            "## Escopo tecnico",
            "- anexar o bundle auditavel da migracao",
            "- sincronizar as paginas oficiais no Confluence",
            "- semear e corrigir o backlog retroativo no Jira",
            "",
            "## Criterios de aceite",
            "- O bundle auditavel desta rodada esta anexado nesta issue.",
            "- As paginas oficiais do Confluence relacionadas a migracao foram criadas ou atualizadas.",
            "- O backlog retroativo ficou legivel, rastreavel e com links oficiais entre Jira, Confluence e GitHub quando aplicavel.",
            "",
            "## Referencias",
            *reference_lines,
        ]
    )


def extract_external_id(issue: dict[str, Any]) -> str:
    fields = issue.get("fields") or {}
    summary = str(fields.get("summary", "")).strip()
    match = LEGACY_EXTERNAL_ID_RE.match(summary)
    if match:
        return match.group("external_id").strip()
    description_text = adf_to_text(fields.get("description")).strip()
    for line in description_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if stripped.startswith("ID local:"):
            return stripped.split(":", 1)[1].strip()
        if stripped.startswith("Worklog local:"):
            return stripped.split(":", 1)[1].strip()
    return ""


def build_existing_issue_index(
    issues: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for issue in issues:
        fields = issue.get("fields") or {}
        issue_type = str(((fields.get("issuetype") or {}).get("name")) or "").strip()
        external_id = extract_external_id(issue)
        if issue_type and external_id:
            index[(issue_type, external_id)] = issue
    return index


def issue_extra_fields(record: dict[str, Any]) -> dict[str, Any]:
    extra_fields: dict[str, Any] = {}
    components = [
        {"name": str(component).strip()}
        for component in record.get("components") or []
        if str(component).strip()
    ]
    if components:
        extra_fields["components"] = components
    priority = str(record.get("priority", "")).strip()
    if priority:
        extra_fields["priority"] = {"name": priority}
    return extra_fields


def sync_issue_content(
    jira: JiraAdapter,
    issue_key: str,
    *,
    summary: str,
    description: str,
    labels: list[str],
    extra_fields: dict[str, Any] | None = None,
) -> None:
    jira.update_issue_fields(
        issue_key,
        {
            "summary": summary.strip(),
            "description": description,
            "labels": [str(label).strip() for label in labels if str(label).strip()],
            **(extra_fields or {}),
        },
    )


def build_list_html(items: list[tuple[str, str]]) -> str:
    if not items:
        return "<p>n/a</p>"
    rendered = "".join(
        f'<li><a href="{escape(url, quote=True)}">{escape(label)}</a></li>' for label, url in items
    )
    return f"<ul>{rendered}</ul>"


def render_inline_markdown_html(text: str) -> str:
    rendered: list[str] = []
    last_index = 0
    for match in MARKDOWN_LINK_TARGET_RE.finditer(text):
        rendered.append(escape(text[last_index : match.start()]))
        rendered.append(
            f'<a href="{escape(match.group(2), quote=True)}">{escape(match.group(1))}</a>'
        )
        last_index = match.end()
    rendered.append(escape(text[last_index:]))
    return "".join(rendered)


def markdown_to_storage_html(source_body: str) -> str:
    if markdown_lib is None:
        blocks: list[str] = []
        bullets: list[str] = []

        def flush_bullets() -> None:
            nonlocal bullets
            if bullets:
                blocks.append(f"<ul>{''.join(bullets)}</ul>")
                bullets = []

        for raw_line in source_body.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                flush_bullets()
                continue
            if stripped.startswith("- "):
                bullets.append(f"<li>{render_inline_markdown_html(stripped[2:].strip())}</li>")
                continue
            flush_bullets()
            if stripped.startswith("# "):
                blocks.append(f"<h1>{render_inline_markdown_html(stripped[2:].strip())}</h1>")
                continue
            blocks.append(f"<p>{render_inline_markdown_html(stripped)}</p>")
        flush_bullets()
        rendered = "".join(blocks).strip()
    else:
        rendered = markdown_lib.markdown(
            source_body,
            extensions=["extra", "sane_lists"],
            output_format="xhtml",
        ).strip()
    return rendered or "<p>Sem conteudo renderizavel.</p>"


def rewrite_markdown_repo_links(
    source_body: str,
    *,
    repo_root: Path,
    repo_artifact: str,
) -> str:
    source_file = (repo_root / repo_artifact).resolve()
    tracked_files = resolve_tracked_repo_files(repo_root)

    def replacer(match: re.Match[str]) -> str:
        label = match.group(1)
        raw_target = match.group(2).strip()
        if not raw_target or "://" in raw_target or raw_target.startswith(("mailto:", "#")):
            return match.group(0)
        target_path, hash_separator, fragment = raw_target.partition("#")
        candidate = (source_file.parent / target_path).resolve()
        try:
            repo_relative = candidate.relative_to(repo_root).as_posix()
        except ValueError:
            return match.group(0)
        if repo_relative not in tracked_files or not candidate.is_file():
            return match.group(0)
        github_url = github_blob_url(repo_root, repo_relative)
        if hash_separator and fragment.strip():
            github_url = f"{github_url}#{fragment.strip()}"
        return f"[{label}]({github_url})"

    rewritten = MARKDOWN_LINK_TARGET_RE.sub(replacer, source_body)
    return linkify_repo_relative_paths(rewritten, repo_root=repo_root)


def confluence_expand_macro(title: str, body_html: str) -> str:
    return (
        '<ac:structured-macro ac:name="expand">'
        f'<ac:parameter ac:name="title">{escape(title)}</ac:parameter>'
        f"<ac:rich-text-body>{body_html}</ac:rich-text-body>"
        "</ac:structured-macro>"
    )


def build_storage_snapshot(
    *,
    title: str,
    repo_root: Path,
    repo_artifact: str,
    related_issues: list[tuple[str, str]],
    extra_notes: list[str] | None = None,
) -> str:
    source_path = repo_root / repo_artifact
    source_body = rewrite_markdown_repo_links(
        source_path.read_text(encoding="utf-8"),
        repo_root=repo_root,
        repo_artifact=repo_artifact,
    )
    rendered_source = markdown_to_storage_html(source_body)
    source_url = github_blob_url(repo_root, repo_artifact)
    notes = extra_notes or []
    notes_html = "".join(f"<li>{escape(note)}</li>" for note in notes if note.strip())
    notes_block = f"<ul>{notes_html}</ul>" if notes_html else "<p>n/a</p>"
    return (
        f"<h1>{escape(title)}</h1>"
        "<p>Pagina sincronizada a partir do artefato versionado no repositorio.</p>"
        f'<p><strong>Origem no GitHub:</strong> <a href="{escape(source_url, quote=True)}">{escape(repo_artifact)}</a></p>'
        "<h2>Issues relacionadas</h2>"
        f"{build_list_html(related_issues)}"
        "<h2>Notas de sincronizacao</h2>"
        f"{notes_block}"
        "<h2>Conteudo sincronizado</h2>"
        f"{rendered_source}"
        "<h2>Conteudo de origem</h2>"
        f"{confluence_expand_macro('Expandir documento de origem', rendered_source)}"
    )


def build_section_body(
    *,
    title: str,
    description: str,
    related_issues: list[tuple[str, str]],
) -> str:
    return (
        f"<h1>{escape(title)}</h1>"
        f"<p>{escape(description)}</p>"
        "<h2>Issues relacionadas</h2>"
        f"{build_list_html(related_issues)}"
    )


def flatten_page_tree(model: dict[str, Any]) -> list[dict[str, str]]:
    page_tree = model.get("page_tree") or []
    if not isinstance(page_tree, list):
        raise AiControlPlaneError("config/ai/confluence-model.yaml page_tree precisa ser lista.")
    entries: list[dict[str, str]] = []
    for root in page_tree:
        if not isinstance(root, dict):
            continue
        root_title = str(root.get("title", "")).strip()
        if not root_title:
            continue
        entries.append(
            {
                "title": root_title,
                "kind": str(root.get("kind", "")).strip(),
                "parent_title": "",
                "repo_artifact": str(root.get("repo_artifact", "")).strip(),
            }
        )
        for section in root.get("sections") or []:
            if not isinstance(section, dict):
                continue
            section_title = str(section.get("title", "")).strip()
            if not section_title:
                continue
            entries.append(
                {
                    "title": section_title,
                    "kind": str(section.get("kind", "")).strip(),
                    "parent_title": root_title,
                    "repo_artifact": str(section.get("repo_artifact", "")).strip(),
                }
            )
            for child in section.get("children") or []:
                if not isinstance(child, dict):
                    continue
                child_title = str(child.get("title", "")).strip()
                if not child_title:
                    continue
                entries.append(
                    {
                        "title": child_title,
                        "kind": str(child.get("kind", "")).strip(),
                        "parent_title": section_title,
                        "repo_artifact": str(child.get("repo_artifact", "")).strip(),
                    }
                )
    return entries


def sync_confluence_page_tree(
    *,
    adapter: ConfluenceAdapter,
    resolved: Any,
    repo_root: Path,
    model: dict[str, Any],
    related_links: list[tuple[str, str]],
    notes: list[str] | None = None,
    version_message: str = "sync-atlassian-seed",
) -> dict[str, dict[str, str]]:
    space = adapter.get_space(resolved.confluence_space_key)
    actual_space_key = (
        str(space.get("currentActiveAlias", "")).strip()
        or str(space.get("key", "")).strip()
        or resolved.confluence_space_key
    )
    page_lookup: dict[str, dict[str, str]] = {}
    parent_ids: dict[str, str] = {}
    sync_notes = [note for note in (notes or []) if str(note).strip()]

    for page in flatten_page_tree(model):
        title = page["title"]
        repo_artifact = page["repo_artifact"]
        parent_title = page["parent_title"]
        if repo_artifact:
            storage_value = build_storage_snapshot(
                title=title,
                repo_root=repo_root,
                repo_artifact=repo_artifact,
                related_issues=related_links,
                extra_notes=sync_notes,
            )
        else:
            storage_value = build_section_body(
                title=title,
                description="Pagina-hub oficial da camada Atlassian + IA do piloto.",
                related_issues=related_links,
            )
        parent_page_id = parent_ids.get(parent_title, "")
        page_payload = ensure_page(
            adapter=adapter,
            space_key=resolved.confluence_space_key,
            title=title,
            storage_value=storage_value,
            parent_page_id=parent_page_id,
            version_message=version_message,
        )
        page_id = str(page_payload.get("id", "")).strip()
        if not page_id:
            raise AtlassianPlatformError(f"Confluence nao retornou id para a pagina {title!r}.")
        parent_ids[title] = page_id
        page_lookup[title] = {
            "id": page_id,
            "url": page_url(resolved.site_url, actual_space_key, page_id),
        }
    return page_lookup


def ensure_page(
    *,
    adapter: ConfluenceAdapter,
    space_key: str,
    title: str,
    storage_value: str,
    parent_page_id: str = "",
    version_message: str = "",
) -> dict[str, Any]:
    existing = adapter.find_page_by_title(space_key=space_key, title=title)
    if existing:
        page_id = str(existing.get("id", "")).strip()
        if not page_id:
            raise AtlassianPlatformError(f"Confluence retornou pagina sem id para {title!r}.")
        return adapter.update_page(
            page_id=page_id,
            title=title,
            storage_value=storage_value,
            parent_page_id=parent_page_id,
            version_message=version_message,
        )
    return adapter.create_page(
        space_key=space_key,
        title=title,
        storage_value=storage_value,
        parent_page_id=parent_page_id,
    )


def attachment_urls(attachments: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for entry in attachments:
        content_url = str(entry.get("content", "")).strip()
        if content_url:
            urls.append(content_url)
    return urls


def ensure_migration_issue(
    *,
    jira: JiraAdapter,
    project_key: str,
    site_url: str,
    repo_root: Path,
    bundle_zip_path: Path,
) -> tuple[dict[str, Any], list[str]]:
    desired_description = build_migration_issue_description(
        repo_root,
        bundle_attachment_name=bundle_zip_path.name,
    )
    existing = jira.find_issue_by_summary(
        project_key=project_key,
        summary=MIGRATION_ISSUE_SUMMARY,
        issue_types=["Task"],
    )
    if existing:
        issue = existing
        issue_key = str(issue.get("key", "")).strip()
        if not issue_key:
            raise AtlassianPlatformError("Nao foi possivel resolver a key da issue de migracao.")
        sync_issue_content(
            jira,
            issue_key,
            summary=MIGRATION_ISSUE_SUMMARY,
            description=desired_description,
            labels=MIGRATION_ISSUE_LABELS,
            extra_fields={
                "components": [{"name": "ai-control-plane"}],
                "priority": {"name": "High"},
            },
        )
    else:
        issue = jira.create_issue(
            project_key=project_key,
            issue_type="Task",
            summary=MIGRATION_ISSUE_SUMMARY,
            description=desired_description,
            labels=MIGRATION_ISSUE_LABELS,
            extra_fields={
                "components": [{"name": "ai-control-plane"}],
                "priority": {"name": "High"},
            },
        )
    issue_key = str(issue.get("key", "")).strip()
    if not issue_key:
        raise AtlassianPlatformError("Nao foi possivel resolver a key da issue de migracao.")

    current = jira.get_issue(issue_key, fields=["attachment", "status"])
    attachments = ((current.get("fields") or {}).get("attachment")) or []
    existing_names = {
        str(entry.get("filename", "")).strip() for entry in attachments if isinstance(entry, dict)
    }
    uploaded: list[dict[str, Any]] = []
    if bundle_zip_path.name not in existing_names:
        uploaded = jira.add_attachment(issue_key, bundle_zip_path)
    return current, attachment_urls(uploaded)


def ensure_issue_reaches_status(
    *,
    jira: JiraAdapter,
    issue_key: str,
    target_logical_status: str,
) -> None:
    issue = jira.get_issue(issue_key, fields=["status"])
    fields = issue.get("fields") or {}
    current_status = str(((fields.get("status") or {}).get("name")) or "").strip()
    current_logical_status = logical_status_from_name(current_status)
    target = target_logical_status.strip().casefold()
    if not current_logical_status or not target:
        return
    transition_path = workflow_transition_path(current_logical_status, target)
    if not transition_path:
        raise AtlassianPlatformError(
            "Nao foi encontrado caminho logico de transicao "
            f"de {current_logical_status!r} para {target!r} na issue {issue_key}."
        )
    if len(transition_path) == 1:
        return
    for next_logical_status in transition_path[1:]:
        candidates = next(
            candidate_values
            for logical, candidate_values in WORKFLOW_ORDER
            if logical == next_logical_status
        )
        candidate_set = {normalize_status_label(value) for value in candidates}
        transitions = jira.get_transitions(issue_key)
        chosen = None
        for transition in transitions:
            to_status = str(((transition.get("to") or {}).get("name")) or "").strip()
            if normalize_status_label(to_status) in candidate_set:
                chosen = transition
                break
        if chosen is None:
            raise AtlassianPlatformError(
                f"Nao foi encontrada transicao para {candidates[0]!r} na issue {issue_key}."
            )
        jira.transition_issue(issue_key, str(chosen.get("id", "")).strip())


def sync_confluence_docs(
    repo_root: str | Path | None = None,
    *,
    issue_keys: list[str] | None = None,
) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    _, confluence_model = load_confluence_model(control_plane.repo_root)
    confluence, documentation_actor = confluence_adapter_for_role(
        control_plane.repo_root,
        "ai-documentation-sync",
        "confluence-page",
    )
    resolved = documentation_actor.as_platform()
    jira = global_jira_adapter(control_plane.repo_root)

    related_links: list[tuple[str, str]] = []
    seen_issue_keys: set[str] = set()
    migration_issue = jira.find_issue_by_summary(
        project_key=resolved.jira_project_key,
        summary=MIGRATION_ISSUE_SUMMARY,
        issue_types=["Task"],
    )
    migration_issue_key = ""
    if migration_issue:
        migration_issue_key = str(migration_issue.get("key", "")).strip()
        if migration_issue_key:
            related_links.append(
                (migration_issue_key, issue_url(resolved.site_url, migration_issue_key))
            )
            seen_issue_keys.add(migration_issue_key)

    for raw_key in issue_keys or []:
        issue_key = str(raw_key).strip().upper()
        if not issue_key or issue_key in seen_issue_keys:
            continue
        jira.get_issue(issue_key, fields=["summary"])
        related_links.append((issue_key, issue_url(resolved.site_url, issue_key)))
        seen_issue_keys.add(issue_key)

    page_lookup = sync_confluence_page_tree(
        adapter=confluence,
        resolved=resolved,
        repo_root=control_plane.repo_root,
        model=confluence_model,
        related_links=related_links,
        notes=[
            "Pagina resincronizada pela camada oficial de sync documental.",
            "Sincronizacao desacoplada do seed completo para manter a documentacao viva sem rebaixar o repo como fonte canonica quando aplicavel.",
        ],
        version_message="sync-atlassian-docs",
    )

    if migration_issue_key:
        with_jira_actor(
            control_plane.repo_root,
            "ai-documentation-sync",
            "jira-comment",
            lambda comment_jira, _actor: comment_jira.ensure_comment(
                migration_issue_key,
                render_structured_comment(
                    {
                        "agent": control_plane.visible_name_for_reference("ai-documentation-sync"),
                        "interaction_type": "documentation-sync",
                        "status": canonicalize_workflow_status("Doing"),
                        "contexto": [
                            "Confluence resincronizado por task dedicada, sem depender da semeadura completa.",
                            "O objetivo e manter a superficie cross-surface oficial viva sem substituir o repo como fonte canonica quando aplicavel.",
                        ],
                        "evidencias": [page["url"] for page in page_lookup.values()],
                        "proximo_passo": "Continuar refletindo no Confluence qualquer atualizacao aprovada do control plane e dos artefatos de migracao.",
                    }
                ),
            ),
            context_issue_key=migration_issue_key,
        )

    return {
        "confluence_pages": page_lookup,
        "counts": {
            "confluence_pages": len(page_lookup),
            "related_issues": len(related_links),
        },
        "related_issue_keys": [entry[0] for entry in related_links],
    }


def confluence_page_issue_links(
    *,
    page_kind: str,
    migration_issue: tuple[str, str],
    seeded_issues: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    if page_kind in {"jira-backfill", "migration-plan"}:
        return [migration_issue, *seeded_issues]
    return [migration_issue]


def relevant_page_titles_for_record(origin: str) -> list[str]:
    if origin in {"roadmap-backlog", "roadmap-suggestion"}:
        return ["DOT - Migration Plan", "DOT - Jira Backfill Ledger"]
    if origin in {"wip-doing", "wip-done"}:
        return ["DOT - Jira Backfill Ledger"]
    return ["DOT - AI Control Plane Hub"]


def seed_atlassian(
    repo_root: str | Path | None = None,
    *,
    allow_visual_board_gap: bool = False,
) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    jira_model_path, jira_model = load_jira_model(control_plane.repo_root)
    if not jira_board_layout_confirmed(jira_model) and not allow_visual_board_gap:
        raise AiControlPlaneError(
            "A semeadura Atlassian esta bloqueada porque o board do Jira ainda "
            "nao foi confirmado como alinhado ao workflow oficial. Ajuste o board "
            "e marque "
            f"{jira_model_path.relative_to(control_plane.repo_root).as_posix()} "
            "com project.target_board.layout_confirmed=true, ou use o override "
            "explicito desta rodada quando aprovado pelo usuario."
        )
    _, confluence_model = load_confluence_model(control_plane.repo_root)
    jira = global_jira_adapter(control_plane.repo_root)
    confluence = global_confluence_adapter(control_plane.repo_root)

    bundle = build_migration_bundle(control_plane.repo_root)
    backfill = build_backfill_plan(control_plane.repo_root)
    migration_issue, bundle_attachment_urls = ensure_migration_issue(
        jira=jira,
        project_key=resolved.jira_project_key,
        site_url=resolved.site_url,
        repo_root=control_plane.repo_root,
        bundle_zip_path=Path(bundle["zip_path"]),
    )
    migration_issue_key = str(migration_issue.get("key", "")) or MIGRATION_ISSUE_SUMMARY
    migration_issue_url = issue_url(resolved.site_url, migration_issue_key)

    seeded_issues: list[dict[str, str]] = []
    jira_records = []
    jira_records.extend(backfill["jira"]["roadmap_backlog"])
    jira_records.extend(backfill["jira"]["roadmap_suggestions"])
    jira_records.extend(backfill["jira"]["worklog_doing"])
    jira_records.extend(backfill["jira"]["worklog_done"])
    existing_project_issues = jira.search_issues(
        f'project = "{resolved.jira_project_key}" ORDER BY created ASC',
        fields=["summary", "description", "issuetype", "labels"],
        max_results=500,
    )
    existing_issue_index = build_existing_issue_index(existing_project_issues)

    for record in jira_records:
        record_issue_type = str(record["issue_type"]).strip()
        record_external_id = str(record["external_id"]).strip()
        existing = existing_issue_index.get((record_issue_type, record_external_id))
        if existing is None:
            existing = jira.find_issue_by_summary(
                project_key=resolved.jira_project_key,
                summary=str(record["summary"]).strip(),
                issue_types=[record_issue_type],
            )
        if existing:
            issue = existing
        else:
            issue = jira.create_issue(
                project_key=resolved.jira_project_key,
                issue_type=record_issue_type,
                summary=str(record["summary"]).strip(),
                description=build_issue_description(record["description_lines"]),
                labels=[str(label).strip() for label in record["labels"] if str(label).strip()],
                extra_fields=issue_extra_fields(record),
            )
        issue_key = str(issue.get("key", "")).strip()
        if not issue_key:
            raise AtlassianPlatformError(
                f"Nao foi possivel resolver a key da issue para {record['summary']!r}."
            )
        sync_issue_content(
            jira,
            issue_key,
            summary=str(record["summary"]).strip(),
            description=build_issue_description(record["description_lines"]),
            labels=[str(label).strip() for label in record["labels"] if str(label).strip()],
            extra_fields=issue_extra_fields(record),
        )
        seeded_issues.append(
            {
                "external_id": str(record["external_id"]).strip(),
                "key": issue_key,
                "origin": str(record["origin"]).strip(),
                "summary": str(record["summary"]).strip(),
            }
        )
        existing_issue_index[(record_issue_type, record_external_id)] = {
            "key": issue_key,
            "fields": {
                "summary": str(record["summary"]).strip(),
                "description": build_issue_description(record["description_lines"]),
                "issuetype": {"name": record_issue_type},
            },
        }
        ensure_issue_reaches_status(
            jira=jira,
            issue_key=issue_key,
            target_logical_status=state_hint_to_logical_status(str(record["state_hint"]).strip()),
        )
    seed_issue_links = [
        (entry["key"], issue_url(resolved.site_url, entry["key"])) for entry in seeded_issues
    ]
    migration_link = (migration_issue_key, migration_issue_url)
    page_lookup = sync_confluence_page_tree(
        adapter=confluence,
        resolved=resolved,
        repo_root=control_plane.repo_root,
        model=confluence_model,
        related_links=[migration_link, *seed_issue_links],
        notes=[
            "Pagina sincronizada automaticamente pela camada oficial de sync documental.",
            f"Bundle de migracao: {Path(bundle['zip_path']).name}",
        ],
        version_message="sync-atlassian-seed",
    )

    migration_evidences = [
        str(Path(bundle["zip_path"]).relative_to(control_plane.repo_root)),
        str(Path(bundle["manifest_path"]).relative_to(control_plane.repo_root)),
        page_lookup["DOT - AI Control Plane Hub"]["url"],
        page_lookup["DOT - Migration Plan"]["url"],
        *bundle_attachment_urls,
    ]
    with_jira_actor(
        control_plane.repo_root,
        "ai-documentation-sync",
        "jira-comment",
        lambda comment_jira, _actor: comment_jira.ensure_comment(
            migration_issue_key,
            render_structured_comment(
                {
                    "agent": control_plane.visible_name_for_reference("ai-documentation-sync"),
                    "interaction_type": "schema-artifact",
                    "status": canonicalize_workflow_status("Doing"),
                    "contexto": [
                        "Schema Jira aplicado e bundle auditavel gerado antes da semeadura.",
                        "Confluence sincronizado como superficie cross-surface oficial da documentacao viva, preservando o repo como fonte canonica quando aplicavel.",
                    ],
                    "evidencias": migration_evidences,
                    "proximo_passo": "Concluir a semeadura retroativa e manter a operacao nativa em Jira/Confluence.",
                }
            ),
        ),
        context_issue_key=migration_issue_key,
    )

    for record in jira_records:
        issue_key = next(
            entry["key"]
            for entry in seeded_issues
            if entry["external_id"] == str(record["external_id"]).strip()
        )
        related_pages = [
            page_lookup[title]["url"]
            for title in relevant_page_titles_for_record(str(record["origin"]).strip())
            if title in page_lookup
        ]
        evidencias = list(record["seed_activity"]["evidencias"])
        evidencias.extend(related_pages)
        evidencias.append(migration_issue_url)
        with_jira_actor(
            control_plane.repo_root,
            str(record["seed_activity"]["agent"]).strip(),
            "jira-comment",
            lambda comment_jira, _actor: comment_jira.ensure_comment(
                issue_key,
                render_structured_comment(
                    {
                        "agent": control_plane.visible_name_for_reference(
                            str(record["seed_activity"]["agent"]).strip()
                        ),
                        "interaction_type": record["seed_activity"]["interaction_type"],
                        "status": record["seed_activity"]["status"],
                        "contexto": record["seed_activity"]["contexto"],
                        "evidencias": evidencias,
                        "proximo_passo": record["seed_activity"]["proximo_passo"],
                    }
                ),
            ),
            context_issue_key=issue_key,
        )

    return {
        "migration_issue": {
            "key": migration_issue_key,
            "url": migration_issue_url,
            "bundle_zip_path": bundle["zip_path"],
            "bundle_manifest_path": bundle["manifest_path"],
            "bundle_attachment_urls": bundle_attachment_urls,
        },
        "confluence_pages": page_lookup,
        "seeded_issues": seeded_issues,
        "counts": {
            "jira_records": len(jira_records),
            "confluence_pages": len(page_lookup),
        },
        "board": {
            "status": "deferred-until-agile-api-is-green",
        },
    }
