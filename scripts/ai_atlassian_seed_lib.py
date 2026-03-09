from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

from scripts.ai_atlassian_backfill_lib import build_backfill_plan
from scripts.ai_atlassian_migration_bundle_lib import build_migration_bundle
from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    load_ai_control_plane,
    load_yaml_map,
    resolve_atlassian_platform,
    resolve_repo_root,
)
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    AtlassianPlatformError,
    ConfluenceAdapter,
    JiraAdapter,
    render_structured_comment,
)

DEFAULT_CONFLUENCE_MODEL_PATH = Path("config/ai/confluence-model.yaml")
DEFAULT_JIRA_MODEL_PATH = Path("config/ai/jira-model.yaml")
MIGRATION_ISSUE_SUMMARY = "[MIGRATION] Bootstrap retro-sync Atlassian AI control plane"
MIGRATION_ISSUE_LABELS = [
    "atlassian-ia",
    "migration",
    "retro-sync",
    "control-plane",
]
WORKFLOW_ORDER = [
    ("backlog", ["backlog"]),
    ("refinement", ["refinement"]),
    ("ready", ["ready"]),
    ("doing", ["doing", "doing".upper()]),
    ("testing", ["testing", "testing".upper()]),
    ("review", ["review"]),
    ("done", ["done"]),
]


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


def state_hint_to_logical_status(state_hint: str) -> str:
    normalized = state_hint.strip().lower()
    if normalized in {"done", "aceita"}:
        return "done"
    if normalized in {"doing", "in progress", "executando"}:
        return "doing"
    if normalized in {"triage", "pendente"}:
        return "backlog"
    return "backlog"


def build_issue_description(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines if line.strip())


def build_list_html(items: list[tuple[str, str]]) -> str:
    if not items:
        return "<p>n/a</p>"
    rendered = "".join(
        f'<li><a href="{escape(url, quote=True)}">{escape(label)}</a></li>' for label, url in items
    )
    return f"<ul>{rendered}</ul>"


def build_storage_snapshot(
    *,
    title: str,
    repo_root: Path,
    repo_artifact: str,
    related_issues: list[tuple[str, str]],
    extra_notes: list[str] | None = None,
) -> str:
    source_path = repo_root / repo_artifact
    source_body = source_path.read_text(encoding="utf-8")
    notes = extra_notes or []
    notes_html = "".join(f"<li>{escape(note)}</li>" for note in notes if note.strip())
    notes_block = f"<ul>{notes_html}</ul>" if notes_html else "<p>n/a</p>"
    return (
        f"<h1>{escape(title)}</h1>"
        "<p>Pagina sincronizada a partir do artefato versionado no repositorio.</p>"
        f"<p><strong>Origem no repo:</strong> <code>{escape(repo_artifact)}</code></p>"
        "<h2>Issues relacionadas</h2>"
        f"{build_list_html(related_issues)}"
        "<h2>Notas de sincronizacao</h2>"
        f"{notes_block}"
        "<h2>Conteudo de origem</h2>"
        f"<pre>{escape(source_body)}</pre>"
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
    actual_space_key = str(space.get("key", "")).strip() or resolved.confluence_space_key
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
    bundle_zip_path: Path,
    bundle_manifest_path: str,
) -> tuple[dict[str, Any], list[str]]:
    existing = jira.find_issue_by_summary(
        project_key=project_key,
        summary=MIGRATION_ISSUE_SUMMARY,
        issue_types=["Task"],
    )
    if existing:
        issue = existing
    else:
        issue = jira.create_issue(
            project_key=project_key,
            issue_type="Task",
            summary=MIGRATION_ISSUE_SUMMARY,
            description=build_issue_description(
                [
                    "Issue de governanca da migracao retroativa do piloto AI control plane.",
                    f"Bundle local: {bundle_zip_path}",
                    f"Manifesto local: {bundle_manifest_path}",
                    "Objetivo: anexar o bundle auditavel, sincronizar paginas Confluence e semear backlog/worklog no Jira.",
                ]
            ),
            labels=MIGRATION_ISSUE_LABELS,
        )
    issue_key = str(issue.get("key", "")).strip()
    if not issue_key:
        raise AtlassianPlatformError("Nao foi possivel resolver a key da issue de migracao.")

    current = jira.get_issue(issue_key, fields=["attachment", "status"])
    attachments = ((current.get("fields") or {}).get("attachment")) or []
    existing_names = {
        str(entry.get("filename", "")).strip()
        for entry in attachments
        if isinstance(entry, dict)
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
    current_index = -1
    target_index = -1
    for index, (logical, candidates) in enumerate(WORKFLOW_ORDER):
        candidate_set = {normalize_status_label(value) for value in candidates}
        if normalize_status_label(current_status) in candidate_set:
            current_index = index
        if logical == target_logical_status:
            target_index = index
    if target_index < 0 or current_index >= target_index:
        return
    for next_index in range(current_index + 1, target_index + 1):
        _, candidates = WORKFLOW_ORDER[next_index]
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
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    _, confluence_model = load_confluence_model(control_plane.repo_root)
    client = AtlassianHttpClient(resolved)
    confluence = ConfluenceAdapter(client)
    jira = JiraAdapter(client)

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
            related_links.append((migration_issue_key, issue_url(resolved.site_url, migration_issue_key)))
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
            "Pagina resincronizada pelo docs sync dedicado do Confluence.",
            "Sincronizacao desacoplada do seed completo para manter a documentacao viva.",
        ],
        version_message="sync-atlassian-docs",
    )

    if migration_issue_key:
        jira.add_comment(
            migration_issue_key,
            render_structured_comment(
                {
                    "agent": "ai-documentation-agent",
                    "interaction_type": "documentation-sync",
                    "status": "Doing",
                    "contexto": [
                        "Confluence resincronizado por task dedicada, sem depender da semeadura completa.",
                        "O objetivo e manter a documentacao oficial viva enquanto o board do Jira Software ainda esta em tratamento.",
                    ],
                    "evidencias": [page["url"] for page in page_lookup.values()],
                    "proximo_passo": "Continuar refletindo no Confluence qualquer atualizacao aprovada do control plane e dos artefatos de migracao.",
                }
            ),
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
    client = AtlassianHttpClient(resolved)
    jira = JiraAdapter(client)
    confluence = ConfluenceAdapter(client)

    bundle = build_migration_bundle(control_plane.repo_root)
    backfill = build_backfill_plan(control_plane.repo_root)
    migration_issue, bundle_attachment_urls = ensure_migration_issue(
        jira=jira,
        project_key=resolved.jira_project_key,
        site_url=resolved.site_url,
        bundle_zip_path=Path(bundle["zip_path"]),
        bundle_manifest_path=str(bundle["manifest_path"]),
    )
    migration_issue_key = str(migration_issue.get("key", "")) or MIGRATION_ISSUE_SUMMARY
    migration_issue_url = issue_url(resolved.site_url, migration_issue_key)

    seeded_issues: list[dict[str, str]] = []
    jira_records = []
    jira_records.extend(backfill["jira"]["roadmap_backlog"])
    jira_records.extend(backfill["jira"]["roadmap_suggestions"])
    jira_records.extend(backfill["jira"]["worklog_doing"])
    jira_records.extend(backfill["jira"]["worklog_done"])

    for record in jira_records:
        existing = jira.find_issue_by_summary(
            project_key=resolved.jira_project_key,
            summary=str(record["summary"]).strip(),
            issue_types=[str(record["issue_type"]).strip()],
        )
        if existing:
            issue = existing
            created = False
        else:
            issue = jira.create_issue(
                project_key=resolved.jira_project_key,
                issue_type=str(record["issue_type"]).strip(),
                summary=str(record["summary"]).strip(),
                description=build_issue_description(record["description_lines"]),
                labels=[str(label).strip() for label in record["labels"] if str(label).strip()],
            )
            created = True
        issue_key = str(issue.get("key", "")).strip()
        if not issue_key:
            raise AtlassianPlatformError(f"Nao foi possivel resolver a key da issue para {record['summary']!r}.")
        seeded_issues.append(
            {
                "external_id": str(record["external_id"]).strip(),
                "key": issue_key,
                "origin": str(record["origin"]).strip(),
                "summary": str(record["summary"]).strip(),
            }
        )
        if created:
            ensure_issue_reaches_status(
                jira=jira,
                issue_key=issue_key,
                target_logical_status=state_hint_to_logical_status(str(record["state_hint"]).strip()),
            )

    seed_issue_links = [(entry["key"], issue_url(resolved.site_url, entry["key"])) for entry in seeded_issues]
    migration_link = (migration_issue_key, migration_issue_url)
    page_lookup = sync_confluence_page_tree(
        adapter=confluence,
        resolved=resolved,
        repo_root=control_plane.repo_root,
        model=confluence_model,
        related_links=[migration_link, *seed_issue_links],
        notes=[
            "Pagina sincronizada automaticamente pelo AI Documentation Agent.",
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
    jira.add_comment(
        migration_issue_key,
        render_structured_comment(
            {
                "agent": "ai-documentation-agent",
                "interaction_type": "schema-artifact",
                "status": "Doing",
                "contexto": [
                    "Schema Jira aplicado e bundle auditavel gerado antes da semeadura.",
                    "Confluence sincronizado como fonte oficial de documentacao viva.",
                ],
                "evidencias": migration_evidences,
                "proximo_passo": "Concluir a semeadura retroativa e manter a operacao nativa em Jira/Confluence.",
            }
        ),
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
        jira.add_comment(
            issue_key,
            render_structured_comment(
                {
                    "agent": record["seed_activity"]["agent"],
                    "interaction_type": record["seed_activity"]["interaction_type"],
                    "status": record["seed_activity"]["status"],
                    "contexto": record["seed_activity"]["contexto"],
                    "evidencias": evidencias,
                    "proximo_passo": record["seed_activity"]["proximo_passo"],
                }
            ),
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
