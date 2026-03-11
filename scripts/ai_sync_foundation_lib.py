from __future__ import annotations

import html
import json
import os
import platform
import re
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # pragma: no cover - execucao direta do script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    load_ai_control_plane,
    load_yaml_map,
    resolve_atlassian_platform,
    resolve_repo_root,
)
from scripts.atlassian_platform_lib import AtlassianHttpClient, ConfluenceAdapter

SYNC_TARGETS_PATH = Path("config/ai/sync-targets.yaml")
WORKSPACE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LEDGER_START_MARKER = "<!-- ai-sync-ledger:start -->"
LEDGER_END_MARKER = "<!-- ai-sync-ledger:end -->"


@dataclass(frozen=True)
class SyncArtifact:
    key: str
    artifact_type: str
    definition_source: str
    sync_eligibility: str
    source_of_truth: str
    remote_target: dict[str, Any]
    local_outbox_path: Path
    retention_policy: dict[str, Any]


@dataclass(frozen=True)
class SyncManifest:
    repo_root: Path
    manifest_path: Path
    workspace_id: str
    state_root: Path
    workspace_dir_template: str
    runtime_fields: list[str]
    runtime_kinds: list[str]
    artifacts: dict[str, SyncArtifact]
    artifact_inventory: dict[str, list[dict[str, Any]]]


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path
    outbox: Path
    status: Path
    checkpoints: Path
    dead_letter: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify_token(raw_value: str, *, fallback: str = "unknown") -> str:
    value = str(raw_value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:  # pragma: no cover - protegido por testes
            raise AiControlPlaneError(
                f"JSONL invalido em {path.as_posix()} linha {line_number}: {exc}"
            ) from exc
        if not isinstance(payload, dict):
            raise AiControlPlaneError(
                f"JSONL invalido em {path.as_posix()} linha {line_number}: esperado objeto."
            )
        records.append(payload)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    content = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records
    )
    path.write_text(f"{content}\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def _ensure_mapping(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AiControlPlaneError(f"{label} precisa ser mapa.")
    return payload


def load_sync_manifest(repo_root: str | Path | None = None) -> SyncManifest:
    resolved_repo_root = resolve_repo_root(repo_root)
    manifest_path = resolved_repo_root / SYNC_TARGETS_PATH
    payload = load_yaml_map(manifest_path)

    workspace = _ensure_mapping(payload.get("workspace"), "config/ai/sync-targets.yaml workspace")
    workspace_id = str(workspace.get("id", "")).strip()
    if not WORKSPACE_ID_RE.fullmatch(workspace_id):
        raise AiControlPlaneError(
            "config/ai/sync-targets.yaml workspace.id precisa ser kebab-case ASCII estavel."
        )
    raw_state_root = str(workspace.get("state_root", "")).strip()
    if not raw_state_root:
        raise AiControlPlaneError("config/ai/sync-targets.yaml workspace.state_root e obrigatorio.")
    workspace_dir_template = str(
        workspace.get("workspace_dir", "workspaces/{workspace_id}")
    ).strip()
    if not workspace_dir_template or Path(workspace_dir_template).is_absolute():
        raise AiControlPlaneError(
            "config/ai/sync-targets.yaml workspace.workspace_dir precisa ser relativo ao state_root."
        )

    runtime_identity = _ensure_mapping(
        payload.get("runtime_identity"),
        "config/ai/sync-targets.yaml runtime_identity",
    )
    runtime_fields_raw = runtime_identity.get("fields")
    if not isinstance(runtime_fields_raw, list) or not runtime_fields_raw:
        raise AiControlPlaneError(
            "config/ai/sync-targets.yaml runtime_identity.fields precisa ser lista nao vazia."
        )
    runtime_fields = [str(field).strip() for field in runtime_fields_raw if str(field).strip()]
    runtime_kinds_raw = runtime_identity.get("runtime_kinds") or []
    if not isinstance(runtime_kinds_raw, list):
        raise AiControlPlaneError(
            "config/ai/sync-targets.yaml runtime_identity.runtime_kinds precisa ser lista."
        )
    runtime_kinds = [str(kind).strip() for kind in runtime_kinds_raw if str(kind).strip()]

    artifacts_payload = _ensure_mapping(
        payload.get("artifacts"),
        "config/ai/sync-targets.yaml artifacts",
    )
    artifacts: dict[str, SyncArtifact] = {}
    for artifact_key, raw_definition in artifacts_payload.items():
        normalized_key = str(artifact_key).strip()
        definition = _ensure_mapping(
            raw_definition,
            f"config/ai/sync-targets.yaml artifacts.{normalized_key}",
        )
        local_outbox = _ensure_mapping(
            definition.get("local_outbox"),
            f"config/ai/sync-targets.yaml artifacts.{normalized_key}.local_outbox",
        )
        local_outbox_path = Path(str(local_outbox.get("path", "")).strip())
        if not str(local_outbox_path) or local_outbox_path.is_absolute():
            raise AiControlPlaneError(
                f"config/ai/sync-targets.yaml artifacts.{normalized_key}.local_outbox.path precisa ser relativo."
            )
        artifacts[normalized_key] = SyncArtifact(
            key=normalized_key,
            artifact_type=str(definition.get("artifact_type", "")).strip(),
            definition_source=str(definition.get("definition_source", "")).strip(),
            sync_eligibility=str(definition.get("sync_eligibility", "")).strip(),
            source_of_truth=str(definition.get("source_of_truth", "")).strip(),
            remote_target=_ensure_mapping(
                definition.get("remote_target"),
                f"config/ai/sync-targets.yaml artifacts.{normalized_key}.remote_target",
            ),
            local_outbox_path=local_outbox_path,
            retention_policy=_ensure_mapping(
                definition.get("retention_policy"),
                f"config/ai/sync-targets.yaml artifacts.{normalized_key}.retention_policy",
            ),
        )

    inventory_payload = payload.get("artifact_inventory") or {}
    if not isinstance(inventory_payload, dict):
        raise AiControlPlaneError(
            "config/ai/sync-targets.yaml artifact_inventory precisa ser mapa."
        )
    artifact_inventory: dict[str, list[dict[str, Any]]] = {}
    for bucket_name, entries in inventory_payload.items():
        if not isinstance(entries, list):
            raise AiControlPlaneError(
                f"config/ai/sync-targets.yaml artifact_inventory.{bucket_name} precisa ser lista."
            )
        normalized_entries: list[dict[str, Any]] = []
        for entry in entries:
            normalized_entries.append(
                _ensure_mapping(
                    entry,
                    f"config/ai/sync-targets.yaml artifact_inventory.{bucket_name}",
                )
            )
        artifact_inventory[str(bucket_name).strip()] = normalized_entries

    return SyncManifest(
        repo_root=resolved_repo_root,
        manifest_path=manifest_path,
        workspace_id=workspace_id,
        state_root=Path(raw_state_root).expanduser(),
        workspace_dir_template=workspace_dir_template,
        runtime_fields=runtime_fields,
        runtime_kinds=runtime_kinds,
        artifacts=artifacts,
        artifact_inventory=artifact_inventory,
    )


def resolve_workspace_paths(
    manifest: SyncManifest,
    *,
    ensure_exists: bool = False,
) -> WorkspacePaths:
    workspace_relative = Path(
        manifest.workspace_dir_template.format(workspace_id=manifest.workspace_id)
    )
    if workspace_relative.is_absolute():
        raise AiControlPlaneError(
            "workspace.workspace_dir precisa permanecer relativo ao state_root."
        )
    root = (manifest.state_root / workspace_relative).expanduser()
    paths = WorkspacePaths(
        root=root,
        outbox=root / "outbox",
        status=root / "status",
        checkpoints=root / "checkpoints",
        dead_letter=root / "dead-letter",
    )
    if ensure_exists:
        for candidate in (
            paths.root,
            paths.outbox,
            paths.status,
            paths.checkpoints,
            paths.dead_letter,
        ):
            candidate.mkdir(parents=True, exist_ok=True)
    return paths


def detect_runtime_kind() -> str:
    if os.environ.get("CI", "").strip():
        return "ci"
    if os.environ.get("WSL_DISTRO_NAME", "").strip() or os.environ.get("WSL_INTEROP", "").strip():
        return "wsl"
    if Path("/.dockerenv").exists() or Path("/run/.containerenv").exists():
        return "container"
    return "host"


def detect_os_family() -> str:
    if os.name == "nt":
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    return slugify_token(sys.platform, fallback="unknown-os")


def detect_distro(os_family: str, runtime_kind: str) -> str:
    if os_family == "windows":
        return "windows"
    if runtime_kind == "wsl":
        return slugify_token(os.environ.get("WSL_DISTRO_NAME", ""), fallback="wsl")
    release_map: dict[str, str] = {}
    if hasattr(platform, "freedesktop_os_release"):
        try:
            release_map = platform.freedesktop_os_release()
        except OSError:
            release_map = {}
    candidate = release_map.get("ID") or release_map.get("NAME") or platform.system()
    return slugify_token(candidate, fallback=os_family)


def derive_runtime_identity(manifest: SyncManifest) -> dict[str, Any]:
    os_family = detect_os_family()
    runtime_kind = detect_runtime_kind()
    if manifest.runtime_kinds and runtime_kind not in manifest.runtime_kinds:
        raise AiControlPlaneError(
            f"runtime_kind derivado fora do contrato de sync: {runtime_kind!r}."
        )
    runtime = {
        "host_name": slugify_token(
            os.environ.get("COMPUTERNAME", "") or os.environ.get("HOSTNAME", "") or platform.node(),
            fallback="unknown-host",
        ),
        "os_family": os_family,
        "runtime_kind": runtime_kind,
        "distro": detect_distro(os_family, runtime_kind),
    }
    tokens = [
        slugify_token(str(runtime.get(field, "")), fallback="unknown")
        for field in manifest.runtime_fields
    ]
    runtime_environment_id = "-".join(token for token in tokens if token)
    runtime["runtime_environment_id"] = runtime_environment_id or "unknown-runtime"
    return runtime


def artifact_outbox_path(paths: WorkspacePaths, artifact: SyncArtifact) -> Path:
    return (paths.root / artifact.local_outbox_path).resolve()


def artifact_status_path(paths: WorkspacePaths, artifact_key: str) -> Path:
    return paths.status / f"{artifact_key}.json"


def artifact_checkpoint_path(paths: WorkspacePaths, artifact_key: str) -> Path:
    return paths.checkpoints / f"{artifact_key}.json"


def artifact_dead_letter_path(paths: WorkspacePaths, artifact_key: str) -> Path:
    return paths.dead_letter / f"{artifact_key}.jsonl"


def pending_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if str((record.get("sync") or {}).get("status", "pending")).strip() != "acked"
    ]


def _load_json_map(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - protegido por testes
        raise AiControlPlaneError(f"JSON invalido em {path.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise AiControlPlaneError(f"JSON invalido em {path.as_posix()}: esperado objeto.")
    return payload


def _write_json_map(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def refresh_artifact_state(
    manifest: SyncManifest,
    paths: WorkspacePaths,
    artifact_key: str,
    *,
    outbox_records: list[dict[str, Any]] | None = None,
    checkpoint_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact = manifest.artifacts[artifact_key]
    outbox_path = artifact_outbox_path(paths, artifact)
    records = outbox_records if outbox_records is not None else read_jsonl(outbox_path)
    dead_letter_records = read_jsonl(artifact_dead_letter_path(paths, artifact_key))
    previous_status = _load_json_map(artifact_status_path(paths, artifact_key))
    status_payload = {
        "artifact_key": artifact_key,
        "outbox_path": str(outbox_path),
        "pending_events": len(pending_events(records)),
        "retained_events": len(records),
        "dead_letter_events": len(dead_letter_records),
        "last_synced_at": str(previous_status.get("last_synced_at", "")).strip(),
        "last_successful_event_id": str(
            previous_status.get("last_successful_event_id", "")
        ).strip(),
        "updated_at": utc_now(),
    }
    if checkpoint_payload:
        if checkpoint_payload.get("synced_at"):
            status_payload["last_synced_at"] = str(checkpoint_payload["synced_at"]).strip()
        if checkpoint_payload.get("last_event_id"):
            status_payload["last_successful_event_id"] = str(
                checkpoint_payload["last_event_id"]
            ).strip()
        _write_json_map(artifact_checkpoint_path(paths, artifact_key), checkpoint_payload)
    _write_json_map(artifact_status_path(paths, artifact_key), status_payload)
    return status_payload


def record_sync_event(
    repo_root: str | Path | None,
    *,
    artifact_key: str,
    record_key: str,
    payload: Any,
    execution_status: str = "success",
    effectiveness_status: str = "effective",
    occurred_at: str = "",
) -> dict[str, Any]:
    manifest = load_sync_manifest(repo_root)
    if artifact_key not in manifest.artifacts:
        raise AiControlPlaneError(f"Artifact de sync desconhecido: {artifact_key}")
    normalized_record_key = str(record_key).strip()
    if not normalized_record_key:
        raise AiControlPlaneError("record_key e obrigatorio para registrar evento de sync.")

    paths = resolve_workspace_paths(manifest, ensure_exists=True)
    artifact = manifest.artifacts[artifact_key]
    outbox_path = artifact_outbox_path(paths, artifact)
    runtime = derive_runtime_identity(manifest)
    event = {
        "event_id": f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "workspace_id": manifest.workspace_id,
        "runtime_environment_id": runtime["runtime_environment_id"],
        "artifact_key": artifact_key,
        "record_key": normalized_record_key,
        "occurred_at": occurred_at.strip() or utc_now(),
        "execution_status": str(execution_status).strip() or "success",
        "effectiveness_status": str(effectiveness_status).strip() or "effective",
        "runtime": runtime,
        "payload": payload,
        "sync": {
            "status": "pending",
            "attempts": 0,
        },
    }
    append_jsonl(outbox_path, event)
    status_payload = refresh_artifact_state(
        manifest,
        paths,
        artifact_key,
    )
    return {
        "event": event,
        "outbox_path": str(outbox_path),
        "workspace_root": str(paths.root),
        "status": status_payload,
    }


def sync_check_payload(repo_root: str | Path | None = None) -> dict[str, Any]:
    manifest = load_sync_manifest(repo_root)
    paths = resolve_workspace_paths(manifest, ensure_exists=False)
    runtime = derive_runtime_identity(manifest)
    return {
        "ok": True,
        "manifest_path": str(manifest.manifest_path),
        "workspace": {
            "id": manifest.workspace_id,
            "state_root": str(manifest.state_root),
            "workspace_root": str(paths.root),
            "workspace_dir_template": manifest.workspace_dir_template,
            "required_dirs": [
                str(paths.outbox),
                str(paths.status),
                str(paths.checkpoints),
                str(paths.dead_letter),
            ],
        },
        "runtime_identity": {
            "fields": list(manifest.runtime_fields),
            "allowed_runtime_kinds": list(manifest.runtime_kinds),
            "resolved": runtime,
        },
        "artifact_keys": sorted(manifest.artifacts),
    }


def sync_status_payload(repo_root: str | Path | None = None) -> dict[str, Any]:
    manifest = load_sync_manifest(repo_root)
    paths = resolve_workspace_paths(manifest, ensure_exists=False)
    runtime = derive_runtime_identity(manifest)
    artifacts_payload: dict[str, Any] = {}
    for artifact_key, artifact in manifest.artifacts.items():
        outbox_path = artifact_outbox_path(paths, artifact)
        records = read_jsonl(outbox_path)
        artifacts_payload[artifact_key] = {
            "artifact_type": artifact.artifact_type,
            "definition_source": artifact.definition_source,
            "sync_eligibility": artifact.sync_eligibility,
            "source_of_truth": artifact.source_of_truth,
            "remote_target": artifact.remote_target,
            "outbox_path": str(outbox_path),
            "pending_events": len(pending_events(records)),
            "retained_events": len(records),
            "dead_letter_path": str(artifact_dead_letter_path(paths, artifact_key)),
        }
    return {
        "manifest_path": str(manifest.manifest_path),
        "workspace": {
            "id": manifest.workspace_id,
            "state_root": str(manifest.state_root),
            "workspace_root": str(paths.root),
            "workspace_dir_template": manifest.workspace_dir_template,
        },
        "runtime_identity": {
            "fields": list(manifest.runtime_fields),
            "allowed_runtime_kinds": list(manifest.runtime_kinds),
            "resolved": runtime,
        },
        "artifact_inventory": manifest.artifact_inventory,
        "artifacts": artifacts_payload,
    }


def _page_url(site_url: str, space_key: str, page_id: str) -> str:
    return f"{site_url.rstrip('/')}/wiki/spaces/{space_key}/pages/{page_id}"


def _event_marker(event_id: str) -> str:
    return f'data-event-id="{html.escape(event_id, quote=True)}"'


def _render_event_row(event: dict[str, Any]) -> str:
    payload_preview = html.escape(
        json.dumps(event.get("payload", {}), ensure_ascii=False, sort_keys=True, indent=2)
    )
    return (
        f"<tr {_event_marker(str(event.get('event_id', '')))}>"
        f"<td><code>{html.escape(str(event.get('event_id', '')))}</code></td>"
        f"<td>{html.escape(str(event.get('occurred_at', '')))}</td>"
        f"<td><code>{html.escape(str(event.get('record_key', '')))}</code></td>"
        f"<td>{html.escape(str(event.get('execution_status', '')))}</td>"
        f"<td>{html.escape(str(event.get('effectiveness_status', '')))}</td>"
        f"<td><pre>{payload_preview}</pre></td>"
        "</tr>"
    )


def _base_ledger_body(
    *, title: str, artifact_key: str, workspace_id: str, runtime_environment_id: str
) -> str:
    return (
        f"<h1>{html.escape(title)}</h1>"
        "<p>Runtime ledger sincronizado a partir do outbox local duravel oficial.</p>"
        f"<p>Workspace: <code>{html.escape(workspace_id)}</code><br />"
        f"Runtime environment de referencia: <code>{html.escape(runtime_environment_id)}</code><br />"
        f"Artifact key: <code>{html.escape(artifact_key)}</code></p>"
        "<table>"
        "<thead><tr><th>event_id</th><th>occurred_at</th><th>record_key</th>"
        "<th>execution_status</th><th>effectiveness_status</th><th>payload</th></tr></thead>"
        f"<tbody>{LEDGER_START_MARKER}\n{LEDGER_END_MARKER}</tbody>"
        "</table>"
    )


def _merge_ledger_rows(
    current_body: str,
    *,
    title: str,
    artifact_key: str,
    workspace_id: str,
    runtime_environment_id: str,
    events: list[dict[str, Any]],
) -> tuple[str, list[str]]:
    body = current_body.strip() or _base_ledger_body(
        title=title,
        artifact_key=artifact_key,
        workspace_id=workspace_id,
        runtime_environment_id=runtime_environment_id,
    )
    if LEDGER_START_MARKER not in body or LEDGER_END_MARKER not in body:
        body = (
            body
            + "<h2>Eventos sincronizados</h2><table><thead><tr><th>event_id</th><th>occurred_at</th>"
            "<th>record_key</th><th>execution_status</th><th>effectiveness_status</th><th>payload</th></tr></thead>"
            f"<tbody>{LEDGER_START_MARKER}\n{LEDGER_END_MARKER}</tbody></table>"
        )
    acknowledged: list[str] = []
    rendered_rows: list[str] = []
    for event in events:
        event_id = str(event.get("event_id", "")).strip()
        if not event_id:
            continue
        marker = _event_marker(event_id)
        if marker in body:
            acknowledged.append(event_id)
            continue
        rendered_rows.append(_render_event_row(event))
        acknowledged.append(event_id)
    if rendered_rows:
        body = body.replace(
            LEDGER_END_MARKER,
            "\n".join(rendered_rows) + "\n" + LEDGER_END_MARKER,
            1,
        )
    return body, acknowledged


def _confluence_body_value(page_payload: dict[str, Any]) -> str:
    body = page_payload.get("body") or {}
    if not isinstance(body, dict):
        return ""
    storage = body.get("storage") or {}
    if not isinstance(storage, dict):
        return ""
    return str(storage.get("value", "")).strip()


def _apply_confluence_sync(
    *,
    adapter: ConfluenceAdapter,
    site_url: str,
    space_key: str,
    artifact_key: str,
    remote_target: dict[str, Any],
    workspace_id: str,
    runtime_environment_id: str,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    page_title = str(remote_target.get("page_title", "")).strip()
    if not page_title:
        raise AiControlPlaneError(
            f"remote_target.page_title e obrigatorio para o artifact {artifact_key}."
        )
    existing_page = adapter.find_page_by_title(space_key=space_key, title=page_title)
    page_id = str((existing_page or {}).get("id", "")).strip()
    current_body = ""
    if page_id:
        current_page = adapter.get_page(page_id, body_format="storage")
        current_body = _confluence_body_value(current_page)
    merged_body, acknowledged_ids = _merge_ledger_rows(
        current_body,
        title=page_title,
        artifact_key=artifact_key,
        workspace_id=workspace_id,
        runtime_environment_id=runtime_environment_id,
        events=events,
    )
    created = False
    updated = False
    if not page_id:
        created_page = adapter.create_page(
            space_key=space_key,
            title=page_title,
            storage_value=merged_body,
        )
        page_id = str(created_page.get("id", "")).strip()
        created = True
    elif acknowledged_ids:
        adapter.update_page(
            page_id=page_id,
            title=page_title,
            storage_value=merged_body,
            version_message="sync-foundation-ledger",
        )
        updated = True
    return {
        "acked_event_ids": acknowledged_ids,
        "created": created,
        "updated": updated,
        "page_id": page_id,
        "page_title": page_title,
        "url": _page_url(site_url, space_key, page_id) if page_id else "",
    }


def drain_sync_events(
    repo_root: str | Path | None = None,
    *,
    artifact_key: str = "",
    apply: bool = False,
    max_events: int = 0,
) -> dict[str, Any]:
    manifest = load_sync_manifest(repo_root)
    paths = resolve_workspace_paths(manifest, ensure_exists=apply)
    runtime = derive_runtime_identity(manifest)
    selected_artifact_keys = [artifact_key] if artifact_key else sorted(manifest.artifacts)
    for key in selected_artifact_keys:
        if key not in manifest.artifacts:
            raise AiControlPlaneError(f"Artifact de sync desconhecido: {key}")

    confluence_adapter: ConfluenceAdapter | None = None
    confluence_space_key = ""
    site_url = ""
    if apply:
        control_plane = load_ai_control_plane(manifest.repo_root)
        resolved = resolve_atlassian_platform(
            control_plane.atlassian_definition(),
            repo_root=control_plane.repo_root,
        )
        confluence_adapter = ConfluenceAdapter(AtlassianHttpClient(resolved))
        confluence_space_key = resolved.confluence_space_key
        site_url = resolved.site_url

    results: dict[str, Any] = {}
    total_pending = 0
    total_acked = 0
    errors: list[str] = []

    for current_key in selected_artifact_keys:
        artifact = manifest.artifacts[current_key]
        outbox_path = artifact_outbox_path(paths, artifact)
        retained_records = read_jsonl(outbox_path)
        current_pending = pending_events(retained_records)
        if max_events > 0:
            current_pending = current_pending[:max_events]
        total_pending += len(current_pending)
        artifact_result: dict[str, Any] = {
            "artifact_key": current_key,
            "pending_events": len(current_pending),
            "apply": apply,
            "outbox_path": str(outbox_path),
            "remote_target": artifact.remote_target,
            "acked_events": 0,
            "dead_lettered_events": 0,
            "page_url": "",
            "status": "noop",
        }
        if not current_pending:
            status_payload = refresh_artifact_state(
                manifest,
                paths,
                current_key,
                outbox_records=retained_records,
            )
            artifact_result["status_snapshot"] = status_payload
            results[current_key] = artifact_result
            continue
        if not apply:
            artifact_result["status"] = "planned"
            results[current_key] = artifact_result
            continue

        try:
            if confluence_adapter is None:
                raise AiControlPlaneError("Adapter Confluence indisponivel para apply.")
            remote_kind = str(artifact.remote_target.get("kind", "")).strip()
            remote_strategy = str(artifact.remote_target.get("strategy", "")).strip()
            if remote_kind != "confluence" or remote_strategy != "append-page-ledger":
                raise AiControlPlaneError(
                    f"Artifact {current_key} usa remote_target ainda nao suportado: "
                    f"{remote_kind}/{remote_strategy}"
                )
            remote_result = _apply_confluence_sync(
                adapter=confluence_adapter,
                site_url=site_url,
                space_key=confluence_space_key,
                artifact_key=current_key,
                remote_target=artifact.remote_target,
                workspace_id=manifest.workspace_id,
                runtime_environment_id=str(runtime["runtime_environment_id"]),
                events=current_pending,
            )
            acked_ids = {str(event_id).strip() for event_id in remote_result["acked_event_ids"]}
            total_acked += len(acked_ids)
            compacted_records = [
                record
                for record in retained_records
                if str(record.get("event_id", "")).strip() not in acked_ids
            ]
            write_jsonl(outbox_path, compacted_records)
            checkpoint_payload = {
                "artifact_key": current_key,
                "synced_at": utc_now(),
                "last_event_id": current_pending[-1]["event_id"],
                "acked_event_ids": sorted(acked_ids),
                "page_id": remote_result["page_id"],
                "page_title": remote_result["page_title"],
                "page_url": remote_result["url"],
            }
            status_payload = refresh_artifact_state(
                manifest,
                paths,
                current_key,
                outbox_records=compacted_records,
                checkpoint_payload=checkpoint_payload,
            )
            artifact_result["status"] = "applied"
            artifact_result["acked_events"] = len(acked_ids)
            artifact_result["page_url"] = remote_result["url"]
            artifact_result["created"] = remote_result["created"]
            artifact_result["updated"] = remote_result["updated"]
            artifact_result["status_snapshot"] = status_payload
        except AiControlPlaneError as exc:
            failure_message = str(exc)
            max_attempts = int(
                artifact.retention_policy.get("max_attempts_before_dead_letter", 5) or 5
            )
            dead_letter_records = read_jsonl(artifact_dead_letter_path(paths, current_key))
            selected_ids = {str(record.get("event_id", "")).strip() for record in current_pending}
            next_records: list[dict[str, Any]] = []
            dead_lettered = 0
            for record in retained_records:
                event_id = str(record.get("event_id", "")).strip()
                if event_id not in selected_ids:
                    next_records.append(record)
                    continue
                sync_payload = record.get("sync") or {}
                if not isinstance(sync_payload, dict):
                    sync_payload = {}
                attempts = int(sync_payload.get("attempts", 0) or 0) + 1
                sync_payload.update(
                    {
                        "status": "pending",
                        "attempts": attempts,
                        "last_attempt_at": utc_now(),
                        "last_error": failure_message,
                    }
                )
                record["sync"] = sync_payload
                if attempts >= max_attempts:
                    record["sync"]["status"] = "dead-letter"
                    record["dead_letter_reason"] = failure_message
                    dead_letter_records.append(record)
                    dead_lettered += 1
                    continue
                next_records.append(record)
            write_jsonl(outbox_path, next_records)
            write_jsonl(artifact_dead_letter_path(paths, current_key), dead_letter_records)
            status_payload = refresh_artifact_state(
                manifest,
                paths,
                current_key,
                outbox_records=next_records,
            )
            artifact_result["status"] = "error"
            artifact_result["error"] = failure_message
            artifact_result["dead_lettered_events"] = dead_lettered
            artifact_result["status_snapshot"] = status_payload
            errors.append(f"{current_key}: {failure_message}")
        results[current_key] = artifact_result

    return {
        "workspace_id": manifest.workspace_id,
        "runtime_environment_id": runtime["runtime_environment_id"],
        "apply": apply,
        "total_pending": total_pending,
        "total_acked": total_acked,
        "errors": errors,
        "artifacts": results,
    }
