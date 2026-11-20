"""Static GitHub Pages publishing, accessibility and safe-link safeguards."""
import json
import re
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
                              {"github.com", "raw.githubusercontent.com", "docs.google.com", "raven.computer"})

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

    def test_design_tokens_use_only_reviewed_four_weights_and_three_radii(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        for token in ("--weight-regular: 400", "--weight-medium: 500",
                      "--weight-semibold: 650", "--weight-bold: 800",
                      "--radius-surface: 16px", "--radius-control: 10px",
                      "--radius-tag: 8px"):
            self.assertIn(token, html)
        self.assertFalse(re.findall(r"font-weight:\s*\d+", html))
        self.assertFalse(re.findall(r"border-radius:\s*\d+px", html))
        self.assertNotIn('style="', html)

    def test_placeholder_and_focus_contrast(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        placeholder = re.search(r'input::placeholder \{ color: (#[0-9a-fA-F]{6})', html)
        focus = re.search(r'--focus: (#[0-9a-fA-F]{6})', html)
        self.assertIsNotNone(placeholder)
        self.assertIsNotNone(focus)

        def luminance(value):
            parts = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            red, green, blue = [
                c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                for c in parts
            ]
            return 0.2126 * red + 0.7152 * green + 0.0722 * blue

        self.assertGreaterEqual(1.05 / (luminance(placeholder.group(1)) + 0.05), 4.5)
        self.assertGreaterEqual(1.05 / (luminance(focus.group(1)) + 0.05), 3.0)
        self.assertIn("outline: 3px solid var(--focus)", html)

    def test_full_bleed_metrics_and_accessible_explainer(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertIn('<main>\n    <section class="metrics-band"', html)
        self.assertIn('<div class="container metrics">', html)
        self.assertIn('<details class="about-prism">', html)
        self.assertIn('<summary>What is Raven Prism?</summary>', html)
        self.assertIn('https://raven.computer/developer', html)
        self.assertIn('class="kicker kicker--tight"', html)
        self.assertIn('class="kicker search-label"', html)

    def test_keyboard_and_touch_search_fallback(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        js = (ROOT / "docs/app.mjs").read_text(encoding="utf-8")
        self.assertIn('<form id="search-form"', html)
        self.assertIn('id="submit-search"', html)
        self.assertIn('type="submit">Search</button>', html)
        self.assertIn('elements.form.addEventListener("submit"', js)
        self.assertIn('event.preventDefault()', js)
        self.assertIn('event.ctrlKey || event.metaKey', js)
        self.assertIn('event.key.toLowerCase() === "k"', js)
        self.assertIn('elements.search.focus()', js)



if __name__ == "__main__":
    unittest.main()
