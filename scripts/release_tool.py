"""Baixar e cachear binarios pinados de ferramentas externas.

Objetivo:
    Garantir que tools criticas de qualidade, como `actionlint` e `gitleaks`,
    sejam obtidas de forma deterministica e reproduzivel.
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLING_CONFIG_PATH = ROOT / "config" / "tooling.releases.yaml"


@dataclass(frozen=True)
class ToolAsset:
    """Metadados de um asset pinado."""

    archive: str
    sha256: str


@dataclass(frozen=True)
class ToolSpec:
    """Metadados completos de uma ferramenta distribuida por release."""

    name: str
    repo: str
    version: str
    executable: str
    cache_root: Path
    assets: dict[str, ToolAsset]


@lru_cache(maxsize=1)
def _raw_config() -> dict[str, object]:
    raw = yaml.safe_load(TOOLING_CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Estrutura invalida em {TOOLING_CONFIG_PATH}")
    return raw


def platform_asset_key() -> str:
    """Mapear a plataforma corrente para a chave de asset configurada."""

    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows" and machine in {"amd64", "x86_64"}:
        return "windows_x64"
    if system == "linux" and machine in {"amd64", "x86_64"}:
        return "linux_x64"
    if system == "linux" and machine in {"aarch64", "arm64"}:
        return "linux_arm64"
    raise RuntimeError(
        f"Plataforma nao suportada para tooling pinado: system={system} machine={machine}"
    )


def load_tool_spec(tool_name: str) -> ToolSpec:
    """Carregar a especificacao pinada de uma ferramenta."""

    raw = _raw_config()
    tooling_raw = raw.get("tooling")
    if not isinstance(tooling_raw, dict):
        raise ValueError(f"Secao 'tooling' ausente em {TOOLING_CONFIG_PATH}")
    tooling = cast(dict[str, object], tooling_raw)

    cache_root_value = tooling.get("cache_root")
    if not isinstance(cache_root_value, str) or not cache_root_value.strip():
        raise ValueError(f"cache_root ausente em {TOOLING_CONFIG_PATH}")
    cache_root = ROOT / cache_root_value

    tool_raw = tooling.get(tool_name)
    if not isinstance(tool_raw, dict):
        raise ValueError(f"Ferramenta '{tool_name}' ausente em {TOOLING_CONFIG_PATH}")
    tool = cast(dict[str, object], tool_raw)

    repo = tool.get("repo")
    version = tool.get("version")
    executable = tool.get("executable")
    assets_raw = tool.get("assets")
    if not isinstance(repo, str) or not repo.strip():
        raise ValueError(f"repo ausente para '{tool_name}'")
    if not isinstance(version, (str, int, float)):
        raise ValueError(f"version ausente para '{tool_name}'")
    if not isinstance(executable, str) or not executable.strip():
        raise ValueError(f"executable ausente para '{tool_name}'")
    if not isinstance(assets_raw, dict):
        raise ValueError(f"assets ausente para '{tool_name}'")

    assets: dict[str, ToolAsset] = {}
    for asset_key, value in assets_raw.items():
        if not isinstance(asset_key, str) or not isinstance(value, dict):
            raise ValueError(f"Asset invalido para '{tool_name}'")
        asset_payload = cast(dict[str, object], value)
        archive = asset_payload.get("archive")
        sha256 = asset_payload.get("sha256")
        if not isinstance(archive, str) or not isinstance(sha256, str):
            raise ValueError(f"Metadados invalidos para '{tool_name}' em '{asset_key}'")
        assets[asset_key] = ToolAsset(archive=archive, sha256=sha256)

    return ToolSpec(
        name=tool_name,
        repo=repo.strip(),
        version=str(version),
        executable=executable.strip(),
        cache_root=cache_root,
        assets=assets,
    )


def _binary_name(executable: str) -> str:
    return f"{executable}.exe" if os.name == "nt" else executable


def _download_url(spec: ToolSpec, asset: ToolAsset) -> str:
    return f"https://github.com/{spec.repo}/releases/download/v{spec.version}/{asset.archive}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as stream:
        shutil.copyfileobj(response, stream)


def _extract_archive(archive_path: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(target_dir)
        return
    if archive_path.suffixes[-2:] == [".tar", ".gz"]:
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(target_dir)
        return
    raise RuntimeError(f"Formato de arquivo nao suportado: {archive_path}")


def _locate_executable(root: Path, executable_name: str) -> Path:
    matches = [path for path in root.rglob(executable_name) if path.is_file()]
    if not matches:
        raise RuntimeError(f"Executavel {executable_name!r} nao encontrado em {root}")
    return matches[0]


def ensure_tool_binary(tool_name: str) -> Path:
    """Baixar, verificar e cachear o binario pinado para a plataforma atual."""

    spec = load_tool_spec(tool_name)
    asset_key = platform_asset_key()
    asset = spec.assets.get(asset_key)
    if asset is None:
        raise RuntimeError(
            f"Nao ha asset configurado para '{tool_name}' na plataforma '{asset_key}'"
        )

    binary_name = _binary_name(spec.executable)
    install_dir = spec.cache_root / spec.name / spec.version / asset_key
    binary_path = install_dir / binary_name
    if binary_path.exists():
        return binary_path

    download_dir = spec.cache_root / ".downloads" / spec.name / spec.version / asset_key
    archive_path = download_dir / asset.archive
    if not archive_path.exists() or _sha256(archive_path) != asset.sha256:
        if archive_path.exists():
            archive_path.unlink()
        _download(_download_url(spec, asset), archive_path)
        if _sha256(archive_path) != asset.sha256:
            raise RuntimeError(f"Checksum invalido para {archive_path}")

    staging_dir = install_dir / ".staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    _extract_archive(archive_path, staging_dir)
    located = _locate_executable(staging_dir, binary_name)
    install_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(located), str(binary_path))
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    binary_path.chmod(binary_path.stat().st_mode | 0o111)
    return binary_path
