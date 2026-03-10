"""Validar links locais e referencias documentais do repositório."""

from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_ROOTS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "LICOES-APRENDIDAS.md",
    ROOT / "SECURITY.md",
    ROOT / "bootstrap" / "README.md",
    ROOT / "tests" / "README.md",
    ROOT / "docs",
    ROOT / ".agents",
]
SKIP_PREFIXES = (
    "archive/",
    "docs/reference/",
    ".agents/prompts/legacy/",
)
SKIP_FILES = {
    "docs/AI-ORTHOGRAPHY-LEDGER.md",
    "docs/AI-REVIEW-LEDGER.md",
    "docs/AI-WIP-TRACKER.md",
    "docs/ROADMAP-DECISIONS.md",
}
NON_REPO_REFERENCE_PREFIXES = (
    ".venv",
    ".cache",
    ".pytest_cache",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LINK_SPAN_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
AUTO_LINK_SPAN_RE = re.compile(r"<(?:https?://[^>]+|mailto:[^>]+)>")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
FENCE_RE = re.compile(r"^(```|~~~)")
URL_RE = re.compile(r"https?://[^\s<>()\]]+")
PATH_TEXT_RE = re.compile(
    r"(?P<target>(?:~?/)?(?:[A-Za-z0-9._-]+/)+(?:[A-Za-z0-9._-]+(?:\.[A-Za-z0-9._-]+)?/?)?)"
)


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


def _trim_trailing_punctuation(target: str) -> str:
    return target.rstrip(".,;:!?")


@lru_cache(maxsize=1)
def _tracked_repo_entries() -> set[str]:
    """Retornar arquivos e diretorios rastreados pelo Git quando disponivel."""

    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return set()

    entries: set[str] = set()
    for raw_path in result.stdout.split(b"\x00"):
        if not raw_path:
            continue
        relative = Path(raw_path.decode("utf-8")).as_posix()
        entries.add(relative)
        parent = Path(relative).parent
        while parent != Path("."):
            entries.add(parent.as_posix())
            parent = parent.parent
    return entries


@lru_cache(maxsize=1)
def _repo_root_entries() -> set[str]:
    if not ROOT.exists():
        return set()
    return {entry.name for entry in ROOT.iterdir()}


@lru_cache(maxsize=2048)
def _is_git_ignored(relative_path: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "-q", "--", relative_path],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def _looks_like_repo_reference(target: str) -> bool:
    cleaned = target.strip()
    if not cleaned:
        return False
    if cleaned.startswith(("http://", "https://", "mailto:", "#")):
        return False
    if any(
        cleaned == prefix or cleaned.startswith(f"{prefix}/")
        for prefix in NON_REPO_REFERENCE_PREFIXES
    ):
        return False
    return (
        "/" in cleaned or "\\" in cleaned or cleaned.startswith(".") or Path(cleaned).suffix != ""
    )


def _looks_like_repoish_reference(target: str) -> bool:
    cleaned = _trim_trailing_punctuation(target.strip()).replace("\\", "/")
    if not _looks_like_repo_reference(cleaned):
        return False
    if cleaned.startswith(("~/", "/")):
        return False
    first_segment = cleaned.split("/", maxsplit=1)[0]
    tracked_entries = _tracked_repo_entries()
    if tracked_entries and cleaned in tracked_entries:
        return True
    return first_segment in _repo_root_entries()


def _resolve_local_target(source: Path, target: str) -> Path | None:
    cleaned = _trim_trailing_punctuation(target.strip())
    if not cleaned or _is_external_link(cleaned) or cleaned.startswith("#"):
        return None

    path_part = cleaned.split("#", maxsplit=1)[0].strip()
    if not path_part:
        return None

    raw_candidate = Path(path_part.replace("\\", "/"))
    tracked_entries = _tracked_repo_entries()
    candidates = [ROOT / raw_candidate, (source.parent / raw_candidate).resolve()]
    for candidate in candidates:
        try:
            relative = candidate.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        normalized = relative.rstrip("/")
        if tracked_entries:
            if normalized in tracked_entries:
                return candidate
            if candidate.exists() and not _is_git_ignored(normalized):
                return candidate
            continue
        if candidate.exists():
            return candidate
    return None


def _span_inside_link(match_start: int, link_spans: list[tuple[int, int]]) -> bool:
    return any(start <= match_start < end for start, end in link_spans)


def _mask_spans(line: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return line
    chars = list(line)
    for start, end in spans:
        for idx in range(start, min(end, len(chars))):
            chars[idx] = " "
    return "".join(chars)


def _iter_bare_repo_references(masked_line: str) -> list[str]:
    hits: list[str] = []
    occupied: list[tuple[int, int]] = []
    for match in PATH_TEXT_RE.finditer(masked_line):
        start, end = match.span("target")
        if any(existing_start <= start < existing_end for existing_start, existing_end in occupied):
            continue
        target = _trim_trailing_punctuation(match.group("target").strip())
        if not _looks_like_repo_reference(target):
            continue
        hits.append(target)
        occupied.append((start, end))
    return hits


def validate_markdown_file(path: Path) -> list[str]:
    """Validar um arquivo Markdown individual."""

    errors: list[str] = []
    inside_code_fence = False

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE_RE.match(line.strip()):
            inside_code_fence = not inside_code_fence
            continue
        if inside_code_fence:
            continue

        link_spans = [
            *[match.span() for match in LINK_SPAN_RE.finditer(line)],
            *[match.span() for match in AUTO_LINK_SPAN_RE.finditer(line)],
        ]
        code_spans = [match.span() for match in INLINE_CODE_RE.finditer(line)]
        masked_line = _mask_spans(line, [*link_spans, *code_spans])
        for match in LINK_RE.finditer(line):
            target = match.group(1)
            if _resolve_local_target(path, target) is None and not (
                _is_external_link(target) or target.startswith("#")
            ):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number} link local invalido: {target}"
                )

        for match in INLINE_CODE_RE.finditer(line):
            if _span_inside_link(match.start(), link_spans):
                continue
            target = _trim_trailing_punctuation(match.group(1).strip())
            if _is_external_link(target):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number} referencia externa sem link: {target}"
                )
                continue
            if not _looks_like_repo_reference(target):
                continue
            if _resolve_local_target(path, target) is None and not _looks_like_repoish_reference(
                target
            ):
                continue
            errors.append(
                f"{path.relative_to(ROOT)}:{line_number} referencia interna sem link: {target}"
            )

        for match in URL_RE.finditer(masked_line):
            target = _trim_trailing_punctuation(match.group(0).strip())
            if not target:
                continue
            errors.append(
                f"{path.relative_to(ROOT)}:{line_number} referencia externa sem link: {target}"
            )

        for target in _iter_bare_repo_references(masked_line):
            if _resolve_local_target(path, target) is None and not _looks_like_repoish_reference(
                target
            ):
                continue
            errors.append(
                f"{path.relative_to(ROOT)}:{line_number} referencia interna sem link: {target}"
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
