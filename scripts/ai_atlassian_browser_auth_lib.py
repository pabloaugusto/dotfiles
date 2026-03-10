from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any
from urllib.parse import urlparse

from scripts.ai_control_plane_lib import (
    AiControlPlaneError,
    load_ai_control_plane,
    resolve_atlassian_platform,
    resolve_repo_root,
)

DEFAULT_STORAGE_STATE_PATH = Path(".cache/playwright/atlassian/storage-state.json")
DEFAULT_EVIDENCE_DIR = Path(".cache/playwright/atlassian/auth-bootstrap")
DEFAULT_TIMEOUT_SECONDS = 180
MAX_MANUAL_CONFIRMATIONS = 3


@dataclass(frozen=True)
class BrowserAuthBootstrapConfig:
    target_url: str
    storage_state_path: Path
    evidence_dir: Path
    timeout_seconds: int
    browser_name: str


class AtlassianBrowserAuthError(AiControlPlaneError):
    """Raised when browser auth bootstrap fails."""


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_target_url(repo_root: str | Path | None = None) -> str:
    control_plane = load_ai_control_plane(repo_root)
    resolved = resolve_atlassian_platform(
        control_plane.atlassian_definition(),
        repo_root=control_plane.repo_root,
    )
    base_url = resolved.site_url.rstrip("/")
    return f"{base_url}/wiki/home"


def bootstrap_config(
    *,
    repo_root: str | Path | None = None,
    storage_state_path: str = "",
    evidence_dir: str = "",
    target_url: str = "",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    browser_name: str = "chromium",
) -> BrowserAuthBootstrapConfig:
    resolved_repo_root = resolve_repo_root(repo_root)
    chosen_storage = (
        (resolved_repo_root / Path(storage_state_path)).resolve()
        if storage_state_path.strip()
        else (resolved_repo_root / DEFAULT_STORAGE_STATE_PATH).resolve()
    )
    chosen_evidence = (
        (resolved_repo_root / Path(evidence_dir)).resolve()
        if evidence_dir.strip()
        else (resolved_repo_root / DEFAULT_EVIDENCE_DIR).resolve()
    )
    return BrowserAuthBootstrapConfig(
        target_url=target_url.strip() or default_target_url(resolved_repo_root),
        storage_state_path=chosen_storage,
        evidence_dir=chosen_evidence,
        timeout_seconds=max(5, timeout_seconds),
        browser_name=(browser_name or "chromium").strip().lower(),
    )


def needs_reauthentication(current_url: str) -> bool:
    normalized = (current_url or "").strip().lower()
    if not normalized:
        return True
    parsed = urlparse(normalized)
    host = parsed.netloc.strip().lower()
    path = parsed.path.strip().lower()
    if host == "id.atlassian.com":
        return True
    if path.startswith("/login"):
        return True
    if "join/user-access" in path:
        return True
    if any(fragment in normalized for fragment in ("two-step", "mfa", "sso")):
        return True
    return False


def wait_for_authenticated_navigation(page: Any, timeout_seconds: int) -> str:
    deadline = monotonic() + max(5, timeout_seconds)
    current_url = page.url
    while monotonic() < deadline:
        current_url = page.url
        if not needs_reauthentication(current_url):
            try:
                page.wait_for_load_state("domcontentloaded", timeout=5_000)
            except Exception:
                pass
            return page.url
        page.wait_for_timeout(1_000)
    return current_url


def browser_auth_status(
    *,
    repo_root: str | Path | None = None,
    storage_state_path: str = "",
    evidence_dir: str = "",
) -> dict[str, Any]:
    config = bootstrap_config(
        repo_root=repo_root,
        storage_state_path=storage_state_path,
        evidence_dir=evidence_dir,
    )
    state_exists = config.storage_state_path.is_file()
    return {
        "target_url": config.target_url,
        "storage_state_path": str(config.storage_state_path),
        "storage_state_exists": state_exists,
        "storage_state_size": config.storage_state_path.stat().st_size if state_exists else 0,
        "evidence_dir": str(config.evidence_dir),
        "evidence_dir_exists": config.evidence_dir.is_dir(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_bootstrap_result(
    config: BrowserAuthBootstrapConfig,
    *,
    status: str,
    current_url: str,
    screenshots: list[str],
    detail: str,
) -> dict[str, Any]:
    payload = {
        "status": status,
        "target_url": config.target_url,
        "current_url": current_url,
        "storage_state_path": str(config.storage_state_path),
        "screenshots": screenshots,
        "detail": detail,
        "updated_at_utc": now_utc_iso(),
    }
    write_json(config.evidence_dir / "result.json", payload)
    return payload


def bootstrap_browser_auth(
    *,
    repo_root: str | Path | None = None,
    storage_state_path: str = "",
    evidence_dir: str = "",
    target_url: str = "",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    browser_name: str = "chromium",
    prompt_callback: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    config = bootstrap_config(
        repo_root=repo_root,
        storage_state_path=storage_state_path,
        evidence_dir=evidence_dir,
        target_url=target_url,
        timeout_seconds=timeout_seconds,
        browser_name=browser_name,
    )
    config.evidence_dir.mkdir(parents=True, exist_ok=True)
    config.storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depende do ambiente local
        raise AtlassianBrowserAuthError(
            "Playwright nao esta disponivel. Instale via `uv add playwright`."
        ) from exc

    prompt = prompt_callback or input
    screenshots: list[str] = []
    current_url = ""
    with sync_playwright() as playwright:
        browser_launcher = getattr(playwright, config.browser_name, None)
        if browser_launcher is None:
            raise AtlassianBrowserAuthError(
                f"Navegador Playwright nao suportado: {config.browser_name}"
            )
        browser = browser_launcher.launch(headless=False)
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(
                config.target_url,
                wait_until="domcontentloaded",
                timeout=config.timeout_seconds * 1000,
            )
            initial_path = config.evidence_dir / "00-login-inicial.png"
            page.screenshot(path=str(initial_path), full_page=True)
            screenshots.append(str(initial_path))
            for attempt in range(1, MAX_MANUAL_CONFIRMATIONS + 1):
                prompt(
                    "Conclua o login Atlassian e aguarde abrir Jira ou Confluence no navegador. "
                    f"Quando a UI final aparecer, pressione ENTER para salvar o storageState "
                    f"(tentativa {attempt}/{MAX_MANUAL_CONFIRMATIONS})."
                )
                current_url = wait_for_authenticated_navigation(page, config.timeout_seconds)
                if not needs_reauthentication(current_url):
                    break
                pending_path = config.evidence_dir / f"00-login-pendente-{attempt}.png"
                page.screenshot(path=str(pending_path), full_page=True)
                screenshots.append(str(pending_path))
            if needs_reauthentication(current_url):
                return save_bootstrap_result(
                    config,
                    status="REAUTENTICACAO_NECESSARIA",
                    current_url=current_url,
                    screenshots=screenshots,
                    detail=(
                        "A sessao nao saiu do fluxo de autenticacao Atlassian. "
                        "Confirme que a navegacao chegou a Jira ou Confluence antes de pressionar ENTER, "
                        "ou rerode com TIMEOUT_SECONDS maior."
                    ),
                )
            success_path = config.evidence_dir / "00-login-concluido.png"
            page.screenshot(path=str(success_path), full_page=True)
            screenshots.append(str(success_path))
            context.storage_state(path=str(config.storage_state_path))
            return save_bootstrap_result(
                config,
                status="PASS",
                current_url=current_url,
                screenshots=screenshots,
                detail="Sessao autenticada persistida com sucesso para reuso do browser validator.",
            )
        finally:
            browser.close()


def page_host(url: str) -> str:
    return urlparse(url).netloc.strip().lower()
