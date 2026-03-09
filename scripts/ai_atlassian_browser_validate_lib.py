from __future__ import annotations

import json
from time import monotonic
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.ai_atlassian_browser_auth_lib import (
    DEFAULT_STORAGE_STATE_PATH,
    AtlassianBrowserAuthError,
    needs_reauthentication,
    now_utc_iso,
)
from scripts.ai_control_plane_lib import resolve_repo_root

DEFAULT_VALIDATE_EVIDENCE_DIR = Path(".cache/playwright/atlassian/validation")
DEFAULT_VALIDATE_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class BrowserValidationConfig:
    target_url: str
    storage_state_path: Path
    evidence_dir: Path
    expected_title_contains: str
    expected_texts: tuple[str, ...]
    timeout_seconds: int
    browser_name: str
    headless: bool


class AtlassianBrowserValidationError(AtlassianBrowserAuthError):
    """Raised when browser validation cannot proceed."""


def evaluate_title_check(
    expected_title_contains: str,
    *,
    title: str,
    body_text: str,
) -> tuple[bool, str]:
    normalized_expected = expected_title_contains.strip().casefold()
    if not normalized_expected:
        return True, "disabled"
    if normalized_expected in title.casefold():
        return True, "title"
    if normalized_expected in body_text.casefold():
        return True, "body-fallback"
    return False, "missing"


def evaluate_expected_text_checks(
    expected_texts: tuple[str, ...],
    *,
    title: str,
    body_text: str,
) -> dict[str, bool]:
    normalized_title = title.casefold()
    normalized_body = body_text.casefold()
    return {
        text: text.casefold() in normalized_body or text.casefold() in normalized_title
        for text in expected_texts
    }


def collect_body_text_with_scroll(page: Any) -> str:
    body = page.locator("body")
    text = body.inner_text()
    total_height = int(
        page.evaluate(
            "() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
        )
        or 0
    )
    viewport_height = 900
    try:
        viewport = page.viewport_size or {}
        viewport_height = int(viewport.get("height") or viewport_height)
    except Exception:
        viewport_height = 900
    step = max(500, int(viewport_height * 0.85))
    position = 0
    while position < total_height:
        page.evaluate("(y) => window.scrollTo(0, y)", position)
        page.wait_for_timeout(200)
        position += step
        total_height = int(
            page.evaluate(
                "() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
            )
            or total_height
        )
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(150)
    return body.inner_text()


def validation_config(
    *,
    repo_root: str | Path | None = None,
    target_url: str,
    storage_state_path: str = "",
    evidence_dir: str = "",
    expected_title_contains: str = "",
    expected_texts: list[str] | None = None,
    timeout_seconds: int = DEFAULT_VALIDATE_TIMEOUT_SECONDS,
    browser_name: str = "chromium",
    headless: bool = True,
) -> BrowserValidationConfig:
    resolved_repo_root = resolve_repo_root(repo_root)
    chosen_storage = (
        (resolved_repo_root / Path(storage_state_path)).resolve()
        if storage_state_path.strip()
        else (resolved_repo_root / DEFAULT_STORAGE_STATE_PATH).resolve()
    )
    chosen_evidence = (
        (resolved_repo_root / Path(evidence_dir)).resolve()
        if evidence_dir.strip()
        else (resolved_repo_root / DEFAULT_VALIDATE_EVIDENCE_DIR).resolve()
    )
    return BrowserValidationConfig(
        target_url=target_url.strip(),
        storage_state_path=chosen_storage,
        evidence_dir=chosen_evidence,
        expected_title_contains=expected_title_contains.strip(),
        expected_texts=tuple(
            text.strip() for text in (expected_texts or []) if text and text.strip()
        ),
        timeout_seconds=max(5, timeout_seconds),
        browser_name=(browser_name or "chromium").strip().lower(),
        headless=bool(headless),
    )


def write_validation_result(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_browser_page(
    *,
    repo_root: str | Path | None = None,
    target_url: str,
    storage_state_path: str = "",
    evidence_dir: str = "",
    expected_title_contains: str = "",
    expected_texts: list[str] | None = None,
    timeout_seconds: int = DEFAULT_VALIDATE_TIMEOUT_SECONDS,
    browser_name: str = "chromium",
    headless: bool = True,
) -> dict[str, Any]:
    config = validation_config(
        repo_root=repo_root,
        target_url=target_url,
        storage_state_path=storage_state_path,
        evidence_dir=evidence_dir,
        expected_title_contains=expected_title_contains,
        expected_texts=expected_texts,
        timeout_seconds=timeout_seconds,
        browser_name=browser_name,
        headless=headless,
    )
    if not config.storage_state_path.is_file():
        raise AtlassianBrowserValidationError(
            "storageState Atlassian nao encontrado. Rode task ai:atlassian:browser:auth:bootstrap primeiro."
        )

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depende do ambiente local
        raise AtlassianBrowserValidationError(
            "Playwright nao esta disponivel. Instale via `uv add playwright`."
        ) from exc

    config.evidence_dir.mkdir(parents=True, exist_ok=True)
    screenshots: list[str] = []
    html_path = config.evidence_dir / "page.html"
    with sync_playwright() as playwright:
        browser_launcher = getattr(playwright, config.browser_name, None)
        if browser_launcher is None:
            raise AtlassianBrowserValidationError(
                f"Navegador Playwright nao suportado: {config.browser_name}"
            )
        browser = browser_launcher.launch(headless=config.headless)
        try:
            context = browser.new_context(storage_state=str(config.storage_state_path))
            page = context.new_page()
            page.goto(
                config.target_url,
                wait_until="domcontentloaded",
                timeout=config.timeout_seconds * 1000,
            )
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception:
                pass
            current_url = page.url
            first_screenshot = config.evidence_dir / "01-page-opened.png"
            page.screenshot(path=str(first_screenshot), full_page=False)
            screenshots.append(str(first_screenshot))
            html_path.write_text(page.content(), encoding="utf-8")
            if needs_reauthentication(current_url):
                payload = {
                    "status": "REAUTENTICACAO_NECESSARIA",
                    "target_url": config.target_url,
                    "current_url": current_url,
                    "expected_title_contains": config.expected_title_contains,
                    "expected_texts": list(config.expected_texts),
                    "title": page.title(),
                    "checks": {
                        "authenticated": False,
                        "title_ok": False,
                        "expected_texts_ok": False,
                    },
                    "screenshots": screenshots,
                    "html_path": str(html_path),
                    "updated_at_utc": now_utc_iso(),
                }
                write_validation_result(config.evidence_dir / "result.json", payload)
                return payload

            title = page.title()
            deadline = monotonic() + max(5, config.timeout_seconds)
            body_text = ""
            text_checks: dict[str, bool] = {}
            while True:
                body_text = collect_body_text_with_scroll(page)
                text_checks = evaluate_expected_text_checks(
                    config.expected_texts,
                    title=title,
                    body_text=body_text,
                )
                if all(text_checks.values()) or monotonic() >= deadline:
                    break
                page.wait_for_timeout(1_500)
                page.reload(
                    wait_until="domcontentloaded",
                    timeout=config.timeout_seconds * 1000,
                )
                try:
                    page.wait_for_load_state("networkidle", timeout=15_000)
                except Exception:
                    pass
                title = page.title()
            full_screenshot = config.evidence_dir / "02-full-page.png"
            page.screenshot(path=str(full_screenshot), full_page=True)
            screenshots.append(str(full_screenshot))
            title_ok, title_match_mode = evaluate_title_check(
                config.expected_title_contains,
                title=title,
                body_text=body_text,
            )
            expected_texts_ok = all(text_checks.values())
            status = "PASS" if title_ok and expected_texts_ok else "FAIL"
            payload = {
                "status": status,
                "target_url": config.target_url,
                "current_url": current_url,
                "expected_title_contains": config.expected_title_contains,
                "expected_texts": list(config.expected_texts),
                "title": title,
                "checks": {
                    "authenticated": True,
                    "title_ok": title_ok,
                    "title_match_mode": title_match_mode,
                    "expected_texts_ok": expected_texts_ok,
                    "text_checks": text_checks,
                },
                "screenshots": screenshots,
                "html_path": str(html_path),
                "updated_at_utc": now_utc_iso(),
            }
            write_validation_result(config.evidence_dir / "result.json", payload)
            return payload
        finally:
            browser.close()
