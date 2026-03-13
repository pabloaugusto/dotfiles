from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    ResolvedAtlassianPlatform,
    load_ai_control_plane,
    resolve_atlassian_platform,
    resolve_value_spec,
)
from scripts.atlassian_platform_lib import (
    AtlassianHttpClient,
    AtlassianPlatformError,
    ConfluenceAdapter,
    JiraAdapter,
)

T = TypeVar("T")

ROLE_SURFACES = {
    "jira-comment",
    "jira-assignee",
    "confluence-comment",
    "confluence-page",
}
DEFAULT_FALLBACK_ISSUE_TYPE = "Bug"
DEFAULT_FALLBACK_LABELS = [
    "atlassian",
    "service-account",
    "runtime-fallback",
]
_ACTOR_CACHE: dict[tuple[str, str, str], "ResolvedAtlassianActor"] = {}
_USER_SEARCH_CACHE: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}


@dataclass(frozen=True)
class ResolvedAtlassianActor:
    role_id: str
    role_visible_name: str
    surface: str
    actor_mode: str
    resolution_reason: str
    search_fallback_used: bool
    search_fallback_type: str
    account_id_source: str
    email: str
    token: str
    account_id: str
    service_account: str
    site_url: str
    cloud_id: str
    auth_mode: str
    jira_project_key: str
    confluence_space_key: str
    fallback_issue_required: bool
    fallback_issue_reason: str
    fallback_issue_type: str
    global_fallback_allowed: bool

    def as_platform(self) -> ResolvedAtlassianPlatform:
        return ResolvedAtlassianPlatform(
            enabled=True,
            provider="atlassian-cloud",
            auth_mode=self.auth_mode,
            site_url=self.site_url,
            email=self.email,
            token=self.token,
            service_account=self.service_account,
            cloud_id=self.cloud_id,
            jira_enabled=True,
            jira_project_key=self.jira_project_key,
            confluence_enabled=True,
            confluence_space_key=self.confluence_space_key,
        )

    def to_public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("token", None)
        payload["has_token"] = bool(self.token)
        return payload


def _state_path(repo_root: Path) -> Path:
    return repo_root / ".cache" / "ai" / "atlassian-actor-resolution.json"


def _startup_ready_path(repo_root: Path) -> Path:
    return repo_root / ".cache" / "ai" / "startup-ready.json"


def _load_state(repo_root: Path) -> dict[str, Any]:
    path = _state_path(repo_root)
    if not path.exists():
        return {"resolutions": {}, "notified_fallbacks": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"resolutions": {}, "notified_fallbacks": {}}
    payload.setdefault("resolutions", {})
    payload.setdefault("notified_fallbacks", {})
    mutated = False
    resolutions = payload.get("resolutions")
    if isinstance(resolutions, dict):
        for entry in resolutions.values():
            if not isinstance(entry, dict):
                continue
            token = entry.pop("token", None)
            if token is not None:
                mutated = True
                entry["has_token"] = bool(token)
            elif "has_token" not in entry:
                entry["has_token"] = False
                mutated = True
    if mutated:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def actor_runtime_state(repo_root: str | Path | None) -> dict[str, Any]:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    payload = _load_state(resolved_repo_root)
    resolutions = payload.get("resolutions") or {}
    if not isinstance(resolutions, dict):
        resolutions = {}
    search_fallback_resolutions = sorted(
        key
        for key, entry in resolutions.items()
        if isinstance(entry, dict) and bool(entry.get("search_fallback_used", False))
    )
    return {
        "state_path": str(_state_path(resolved_repo_root)),
        "resolution_count": len(resolutions),
        "search_fallback_resolutions": search_fallback_resolutions,
        "resolutions": resolutions,
    }


def clear_actor_resolution_caches() -> None:
    _ACTOR_CACHE.clear()
    _USER_SEARCH_CACHE.clear()


def _save_state(repo_root: Path, payload: dict[str, Any]) -> None:
    path = _state_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _session_fingerprint(repo_root: Path) -> str:
    path = _startup_ready_path(repo_root)
    if not path.exists():
        return "startup-missing"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return "startup-invalid"
    status = payload.get("startup_governor_status") or {}
    if isinstance(status, dict):
        fingerprint = str(status.get("context_fingerprint", "")).strip()
        if fingerprint:
            return fingerprint
    return "startup-no-fingerprint"


def _global_actor(
    *,
    repo_root: Path,
    role_id: str,
    surface: str,
    base_platform: ResolvedAtlassianPlatform,
    fallback_issue_required: bool = False,
    fallback_issue_reason: str = "",
    fallback_issue_type: str = "",
) -> ResolvedAtlassianActor:
    account_id: dict[str, Any] = {
        "account_id": "",
        "source": "global-unresolved",
        "search_type": "",
        "resolved_from_secret": False,
    }
    try:
        account_id = _resolve_user_account_id(
            repo_root=repo_root,
            platform=base_platform,
            query=str(base_platform.service_account or "").strip(),
            preferred_email=str(base_platform.email or "").strip(),
            expected_display_name=str(base_platform.service_account or "").strip(),
            expected_account_type="app",
            require_active=True,
        )
    except AtlassianPlatformError:
        account_id = {
            "account_id": "",
            "source": "global-unresolved",
            "search_type": "",
            "resolved_from_secret": False,
        }
    control_plane = load_ai_control_plane(repo_root)
    return ResolvedAtlassianActor(
        role_id=role_id,
        role_visible_name=control_plane.visible_name_for_reference(role_id),
        surface=surface,
        actor_mode="global-service-account",
        resolution_reason="global-default",
        search_fallback_used=not bool(account_id.get("resolved_from_secret", False)),
        search_fallback_type=str(account_id.get("search_type", "")).strip(),
        account_id_source=str(account_id.get("source", "")).strip(),
        email=base_platform.email,
        token=base_platform.token,
        account_id=str(account_id.get("account_id", "")).strip(),
        service_account=base_platform.service_account,
        site_url=base_platform.site_url,
        cloud_id=base_platform.cloud_id,
        auth_mode=base_platform.auth_mode,
        jira_project_key=base_platform.jira_project_key,
        confluence_space_key=base_platform.confluence_space_key,
        fallback_issue_required=fallback_issue_required,
        fallback_issue_reason=fallback_issue_reason,
        fallback_issue_type=fallback_issue_type,
        global_fallback_allowed=False,
    )


def _surface_slug(surface: str) -> str:
    return str(surface or "").strip().lower()


def _fallback_summary(role_id: str, surface: str, reason: str, fallback_type: str) -> str:
    return (
        "Fallback Atlassian actor: "
        f"{role_id} | {surface} | {reason} | {fallback_type}"
    )


def _context_parent_key(jira: JiraAdapter, issue_key: str) -> str:
    normalized_issue_key = str(issue_key or "").strip().upper()
    if not normalized_issue_key:
        return ""
    issue = jira.get_issue(normalized_issue_key, fields=["parent"])
    fields = issue.get("fields") or {}
    parent = fields.get("parent") or {}
    if not isinstance(parent, dict):
        return ""
    return str(parent.get("key", "")).strip().upper()


def _ensure_fallback_issue(
    *,
    repo_root: Path,
    summary: str,
    description_lines: list[str],
    context_issue_key: str,
    labels: list[str],
) -> None:
    global_platform = _resolve_global_platform(repo_root)
    jira = JiraAdapter(AtlassianHttpClient(global_platform))
    existing = jira.find_issue_by_summary(
        project_key=global_platform.jira_project_key,
        summary=summary,
        issue_types=[DEFAULT_FALLBACK_ISSUE_TYPE],
    )
    body = "\n".join(description_lines).strip()
    if existing:
        issue_key = str(existing.get("key", "")).strip()
        if issue_key:
            jira.ensure_comment(issue_key, body)
            if context_issue_key:
                jira.ensure_issue_link(issue_key, context_issue_key, link_type="Relates")
        return

    extra_fields: dict[str, Any] = {}
    parent_key = _context_parent_key(jira, context_issue_key) if context_issue_key else ""
    if parent_key:
        extra_fields["parent"] = {"key": parent_key}
    created = jira.create_issue(
        project_key=global_platform.jira_project_key,
        issue_type=DEFAULT_FALLBACK_ISSUE_TYPE,
        summary=summary,
        description=body,
        labels=labels,
        extra_fields=extra_fields or None,
    )
    created_key = str(created.get("key", "")).strip()
    if created_key and context_issue_key:
        jira.ensure_issue_link(created_key, context_issue_key, link_type="Relates")


def _record_resolution(
    repo_root: Path,
    actor: ResolvedAtlassianActor,
    *,
    resolution_key: str | None = None,
) -> None:
    payload = _load_state(repo_root)
    resolutions = payload.get("resolutions") or {}
    if not isinstance(resolutions, dict):
        resolutions = {}
    key = resolution_key or f"{actor.role_id}::{actor.surface}"
    resolutions[key] = actor.to_public_dict()
    payload["resolutions"] = resolutions
    _save_state(repo_root, payload)


def _notify_fallback_issue_if_needed(
    *,
    repo_root: Path,
    actor: ResolvedAtlassianActor,
    context_issue_key: str,
    evidence_lines: list[str],
) -> None:
    if not actor.fallback_issue_required:
        return
    state = _load_state(repo_root)
    notified = state.get("notified_fallbacks") or {}
    if not isinstance(notified, dict):
        notified = {}
    session_key = _session_fingerprint(repo_root)
    dedupe_key = _fallback_summary(
        actor.role_id,
        actor.surface,
        actor.fallback_issue_reason,
        actor.fallback_issue_type,
    )
    session_entries = notified.get(session_key) or []
    if not isinstance(session_entries, list):
        session_entries = []
    if dedupe_key in session_entries:
        return
    summary = dedupe_key
    description_lines = [
        "# Incidente de fallback de actor Atlassian",
        "",
        f"- Agente: `{actor.role_id}`",
        f"- Nome visivel: `{actor.role_visible_name}`",
        f"- Surface: `{actor.surface}`",
        f"- Motivo: `{actor.fallback_issue_reason}`",
        f"- Tipo de fallback: `{actor.fallback_issue_type}`",
        f"- Sessao: `{session_key}`",
        f"- Modo resultante: `{actor.actor_mode}`",
        f"- Fonte do account_id: `{actor.account_id_source or 'n/a'}`",
    ]
    if context_issue_key:
        description_lines.append(f"- Issue de contexto: `{context_issue_key}`")
    if evidence_lines:
        description_lines.extend(["", "## Evidencias"])
        description_lines.extend(f"- {line}" for line in evidence_lines if line.strip())
    _ensure_fallback_issue(
        repo_root=repo_root,
        summary=summary,
        description_lines=description_lines,
        context_issue_key=context_issue_key,
        labels=[
            *DEFAULT_FALLBACK_LABELS,
            f"agent-{actor.role_id}",
            f"surface-{actor.surface}",
        ],
    )
    session_entries.append(dedupe_key)
    notified[session_key] = session_entries
    state["notified_fallbacks"] = notified
    _save_state(repo_root, state)


def _resolve_global_platform(repo_root: Path) -> ResolvedAtlassianPlatform:
    control_plane = load_ai_control_plane(repo_root)
    return resolve_atlassian_platform(control_plane.atlassian_definition(), repo_root=repo_root)


def _resolve_candidate_matches(
    *,
    candidates: list[dict[str, Any]],
    expected_email: str,
    expected_display_name: str,
    expected_account_type: str,
    require_active: bool,
) -> list[dict[str, Any]]:
    normalized_email = expected_email.strip().casefold()
    normalized_display_name = expected_display_name.strip().casefold()
    normalized_account_type = expected_account_type.strip().casefold()
    matches: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_email = str(candidate.get("emailAddress", "")).strip().casefold()
        candidate_display_name = str(candidate.get("displayName", "")).strip().casefold()
        candidate_type = str(candidate.get("accountType", "")).strip().casefold()
        candidate_active = bool(candidate.get("active", False))
        if normalized_account_type and candidate_type != normalized_account_type:
            continue
        if require_active and not candidate_active:
            continue
        if normalized_email and candidate_email and candidate_email != normalized_email:
            continue
        if normalized_display_name and candidate_display_name and candidate_display_name != normalized_display_name:
            continue
        matches.append(candidate)
    return matches


def _resolve_user_account_id(
    *,
    repo_root: Path,
    platform: ResolvedAtlassianPlatform,
    query: str,
    preferred_email: str,
    expected_display_name: str,
    expected_account_type: str,
    require_active: bool,
) -> dict[str, Any]:
    normalized_query = query.strip()
    normalized_email = preferred_email.strip()
    cache_key = (
        platform.email,
        platform.cloud_id,
        normalized_query,
        normalized_email,
        expected_display_name.strip(),
    )
    cached = _USER_SEARCH_CACHE.get(cache_key)
    if cached is not None:
        return dict(cached)

    jira = JiraAdapter(AtlassianHttpClient(platform))
    candidates: list[dict[str, Any]] = []
    search_type = ""
    if normalized_email:
        candidates = jira.search_users(normalized_email, max_results=20)
        matches = _resolve_candidate_matches(
            candidates=candidates,
            expected_email=normalized_email,
            expected_display_name=expected_display_name,
            expected_account_type=expected_account_type,
            require_active=require_active,
        )
        if len(matches) == 1:
            payload = {
                "account_id": str(matches[0].get("accountId", "")).strip(),
                "source": "search-email",
                "search_type": "search-email",
                "resolved_from_secret": False,
            }
            _USER_SEARCH_CACHE[cache_key] = payload
            return dict(payload)
    if normalized_query:
        candidates = jira.search_users(normalized_query, max_results=20)
        matches = _resolve_candidate_matches(
            candidates=candidates,
            expected_email=normalized_email,
            expected_display_name=expected_display_name,
            expected_account_type=expected_account_type,
            require_active=require_active,
        )
        search_type = "search-query"
        if len(matches) == 1:
            payload = {
                "account_id": str(matches[0].get("accountId", "")).strip(),
                "source": "search-query",
                "search_type": "search-query",
                "resolved_from_secret": False,
            }
            _USER_SEARCH_CACHE[cache_key] = payload
            return dict(payload)
        if len(matches) > 1:
            raise AtlassianPlatformError(
                "Busca de account_id Atlassian retornou mais de um candidato valido "
                f"para query={normalized_query!r}."
            )
    raise AtlassianPlatformError(
        "Nao foi possivel resolver account_id Atlassian por busca para "
        f"query={normalized_query!r} email={normalized_email!r}."
    )


def _resolve_actor_from_role(
    *,
    repo_root: Path,
    role_id: str,
    surface: str,
    context_issue_key: str,
    base_platform: ResolvedAtlassianPlatform,
) -> ResolvedAtlassianActor:
    control_plane = load_ai_control_plane(repo_root)
    actor_payload = control_plane.role_atlassian_actor_payload(role_id)
    fallback_reason = ""
    fallback_type = ""
    if not actor_payload or not control_plane.role_atlassian_actor_enabled(role_id):
        return _global_actor(
            repo_root=repo_root,
            role_id=role_id,
            surface=surface,
            base_platform=base_platform,
        )
    if not control_plane.role_atlassian_actor_surface_enabled(role_id, surface):
        return _global_actor(
            repo_root=repo_root,
            role_id=role_id,
            surface=surface,
            base_platform=base_platform,
        )

    search_fallback = actor_payload.get("search_fallback") or {}
    if search_fallback and not isinstance(search_fallback, dict):
        raise AiControlPlaneError(
            f"roles.{role_id}.atlassian_actor.search_fallback precisa ser mapa."
        )
    visible_name = control_plane.visible_name_for_reference(role_id)
    expected_display_name = str(search_fallback.get("expected_display_name", "")).strip()
    query = str(search_fallback.get("query", "")).strip()
    email_spec = str(actor_payload.get("email_secret_ref", "")).strip()
    token_spec = str(actor_payload.get("token_secret_ref", "")).strip()
    account_id_spec = str(actor_payload.get("account_id_secret_ref", "")).strip()
    expected_email_spec = str(search_fallback.get("expected_email_secret_ref", "")).strip()
    search_enabled = bool(search_fallback.get("enabled", False))

    try:
        email = resolve_value_spec(email_spec, repo_root=repo_root)
        token = resolve_value_spec(token_spec, repo_root=repo_root)
    except AiControlPlaneError:
        fallback_reason = "missing-primary-credentials"
        fallback_type = "global-fallback"
        actor = _global_actor(
            repo_root=repo_root,
            role_id=role_id,
            surface=surface,
            base_platform=base_platform,
            fallback_issue_required=True,
            fallback_issue_reason=fallback_reason,
            fallback_issue_type=fallback_type,
        )
        _notify_fallback_issue_if_needed(
            repo_root=repo_root,
            actor=actor,
            context_issue_key=context_issue_key,
            evidence_lines=[
                "Falha ao resolver email/token da service account propria via control plane.",
                f"Surface afetada: {surface}",
            ],
        )
        return actor

    expected_email = ""
    if expected_email_spec:
        try:
            expected_email = resolve_value_spec(expected_email_spec, repo_root=repo_root)
        except AiControlPlaneError:
            expected_email = ""
    if not expected_email:
        expected_email = email
    account_id = ""
    account_id_source = ""
    search_type = ""
    search_used = False
    if account_id_spec:
        try:
            account_id = resolve_value_spec(account_id_spec, repo_root=repo_root)
            account_id_source = "secret"
        except AiControlPlaneError:
            account_id = ""
    if not account_id and search_enabled:
        resolved_account = _resolve_user_account_id(
            repo_root=repo_root,
            platform=ResolvedAtlassianPlatform(
                enabled=True,
                provider=base_platform.provider,
                auth_mode=base_platform.auth_mode,
                site_url=base_platform.site_url,
                email=email,
                token=token,
                service_account=expected_display_name or visible_name,
                cloud_id=base_platform.cloud_id,
                jira_enabled=True,
                jira_project_key=base_platform.jira_project_key,
                confluence_enabled=True,
                confluence_space_key=base_platform.confluence_space_key,
            ),
            query=query or expected_display_name or visible_name,
            preferred_email=expected_email if bool(search_fallback.get("prefer_email_lookup", True)) else "",
            expected_display_name=expected_display_name or visible_name,
            expected_account_type=str(search_fallback.get("expected_account_type", "app")).strip()
            or "app",
            require_active=bool(search_fallback.get("require_active", True)),
        )
        account_id = str(resolved_account.get("account_id", "")).strip()
        account_id_source = str(resolved_account.get("source", "")).strip()
        search_type = str(resolved_account.get("search_type", "")).strip()
        search_used = True

    if surface == "jira-assignee" and not account_id:
        fallback_reason = "missing-primary-account-id"
        fallback_type = "search-or-global-fallback"
        actor = _global_actor(
            repo_root=repo_root,
            role_id=role_id,
            surface=surface,
            base_platform=base_platform,
            fallback_issue_required=True,
            fallback_issue_reason=fallback_reason,
            fallback_issue_type=fallback_type,
        )
        _notify_fallback_issue_if_needed(
            repo_root=repo_root,
            actor=actor,
            context_issue_key=context_issue_key,
            evidence_lines=[
                "Falha ao resolver account_id da service account propria.",
                f"Search fallback habilitado: {search_enabled}",
                f"Query configurada: {query or '(vazia)'}",
            ],
        )
        return actor

    actor = ResolvedAtlassianActor(
        role_id=role_id,
        role_visible_name=visible_name,
        surface=surface,
        actor_mode="role-service-account",
        resolution_reason="role-service-account",
        search_fallback_used=search_used,
        search_fallback_type=search_type,
        account_id_source=account_id_source,
        email=email,
        token=token,
        account_id=account_id,
        service_account=expected_display_name or visible_name,
        site_url=base_platform.site_url,
        cloud_id=base_platform.cloud_id,
        auth_mode=base_platform.auth_mode,
        jira_project_key=base_platform.jira_project_key,
        confluence_space_key=base_platform.confluence_space_key,
        fallback_issue_required=search_used,
        fallback_issue_reason="primary-account-id-secret-missing" if search_used else "",
        fallback_issue_type=search_type,
        global_fallback_allowed=bool(
            actor_payload.get("fallback_to_global_on_error", True)
        ),
    )
    if search_used:
        _notify_fallback_issue_if_needed(
            repo_root=repo_root,
            actor=actor,
            context_issue_key=context_issue_key,
            evidence_lines=[
                "Account_id da service account propria precisou ser resolvido por busca em Jira.",
                f"Query configurada: {query or '(vazia)'}",
                f"Fonte do account_id: {account_id_source}",
            ],
        )
    return actor


def resolve_atlassian_actor(
    repo_root: str | Path | None,
    role_id: str,
    surface: str,
    *,
    context_issue_key: str = "",
) -> ResolvedAtlassianActor:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    normalized_surface = _surface_slug(surface)
    if normalized_surface not in ROLE_SURFACES:
        raise AiControlPlaneError(f"Surface Atlassian nao suportada: {surface}")
    control_plane = load_ai_control_plane(resolved_repo_root)
    normalized_role_id = control_plane.resolve_role_reference(role_id) or str(role_id).strip()
    cache_key = (str(resolved_repo_root), normalized_role_id, normalized_surface)
    cached = _ACTOR_CACHE.get(cache_key)
    if cached is not None:
        return cached
    base_platform = _resolve_global_platform(resolved_repo_root)
    actor = _resolve_actor_from_role(
        repo_root=resolved_repo_root,
        role_id=normalized_role_id,
        surface=normalized_surface,
        context_issue_key=context_issue_key,
        base_platform=base_platform,
    )
    _ACTOR_CACHE[cache_key] = actor
    _record_resolution(resolved_repo_root, actor)
    return actor


def resolve_global_atlassian_actor(
    repo_root: str | Path | None,
    role_id: str,
    surface: str,
) -> ResolvedAtlassianActor:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    control_plane = load_ai_control_plane(resolved_repo_root)
    normalized_role_id = control_plane.resolve_role_reference(role_id) or str(role_id).strip()
    normalized_surface = _surface_slug(surface)
    if normalized_surface not in ROLE_SURFACES:
        raise AiControlPlaneError(f"Surface Atlassian nao suportada: {surface}")
    actor = _global_actor(
        repo_root=resolved_repo_root,
        role_id=normalized_role_id,
        surface=normalized_surface,
        base_platform=_resolve_global_platform(resolved_repo_root),
    )
    _record_resolution(
        resolved_repo_root,
        actor,
        resolution_key=f"global::{normalized_role_id}::{normalized_surface}",
    )
    return actor


def jira_adapter_for_role(
    repo_root: str | Path | None,
    role_id: str,
    surface: str,
    *,
    context_issue_key: str = "",
) -> tuple[JiraAdapter, ResolvedAtlassianActor]:
    actor = resolve_atlassian_actor(
        repo_root,
        role_id,
        surface,
        context_issue_key=context_issue_key,
    )
    return JiraAdapter(AtlassianHttpClient(actor.as_platform())), actor


def confluence_adapter_for_role(
    repo_root: str | Path | None,
    role_id: str,
    surface: str,
    *,
    context_issue_key: str = "",
) -> tuple[ConfluenceAdapter, ResolvedAtlassianActor]:
    actor = resolve_atlassian_actor(
        repo_root,
        role_id,
        surface,
        context_issue_key=context_issue_key,
    )
    return ConfluenceAdapter(AtlassianHttpClient(actor.as_platform())), actor


def global_jira_adapter(repo_root: str | Path | None) -> JiraAdapter:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    return JiraAdapter(AtlassianHttpClient(_resolve_global_platform(resolved_repo_root)))


def global_confluence_adapter(repo_root: str | Path | None) -> ConfluenceAdapter:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    return ConfluenceAdapter(AtlassianHttpClient(_resolve_global_platform(resolved_repo_root)))


def with_jira_actor(
    repo_root: str | Path | None,
    role_id: str,
    surface: str,
    operation: Callable[[JiraAdapter, ResolvedAtlassianActor], T],
    *,
    context_issue_key: str = "",
) -> tuple[T, ResolvedAtlassianActor]:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    jira, actor = jira_adapter_for_role(
        resolved_repo_root,
        role_id,
        surface,
        context_issue_key=context_issue_key,
    )
    try:
        return operation(jira, actor), actor
    except (AtlassianPlatformError, AiControlPlaneError) as exc:
        if actor.actor_mode != "role-service-account" or not actor.global_fallback_allowed:
            raise
        fallback_actor = _global_actor(
            repo_root=resolved_repo_root,
            role_id=actor.role_id,
            surface=actor.surface,
            base_platform=_resolve_global_platform(resolved_repo_root),
            fallback_issue_required=True,
            fallback_issue_reason="surface-write-failure",
            fallback_issue_type="global-fallback-after-write-error",
        )
        _notify_fallback_issue_if_needed(
            repo_root=resolved_repo_root,
            actor=fallback_actor,
            context_issue_key=context_issue_key,
            evidence_lines=[
                f"Falha ao escrever com a service account propria: {exc}",
                f"Surface afetada: {surface}",
            ],
        )
        _record_resolution(resolved_repo_root, fallback_actor)
        fallback_jira = JiraAdapter(AtlassianHttpClient(fallback_actor.as_platform()))
        return operation(fallback_jira, fallback_actor), fallback_actor


def with_confluence_actor(
    repo_root: str | Path | None,
    role_id: str,
    surface: str,
    operation: Callable[[ConfluenceAdapter, ResolvedAtlassianActor], T],
    *,
    context_issue_key: str = "",
) -> tuple[T, ResolvedAtlassianActor]:
    resolved_repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    adapter, actor = confluence_adapter_for_role(
        resolved_repo_root,
        role_id,
        surface,
        context_issue_key=context_issue_key,
    )
    try:
        return operation(adapter, actor), actor
    except (AtlassianPlatformError, AiControlPlaneError) as exc:
        if actor.actor_mode != "role-service-account" or not actor.global_fallback_allowed:
            raise
        fallback_actor = _global_actor(
            repo_root=resolved_repo_root,
            role_id=actor.role_id,
            surface=actor.surface,
            base_platform=_resolve_global_platform(resolved_repo_root),
            fallback_issue_required=True,
            fallback_issue_reason="surface-write-failure",
            fallback_issue_type="global-fallback-after-write-error",
        )
        _notify_fallback_issue_if_needed(
            repo_root=resolved_repo_root,
            actor=fallback_actor,
            context_issue_key=context_issue_key,
            evidence_lines=[
                f"Falha ao escrever no Confluence com a service account propria: {exc}",
                f"Surface afetada: {surface}",
            ],
        )
        _record_resolution(resolved_repo_root, fallback_actor)
        fallback_adapter = ConfluenceAdapter(AtlassianHttpClient(fallback_actor.as_platform()))
        return operation(fallback_adapter, fallback_actor), fallback_actor
