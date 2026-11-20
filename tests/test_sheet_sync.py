"""Offline tests; no Google account, token or network required."""
import importlib.util
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync_google_sheet.py"
spec = importlib.util.spec_from_file_location("sheet_sync", SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class SheetsMirrorTests(unittest.TestCase):
    def test_catalog_stays_alphabetical(self):
        apps = sync.public_apps()
        self.assertEqual([a["name"] for a in apps],
                         sorted((a["name"] for a in apps), key=str.casefold))

    def test_source_and_demo_are_short_clickable_labels(self):
        sample = {
            "name": "Test App", "category": "Games", "developer": "Author",
            "description": "Test", "source_url": "https://github.com/author/repo",
            "demo_url": "https://youtu.be/example",
            "availability": "Source code",
        }
        row = sync.app_rows([sample])[0]["values"]
        self.assertEqual(row[4]["userEnteredValue"]["stringValue"], "GitHub")
        self.assertEqual(row[4]["userEnteredFormat"]["textFormat"]["link"]["uri"],
                         sample["source_url"])
        self.assertEqual(row[5]["userEnteredValue"]["stringValue"], "Video")

    def test_removed_entries_are_cleared_not_left_behind(self):
        current = [{"values": [sync.linked("A"), sync.linked("B")]}]
        requests = sync.replace_tab(
            100, ["Name", "Other"], current, previous_count=4, grid_rows=200
        )
        update = requests[0]["updateCells"]
        self.assertEqual(update["range"]["endRowIndex"], 5)
        self.assertEqual(len(update["rows"]), 5)
        self.assertEqual(update["rows"][4]["values"][0]["userEnteredValue"]["stringValue"], "")

    def test_unverified_suggestions_are_not_approved_app_rows(self):
        record = {"name": "Candidate", "origin": "Issue",
                  "url": "https://github.com/owner/repo/issues/4"}
        row = sync.suggestion_rows([record])[0]["values"]
        self.assertEqual(row[2]["userEnteredValue"]["stringValue"], "Awaiting review")
        self.assertEqual(row[3]["userEnteredFormat"]["textFormat"]["link"]["uri"],
                         record["url"])

    def test_existing_filter_is_cleared_before_replacing(self):
        records = [{"values": [sync.linked("Test")]}]
        actions = sync.replace_tab(
            100, ["Name"], records, previous_count=1,
            grid_rows=200, has_filter=True,
        )
        self.assertEqual(next(iter(actions[0])), "clearBasicFilter")
        self.assertIn("setBasicFilter", actions[-1])

    def test_no_filter_on_empty_pending_suggestions(self):
        actions = sync.replace_tab(
            100, ["Name"], [], previous_count=0, grid_rows=200,
            has_filter=False,
        )
        self.assertFalse(any("setBasicFilter" in action for action in actions))

    def test_unreviewed_issue_and_pr_titles_are_never_exported(self):
        def fake_get(path, token):
            return {"private": False}

        def fake_list(path, token, maximum_pages=10):
            if "/issues?" in path:
                return [{"number": 8, "title": "[App] PRIVATE TEXT",
                         "labels": []}]
            if "/pulls?" in path:
                return [{"number": 13, "title": "SENSITIVE PR TITLE"}]
            if path.endswith("/pulls/13/files"):
                return [{"filename": "data/apps.json"}]
            return []

        with patch.object(sync, "github_get", side_effect=fake_get), \
             patch.object(sync, "github_list", side_effect=fake_list):
            items = sync.community_suggestions("read-only-token")
        self.assertEqual({x["name"] for x in items}, {"Issue #8", "PR #13"})
        self.assertFalse(any("PRIVATE" in x["name"] or
                             "SENSITIVE" in x["name"] for x in items))

    def test_invalid_link_rejected(self):
        with self.assertRaises(ValueError):
            sync.linked("Bad", "javascript:alert(1)")


if __name__ == "__main__":
    unittest.main()
