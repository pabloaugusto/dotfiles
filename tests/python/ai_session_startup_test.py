from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.ai_session_startup_lib import (
    load_pending_chat_contracts,
    render_startup_session_markdown,
    resolve_startup_manifest_paths,
    startup_session_payload,
    write_startup_session_report,
)


class AiSessionStartupTests(unittest.TestCase):
    def test_resolve_startup_manifest_paths_collects_explicit_and_recursive_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            cards_dir = repo_root / ".agents" / "cards"
            docs_dir.mkdir(parents=True)
            cards_dir.mkdir(parents=True)
            (docs_dir / "AI-STARTUP-GOVERNANCE-MANIFEST.md").write_text(
                textwrap.dedent(
                    """\
                    # Manifest

                    - [`AGENTS.md`](../AGENTS.md)
                    - todos os arquivos `AI-*` em [`docs/`](./)
                    - todos os arquivos em [`.agents/cards/`](../.agents/cards/)
                    """
                ),
                encoding="utf-8",
            )
            (repo_root / "AGENTS.md").write_text("# contrato\n", encoding="utf-8")
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                "# register\n", encoding="utf-8"
            )
            (docs_dir / "AI-STARTUP-AND-RESTART.md").write_text("# runbook\n", encoding="utf-8")
            (cards_dir / "ai-product-owner.md").write_text("# card\n", encoding="utf-8")

            resolved = resolve_startup_manifest_paths(repo_root)

        self.assertIn("AGENTS.md", resolved)
        self.assertIn("docs/AI-CHAT-CONTRACTS-REGISTER.md", resolved)
        self.assertIn("docs/AI-STARTUP-AND-RESTART.md", resolved)
        self.assertIn(".agents/cards/ai-product-owner.md", resolved)

    def test_load_pending_chat_contracts_reads_markdown_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            docs_dir.mkdir(parents=True)
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                textwrap.dedent(
                    """\
                    # Register

                    <!-- ai-chat-contracts:pending:start -->
                    | ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
                    | --- | --- | --- | --- | --- | --- |
                    | CHAT-001 | Exemplo | Busca | DOT-999 | cards | pendente |
                    <!-- ai-chat-contracts:pending:end -->
                    """
                ),
                encoding="utf-8",
            )

            entries = load_pending_chat_contracts(repo_root)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].contract_id, "CHAT-001")
        self.assertEqual(entries[0].status, "pendente")

    def test_write_startup_session_report_persists_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            agents_cards = repo_root / ".agents" / "cards"
            docs_dir.mkdir(parents=True)
            agents_cards.mkdir(parents=True)
            (repo_root / "AGENTS.md").write_text("# contrato\n", encoding="utf-8")
            (docs_dir / "AI-STARTUP-GOVERNANCE-MANIFEST.md").write_text(
                textwrap.dedent(
                    """\
                    # Manifest

                    - [`AGENTS.md`](../AGENTS.md)
                    - todos os arquivos `AI-*` em [`docs/`](./)
                    - todos os arquivos em [`.agents/cards/`](../.agents/cards/)
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                textwrap.dedent(
                    """\
                    # Register

                    <!-- ai-chat-contracts:pending:start -->
                    | ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
                    | --- | --- | --- | --- | --- | --- |
                    | CHAT-001 | Exemplo | Busca | DOT-999 | cards | pendente |
                    <!-- ai-chat-contracts:pending:end -->
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-STARTUP-AND-RESTART.md").write_text("# runbook\n", encoding="utf-8")
            (agents_cards / "ai-product-owner.md").write_text("# card\n", encoding="utf-8")

            payload = write_startup_session_report(repo_root)
            report_path = repo_root / payload["report_path"]
            report_text = report_path.read_text(encoding="utf-8")
            report_exists = report_path.exists()

        self.assertTrue(report_exists)
        self.assertIn("AI Startup Session Report", report_text)
        self.assertIn("CHAT-001", report_text)
        self.assertIn("AGENTS.md", report_text)

    def test_render_startup_session_markdown_lists_pending_contracts(self) -> None:
        payload = {
            "generated_at": "2026-03-09 22:00:00",
            "manifest_path": "docs/AI-STARTUP-GOVERNANCE-MANIFEST.md",
            "chat_contracts_register_path": "docs/AI-CHAT-CONTRACTS-REGISTER.md",
            "resolved_paths": ["AGENTS.md", "docs/AI-CHAT-CONTRACTS-REGISTER.md"],
            "resolved_count": 2,
            "pending_chat_contracts": [
                {
                    "contract_id": "CHAT-001",
                    "summary": "Exemplo",
                    "evidence": "Busca",
                    "owner": "DOT-999",
                    "destination": "cards",
                    "status": "pendente",
                }
            ],
            "pending_chat_contract_count": 1,
        }

        markdown = render_startup_session_markdown(payload)

        self.assertIn("CHAT-001", markdown)
        self.assertIn("docs/AI-CHAT-CONTRACTS-REGISTER.md", markdown)
        self.assertIn("Acoes obrigatorias da sessao", markdown)

    def test_startup_session_payload_counts_pending_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_dir = repo_root / "docs"
            docs_dir.mkdir(parents=True)
            (repo_root / "AGENTS.md").write_text("# contrato\n", encoding="utf-8")
            (docs_dir / "AI-STARTUP-GOVERNANCE-MANIFEST.md").write_text(
                textwrap.dedent(
                    """\
                    # Manifest

                    - [`AGENTS.md`](../AGENTS.md)
                    - todos os arquivos `AI-*` em [`docs/`](./)
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-CHAT-CONTRACTS-REGISTER.md").write_text(
                textwrap.dedent(
                    """\
                    # Register

                    <!-- ai-chat-contracts:pending:start -->
                    | ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
                    | --- | --- | --- | --- | --- | --- |
                    | CHAT-001 | Exemplo | Busca | DOT-999 | cards | pendente |
                    | CHAT-002 | Exemplo 2 | Busca | DOT-998 | docs | pendente |
                    <!-- ai-chat-contracts:pending:end -->
                    """
                ),
                encoding="utf-8",
            )
            (docs_dir / "AI-STARTUP-AND-RESTART.md").write_text("# runbook\n", encoding="utf-8")

            payload = startup_session_payload(repo_root)

        self.assertEqual(payload["pending_chat_contract_count"], 2)
        self.assertGreaterEqual(payload["resolved_count"], 3)


if __name__ == "__main__":
    unittest.main()
