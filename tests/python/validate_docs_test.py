from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import subprocess

from scripts import validate_docs


class ValidateDocsTest(unittest.TestCase):
    def test_detects_invalid_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            markdown = root / "README.md"
            markdown.write_text("[link](docs/inexistente.md)\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(len(errors), 1)
        self.assertIn("link local invalido", errors[0])

    def test_detects_inline_repo_path_without_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "docs" / "guia.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Guia\n", encoding="utf-8")
            markdown = root / "README.md"
            markdown.write_text("Veja `docs/guia.md`.\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(len(errors), 1)
        self.assertIn("referencia interna sem link", errors[0])

    def test_accepts_valid_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "docs" / "guia.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Guia\n", encoding="utf-8")
            markdown = root / "README.md"
            markdown.write_text("[Guia](docs/guia.md)\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(errors, [])

    def test_accepts_valid_link_to_existing_untracked_file_inside_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            markdown = root / "README.md"
            markdown.write_text("[Guia](docs/guia.md)\n", encoding="utf-8")
            target = root / "docs" / "guia.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Guia\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True, capture_output=True)

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                validate_docs._is_git_ignored.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                validate_docs._is_git_ignored.cache_clear()

        self.assertEqual(errors, [])

    def test_rejects_link_to_existing_but_git_ignored_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / ".gitignore").write_text("docs/*.local.md\n", encoding="utf-8")
            markdown = root / "README.md"
            markdown.write_text("[Local](docs/guia.local.md)\n", encoding="utf-8")
            target = root / "docs" / "guia.local.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Local\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "README.md", ".gitignore"],
                cwd=root,
                check=True,
                capture_output=True,
            )

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                validate_docs._is_git_ignored.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                validate_docs._is_git_ignored.cache_clear()

        self.assertEqual(len(errors), 1)
        self.assertIn("link local invalido", errors[0])

    def test_accepts_code_label_inside_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "docs" / "guia.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Guia\n", encoding="utf-8")
            markdown = root / "README.md"
            markdown.write_text("[`docs/guia.md`](docs/guia.md)\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(errors, [])

    def test_detects_plain_repo_path_without_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "bootstrap" / "_start.ps1"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# noop\n", encoding="utf-8")
            markdown = root / "README.md"
            markdown.write_text(
                "Bootstrap Windows: bootstrap/_start.ps1 -> bootstrap/bootstrap-windows.ps1\n",
                encoding="utf-8",
            )
            second_target = root / "bootstrap" / "bootstrap-windows.ps1"
            second_target.write_text("# noop\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(len(errors), 2)
        self.assertIn("bootstrap/_start.ps1", errors[0] + errors[1])
        self.assertIn("bootstrap/bootstrap-windows.ps1", errors[0] + errors[1])

    def test_detects_external_url_without_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            markdown = root / "README.md"
            markdown.write_text("Fonte: https://example.com/docs\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(len(errors), 1)
        self.assertIn("referencia externa sem link", errors[0])

    def test_accepts_external_autolink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            markdown = root / "README.md"
            markdown.write_text("Fonte: <https://example.com/docs>\n", encoding="utf-8")

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(errors, [])

    def test_detects_repo_path_inside_markdown_table_without_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "docs" / "guia.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Guia\n", encoding="utf-8")
            markdown = root / "README.md"
            markdown.write_text(
                "| Item | Arquivo |\n| --- | --- |\n| Guia | docs/guia.md |\n",
                encoding="utf-8",
            )

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots

        self.assertEqual(len(errors), 1)
        self.assertIn("docs/guia.md", errors[0])

    def test_detects_repoish_path_even_when_target_file_is_local_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "bootstrap").mkdir(parents=True, exist_ok=True)
            markdown = root / "README.md"
            markdown.write_text(
                "Arquivo local ignorado: `bootstrap/user-config.yaml`\n",
                encoding="utf-8",
            )

            original_root = validate_docs.ROOT
            original_markdown_roots = validate_docs.MARKDOWN_ROOTS
            try:
                validate_docs.ROOT = root
                validate_docs.MARKDOWN_ROOTS = [markdown]
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots
                validate_docs._tracked_repo_entries.cache_clear()
                validate_docs._repo_root_entries.cache_clear()

        self.assertEqual(len(errors), 1)
        self.assertIn("bootstrap/user-config.yaml", errors[0])


if __name__ == "__main__":
    unittest.main()
