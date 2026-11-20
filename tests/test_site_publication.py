"""Static GitHub Pages publishing safeguards."""
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
    def test_footer_links_work_when_docs_is_pages_root(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        parser = Links()
        parser.feed(html)
        self.assertGreaterEqual(len(parser.hrefs), 4)
        for url in parser.hrefs:
            with self.subTest(url=url):
                parts = urlsplit(url)
                self.assertEqual(parts.scheme, "https")
                self.assertIn(parts.hostname,
                              {"github.com", "raw.githubusercontent.com"})

    def test_untrusted_catalog_content_is_text_not_html(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertIn("textContent", html)
        self.assertNotIn("innerHTML", html)
        self.assertIn('a.rel="noopener noreferrer"', html)

    def test_public_site_data_mirrors_approved_json(self):
        source = json.loads((ROOT / "data/apps.json").read_text(encoding="utf-8"))
        generated = json.loads((ROOT / "docs/apps.json").read_text(encoding="utf-8"))
        self.assertEqual(source, generated)


if __name__ == "__main__":
    unittest.main()
