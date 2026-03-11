from __future__ import annotations

import json
import os
import pathlib
import tempfile
import textwrap
import types
import unittest
from unittest.mock import patch

from scripts.ai_sync_foundation_lib import (
    drain_sync_events,
    load_sync_manifest,
    record_sync_event,
    resolve_workspace_paths,
    sync_check_payload,
    sync_status_payload,
)


def write_sync_manifest(repo_root: pathlib.Path) -> None:
    config_dir = repo_root / "config" / "ai"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "sync-targets.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            workspace:
              id: workstation-governance
              state_root: ~/.ai-control-plane
              workspace_dir: workspaces/{workspace_id}
            runtime_identity:
              strategy: derived
              fields:
                - host_name
                - os_family
                - runtime_kind
                - distro
              runtime_kinds:
                - host
                - wsl
                - container
                - ci
            artifacts:
              prompt_runs:
                artifact_type: runtime_ledger
                definition_source: repo
                sync_eligibility: candidate
                source_of_truth: confluence
                remote_target:
                  kind: confluence
                  strategy: append-page-ledger
                  page_title: DOT - Prompt Runtime Ledger
                  page_scope: prompts
                local_outbox:
                  path: outbox/confluence/prompt-runs.jsonl
                retention_policy:
                  on_remote_ack: compact
                  keep_last_synced_days: 14
                  max_attempts_before_dead_letter: 5
            artifact_inventory:
              repo_canonical:
                - path: config/ai/
                  reason: contratos
              runtime_ledger_candidates:
                - path: prompt-runs
                  artifact_key: prompt_runs
                  reason: eventos de prompt
              remote_ineligible:
                - path: .cache/
                  reason: efemero
            """
        ),
        encoding="utf-8",
    )


class FakeConfluenceAdapter:
    def __init__(self, client: object) -> None:
        self.client = client
        self.pages: dict[str, dict[str, str]] = {}
        self.next_id = 1000

    def find_page_by_title(self, *, space_key: str, title: str) -> dict[str, str] | None:
        for page_id, page in self.pages.items():
            if page["space_key"] == space_key and page["title"] == title:
                return {"id": page_id, "title": title}
        return None

    def get_page(self, page_id: str, *, body_format: str = "storage") -> dict[str, object]:
        page = self.pages[page_id]
        return {
            "id": page_id,
            "title": page["title"],
            "body": {
                "storage": {
                    "value": page["body"],
                }
            },
        }

    def create_page(self, *, space_key: str, title: str, storage_value: str) -> dict[str, str]:
        self.next_id += 1
        page_id = str(self.next_id)
        self.pages[page_id] = {
            "space_key": space_key,
            "title": title,
            "body": storage_value,
        }
        return {"id": page_id, "title": title}

    def update_page(
        self,
        *,
        page_id: str,
        title: str,
        storage_value: str,
        version_message: str = "",
    ) -> dict[str, str]:
        self.pages[page_id]["title"] = title
        self.pages[page_id]["body"] = storage_value
        return {"id": page_id, "title": title}


class AiSyncFoundationTests(unittest.TestCase):
    def test_load_manifest_and_sync_check_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_sync_manifest(repo_root)
            with patch.dict(os.environ, {"HOME": tmp, "USERPROFILE": tmp}, clear=False):
                manifest = load_sync_manifest(repo_root)
                payload = sync_check_payload(repo_root)

        self.assertEqual(manifest.workspace_id, "workstation-governance")
        self.assertEqual(payload["workspace"]["id"], "workstation-governance")
        self.assertIn("prompt_runs", payload["artifact_keys"])
        self.assertEqual(
            pathlib.Path(payload["workspace"]["workspace_root"]).as_posix(),
            (
                pathlib.Path(tmp) / ".ai-control-plane" / "workspaces" / "workstation-governance"
            ).as_posix(),
        )

    def test_record_sync_event_creates_outbox_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_sync_manifest(repo_root)
            with patch.dict(os.environ, {"HOME": tmp, "USERPROFILE": tmp}, clear=False):
                result = record_sync_event(
                    repo_root,
                    artifact_key="prompt_runs",
                    record_key="prompt/startup-alignment",
                    payload={"status": "ok"},
                )
                manifest = load_sync_manifest(repo_root)
                paths = resolve_workspace_paths(manifest)
                outbox_path = paths.root / "outbox" / "confluence" / "prompt-runs.jsonl"
                status_path = paths.status / "prompt_runs.json"
                self.assertTrue(outbox_path.exists())
                self.assertTrue(status_path.exists())
                records = [
                    json.loads(line)
                    for line in outbox_path.read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["record_key"], "prompt/startup-alignment")
                self.assertEqual(result["status"]["pending_events"], 1)

    def test_sync_status_payload_counts_pending_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_sync_manifest(repo_root)
            with patch.dict(os.environ, {"HOME": tmp, "USERPROFILE": tmp}, clear=False):
                record_sync_event(
                    repo_root,
                    artifact_key="prompt_runs",
                    record_key="prompt/one",
                    payload={"status": "ok"},
                )
                record_sync_event(
                    repo_root,
                    artifact_key="prompt_runs",
                    record_key="prompt/two",
                    payload={"status": "ok"},
                )
                payload = sync_status_payload(repo_root)

        self.assertEqual(payload["artifacts"]["prompt_runs"]["pending_events"], 2)
        self.assertEqual(payload["artifacts"]["prompt_runs"]["sync_eligibility"], "candidate")

    def test_drain_sync_events_apply_acks_and_compacts_outbox(self) -> None:
        fake_adapter = FakeConfluenceAdapter(client=object())
        resolved = types.SimpleNamespace(
            site_url="https://example.atlassian.net",
            confluence_space_key="DOT",
        )
        fake_control_plane = types.SimpleNamespace(
            repo_root=pathlib.Path("."),
            atlassian_definition=lambda: object(),
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = pathlib.Path(tmp)
            write_sync_manifest(repo_root)
            fake_control_plane.repo_root = repo_root
            with patch.dict(os.environ, {"HOME": tmp, "USERPROFILE": tmp}, clear=False):
                record_sync_event(
                    repo_root,
                    artifact_key="prompt_runs",
                    record_key="prompt/sync-outbox-foundation",
                    payload={"summary": "foundation ok"},
                )
                with patch(
                    "scripts.ai_sync_foundation_lib.load_ai_control_plane",
                    return_value=fake_control_plane,
                ):
                    with patch(
                        "scripts.ai_sync_foundation_lib.resolve_atlassian_platform",
                        return_value=resolved,
                    ):
                        with patch(
                            "scripts.ai_sync_foundation_lib.AtlassianHttpClient",
                            return_value=object(),
                        ):
                            with patch(
                                "scripts.ai_sync_foundation_lib.ConfluenceAdapter",
                                return_value=fake_adapter,
                            ):
                                result = drain_sync_events(repo_root, apply=True)
                manifest = load_sync_manifest(repo_root)
                paths = resolve_workspace_paths(manifest)
                outbox_path = paths.root / "outbox" / "confluence" / "prompt-runs.jsonl"
                checkpoint_path = paths.checkpoints / "prompt_runs.json"
                self.assertEqual(result["total_acked"], 1)
                self.assertEqual(result["artifacts"]["prompt_runs"]["status"], "applied")
                self.assertTrue(checkpoint_path.exists())
                self.assertEqual(outbox_path.read_text(encoding="utf-8"), "")
                created_page = next(iter(fake_adapter.pages.values()))
                self.assertIn("foundation ok", created_page["body"])


if __name__ == "__main__":
    unittest.main()
