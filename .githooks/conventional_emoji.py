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
    "prompt",
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
PROMPT_SCOPE = "prompt"
PROMPT_BRANCH_TYPE = "prompt"
PROMPT_TASK_PREFIX = "prompt/"
PROMPT_PATH_PREFIX = ".agents/prompts/"

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
    warning: str | None = None


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


JIRA_KEY_RE = re.compile(r"(?<![A-Z0-9-])([A-Z][A-Z0-9]+-\d+)(?![A-Z0-9-])")


def validate_message(
    text: str,
    *,
    require_emoji: bool,
    require_issue_key: bool = False,
    required_scope: str | None = None,
) -> ValidationResult:
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

    scope = (match.group("scope") or "").strip()
    if required_scope and scope != required_scope:
        return ValidationResult(
            ok=False,
            error=(
                f"Scope obrigatorio: '{required_scope}'. Exemplo: "
                f"'📝 docs({required_scope}): DOT-179 documentar regra'."
            ),
        )

    if require_issue_key:
        jira_keys = JIRA_KEY_RE.findall(first_line)
        if not jira_keys:
            return ValidationResult(
                ok=False,
                error=(
                    "Chave Jira obrigatoria. Inclua um work item no subject, por "
                    "exemplo: '🔧 chore(git): DOT-81 endurecer convencoes'."
                ),
            )
        if len(jira_keys) != 1:
            return ValidationResult(
                ok=False,
                error="O subject deve carregar exatamente uma chave Jira real.",
            )

    return ValidationResult(ok=True)


def normalize_repo_path(path: str) -> str:
    normalized = (path or "").strip().replace("\\", "/")
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def requires_prompt_prefix(paths: list[str]) -> bool:
    return any(normalize_repo_path(path).startswith(PROMPT_PATH_PREFIX) for path in paths)


def branch_uses_prompt_prefix(branch: str) -> bool:
    branch_name = (branch or "").strip()
    return branch_name.startswith(f"{PROMPT_BRANCH_TYPE}/")


def required_scope_for_paths_and_branch(paths: list[str], branch: str = "") -> str | None:
    if requires_prompt_prefix(paths) or branch_uses_prompt_prefix(branch):
        return PROMPT_SCOPE
    return None


def parse_paths_json(raw_json: str | None) -> list[str]:
    if not raw_json:
        return []
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalido em --paths-json: {exc.msg}") from exc
    if not isinstance(payload, list):
        raise ValueError("--paths-json deve receber uma lista JSON de strings.")
    paths: list[str] = []
    for entry in payload:
        if not isinstance(entry, str):
            raise ValueError("--paths-json deve receber apenas strings.")
        normalized = normalize_repo_path(entry)
        if normalized:
            paths.append(normalized)
    return paths


def validate_branch_name(branch: str, *, require_prompt_type: bool = False) -> ValidationResult:
    branch_name = (branch or "").strip()
    if not branch_name:
        return ValidationResult(ok=False, error="Branch vazia.")
    if branch_name.startswith(("dependabot/", "renovate/")):
        return ValidationResult(ok=True)
    branch_label = "<type>/<jira-key>-<slug>"

    canonical_pattern = re.compile(
        r"^(?P<type>[a-z]+)(?:\([^\)]+\))?/"
        r"(?P<issue>[A-Z][A-Z0-9]+-\d+)-(?P<slug>[a-z0-9][a-z0-9._-]{2,})$"
    )
    legacy_pattern = re.compile(
        r"^(?P<type>[a-z]+)(?:\([^\)]+\))?/(?P<slug>[a-z0-9][a-z0-9._-]{2,})$"
    )
    match = canonical_pattern.match(branch_name)
    legacy_match = legacy_pattern.match(branch_name)
    if not match:
        if not legacy_match:
            return ValidationResult(
                ok=False,
                error=(
                    f"Branch deve seguir '{branch_label}' "
                    "(ex: feat/DOT-81-git-traceability)."
                ),
            )
        match = legacy_match

    branch_type = match.group("type")
    if branch_type not in VALID_BRANCH_TYPES:
        valid = ", ".join(sorted(VALID_BRANCH_TYPES))
        return ValidationResult(
            ok=False,
            error=f"Tipo de branch invalido: '{branch_type}'. Tipos permitidos: {valid}.",
        )

    if require_prompt_type and branch_type != PROMPT_BRANCH_TYPE:
        return ValidationResult(
            ok=False,
            error=(
                "Mudancas em .agents/prompts exigem branch com prefixo 'prompt'. "
                f"Use '{PROMPT_BRANCH_TYPE}/DOT-179-slug'."
            ),
        )

    if legacy_match and not canonical_pattern.match(branch_name):
        return ValidationResult(
            ok=True,
            warning=(
                "Branch legada aceita temporariamente sem chave Jira. Novo "
                f"padrao canonico: '{branch_label}'."
            ),
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
    parser.add_argument("--require-issue-key", action="store_true")
    parser.add_argument("--require-scope", default="")
    parser.add_argument("--paths-json", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--validate-branch", default=None)
    args = parser.parse_args(argv)

    if args.validate_branch is not None:
        try:
            changed_paths = parse_paths_json(args.paths_json)
        except ValueError as exc:
            _print_error_block("INPUT INVALIDO", f"│ {str(exc):<63} │")
            return 2
        result = validate_branch_name(
            args.validate_branch,
            require_prompt_type=requires_prompt_prefix(changed_paths),
        )
        if result.ok:
            if result.warning:
                print(result.warning, file=sys.stderr)
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
            paths: list[str] = []
            if isinstance(subject, dict):
                entry_subject = subject.get("subject") or subject.get("message") or ""
                entry_paths = subject.get("paths") or []
                if not isinstance(entry_subject, str):
                    failed = True
                    print(f"❌ Item invalido (subject ausente): {subject!r}", file=sys.stderr)
                    continue
                if not isinstance(entry_paths, list) or any(
                    not isinstance(path, str) for path in entry_paths
                ):
                    failed = True
                    print(
                        f"❌ Item invalido (paths ausentes ou invalidos): {subject!r}",
                        file=sys.stderr,
                    )
                    continue
                paths = [normalize_repo_path(path) for path in entry_paths if path.strip()]
                subject = entry_subject
            if not isinstance(subject, str):
                failed = True
                print(f"❌ Item invalido (nao-string): {subject!r}", file=sys.stderr)
                continue
            required_scope = args.require_scope or required_scope_for_paths_and_branch(
                paths, args.branch
            )
            result = validate_message(
                subject,
                require_emoji=args.require_emoji,
                require_issue_key=args.require_issue_key,
                required_scope=required_scope or None,
            )
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
        try:
            changed_paths = parse_paths_json(args.paths_json)
        except ValueError as exc:
            _print_error_block("INPUT INVALIDO", f"│ {str(exc):<63} │")
            return 2
        required_scope = args.require_scope or required_scope_for_paths_and_branch(
            changed_paths, args.branch
        )
        result = validate_message(
            text,
            require_emoji=args.require_emoji,
            require_issue_key=args.require_issue_key,
            required_scope=required_scope or None,
        )
        if result.ok:
            return 0
        _print_error_block("COMMIT/PR INVALIDO", f"│ {result.error:<63} │")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
