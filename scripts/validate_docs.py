"""Validar links locais e referencias documentais do repositório."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_ROOTS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "SECURITY.md",
    ROOT / "bootstrap" / "README.md",
    ROOT / "tests" / "README.md",
    ROOT / "docs",
]
SKIP_PREFIXES = (
    "archive/",
    ".agents/",
    "docs/reference/",
)
SKIP_FILES = {
    "docs/AI-WIP-TRACKER.md",
    "docs/ROADMAP-DECISIONS.md",
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")


def iter_markdown_files() -> list[Path]:
    """Retornar os arquivos Markdown sob governanca desta validacao."""

    markdown_files: list[Path] = []
    for root in MARKDOWN_ROOTS:
        if root.is_file():
            markdown_files.append(root)
            continue
        markdown_files.extend(sorted(root.rglob("*.md")))

    filtered: list[Path] = []
    for path in markdown_files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in SKIP_FILES:
            continue
        if any(relative.startswith(prefix) for prefix in SKIP_PREFIXES):
            continue
        filtered.append(path)
    return sorted(dict.fromkeys(filtered))


def _is_external_link(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto"}


def _resolve_local_target(source: Path, target: str) -> Path | None:
    cleaned = target.strip()
    if not cleaned or _is_external_link(cleaned) or cleaned.startswith("#"):
        return None

    path_part = cleaned.split("#", maxsplit=1)[0].strip()
    if not path_part:
        return None

    raw_candidate = Path(path_part)
    candidates = [ROOT / raw_candidate, (source.parent / raw_candidate).resolve()]
    for candidate in candidates:
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            continue
        if candidate.exists():
            return candidate
    return None


def validate_markdown_file(path: Path) -> list[str]:
    """Validar um arquivo Markdown individual."""

    errors: list[str] = []
    inside_code_fence = False

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE_RE.match(line.strip()):
            inside_code_fence = not inside_code_fence
            continue
        if inside_code_fence or line.lstrip().startswith("|"):
            continue

        for match in LINK_RE.finditer(line):
            target = match.group(1)
            if _resolve_local_target(path, target) is None and not (
                _is_external_link(target) or target.startswith("#")
            ):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number} link local invalido: {target}"
                )

    return errors


def validate_docs() -> list[str]:
    """Validar toda a documentacao governada pelo repo."""

    errors: list[str] = []
    for markdown_file in iter_markdown_files():
        errors.extend(validate_markdown_file(markdown_file))
    return errors


def main() -> int:
    errors = validate_docs()
    if errors:
        print("[FAIL] Erros de governanca documental:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("[OK] Documentacao validada com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
