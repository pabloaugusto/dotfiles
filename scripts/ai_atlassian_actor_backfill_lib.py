from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scripts.ai_atlassian_actor_lib import (
    ResolvedAtlassianActor,
    global_jira_adapter,
    resolve_atlassian_actor,
    resolve_global_atlassian_actor,
    with_jira_actor,
)
from scripts.ai_atlassian_agent_comment_audit_lib import parse_structured_comment
from scripts.ai_control_plane_lib import load_ai_control_plane
from scripts.atlassian_platform_lib import (
    AtlassianPlatformError,
    JiraAdapter,
    adf_to_text,
    render_structured_comment,
)

DEFAULT_MAX_ISSUES = 500
DEFAULT_READ_RETRY_ATTEMPTS = 4
DEFAULT_READ_RETRY_DELAY_SECONDS = 2.0


@dataclass(frozen=True)
class ActorCommentBackfillCandidate:
    issue_key: str
    issue_summary: str
    legacy_comment_id: str
    legacy_author_account_id: str
    legacy_author_display_name: str
    role_id: str
    role_visible_name: str
    desired_body: str
    normalized_body: str
    has_role_owned_duplicate: bool


def _normalized_text(value: str) -> str:
    return " ".join(str(value or "").split()).strip().casefold()


def _role_identity_variants(role_id: str, repo_root: Path) -> set[str]:
    control_plane = load_ai_control_plane(repo_root)
    normalized_role_id = control_plane.resolve_role_reference(role_id) or str(role_id).strip()
    variants = {
        normalized_role_id,
        control_plane.visible_name_for_reference(normalized_role_id),
        control_plane.formal_name_for_agent(normalized_role_id),
        control_plane.chat_alias_for_agent(normalized_role_id),
    }
    return {_normalized_text(entry) for entry in variants if str(entry).strip()}


def _author_matches_actor(author: dict[str, Any], actor: ResolvedAtlassianActor) -> bool:
    author_account_id = str(author.get("accountId", "")).strip()
    author_display_name = str(author.get("displayName", "")).strip()
    author_email = str(author.get("emailAddress", "")).strip()
    actor_candidates = {
        _normalized_text(actor.account_id),
        _normalized_text(actor.service_account),
        _normalized_text(actor.email),
        _normalized_text(actor.role_visible_name),
    }
    author_candidates = {
        _normalized_text(author_account_id),
        _normalized_text(author_display_name),
        _normalized_text(author_email),
    }
    actor_candidates.discard("")
    author_candidates.discard("")
    if not actor_candidates or not author_candidates:
        return False
    return bool(actor_candidates & author_candidates)


def _desired_comment_body(parsed: dict[str, Any], visible_name: str) -> str:
    payload = {
        "agent": visible_name,
        "interaction_type": str(parsed.get("interaction_type", "")).strip(),
        "status": str(parsed.get("status", "")).strip(),
        "contexto": parsed.get("contexto") or [],
        "evidencias": parsed.get("evidencias") or [],
        "proximo_passo": parsed.get("proximo_passo") or [],
    }
    if isinstance(payload["proximo_passo"], list):
        values = [str(entry).strip() for entry in payload["proximo_passo"] if str(entry).strip()]
        payload["proximo_passo"] = values[0] if values else ""
    return render_structured_comment(payload)


def _is_transient_read_error(exc: AtlassianPlatformError) -> bool:
    detail = str(exc or "").casefold()
    transient_markers = (
        "falha de conectividade com atlassian",
        "timed out",
        "connection reset",
        "winerror 10054",
        "temporarily unavailable",
        "remote host",
    )
    return any(marker in detail for marker in transient_markers)


def _read_with_retry(label: str, operation: Any) -> Any:
    last_error: AtlassianPlatformError | None = None
    for attempt in range(1, DEFAULT_READ_RETRY_ATTEMPTS + 1):
        try:
            return operation()
        except AtlassianPlatformError as exc:
            last_error = exc
            if not _is_transient_read_error(exc) or attempt >= DEFAULT_READ_RETRY_ATTEMPTS:
                raise
            time.sleep(DEFAULT_READ_RETRY_DELAY_SECONDS * attempt)
    assert last_error is not None
    raise last_error


def _iter_issue_candidates(
    jira: JiraAdapter,
    *,
    project_key: str,
    issue_keys: list[str] | None,
    max_issues: int,
) -> list[dict[str, Any]]:
    if issue_keys:
        issues: list[dict[str, Any]] = []
        for raw_key in issue_keys:
            issue_key = str(raw_key or "").strip().upper()
            if not issue_key:
                continue
            issues.append(
                _read_with_retry(
                    f"get-issue:{issue_key}",
                    lambda issue_key=issue_key: jira.get_issue(issue_key, fields=["summary", "status"]),
                )
            )
        return issues
    return _read_with_retry(
        f"search-issues:{project_key}",
        lambda: jira.search_issues(
            f'project = "{project_key}" ORDER BY updated DESC',
            fields=["summary", "status"],
            max_results=max_issues,
        ),
    )


def audit_actor_comment_backfill(
    repo_root: str | Path | None = None,
    *,
    role_id: str = "ai-product-owner",
    issue_keys: list[str] | None = None,
    max_issues: int = DEFAULT_MAX_ISSUES,
    only_global_authored: bool = True,
) -> dict[str, Any]:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    control_plane = load_ai_control_plane(resolved_repo_root)
    normalized_role_id = control_plane.resolve_role_reference(role_id) or str(role_id).strip()
    role_actor = resolve_atlassian_actor(resolved_repo_root, normalized_role_id, "jira-comment")
    global_actor = resolve_global_atlassian_actor(resolved_repo_root, normalized_role_id, "jira-comment")
    jira = global_jira_adapter(resolved_repo_root)
    issues = _iter_issue_candidates(
        jira,
        project_key=jira.client.resolved.jira_project_key,
        issue_keys=issue_keys,
        max_issues=max_issues,
    )
    role_variants = _role_identity_variants(normalized_role_id, resolved_repo_root)
    candidates: list[ActorCommentBackfillCandidate] = []

    for issue in issues:
        issue_key = str(issue.get("key", "")).strip().upper()
        fields = issue.get("fields") or {}
        issue_summary = str(fields.get("summary", "")).strip()
        if not issue_key:
            continue
        comments = _read_with_retry(
            f"list-comments:{issue_key}",
            lambda issue_key=issue_key: jira.list_comments(issue_key, max_results=500),
        )
        role_owned_bodies = {
            _normalized_text(adf_to_text(comment.get("body")).strip())
            for comment in comments
            if _author_matches_actor(comment.get("author") or {}, role_actor)
        }
        for comment in comments:
            author = comment.get("author") or {}
            raw_text = adf_to_text(comment.get("body")).strip()
            parsed = parse_structured_comment(raw_text)
            if not parsed:
                continue
            parsed_agent = _normalized_text(str(parsed.get("agent", "")).strip())
            if not parsed_agent or parsed_agent not in role_variants:
                continue
            if _author_matches_actor(author, role_actor):
                continue
            if only_global_authored and not _author_matches_actor(author, global_actor):
                continue
            desired_body = _desired_comment_body(parsed, role_actor.role_visible_name)
            normalized_body = _normalized_text(desired_body)
            candidates.append(
                ActorCommentBackfillCandidate(
                    issue_key=issue_key,
                    issue_summary=issue_summary,
                    legacy_comment_id=str(comment.get("id", "")).strip(),
                    legacy_author_account_id=str(author.get("accountId", "")).strip(),
                    legacy_author_display_name=str(author.get("displayName", "")).strip(),
                    role_id=normalized_role_id,
                    role_visible_name=role_actor.role_visible_name,
                    desired_body=desired_body,
                    normalized_body=normalized_body,
                    has_role_owned_duplicate=normalized_body in role_owned_bodies,
                )
            )

    return {
        "repo_root": str(resolved_repo_root),
        "role_id": normalized_role_id,
        "role_visible_name": role_actor.role_visible_name,
        "role_actor": role_actor.to_public_dict(),
        "global_actor": global_actor.to_public_dict(),
        "only_global_authored": only_global_authored,
        "counts": {
            "issues_scanned": len(issues),
            "candidate_comments": len(candidates),
            "candidate_comments_with_duplicate": sum(
                1 for candidate in candidates if candidate.has_role_owned_duplicate
            ),
        },
        "candidates": [asdict(candidate) for candidate in candidates],
    }


def apply_actor_comment_backfill(
    repo_root: str | Path | None = None,
    *,
    role_id: str = "ai-product-owner",
    issue_keys: list[str] | None = None,
    max_issues: int = DEFAULT_MAX_ISSUES,
    delete_legacy_comments: bool = True,
    only_global_authored: bool = True,
) -> dict[str, Any]:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    audit = audit_actor_comment_backfill(
        resolved_repo_root,
        role_id=role_id,
        issue_keys=issue_keys,
        max_issues=max_issues,
        only_global_authored=only_global_authored,
    )
    role_actor_payload = audit.get("role_actor") or {}
    if str(role_actor_payload.get("actor_mode", "")).strip() != "role-service-account":
        audit["apply_status"] = "skipped-no-role-service-account"
        audit["apply_counts"] = {
            "created_comments": 0,
            "deleted_legacy_comments": 0,
            "reused_role_owned_comments": 0,
            "skipped_comments": audit["counts"]["candidate_comments"],
        }
        return audit

    jira = global_jira_adapter(resolved_repo_root)
    created_comments = 0
    deleted_legacy_comments = 0
    reused_role_owned_comments = 0
    skipped_comments = 0
    applied: list[dict[str, Any]] = []

    for candidate_payload in audit["candidates"]:
        candidate = ActorCommentBackfillCandidate(**candidate_payload)
        item_result = {
            "issue_key": candidate.issue_key,
            "legacy_comment_id": candidate.legacy_comment_id,
            "action": "",
            "actor_mode": "",
        }
        if candidate.has_role_owned_duplicate:
            item_result["action"] = "reuse-existing-role-comment"
            item_result["actor_mode"] = str(role_actor_payload.get("actor_mode", "")).strip()
            reused_role_owned_comments += 1
        else:
            created_comment, used_actor = with_jira_actor(
                resolved_repo_root,
                candidate.role_id,
                "jira-comment",
                lambda actor_jira, _actor: actor_jira.add_comment(
                    candidate.issue_key,
                    candidate.desired_body,
                ),
                context_issue_key=candidate.issue_key,
            )
            item_result["action"] = "create-role-comment"
            item_result["created_comment_id"] = str(created_comment.get("id", "")).strip()
            item_result["actor_mode"] = used_actor.actor_mode
            if used_actor.actor_mode != "role-service-account":
                skipped_comments += 1
                item_result["action"] = "skipped-global-fallback"
                applied.append(item_result)
                continue
            created_comments += 1
        if delete_legacy_comments and candidate.legacy_comment_id:
            jira.delete_comment(candidate.issue_key, candidate.legacy_comment_id)
            deleted_legacy_comments += 1
            item_result["deleted_legacy_comment_id"] = candidate.legacy_comment_id
        applied.append(item_result)

    audit["apply_status"] = "applied"
    audit["apply_counts"] = {
        "created_comments": created_comments,
        "deleted_legacy_comments": deleted_legacy_comments,
        "reused_role_owned_comments": reused_role_owned_comments,
        "skipped_comments": skipped_comments,
    }
    audit["applied"] = applied
    return audit
