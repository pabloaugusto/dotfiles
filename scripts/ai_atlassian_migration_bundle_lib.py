from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ai_atlassian_backfill_lib import build_backfill_plan
from scripts.ai_control_plane_lib import resolve_repo_root

DEFAULT_BUNDLE_ROOT = Path(".cache/atlassian-migration")


def timestamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_source_paths(repo_root: Path) -> list[tuple[Path, str]]:
    pairs: list[tuple[Path, str]] = []

    def add_file(relative_path: str, category: str) -> None:
        path = repo_root / relative_path
        if path.exists() and path.is_file():
            pairs.append((path, category))

    def add_glob(pattern: str, category: str) -> None:
        for path in sorted(repo_root.glob(pattern)):
            if path.is_file():
                pairs.append((path, category))

    add_file("ROADMAP.md", "roadmap")
    add_file("docs/ROADMAP-DECISIONS.md", "roadmap")
    add_file("docs/AI-WIP-TRACKER.md", "worklog")
    add_file("docs/TASKS.md", "docs")
    add_file("docs/config-reference.md", "docs")

    add_file("config/ai/platforms.yaml", "control-plane")
    add_file("config/ai/platforms.local.yaml.tpl", "control-plane")
    add_file("config/ai/agents.yaml", "control-plane")
    add_file("config/ai/contracts.yaml", "control-plane")
    add_file("config/ai/jira-model.yaml", "control-plane")
    add_file("config/ai/confluence-model.yaml", "control-plane")

    add_file("scripts/ai-atlassian-backfill.py", "logic")
    add_file("scripts/ai_atlassian_backfill_lib.py", "logic")
    add_file("scripts/ai-jira-model.py", "logic")
    add_file("scripts/ai_jira_model_lib.py", "logic")
    add_file("scripts/atlassian_platform_lib.py", "logic")
    add_file("scripts/ai-atlassian-migration-bundle.py", "logic")
    add_file("scripts/ai_atlassian_migration_bundle_lib.py", "logic")
    add_file("scripts/ai-atlassian-seed.py", "logic")
    add_file("scripts/ai_atlassian_seed_lib.py", "logic")

    add_glob("docs/atlassian-ia/*.md", "atlassian-doc")
    add_glob("docs/atlassian-ia/artifacts/*.md", "artifact-doc")

    deduped: dict[str, tuple[Path, str]] = {}
    for path, category in pairs:
        deduped[path.relative_to(repo_root).as_posix()] = (path, category)
    return [deduped[key] for key in sorted(deduped)]


def ensure_clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_sources_into_bundle(bundle_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for source_path, category in bundle_source_paths(repo_root):
        relative = source_path.relative_to(repo_root)
        target = bundle_root / "repo" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)
        entries.append(
            {
                "path": relative.as_posix(),
                "category": category,
                "size_bytes": source_path.stat().st_size,
                "sha256": sha256_file(source_path),
            }
        )
    return entries


def write_generated_payloads(bundle_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    generated_dir = bundle_root / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    backfill_plan = build_backfill_plan(repo_root)
    files_to_write = {
        "backfill-plan.json": backfill_plan,
        "jira-export-records.json": backfill_plan["jira"],
        "confluence-export-records.json": backfill_plan["confluence"],
    }

    entries: list[dict[str, Any]] = []
    for file_name, payload in files_to_write.items():
        target = generated_dir / file_name
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        entries.append(
            {
                "path": f"generated/{file_name}",
                "category": "generated",
                "size_bytes": target.stat().st_size,
                "sha256": sha256_file(target),
            }
        )
    return entries


def build_migration_bundle(
    repo_root: str | Path | None = None,
    *,
    output_root: str | Path = "",
) -> dict[str, Any]:
    resolved_repo_root = resolve_repo_root(repo_root)
    base_output_root = (
        Path(output_root).resolve()
        if str(output_root).strip()
        else (resolved_repo_root / DEFAULT_BUNDLE_ROOT).resolve()
    )
    slug = f"atlassian-migration-{timestamp_utc()}"
    bundle_root = base_output_root / slug
    ensure_clean_directory(bundle_root)

    source_entries = copy_sources_into_bundle(bundle_root, resolved_repo_root)
    generated_entries = write_generated_payloads(bundle_root, resolved_repo_root)

    manifest = {
        "metadata": {
            "generated_on_utc": datetime.now(timezone.utc).isoformat(),
            "repo_root": str(resolved_repo_root),
            "bundle_root": str(bundle_root),
            "bundle_kind": "atlassian-migration",
            "review_intent": "attach-to-jira-migration-issue-and-link-from-confluence",
        },
        "counts": {
            "source_files": len(source_entries),
            "generated_files": len(generated_entries),
            "total_files": len(source_entries) + len(generated_entries),
        },
        "source_files": source_entries,
        "generated_files": generated_entries,
    }

    manifest_path = bundle_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = base_output_root / f"{slug}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root).as_posix())

    return {
        "bundle_root": str(bundle_root),
        "manifest_path": str(manifest_path),
        "zip_path": str(zip_path),
        "counts": manifest["counts"],
    }
