from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.ai_atlassian_backfill_lib import build_backfill_plan
from scripts.ai_atlassian_seed_lib import (
    MIGRATION_ISSUE_SUMMARY,
    build_issue_description,
    build_migration_issue_description,
    extract_external_id,
    issue_extra_fields,
    sync_confluence_docs,
)
from scripts.ai_control_plane_lib import (
    linkify_repo_relative_paths,
    load_ai_control_plane,
    resolve_atlassian_platform,
)
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    ConfluenceAdapter,
    JiraAdapter,
    adf_text_document,
    adf_to_text,
    normalize_text_for_dedup,
    render_structured_comment,
)

AI_LABEL_HINTS = {
    "atlassian-ia",
    "retro-sync",
    "control-plane",
    "migration",
    "worklog",
}
LEGACY_MIGRATION_SUMMARY = "[MIGRATION] Bootstrap retro-sync Atlassian AI control plane"
STRUCTURED_COMMENT_ALIASES = {
    "agent": "agent",
    "agente": "agent",
    "interaction type": "interaction_type",
    "tipo de interacao": "interaction_type",
    "status": "status",
    "status atual": "status",
    "contexto": "contexto",
    "evidencias": "evidencias",
    "proximo passo": "proximo_passo",
}
STRUCTURED_LIST_KEYS = {"contexto", "evidencias"}
PLAYWRIGHT_STORAGE_STATE_RE = (
    r"(?i)\.cache[/\\]playwright[/\\]atlassian[/\\]storage-state\.json\.?"
)


def issue_is_ai_generated(issue: dict[str, Any], *, author_account_id: str) -> bool:
    fields = issue.get("fields") or {}
    reporter = fields.get("reporter") or {}
    reporter_account_id = str(reporter.get("accountId", "")).strip()
    if reporter_account_id and reporter_account_id == author_account_id:
        return True
    labels = fields.get("labels") or []
    if isinstance(labels, list):
        normalized_labels = {str(item).strip().casefold() for item in labels if str(item).strip()}
        if normalized_labels.intersection(AI_LABEL_HINTS):
            return True
    summary = str(fields.get("summary", "")).strip()
    return summary in {MIGRATION_ISSUE_SUMMARY, LEGACY_MIGRATION_SUMMARY}


def parse_structured_comment(raw_text: str) -> dict[str, Any] | None:
    parsed: dict[str, Any] = {}
    current_key = ""
    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        matched_key = ""
        for label, key in STRUCTURED_COMMENT_ALIASES.items():
            if stripped.casefold() == label:
                matched_key = key
                value = ""
                break
            prefix = f"{label}:"
            if stripped.casefold().startswith(prefix):
                matched_key = key
                value = stripped.split(":", 1)[1].strip()
                break
        else:
            value = ""
        if matched_key:
            current_key = matched_key
            if current_key in STRUCTURED_LIST_KEYS:
                parsed[current_key] = [value] if value else []
            else:
                parsed[current_key] = value
            continue
        if not current_key:
            continue
        item = stripped[2:].strip() if stripped.startswith("- ") else stripped
        if not item:
            continue
        if current_key in STRUCTURED_LIST_KEYS:
            parsed.setdefault(current_key, []).append(item)
        else:
            existing = str(parsed.get(current_key, "")).strip()
            parsed[current_key] = f"{existing} {item}".strip() if existing else item
    return parsed or None


def repair_issue_description(
    jira: JiraAdapter,
    issue_key: str,
    description: Any,
    *,
    repo_root: str | Path | None,
    legacy_space_key: str,
    canonical_space_key: str,
) -> bool:
    raw_text = canonicalize_generated_text(
        adf_to_text(description).strip(),
        repo_root=repo_root,
        legacy_space_key=legacy_space_key,
        canonical_space_key=canonical_space_key,
    )
    if not raw_text:
        return False
    desired = adf_text_document(raw_text, site_url=jira.site_url())
    if description == desired:
        return False
    jira.update_issue_fields(issue_key, {"description": raw_text})
    return True


def canonicalize_generated_comment_text(
    raw_text: str,
    *,
    repo_root: str | Path | None = None,
    legacy_space_key: str,
    canonical_space_key: str,
) -> str:
    normalized = canonicalize_generated_text(
        raw_text,
        repo_root=repo_root,
        legacy_space_key=legacy_space_key,
        canonical_space_key=canonical_space_key,
    )
    parsed = parse_structured_comment(normalized)
    if parsed:
        return render_structured_comment(parsed)
    return normalized


def repair_issue_comments(
    jira: JiraAdapter,
    issue_key: str,
    *,
    author_account_id: str,
    repo_root: str | Path | None,
    legacy_space_key: str,
    canonical_space_key: str,
) -> dict[str, int]:
    comments = jira.list_comments(issue_key, max_results=500)
    dedup_groups: dict[str, list[tuple[dict[str, Any], str]]] = {}
    for comment in comments:
        author = comment.get("author") or {}
        if str(author.get("accountId", "")).strip() != author_account_id:
            continue
        raw_text = canonicalize_generated_comment_text(
            adf_to_text(comment.get("body")).strip(),
            repo_root=repo_root,
            legacy_space_key=legacy_space_key,
            canonical_space_key=canonical_space_key,
        )
        normalized = normalize_text_for_dedup(raw_text)
        if not normalized:
            continue
        dedup_groups.setdefault(normalized, []).append((comment, raw_text))

    deleted = 0
    updated = 0
    for entries in dedup_groups.values():
        keep_comment, keep_text = entries[0]
        keep_id = str(keep_comment.get("id", "")).strip()
        desired = adf_text_document(keep_text, site_url=jira.site_url())
        if keep_id and keep_comment.get("body") != desired:
            jira.update_comment(issue_key, keep_id, keep_text)
            updated += 1
        for duplicate_comment, _duplicate_text in entries[1:]:
            duplicate_id = str(duplicate_comment.get("id", "")).strip()
            if not duplicate_id:
                continue
            jira.delete_comment(issue_key, duplicate_id)
            deleted += 1
    return {
        "updated_comments": updated,
        "deleted_comments": deleted,
    }


def canonicalize_generated_text(
    raw_text: str,
    *,
    repo_root: str | Path | None = None,
    legacy_space_key: str,
    canonical_space_key: str,
) -> str:
    normalized = raw_text.strip()
    if not normalized:
        return ""
    if legacy_space_key and canonical_space_key and legacy_space_key != canonical_space_key:
        normalized = normalized.replace(
            f"/wiki/spaces/{legacy_space_key}/",
            f"/wiki/spaces/{canonical_space_key}/",
        )
    normalized = re.sub(
        PLAYWRIGHT_STORAGE_STATE_RE,
        "storageState local do Playwright (nao versionado).",
        normalized,
    )
    return linkify_repo_relative_paths(normalized, repo_root=repo_root)


def prune_redundant_migration_links(
    jira: JiraAdapter,
    issue_key: str,
    *,
    migration_issue_key: str,
) -> int:
    if not migration_issue_key or issue_key.strip().upper() == migration_issue_key.strip().upper():
        return 0
    deleted = 0
    for entry in jira.list_issue_links(issue_key):
        link_id = str(entry.get("id", "")).strip()
        if not link_id:
            continue
        type_payload = entry.get("type") or {}
        link_name = str(type_payload.get("name", "")).strip()
        linked_issue = entry.get("outwardIssue") or entry.get("inwardIssue") or {}
        linked_key = str(linked_issue.get("key", "")).strip().upper()
        if link_name == "Relates" and linked_key == migration_issue_key.strip().upper():
            jira.delete_issue_link(link_id)
            deleted += 1
    return deleted


def repair_generated_atlassian(repo_root: str | Path | None = None) -> dict[str, Any]:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    client = AtlassianHttpClient(resolved)
    jira = JiraAdapter(client)
    confluence = ConfluenceAdapter(client)
    current_user = jira.current_user()
    author_account_id = str(current_user.get("accountId", "")).strip()
    space = confluence.get_space(resolved.confluence_space_key)
    legacy_space_key = str(space.get("key", "")).strip()
    canonical_space_key = (
        str(space.get("currentActiveAlias", "")).strip() or resolved.confluence_space_key
    )
    issues = jira.search_issues(
        f'project = "{resolved.jira_project_key}" ORDER BY created ASC',
        fields=["summary", "description", "reporter", "labels", "issuetype"],
        max_results=500,
    )
    migration_issue_key = ""
    for issue in issues:
        if issue_is_ai_generated(issue, author_account_id=author_account_id):
            fields = issue.get("fields") or {}
            labels = {str(label).strip().casefold() for label in fields.get("labels") or []}
            summary = str(fields.get("summary", "")).strip()
            if "migration" in labels or summary in {
                LEGACY_MIGRATION_SUMMARY,
                MIGRATION_ISSUE_SUMMARY,
            }:
                migration_issue_key = str(issue.get("key", "")).strip()
                if migration_issue_key:
                    break
    backfill = build_backfill_plan(control_plane.repo_root)
    desired_records: dict[str, dict[str, Any]] = {}
    for bucket in (
        "roadmap_backlog",
        "roadmap_suggestions",
        "worklog_doing",
        "worklog_done",
    ):
        for record in backfill["jira"][bucket]:
            desired_records[str(record["external_id"]).strip()] = record

    repaired_issue_keys: list[str] = []
    updated_descriptions = 0
    updated_summaries = 0
    updated_comments = 0
    deleted_comments = 0
    deleted_links = 0

    for issue in issues:
        issue_key = str(issue.get("key", "")).strip()
        if not issue_key or not issue_is_ai_generated(issue, author_account_id=author_account_id):
            continue
        fields = issue.get("fields") or {}
        description = fields.get("description")
        issue_changed = False
        summary = str(fields.get("summary", "")).strip()
        external_id = extract_external_id(issue)
        desired_record = desired_records.get(external_id)
        if desired_record is not None:
            desired_summary = str(desired_record["summary"]).strip()
            desired_description = build_issue_description(desired_record["description_lines"])
            current_summary = str(fields.get("summary", "")).strip()
            current_description = canonicalize_generated_text(
                adf_to_text(description).strip(),
                repo_root=control_plane.repo_root,
                legacy_space_key=legacy_space_key,
                canonical_space_key=canonical_space_key,
            )
            if current_summary != desired_summary or current_description != desired_description:
                jira.update_issue_fields(
                    issue_key,
                    {
                        "summary": desired_summary,
                        "description": desired_description,
                        "labels": [
                            str(label).strip()
                            for label in desired_record.get("labels") or []
                            if str(label).strip()
                        ],
                        **issue_extra_fields(desired_record),
                    },
                )
                if current_summary != desired_summary:
                    updated_summaries += 1
                if current_description != desired_description:
                    updated_descriptions += 1
                issue_changed = True
            if migration_issue_key:
                jira.ensure_issue_link(issue_key, migration_issue_key, link_type="Relates")
        elif "migration" in {
            str(label).strip().casefold() for label in fields.get("labels") or []
        } and summary in {LEGACY_MIGRATION_SUMMARY, MIGRATION_ISSUE_SUMMARY}:
            attachments = fields.get("attachment") or []
            attachment_name = "bundle-auditavel-anexado"
            if isinstance(attachments, list):
                for entry in attachments:
                    if not isinstance(entry, dict):
                        continue
                    candidate = str(entry.get("filename", "")).strip()
                    if candidate.endswith(".zip"):
                        attachment_name = candidate
                        break
            desired_description = build_migration_issue_description(
                control_plane.repo_root,
                bundle_attachment_name=attachment_name,
            )
            current_description = canonicalize_generated_text(
                adf_to_text(description).strip(),
                repo_root=control_plane.repo_root,
                legacy_space_key=legacy_space_key,
                canonical_space_key=canonical_space_key,
            )
            if summary != MIGRATION_ISSUE_SUMMARY or current_description != desired_description:
                jira.update_issue_fields(
                    issue_key,
                    {
                        "summary": MIGRATION_ISSUE_SUMMARY,
                        "description": desired_description,
                    },
                )
                if summary != MIGRATION_ISSUE_SUMMARY:
                    updated_summaries += 1
                if current_description != desired_description:
                    updated_descriptions += 1
                issue_changed = True
        elif repair_issue_description(
            jira,
            issue_key,
            description,
            repo_root=control_plane.repo_root,
            legacy_space_key=legacy_space_key,
            canonical_space_key=canonical_space_key,
        ):
            updated_descriptions += 1
            issue_changed = True
        comment_result = repair_issue_comments(
            jira,
            issue_key,
            author_account_id=author_account_id,
            repo_root=control_plane.repo_root,
            legacy_space_key=legacy_space_key,
            canonical_space_key=canonical_space_key,
        )
        updated_comments += comment_result["updated_comments"]
        deleted_comments += comment_result["deleted_comments"]
        removed_links = prune_redundant_migration_links(
            jira,
            issue_key,
            migration_issue_key=migration_issue_key,
        )
        deleted_links += removed_links
        if issue_changed or any(comment_result.values()) or removed_links:
            repaired_issue_keys.append(issue_key)

    docs_sync = sync_confluence_docs(
        control_plane.repo_root,
        issue_keys=repaired_issue_keys,
    )
    return {
        "jira": {
            "issues_scanned": len(issues),
            "issues_repaired": len(repaired_issue_keys),
            "updated_summaries": updated_summaries,
            "updated_descriptions": updated_descriptions,
            "updated_comments": updated_comments,
            "deleted_comments": deleted_comments,
            "deleted_links": deleted_links,
            "issue_keys": repaired_issue_keys,
        },
        "confluence": docs_sync,
    }
