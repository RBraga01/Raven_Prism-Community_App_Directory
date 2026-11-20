"""Regression gates for the calm light palette, external labels and category reset."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "docs/index.html").read_text(encoding="utf-8")
JS = (ROOT / "docs/app.mjs").read_text(encoding="utf-8")


def luminance(hex_color):
    values = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in values
    ]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    bright, dark = sorted((luminance(a), luminance(b)), reverse=True)
    return (bright + 0.05) / (dark + 0.05)


class LightDirectoryThemeTests(unittest.TestCase):
    def test_palette_is_light_warm_neutral_without_artificial_gradients(self):
        for key in (
            "--ink: #242824", "--muted: #4f5750", "--subtle: #5e675e",
            "--border: #d9ddd5", "--primary: #3b5449",
            "--primary-deep: #294137", "--focus: #3f6252",
            "--surface: #fffefa",
            "background: #f5f5f1",
            "background: #eeefe9",
        ):
            self.assertIn(key, HTML, key)
        self.assertNotIn("linear-gradient(", HTML)
        self.assertNotIn("radial-gradient(", HTML)
        for old_blue in ("#304ab1", "#273c8e", "#526bc7", "#dde2ff"):
            self.assertNotIn(old_blue, HTML.lower())

    def test_text_and_focus_colors_have_practical_wcag_contrast(self):
        checks = (
            ("#242824", "#f5f5f1", 4.5),
            ("#4f5750", "#fffefa", 4.5),
            ("#5e675e", "#fffefa", 4.5),
            ("#535c54", "#fffefa", 4.5),  # Search placeholder
            ("#3b5449", "#fffefa", 4.5),  # Primary text links
            ("#3f6252", "#fffefa", 3.0),  # Focus indicator
        )
        for foreground, background, minimum in checks:
            with self.subTest(foreground=foreground, background=background):
                self.assertGreaterEqual(contrast(foreground, background), minimum)

    def test_no_external_arrow_glyph_in_public_site_source(self):
        for text in (HTML, JS):
            self.assertNotIn("\u2197", text)
            self.assertNotRegex(text, r"&#(?:8599|x2197);")
        self.assertIn("View source", JS)
        self.assertIn("href=", HTML)

    def test_all_categories_has_explicit_empty_value(self):
        self.assertIn('const allCategories = create("option", "", "All categories")', JS)
        self.assertIn('allCategories.value = ""', JS)
        self.assertIn("elements.category.replaceChildren(allCategories)", JS)
        self.assertIn("elements.category.value = state.category", JS)
        self.assertIn("(!state.category || app.category === state.category)", 
                      (ROOT / "docs/catalog-core.mjs").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
