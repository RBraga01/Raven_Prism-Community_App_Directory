"""Static GitHub Pages publishing, accessibility and safe-link safeguards."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(value for key, value in attrs if key == "href")


class PublicWebsiteTests(unittest.TestCase):
    def test_navigation_links_are_safe_and_work_with_pages_path(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        parser = Links()
        parser.feed(html)
        self.assertGreaterEqual(len(parser.hrefs), 8)
        for url in parser.hrefs:
            with self.subTest(url=url):
                if url.startswith("#"):
                    self.assertIn('id="' + url[1:] + '"', html)
                    continue
                if url == "./":
                    continue
                parts = urlsplit(url)
                self.assertEqual(parts.scheme, "https")
                self.assertIn(parts.hostname,
                              {"github.com", "raw.githubusercontent.com", "docs.google.com"})

    def test_untrusted_catalog_is_rendered_as_text_and_external_links_are_safe(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        script = (ROOT / "docs/app.mjs").read_text(encoding="utf-8")
        self.assertIn("textContent", script)
        self.assertNotIn("innerHTML", html + script)
        self.assertNotIn("outerHTML", html + script)
        self.assertIn('a.rel = "noopener noreferrer"', script)
        self.assertIn('parsed.protocol !== "https:"', script)
        self.assertIn('type="module" src="./app.mjs"', html)

    def test_public_site_data_mirrors_approved_json(self):
        source = json.loads((ROOT / "data/apps.json").read_text(encoding="utf-8"))
        generated = json.loads((ROOT / "docs/apps.json").read_text(encoding="utf-8"))
        self.assertEqual(source, generated)

    def test_accessible_controls_exist(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        for label_target in ("search", "category-filter", "availability-filter",
                             "sort-filter", "demo-filter"):
            self.assertIn('for="' + label_target + '"', html)
            self.assertIn('id="' + label_target + '"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('aria-busy="true"', html)
        self.assertIn('href="#directory"', html)

    def test_external_dependencies_and_tracking_are_not_loaded(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertNotIn("<iframe", html)
        self.assertNotIn("https://cdn.", html)
        self.assertNotIn("analytics.js", html)
        self.assertIn('src="./app.mjs"', html)


if __name__ == "__main__":
    unittest.main()
