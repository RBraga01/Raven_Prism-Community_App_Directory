"""Adversarial public-input and generated Markdown regression tests."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from catalog_lib import (  # noqa: E402
    load_apps, markdown_text, render_markdown_table, validate_apps,
    verify_url, SOURCE_HOSTS,
)


class CatalogSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.apps = load_apps(ROOT / "data/apps.json")

    def altered(self, **changes):
        records = copy.deepcopy(self.apps)
        records[0].update(changes)
        return records

    def test_real_catalog_has_unique_ids_and_names(self):
        self.assertEqual(len(self.apps),
                         len({a["id"] for a in self.apps}))

    def test_pipe_and_link_syntax_are_escaped(self):
        label = "Bird | [spoof](https://evil.example)"
        escaped = markdown_text(label)
        self.assertIn(r"\|", escaped)
        self.assertIn(r"\[spoof\]", escaped)
        self.assertIn(r"\]", escaped)
        table = render_markdown_table(self.altered(name=label))
        self.assertIn(r"Bird \| \[spoof\]", table)

    def test_control_characters_rejected(self):
        for label in ("Bad\nName", "Bad\tName", "Spoof\u202ename"):
            with self.subTest(label=repr(label)):
                with self.assertRaises(ValueError):
                    validate_apps(self.altered(name=label), require_order=False)

    def test_spreadsheet_formula_injection_rejected(self):
        for label in ('=HYPERLINK("https://example.com")', "+SUM(A1:A2)", "@A1"):
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    validate_apps(self.altered(name=label), require_order=False)

    def test_host_spoofing_rejected(self):
        invalid = (
            "https://github.com.evil.example/owner/repo",
            "https://github.com@evil.example/owner/repo",
            "http://github.com/owner/repo",
            "https://127.0.0.1/payload",
            "https://github.com:444/owner/repo",
            "https://github.com/evil(redirect)",
        )
        for url in invalid:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    verify_url(url, "source_url", SOURCE_HOSTS)

    def test_duplicate_names_rejected(self):
        records = copy.deepcopy(self.apps)
        records[1]["name"] = records[0]["name"].upper()
        with self.assertRaisesRegex(ValueError, "duplicate name"):
            validate_apps(records, require_order=False)

    def test_unknown_fields_and_secrets_rejected(self):
        with self.assertRaises(ValueError):
            validate_apps(self.altered(private_test="not for publication"),
                          require_order=False)
        with self.assertRaises(ValueError):
            validate_apps(self.altered(description="sk-proj-PLACEHOLDER"),
                          require_order=False)

    def test_source_data_is_alphabetical(self):
        self.assertEqual(
            [a["name"] for a in self.apps],
            sorted((a["name"] for a in self.apps), key=str.casefold),
        )


if __name__ == "__main__":
    unittest.main()
