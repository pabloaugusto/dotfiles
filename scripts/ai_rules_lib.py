from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback para Python < 3.11
    tomllib = None  # type: ignore[assignment]

from scripts.ai_contract_paths import config_path, rules_root


class AiRulesError(RuntimeError):
    """Raised when the rules layer cannot be loaded consistently."""


def _load_toml_map(path: Path) -> dict[str, Any]:
    if tomllib is None:
        raise AiRulesError("Python sem suporte a tomllib para ler .agents/config.toml.")
    if not path.is_file():
        raise AiRulesError(f"Arquivo TOML ausente: {path.as_posix()}")
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    if not isinstance(payload, dict):
        raise AiRulesError(f"TOML invalido em {path.as_posix()}: payload nao e mapa.")
    return payload


def _load_yaml_map(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AiRulesError(f"Arquivo YAML ausente: {path.as_posix()}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise AiRulesError(f"YAML invalido em {path.as_posix()}: payload nao e mapa.")
    return payload


def rules_contract_paths(repo_root: str | Path | None = None) -> dict[str, str]:
    resolved_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    payload = _load_toml_map(config_path(resolved_root))
    rules = payload.get("rules") or {}
    if not isinstance(rules, dict):
        raise AiRulesError(".agents/config.toml precisa conter [rules] como mapa.")
    normalized: dict[str, str] = {}
    for key, value in rules.items():
        if isinstance(key, str) and isinstance(value, str) and value.strip():
            normalized[key] = value.strip()
    return normalized


def projections_catalog_path(repo_root: str | Path | None = None) -> Path:
    resolved_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    rules = rules_contract_paths(resolved_root)
    relative = rules.get("projections", ".agents/rules/projections.yaml")
    return (resolved_root / relative).resolve()


def load_rules_projection_catalog(repo_root: str | Path | None = None) -> dict[str, Any]:
    resolved_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    payload = _load_yaml_map(projections_catalog_path(resolved_root))
    projections = payload.get("projections") or {}
    if not isinstance(projections, dict):
        raise AiRulesError("Catalogo de projecoes precisa conter 'projections' como mapa.")
    normalized: dict[str, dict[str, Any]] = {}
    for projection_id, entry in projections.items():
        if not isinstance(projection_id, str) or not isinstance(entry, dict):
            raise AiRulesError("Cada projecao precisa usar id string e payload em mapa.")
        normalized[projection_id] = dict(entry)
    return {
        "path": projections_catalog_path(resolved_root).relative_to(resolved_root).as_posix(),
        "projections": normalized,
    }


def parse_rules_text(content: str) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_must = False

    def flush() -> None:
        nonlocal current, in_must
        if current:
            rules.append(
                {
                    "id": str(current.get("id", "")).strip(),
                    "when": str(current.get("when", "")).strip(),
                    "must": list(current.get("must", [])),
                }
            )
        current = None
        in_must = False

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("rule "):
            flush()
            current = {"id": line.split(None, 1)[1].strip(), "when": "", "must": []}
            continue
        if current is None:
            continue
        if line.startswith("when:"):
            current["when"] = line.partition(":")[2].strip()
            in_must = False
            continue
        if line == "must:":
            in_must = True
            continue
        if in_must and line.startswith("- "):
            current["must"].append(line[2:].strip())
            continue
        in_must = False

    flush()
    return rules


def parse_rules_file(path: str | Path) -> list[dict[str, Any]]:
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise AiRulesError(f"Arquivo .rules ausente: {resolved.as_posix()}")
    return parse_rules_text(resolved.read_text(encoding="utf-8"))


def rules_projection_payload(repo_root: str | Path | None = None) -> dict[str, Any]:
    resolved_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    try:
        catalog = load_rules_projection_catalog(resolved_root)
    except AiRulesError as exc:
        return {"status": "error", "error": str(exc)}

    required_for_startup: list[str] = []
    loaded_for_startup: list[str] = []
    missing_required: list[str] = []
    projections_payload: dict[str, Any] = {}

    for projection_id, entry in sorted(catalog["projections"].items()):
        human_source = str(entry.get("human_source", "")).strip()
        machine_projection = str(entry.get("machine_projection", "")).strip()
        parity_terms = [
            str(term).strip() for term in entry.get("parity_terms", []) if str(term).strip()
        ]
        required = bool(entry.get("required_for_startup", False))
        if required:
            required_for_startup.append(projection_id)

        human_path = (resolved_root / human_source).resolve() if human_source else None
        machine_path = (
            (resolved_root / machine_projection).resolve() if machine_projection else None
        )
        missing_paths: list[str] = []
        if human_path is None or not human_path.is_file():
            missing_paths.append(human_source or f"{projection_id}:human_source")
        if machine_path is None or not machine_path.is_file():
            missing_paths.append(machine_projection or f"{projection_id}:machine_projection")

        parsed_rules: list[dict[str, Any]] = []
        if machine_path and machine_path.is_file():
            parsed_rules = parse_rules_file(machine_path)

        if required and not missing_paths and parsed_rules:
            loaded_for_startup.append(projection_id)
        if required and (missing_paths or not parsed_rules):
            missing_required.append(projection_id)

        projections_payload[projection_id] = {
            "status": "ok" if not missing_paths and parsed_rules else "missing",
            "human_source": human_source,
            "machine_projection": machine_projection,
            "required_for_startup": required,
            "parity_terms": parity_terms,
            "rule_ids": [str(rule.get("id", "")).strip() for rule in parsed_rules],
            "when_clauses": [str(rule.get("when", "")).strip() for rule in parsed_rules],
            "must": [
                item
                for rule in parsed_rules
                for item in rule.get("must", [])
                if isinstance(item, str) and item.strip()
            ],
            "missing_paths": missing_paths,
        }

    status = "ok" if not missing_required else "missing"
    return {
        "status": status,
        "catalog_path": str(catalog["path"]).strip(),
        "declared_projection_ids": sorted(projections_payload),
        "required_for_startup": required_for_startup,
        "loaded_for_startup": sorted(loaded_for_startup),
        "missing_required": sorted(set(missing_required)),
        "projections": projections_payload,
    }


def default_rules_path(repo_root: str | Path | None = None, rule_name: str = "") -> Path:
    resolved_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    if not rule_name:
        raise AiRulesError("rule_name obrigatorio para resolver caminho .rules.")
    return (rules_root(resolved_root) / f"{rule_name}.rules").resolve()
