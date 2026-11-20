"""Public README must remain welcoming, factual and low-maintenance."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


class ReadmeWelcomeTests(unittest.TestCase):
    def test_project_name_and_platform_context_are_clear(self):
        self.assertTrue(README.startswith("# Community App Directory\n### Raven Prism\n"))
        first_part = README.split("<!-- BEGIN GENERATED APPS -->", 1)[0]
        self.assertIn("Independent project", first_part)
        self.assertIn("Not affiliated with or endorsed by Raven Resonance", first_part)

    def test_badges_are_factual_static_and_neutral(self):
        first_part = README.split("## Explore the directory", 1)[0]
        badges = re.findall(r"!\[([^\]]+)\]\((https://img\.shields\.io/badge/[^\s)]+)\)", first_part)
        self.assertEqual(len(badges), 4)
        labels = [a for a, _ in badges]
        self.assertEqual(labels, [
            "Platform: Raven Prism",
            "Independent: Community directory",
            "Catalog: Public source links",
            "Directory code: MIT",
        ])
        self.assertTrue(all("?style=flat-square" in url for _, url in badges))
        self.assertNotIn("download-count", first_part)
        self.assertNotIn("passing-hardware", first_part)

    def test_shortcuts_go_to_real_publication_surfaces(self):
        first_part = README.split("## Explore the directory", 1)[0]
        for url in (
            "https://rbraga01.github.io/Raven_Prism-Community_App_Directory/",
            "https://docs.google.com/spreadsheets/d/1zpmI-z8rMLl50vsgDA0O8s4FfXIWPjRvKly5hzH-t14/edit",
            "https://github.com/RBraga01/Raven_Prism-Community_App_Directory/issues/new/choose",
        ):
            self.assertIn(url, first_part)
        self.assertIn("[How to contribute](CONTRIBUTING.md)", first_part)

    def test_generated_catalog_is_still_present_and_unmodified(self):
        self.assertEqual(README.count("<!-- BEGIN GENERATED APPS -->"), 1)
        self.assertEqual(README.count("<!-- END GENERATED APPS -->"), 1)
        table = README.split("<!-- BEGIN GENERATED APPS -->", 1)[1].split(
            "<!-- END GENERATED APPS -->", 1)[0]
        self.assertIn("| Application | Category | Developer | Public availability |", table)
        self.assertIn("Webtoon XR", table)


if __name__ == "__main__":
    unittest.main()
