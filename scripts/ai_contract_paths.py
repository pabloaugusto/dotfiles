from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_ROOT_NAME = ".agents"
LEGACY_CODEX_ROOT_NAME = ".codex"


def ai_root(repo_root: Path = ROOT) -> Path:
    return repo_root / AI_ROOT_NAME


def cards_root(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "cards"


def skills_root(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "skills"


def registry_root(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "registry"


def orchestration_root(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "orchestration"


def rules_root(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "rules"


def evals_root(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "evals"


def config_path(repo_root: Path = ROOT) -> Path:
    return ai_root(repo_root) / "config.toml"


def legacy_codex_root(repo_root: Path = ROOT) -> Path:
    return repo_root / LEGACY_CODEX_ROOT_NAME


def legacy_codex_readme(repo_root: Path = ROOT) -> Path:
    return legacy_codex_root(repo_root) / "README.md"
