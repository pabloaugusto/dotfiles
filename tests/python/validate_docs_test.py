from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots

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
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots

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
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots

        self.assertEqual(errors, [])

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
                errors = validate_docs.validate_markdown_file(markdown)
            finally:
                validate_docs.ROOT = original_root
                validate_docs.MARKDOWN_ROOTS = original_markdown_roots

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
