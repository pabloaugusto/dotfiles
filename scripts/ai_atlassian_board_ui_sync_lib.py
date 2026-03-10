from __future__ import annotations

import json
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

DEFAULT_BOARD_UI_SYNC_EVIDENCE_DIR = Path(".cache/playwright/atlassian/board-sync")
DEFAULT_BOARD_UI_SYNC_TIMEOUT_SECONDS = 90


@dataclass(frozen=True)
class ColumnRename:
    current_name: str
    desired_name: str


@dataclass(frozen=True)
class StatusColumnMapping:
    status_name: str
    column_name: str


@dataclass(frozen=True)
class BoardUiSyncConfig:
    settings_url: str
    storage_state_path: Path
    evidence_dir: Path
    rename_columns: tuple[ColumnRename, ...]
    add_columns: tuple[str, ...]
    card_fields: tuple[str, ...]
    remove_statuses: tuple[str, ...]
    map_statuses: tuple[StatusColumnMapping, ...]
    timeout_seconds: int
    browser_name: str
    headless: bool


class AtlassianBoardUiSyncError(AtlassianBrowserAuthError):
    """Raised when the Jira board UI cannot be synchronized."""


def parse_rename_columns(raw_values: list[str] | None) -> tuple[ColumnRename, ...]:
    mappings: list[ColumnRename] = []
    for raw_value in raw_values or []:
        normalized = str(raw_value).strip()
        if not normalized:
            continue
        if "=" not in normalized:
            raise AtlassianBoardUiSyncError(
                f"rename-column invalido: {normalized!r}. Use o formato atual=novo."
            )
        current_name, desired_name = (part.strip() for part in normalized.split("=", 1))
        if not current_name or not desired_name:
            raise AtlassianBoardUiSyncError(
                f"rename-column invalido: {normalized!r}. Ambos os lados precisam de valor."
            )
        mappings.append(ColumnRename(current_name=current_name, desired_name=desired_name))
    return tuple(mappings)


def parse_add_columns(raw_values: list[str] | None) -> tuple[str, ...]:
    return tuple(
        str(raw_value).strip() for raw_value in (raw_values or []) if str(raw_value).strip()
    )


def parse_card_fields(raw_values: list[str] | None) -> tuple[str, ...]:
    return tuple(
        str(raw_value).strip() for raw_value in (raw_values or []) if str(raw_value).strip()
    )


def parse_map_statuses(raw_values: list[str] | None) -> tuple[StatusColumnMapping, ...]:
    mappings: list[StatusColumnMapping] = []
    for raw_value in raw_values or []:
        normalized = str(raw_value).strip()
        if not normalized:
            continue
        if "=" not in normalized:
            raise AtlassianBoardUiSyncError(
                f"map-status invalido: {normalized!r}. Use o formato status=coluna."
            )
        status_name, column_name = (part.strip() for part in normalized.split("=", 1))
        if not status_name or not column_name:
            raise AtlassianBoardUiSyncError(
                f"map-status invalido: {normalized!r}. Ambos os lados precisam de valor."
            )
        mappings.append(StatusColumnMapping(status_name=status_name, column_name=column_name))
    return tuple(mappings)


def board_ui_sync_config(
    *,
    repo_root: str | Path | None = None,
    settings_url: str,
    storage_state_path: str = "",
    evidence_dir: str = "",
    rename_columns: list[str] | None = None,
    add_columns: list[str] | None = None,
    card_fields: list[str] | None = None,
    remove_statuses: list[str] | None = None,
    map_statuses: list[str] | None = None,
    timeout_seconds: int = DEFAULT_BOARD_UI_SYNC_TIMEOUT_SECONDS,
    browser_name: str = "chromium",
    headless: bool = True,
) -> BoardUiSyncConfig:
    resolved_repo_root = resolve_repo_root(repo_root)
    chosen_storage = (
        (resolved_repo_root / Path(storage_state_path)).resolve()
        if storage_state_path.strip()
        else (resolved_repo_root / DEFAULT_STORAGE_STATE_PATH).resolve()
    )
    chosen_evidence = (
        (resolved_repo_root / Path(evidence_dir)).resolve()
        if evidence_dir.strip()
        else (resolved_repo_root / DEFAULT_BOARD_UI_SYNC_EVIDENCE_DIR).resolve()
    )
    return BoardUiSyncConfig(
        settings_url=settings_url.strip(),
        storage_state_path=chosen_storage,
        evidence_dir=chosen_evidence,
        rename_columns=parse_rename_columns(rename_columns),
        add_columns=parse_add_columns(add_columns),
        card_fields=parse_card_fields(card_fields),
        remove_statuses=tuple(
            entry.strip() for entry in (remove_statuses or []) if str(entry).strip()
        ),
        map_statuses=parse_map_statuses(map_statuses),
        timeout_seconds=max(5, timeout_seconds),
        browser_name=(browser_name or "chromium").strip().lower(),
        headless=bool(headless),
    )


def write_board_ui_sync_result(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _rename_column(page: Any, current_name: str, desired_name: str) -> bool:
    if current_name == desired_name:
        return False
    title_locator = page.locator('span[data-testid="column.header.title.data.test.id"]')
    title_match = title_locator.filter(has_text=current_name)
    if title_match.count() < 1:
        return False
    title_match.first.click()
    page.wait_for_timeout(300)
    target_input = None
    for candidate in page.locator("input").all():
        try:
            if candidate.input_value().strip() == current_name:
                target_input = candidate
                break
        except Exception:
            continue
    if target_input is None:
        return False
    target_input.fill(desired_name)
    target_input.press("Enter")
    page.wait_for_timeout(500)
    page.get_by_text(desired_name, exact=True).first.wait_for(timeout=10_000)
    return True


def _remove_status_from_board(page: Any, status_name: str) -> bool:
    card = page.locator(
        f'[aria-label="Card {status_name} can be moved. Press the space bar to grab it."]'
    )
    if card.count() < 1:
        return False
    unmapped_dropzone = page.locator('[data-rbd-droppable-id="COLUMN::0"]').first
    card.first.scroll_into_view_if_needed()
    unmapped_dropzone.scroll_into_view_if_needed()
    card_box = card.first.bounding_box()
    target_box = unmapped_dropzone.bounding_box()
    if card_box is None or target_box is None:
        return False
    page.mouse.move(
        card_box["x"] + (card_box["width"] / 2),
        card_box["y"] + (card_box["height"] / 2),
    )
    page.mouse.down()
    page.mouse.move(
        target_box["x"] + (target_box["width"] / 2),
        target_box["y"] + min(target_box["height"] / 2, 120),
        steps=20,
    )
    page.mouse.up()
    page.wait_for_timeout(500)
    if card.count() > 0:
        page.wait_for_timeout(1_000)
    return card.count() == 0


def _column_exists(page: Any, column_name: str) -> bool:
    expected = column_name.strip().casefold()
    for text in page.locator(
        'span[data-testid="column.header.title.data.test.id"]'
    ).all_inner_texts():
        if " ".join(text.split()).casefold() == expected:
            return True
    return False


def _add_column(page: Any, column_name: str) -> bool:
    if _column_exists(page, column_name):
        return False
    page.get_by_label("Create column").click()
    page.wait_for_timeout(300)
    input_locator = page.get_by_label("Add column name")
    input_locator.wait_for(timeout=10_000)
    input_locator.fill(column_name)
    page.get_by_role("button", name="Confirm").click()
    page.wait_for_timeout(800)
    return _column_exists(page, column_name)


def _column_dropzone(page: Any, column_name: str) -> Any | None:
    expected = column_name.strip().casefold()
    wrappers = page.locator('div[data-testid="column-wrapper.data.test.id"]')
    for index in range(wrappers.count()):
        wrapper = wrappers.nth(index)
        announced = str(wrapper.get_attribute("data-announced-column-header") or "").strip()
        if announced.casefold() == expected:
            return wrapper
    return None


def _map_status_to_column(page: Any, status_name: str, column_name: str) -> bool:
    selector = f'[aria-label="Card {status_name} can be moved. Press the space bar to grab it."]'
    card = page.locator(selector)
    if card.count() < 1:
        return False
    target = _column_dropzone(page, column_name)
    if target is None:
        return False
    card.first.scroll_into_view_if_needed()
    target.scroll_into_view_if_needed()
    card_box = card.first.bounding_box()
    target_box = target.bounding_box()
    if card_box is None or target_box is None:
        return False
    page.mouse.move(
        card_box["x"] + (card_box["width"] / 2),
        card_box["y"] + (card_box["height"] / 2),
    )
    page.mouse.down()
    page.mouse.move(
        target_box["x"] + (target_box["width"] / 2),
        target_box["y"] + min(target_box["height"] / 2, 180),
        steps=20,
    )
    page.mouse.up()
    page.wait_for_timeout(800)
    return target.locator(selector).count() > 0


def _collect_board_snapshot(page: Any) -> dict[str, Any]:
    column_titles = [
        " ".join(text.split())
        for text in page.locator(
            'span[data-testid="column.header.title.data.test.id"]'
        ).all_inner_texts()
        if text and text.strip()
    ]
    warning_count = page.locator(
        '[data-testid="colum.status.invalid-warning.data.test.id--button"]'
    ).count()
    body_text = page.locator("body").inner_text()
    return {
        "column_titles": column_titles,
        "warning_count": warning_count,
        "body_excerpt": body_text.replace("\ufeff", "")[:2000],
    }


def board_card_layout_url(settings_url: str) -> str:
    marker = "/settings/"
    if marker not in settings_url:
        raise AtlassianBoardUiSyncError(
            f"settings_url invalida para derivar o card layout: {settings_url!r}."
        )
    prefix, _, suffix = settings_url.partition(marker)
    query = ""
    if "?" in suffix:
        _, _, raw_query = suffix.partition("?")
        query = f"?{raw_query}" if raw_query else ""
    return f"{prefix}{marker}cardLayout{query}"


def _card_layout_field_names(page: Any) -> tuple[str, ...]:
    body_text = page.locator("body").inner_text().replace("\ufeff", "")
    marker = "Add up to three fields."
    if marker not in body_text:
        return ()
    _, _, tail = body_text.partition(marker)
    candidates: list[str] = []
    for raw_line in tail.splitlines():
        normalized = " ".join(raw_line.split())
        if not normalized or normalized in {
            "Name Actions",
            "Add field",
            "Cancel",
            "Save",
            "Delete",
        }:
            continue
        if normalized.startswith("Track how long"):
            break
        candidates.append(normalized)
    return tuple(dict.fromkeys(candidates))


def _ensure_card_field(page: Any, field_name: str) -> bool:
    normalized_target = " ".join(field_name.split()).casefold()
    existing_names = _card_layout_field_names(page)
    existing = {name.casefold() for name in existing_names}
    if normalized_target in existing:
        return False
    if len(existing_names) >= 3:
        raise AtlassianBoardUiSyncError(
            f"Card layout do board ja usa tres campos e nao tem vaga para adicionar {field_name!r}."
        )
    page.get_by_test_id(
        "software-board-settings-card-layout.ui.card-layout-settings-page.card-layout-table.add-field.button"
    ).click()
    page.wait_for_timeout(700)
    combo = page.get_by_role("combobox", name="Field name")
    combo.click()
    combo.fill(field_name)
    page.wait_for_timeout(800)
    option = page.get_by_role("option", name=field_name).first
    option.wait_for(timeout=10_000)
    option.click()
    page.get_by_test_id(
        "software-board-settings-card-layout.ui.card-layout-settings-page.card-layout-table.add-field.submit"
    ).click()
    page.wait_for_timeout(1_500)
    updated = {name.casefold() for name in _card_layout_field_names(page)}
    return normalized_target in updated


def sync_jira_board_ui(
    *,
    repo_root: str | Path | None = None,
    settings_url: str,
    storage_state_path: str = "",
    evidence_dir: str = "",
    rename_columns: list[str] | None = None,
    add_columns: list[str] | None = None,
    card_fields: list[str] | None = None,
    remove_statuses: list[str] | None = None,
    map_statuses: list[str] | None = None,
    timeout_seconds: int = DEFAULT_BOARD_UI_SYNC_TIMEOUT_SECONDS,
    browser_name: str = "chromium",
    headless: bool = True,
) -> dict[str, Any]:
    config = board_ui_sync_config(
        repo_root=repo_root,
        settings_url=settings_url,
        storage_state_path=storage_state_path,
        evidence_dir=evidence_dir,
        rename_columns=rename_columns,
        add_columns=add_columns,
        card_fields=card_fields,
        remove_statuses=remove_statuses,
        map_statuses=map_statuses,
        timeout_seconds=timeout_seconds,
        browser_name=browser_name,
        headless=headless,
    )
    if not config.storage_state_path.is_file():
        raise AtlassianBoardUiSyncError(
            "storageState Atlassian nao encontrado. Rode task ai:atlassian:browser:auth:bootstrap primeiro."
        )

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depende do ambiente local
        raise AtlassianBoardUiSyncError(
            "Playwright nao esta disponivel. Instale via `uv add playwright`."
        ) from exc

    config.evidence_dir.mkdir(parents=True, exist_ok=True)
    screenshots: list[str] = []
    html_path = config.evidence_dir / "page.html"
    result_path = config.evidence_dir / "result.json"

    with sync_playwright() as playwright:
        browser_launcher = getattr(playwright, config.browser_name, None)
        if browser_launcher is None:
            raise AtlassianBoardUiSyncError(
                f"Navegador Playwright nao suportado: {config.browser_name}"
            )
        browser = browser_launcher.launch(headless=config.headless)
        try:
            context = browser.new_context(
                storage_state=str(config.storage_state_path),
                viewport={"width": 1600, "height": 1200},
            )
            page = context.new_page()
            page.goto(
                config.settings_url,
                wait_until="domcontentloaded",
                timeout=config.timeout_seconds * 1000,
            )
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception:
                pass
            if needs_reauthentication(page.url):
                payload = {
                    "status": "REAUTENTICACAO_NECESSARIA",
                    "settings_url": config.settings_url,
                    "current_url": page.url,
                    "rename_columns": [
                        {"current_name": entry.current_name, "desired_name": entry.desired_name}
                        for entry in config.rename_columns
                    ],
                    "add_columns": list(config.add_columns),
                    "card_fields": list(config.card_fields),
                    "remove_statuses": list(config.remove_statuses),
                    "map_statuses": [
                        {"status_name": entry.status_name, "column_name": entry.column_name}
                        for entry in config.map_statuses
                    ],
                    "updated_at_utc": now_utc_iso(),
                }
                write_board_ui_sync_result(result_path, payload)
                return payload

            before_screenshot = config.evidence_dir / "01-before-sync.png"
            page.screenshot(path=str(before_screenshot), full_page=True)
            screenshots.append(str(before_screenshot))
            before_snapshot = _collect_board_snapshot(page)

            added_columns: list[str] = []
            missing_new_columns: list[str] = []
            for column_name in config.add_columns:
                if _add_column(page, column_name):
                    added_columns.append(column_name)
                elif _column_exists(page, column_name):
                    continue
                else:
                    missing_new_columns.append(column_name)

            removed_statuses: list[str] = []
            missing_statuses: list[str] = []
            for status_name in config.remove_statuses:
                if _remove_status_from_board(page, status_name):
                    removed_statuses.append(status_name)
                else:
                    missing_statuses.append(status_name)

            renamed_columns: list[dict[str, str]] = []
            missing_columns: list[str] = []
            for entry in config.rename_columns:
                if _rename_column(page, entry.current_name, entry.desired_name):
                    renamed_columns.append(
                        {
                            "current_name": entry.current_name,
                            "desired_name": entry.desired_name,
                        }
                    )
                else:
                    missing_columns.append(entry.current_name)

            mapped_statuses: list[dict[str, str]] = []
            missing_status_mappings: list[dict[str, str]] = []
            for entry in config.map_statuses:
                if _map_status_to_column(page, entry.status_name, entry.column_name):
                    mapped_statuses.append(
                        {
                            "status_name": entry.status_name,
                            "column_name": entry.column_name,
                        }
                    )
                else:
                    missing_status_mappings.append(
                        {
                            "status_name": entry.status_name,
                            "column_name": entry.column_name,
                        }
                    )

            added_card_fields: list[str] = []
            card_layout_snapshot: dict[str, Any] = {}
            if config.card_fields:
                card_layout_url = board_card_layout_url(config.settings_url)
                page.goto(
                    card_layout_url,
                    wait_until="domcontentloaded",
                    timeout=config.timeout_seconds * 1000,
                )
                try:
                    page.wait_for_load_state("networkidle", timeout=10_000)
                except Exception:
                    pass
                if needs_reauthentication(page.url):
                    payload = {
                        "status": "REAUTENTICACAO_NECESSARIA",
                        "settings_url": card_layout_url,
                        "current_url": page.url,
                        "card_fields": list(config.card_fields),
                        "updated_at_utc": now_utc_iso(),
                    }
                    write_board_ui_sync_result(result_path, payload)
                    return payload
                card_before = config.evidence_dir / "03-card-layout-before-sync.png"
                page.screenshot(path=str(card_before), full_page=True)
                screenshots.append(str(card_before))
                for field_name in config.card_fields:
                    if _ensure_card_field(page, field_name):
                        added_card_fields.append(field_name)
                card_after = config.evidence_dir / "04-card-layout-after-sync.png"
                page.screenshot(path=str(card_after), full_page=True)
                screenshots.append(str(card_after))
                card_layout_snapshot = {
                    "url": page.url,
                    "field_names": list(_card_layout_field_names(page)),
                }

            try:
                page.wait_for_load_state("networkidle", timeout=10_000)
            except Exception:
                pass
            after_screenshot = config.evidence_dir / "02-after-sync.png"
            page.screenshot(path=str(after_screenshot), full_page=True)
            screenshots.append(str(after_screenshot))
            html_path.write_text(page.content(), encoding="utf-8")
            after_snapshot = _collect_board_snapshot(page)

            payload = {
                "status": "PASS",
                "settings_url": config.settings_url,
                "current_url": page.url,
                "rename_columns": [
                    {"current_name": entry.current_name, "desired_name": entry.desired_name}
                    for entry in config.rename_columns
                ],
                "add_columns": list(config.add_columns),
                "card_fields": list(config.card_fields),
                "remove_statuses": list(config.remove_statuses),
                "map_statuses": [
                    {"status_name": entry.status_name, "column_name": entry.column_name}
                    for entry in config.map_statuses
                ],
                "added_columns": added_columns,
                "missing_new_columns": missing_new_columns,
                "renamed_columns": renamed_columns,
                "missing_columns": missing_columns,
                "removed_statuses": removed_statuses,
                "missing_statuses": missing_statuses,
                "mapped_statuses": mapped_statuses,
                "missing_status_mappings": missing_status_mappings,
                "added_card_fields": added_card_fields,
                "card_layout_snapshot": card_layout_snapshot,
                "before": before_snapshot,
                "after": after_snapshot,
                "screenshots": screenshots,
                "html_path": str(html_path),
                "updated_at_utc": now_utc_iso(),
            }
            write_board_ui_sync_result(result_path, payload)
            return payload
        finally:
            browser.close()
