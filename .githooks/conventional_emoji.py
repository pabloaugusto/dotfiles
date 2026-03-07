#!/usr/bin/env python3
"""Validador e injetor de emoji para Conventional Commits.

Fonte de verdade para:

1. injeção automática de emoji em commits locais;
2. validação de commit subject, PR title e nomes de branch;
3. validação em lote de subjects de commits.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass


COMMIT_TYPE_EMOJI = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📝",
    "style": "💄",
    "refactor": "♻️",
    "perf": "⚡",
    "test": "✅",
    "build": "👷",
    "ci": "💚",
    "chore": "🔧",
    "revert": "⏪",
    "wip": "🚧",
    "hotfix": "🚑",
    "security": "🔒",
    "deps": "⬆️",
    "i18n": "🌐",
    "init": "🎉",
    "release": "🔖",
    "merge": "🔀",
}

VALID_COMMIT_TYPES = set(COMMIT_TYPE_EMOJI)
VALID_BRANCH_TYPES = {
    "feat",
    "fix",
    "docs",
    "refactor",
    "perf",
    "test",
    "ci",
    "chore",
    "build",
    "hotfix",
    "deps",
    "security",
    "i18n",
    "wip",
    "init",
    "release",
}
MAX_SUBJECT_LEN = 72

CONVENTIONAL_RE = re.compile(
    r"^(?P<emoji>[^\w\s:(\-]+\s+)?"
    r"(?P<type>\w+)"
    r"(?:\((?P<scope>[^\)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s+"
    r"(?P<description>.+)"
)

KEYWORD_EMOJI = {
    "add": "✨",
    "create": "✨",
    "new": "✨",
    "update": "⬆️",
    "upgrade": "⬆️",
    "remove": "🔥",
    "delete": "🔥",
    "fix": "🐛",
    "bugfix": "🐛",
    "hotfix": "🚑",
    "merge": "🔀",
    "improve": "⚡",
    "optimize": "⚡",
    "doc": "📝",
    "documentation": "📝",
    "readme": "📝",
    "test": "✅",
    "testing": "✅",
    "config": "🔧",
    "configuration": "🔧",
    "refactor": "♻️",
    "clean": "♻️",
    "release": "🔖",
    "version": "🔖",
    "init": "🎉",
    "initial": "🎉",
    "wip": "🚧",
    "progress": "🚧",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    error: str | None = None


def _read_text_from_file_or_stdin(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def inject_emoji(commit_msg_text: str) -> str:
    raw = commit_msg_text
    if raw.startswith("#"):
        return raw

    msg = raw.strip("\n")
    if not msg.strip():
        return raw

    lines = msg.split("\n")
    first = lines[0].strip()

    conventional = CONVENTIONAL_RE.match(first)
    if conventional:
        commit_type = (conventional.group("type") or "").lower()
        emoji = COMMIT_TYPE_EMOJI.get(commit_type)
        if emoji:
            scope = conventional.group("scope")
            breaking = conventional.group("breaking") or ""
            description = conventional.group("description")
            scope_part = f"({scope})" if scope else ""
            lines[0] = f"{emoji} {commit_type}{scope_part}{breaking}: {description}"
            return "\n".join(lines) + "\n"

    first_word = first.split()[0].lower() if first.split() else ""
    emoji = KEYWORD_EMOJI.get(first_word)
    if emoji:
        return f"{emoji} {msg}\n"

    return raw


def validate_message(text: str, *, require_emoji: bool) -> ValidationResult:
    message = (text or "").strip()
    if not message or message.startswith("#"):
        return ValidationResult(ok=True)

    first_line = message.split("\n")[0].strip()

    if first_line.startswith("Merge pull request #"):
        return ValidationResult(
            ok=False,
            error=(
                "Merge commit fora do padrao. Use o titulo do PR como subject "
                "no merge commit (Conventional + emoji)."
            ),
        )

    if len(first_line) > MAX_SUBJECT_LEN:
        return ValidationResult(
            ok=False,
            error=(
                f"Mensagem muito longa ({len(first_line)}). "
                f"Maximo recomendado: {MAX_SUBJECT_LEN}."
            ),
        )

    match = CONVENTIONAL_RE.match(first_line)
    if not match:
        return ValidationResult(
            ok=False,
            error=(
                "Mensagem nao segue Conventional Commits. Ex: "
                "'✨ feat(api): add endpoint'. Formato: <emoji> type(scope?): description"
            ),
        )

    commit_type = (match.group("type") or "").lower()
    if commit_type not in VALID_COMMIT_TYPES:
        valid = ", ".join(sorted(VALID_COMMIT_TYPES))
        return ValidationResult(
            ok=False,
            error=f"Tipo invalido: '{commit_type}'. Tipos validos: {valid}",
        )

    if require_emoji:
        emoji_part = (match.group("emoji") or "").strip()
        if not emoji_part:
            return ValidationResult(
                ok=False,
                error="Emoji obrigatorio. Ex: '✨ feat: ...'.",
            )
        expected = COMMIT_TYPE_EMOJI.get(commit_type)
        if expected and emoji_part != expected:
            return ValidationResult(
                ok=False,
                error=(
                    f"Emoji nao corresponde ao tipo '{commit_type}'. "
                    f"Encontrado: '{emoji_part}'. Esperado: '{expected}'."
                ),
            )

    description = (match.group("description") or "").strip()
    if len(description) < 3:
        return ValidationResult(ok=False, error="Descricao muito curta.")

    return ValidationResult(ok=True)


def validate_branch_name(branch: str) -> ValidationResult:
    branch_name = (branch or "").strip()
    if not branch_name:
        return ValidationResult(ok=False, error="Branch vazia.")
    if branch_name.startswith(("dependabot/", "renovate/")):
        return ValidationResult(ok=True)

    pattern = re.compile(
        r"^(?P<type>[a-z]+)(?:\([^\)]+\))?/(?P<slug>[a-z0-9][a-z0-9._-]{2,})$"
    )
    match = pattern.match(branch_name)
    if not match:
        return ValidationResult(
            ok=False,
            error="Branch deve seguir '<type>/<slug>' (ex: feat/add-login).",
        )

    branch_type = match.group("type")
    if branch_type not in VALID_BRANCH_TYPES:
        valid = ", ".join(sorted(VALID_BRANCH_TYPES))
        return ValidationResult(
            ok=False,
            error=f"Tipo de branch invalido: '{branch_type}'. Tipos permitidos: {valid}.",
        )

    return ValidationResult(ok=True)


def _print_error_block(title: str, details: str) -> None:
    print(
        (
            "\n╭─────────────────────────────────────────────────────────────────╮\n"
            f"│ {title:<63} │\n"
            "├─────────────────────────────────────────────────────────────────┤\n"
            f"{details}\n"
            "╰─────────────────────────────────────────────────────────────────╯\n"
        ),
        file=sys.stderr,
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("commit_msg_file", nargs="?", default=None)
    parser.add_argument("--inject", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--text", default=None)
    parser.add_argument("--validate-many-json", default=None)
    parser.add_argument("--require-emoji", action="store_true")
    parser.add_argument("--validate-branch", default=None)
    args = parser.parse_args(argv)

    if args.validate_branch is not None:
        result = validate_branch_name(args.validate_branch)
        if result.ok:
            return 0
        _print_error_block("BRANCH INVALIDA", f"│ {result.error:<63} │")
        return 1

    if args.validate_many_json is not None:
        try:
            subjects = json.loads(args.validate_many_json)
        except json.JSONDecodeError as exc:
            _print_error_block(
                "INPUT INVALIDO",
                f"│ JSON invalido em --validate-many-json: {exc.msg:<34} │",
            )
            return 2

        if not isinstance(subjects, list):
            _print_error_block(
                "INPUT INVALIDO",
                "│ --validate-many-json deve receber uma lista JSON de strings. │",
            )
            return 2

        failed = False
        for subject in subjects:
            if not isinstance(subject, str):
                failed = True
                print(f"❌ Item invalido (nao-string): {subject!r}", file=sys.stderr)
                continue
            result = validate_message(subject, require_emoji=args.require_emoji)
            if not result.ok:
                failed = True
                print(f"❌ Invalid commit subject: {subject}", file=sys.stderr)
                if result.error:
                    print(f"   ↳ {result.error}", file=sys.stderr)
        return 1 if failed else 0

    mode_inject = args.inject
    mode_validate = args.validate or not args.inject

    if args.text is not None:
        text = args.text
    else:
        if not args.commit_msg_file:
            parser.print_help(sys.stderr)
            return 2
        text = _read_text_from_file_or_stdin(args.commit_msg_file)

    if mode_inject:
        output = inject_emoji(text)
        if args.commit_msg_file and args.commit_msg_file != "-" and args.text is None:
            with open(args.commit_msg_file, "w", encoding="utf-8") as handle:
                handle.write(output)
        else:
            sys.stdout.write(output)
        return 0

    if mode_validate:
        result = validate_message(text, require_emoji=args.require_emoji)
        if result.ok:
            return 0
        _print_error_block("COMMIT/PR INVALIDO", f"│ {result.error:<63} │")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
