from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for Python < 3.11
    tomllib = None  # type: ignore[assignment]


class ConfigContextError(RuntimeError):
    """Raised when config manifests cannot be resolved safely."""


@dataclass(frozen=True)
class ConfigReference:
    raw: str
    relative_path: str
    key_path: str


ROOT_CONFIG_PATH = Path("config/config.toml")
APP_CONFIG_PATH = Path("app/config/config.toml")
AI_CONFIG_PATH = Path(".agents/config/config.toml")
AI_BRIDGE_PATH = Path(".agents/config.toml")


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    return Path(repo_root).resolve()


def root_config_path(repo_root: str | Path | None = None) -> Path:
    return (resolve_repo_root(repo_root) / ROOT_CONFIG_PATH).resolve()


def app_config_path(repo_root: str | Path | None = None) -> Path:
    return (resolve_repo_root(repo_root) / APP_CONFIG_PATH).resolve()


def ai_config_path(repo_root: str | Path | None = None) -> Path:
    return (resolve_repo_root(repo_root) / AI_CONFIG_PATH).resolve()


def ai_bridge_path(repo_root: str | Path | None = None) -> Path:
    return (resolve_repo_root(repo_root) / AI_BRIDGE_PATH).resolve()


def overlay_path_for(base_path: Path) -> Path:
    return base_path.with_name(f"{base_path.stem}.local{base_path.suffix}")


def merge_maps(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, override_value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, Mapping):
            merged[key] = merge_maps(base_value, override_value)
            continue
        merged[key] = override_value
    return merged


def load_toml_map(path: Path) -> dict[str, Any]:
    if tomllib is None:
        raise ConfigContextError("tomllib nao esta disponivel neste runtime Python.")
    if not path.is_file():
        raise ConfigContextError(f"Arquivo TOML nao encontrado: {path.as_posix()}")
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    if not isinstance(payload, dict):
        raise ConfigContextError(f"TOML invalido em {path.as_posix()}: payload nao e mapa.")
    return payload


def load_yaml_map(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigContextError(f"Arquivo YAML nao encontrado: {path.as_posix()}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ConfigContextError(f"YAML invalido em {path.as_posix()}: payload nao e mapa.")
    return payload


def load_config_map(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".toml":
        return load_toml_map(path)
    if suffix in {".yaml", ".yml"}:
        return load_yaml_map(path)
    raise ConfigContextError(
        f"Formato de config nao suportado em {path.as_posix()}: esperado .toml/.yaml/.yml"
    )


def load_config_map_with_optional_overlay(base_path: Path) -> tuple[dict[str, Any], Path]:
    payload = load_config_map(base_path)
    local_path = overlay_path_for(base_path)
    if not local_path.exists():
        return payload, local_path
    return merge_maps(payload, load_config_map(local_path)), local_path


def load_context_manifest(
    repo_root: str | Path | None = None,
    *,
    context: str,
) -> tuple[Path, dict[str, Any]]:
    resolved_root = resolve_repo_root(repo_root)
    match context:
        case "root":
            path = root_config_path(resolved_root)
        case "app":
            path = app_config_path(resolved_root)
        case "ai":
            path = ai_config_path(resolved_root)
        case _:
            raise ConfigContextError(f"Contexto de config desconhecido: {context}")
    return path, load_toml_map(path)


def parse_config_ref(raw_value: str) -> ConfigReference:
    value = str(raw_value or "").strip()
    if "::" not in value:
        raise ConfigContextError(
            f"Config ref invalida: {value!r}. Use o formato arquivo::chave."
        )
    relative_path, key_path = value.split("::", 1)
    relative_path = relative_path.strip()
    key_path = key_path.strip()
    if not relative_path or not key_path:
        raise ConfigContextError(
            f"Config ref invalida: {value!r}. Use o formato arquivo::chave."
        )
    return ConfigReference(raw=value, relative_path=relative_path, key_path=key_path)


def lookup_key_path(payload: Any, key_path: str) -> Any:
    current = payload
    for segment in [part.strip() for part in key_path.split(".") if part.strip()]:
        if not isinstance(current, Mapping):
            raise ConfigContextError(
                f"Chave {key_path!r} nao pode ser resolvida porque um segmento nao e mapa."
            )
        if segment not in current:
            raise ConfigContextError(f"Chave ausente na config: {key_path!r}")
        current = current[segment]
    return current


def resolve_config_ref(
    raw_value: str,
    *,
    repo_root: str | Path | None = None,
) -> Any:
    reference = parse_config_ref(raw_value)
    resolved_root = resolve_repo_root(repo_root)
    candidate_pattern = (resolved_root / reference.relative_path).as_posix()
    if "*" in reference.relative_path or "?" in reference.relative_path:
        matches = sorted(resolved_root.glob(reference.relative_path))
        if not matches:
            raise ConfigContextError(
                f"Nenhum arquivo encontrado para config ref: {reference.relative_path}"
            )
        resolved: dict[str, Any] = {}
        for candidate in matches:
            payload = load_config_map(candidate)
            try:
                resolved[candidate.stem] = lookup_key_path(payload, reference.key_path)
            except ConfigContextError:
                continue
        if not resolved:
            raise ConfigContextError(
                f"Nenhum valor valido encontrado para config ref wildcard: {reference.raw}"
            )
        return resolved
    candidate = Path(candidate_pattern)
    payload = load_config_map(candidate)
    return lookup_key_path(payload, reference.key_path)


def manifest_domain_paths(manifest_payload: Mapping[str, Any]) -> dict[str, str]:
    domains = manifest_payload.get("domains") or {}
    if not isinstance(domains, Mapping):
        raise ConfigContextError("Manifesto de contexto sem bloco [domains] valido.")
    normalized: dict[str, str] = {}
    for key, value in domains.items():
        if isinstance(key, str) and isinstance(value, str) and value.strip():
            normalized[key] = value.strip()
    return normalized
