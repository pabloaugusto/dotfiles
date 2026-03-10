from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from scripts.ai_control_plane_lib import resolve_repo_root

SPEC_SOURCES = {
    "jira": {
        "human_url": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/",
        "openapi_url": "https://dac-static.atlassian.com/cloud/jira/platform/swagger-v3.v3.json?_v=1.8409.0",
        "vendor_path": "vendor/atlassian/jira-openapi.json",
    },
    "confluence": {
        "human_url": "https://developer.atlassian.com/cloud/confluence/rest/v2/",
        "openapi_url": "https://dac-static.atlassian.com/cloud/confluence/openapi-v2.v3.json?_v=1.8409.0",
        "vendor_path": "vendor/atlassian/confluence-openapi.json",
    },
}


def spec_catalog_payload(repo_root: str | Path | None = None) -> dict[str, object]:
    resolved_repo_root = resolve_repo_root(repo_root)
    return {
        "repo_root": str(resolved_repo_root),
        "specs": {
            name: {
                "human_url": values["human_url"],
                "openapi_url": values["openapi_url"],
                "vendor_path": str((resolved_repo_root / values["vendor_path"]).resolve()),
            }
            for name, values in SPEC_SOURCES.items()
        },
    }


def vendor_openapi_specs(repo_root: str | Path | None = None) -> dict[str, object]:
    resolved_repo_root = resolve_repo_root(repo_root)
    manifest_entries: list[dict[str, str]] = []

    for name, values in SPEC_SOURCES.items():
        vendor_path = resolved_repo_root / values["vendor_path"]
        vendor_path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(values["openapi_url"], timeout=120) as response:
            content = response.read()
        vendor_path.write_bytes(content)
        manifest_entries.append(
            {
                "name": name,
                "human_url": values["human_url"],
                "openapi_url": values["openapi_url"],
                "vendor_path": str(vendor_path.relative_to(resolved_repo_root)).replace("\\", "/"),
            }
        )

    manifest_path = resolved_repo_root / "vendor" / "atlassian" / "manifest.json"
    manifest = {
        "generated_on_utc": datetime.now(timezone.utc).isoformat(),
        "specs": manifest_entries,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "manifest_path": str(manifest_path),
        "specs": manifest_entries,
    }
