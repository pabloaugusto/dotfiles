from __future__ import annotations

import unittest

from scripts.ai_atlassian_board_ui_sync_lib import (
    AtlassianBoardUiSyncError,
    ColumnRename,
    StatusColumnMapping,
    board_card_layout_url,
    parse_add_columns,
    parse_card_fields,
    parse_map_statuses,
    parse_rename_columns,
)


class ParseRenameColumnsTest(unittest.TestCase):
    def test_parse_rename_columns_accepts_valid_pairs(self) -> None:
        self.assertEqual(
            parse_rename_columns(["Selected for Development=Ready", "In Progress=Doing"]),
            (
                ColumnRename("Selected for Development", "Ready"),
                ColumnRename("In Progress", "Doing"),
            ),
        )

    def test_parse_rename_columns_rejects_invalid_mapping(self) -> None:
        with self.assertRaises(AtlassianBoardUiSyncError):
            parse_rename_columns(["Selected for Development"])

    def test_parse_rename_columns_rejects_empty_side(self) -> None:
        with self.assertRaises(AtlassianBoardUiSyncError):
            parse_rename_columns(["Selected for Development="])

    def test_parse_add_columns_accepts_non_empty_values(self) -> None:
        self.assertEqual(parse_add_columns(["Paused", "", "Review"]), ("Paused", "Review"))

    def test_parse_card_fields_accepts_non_empty_values(self) -> None:
        self.assertEqual(
            parse_card_fields(["Current Agent Role", "", "Next Required Role"]),
            ("Current Agent Role", "Next Required Role"),
        )

    def test_parse_map_statuses_accepts_valid_pairs(self) -> None:
        self.assertEqual(
            parse_map_statuses(["PAUSED=Paused"]),
            (StatusColumnMapping("PAUSED", "Paused"),),
        )

    def test_parse_map_statuses_rejects_invalid_mapping(self) -> None:
        with self.assertRaises(AtlassianBoardUiSyncError):
            parse_map_statuses(["PAUSED"])

    def test_board_card_layout_url_preserves_query(self) -> None:
        self.assertEqual(
            board_card_layout_url(
                "https://example.atlassian.net/jira/software/c/projects/DOT/boards/6/settings/columns?config=filter"
            ),
            "https://example.atlassian.net/jira/software/c/projects/DOT/boards/6/settings/cardLayout?config=filter",
        )

    def test_board_card_layout_url_rejects_invalid_url(self) -> None:
        with self.assertRaises(AtlassianBoardUiSyncError):
            board_card_layout_url(
                "https://example.atlassian.net/jira/software/c/projects/DOT/boards/6"
            )


if __name__ == "__main__":
    unittest.main()
