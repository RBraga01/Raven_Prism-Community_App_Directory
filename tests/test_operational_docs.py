"""Ensure public documentation reflects the live directory and remains usable."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class PublicDocumentationTests(unittest.TestCase):
    def test_readme_has_current_public_status_and_right_suggestion_link(self):
        readme = read("README.md")
        self.assertNotIn("Before making this repository public", readme)
        self.assertNotIn("a fresh repository needs its own Actions credential", readme)
        self.assertNotIn("demos-only view", readme)
        self.assertIn("additional-links filter", readme)
        suggestion = (
            "https://github.com/RBraga01/Raven_Prism-Community_App_Directory"
            "/issues/new/choose"
        )
        self.assertGreaterEqual(readme.count(suggestion), 2)
        self.assertNotIn("](.github/ISSUE_TEMPLATE/suggest-app.yml)", readme)
        self.assertIn("[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)", readme)

    def test_dev_guide_supports_local_preview_and_complete_test_flow(self):
        guide = read("docs/DEVELOPMENT.md")
        for command in (
            "python scripts/build_site.py",
            "python scripts/validate_catalog.py",
            "python -m http.server 8000 --directory docs",
            "python -m unittest discover -s tests -v",
            "node --check docs/catalog-core.mjs",
            "node --check docs/app.mjs",
            "node --test tests/catalog-ui.test.mjs",
        ):
            with self.subTest(command=command):
                self.assertIn(command, guide)
        self.assertIn("data/apps.json", guide)
        self.assertIn("docs/apps.json", guide)
        self.assertIn("no npm dependencies", guide)
        self.assertIn("does not require Google access", guide)

    def test_maintainer_policy_invites_volunteers_without_fake_team(self):
        readme = read("README.md")
        contributing = read("CONTRIBUTING.md")
        self.assertIn("Additional maintainers are welcome", readme)
        self.assertIn("open to additional volunteer maintainers", contributing)
        self.assertIn("currently requires PRs and passing CI", contributing)
        self.assertIn("Once more trusted maintainers", contributing)
        self.assertIn("No fixed team size, formal", contributing)

    def test_operational_documents_no_longer_look_like_prelaunch_gates(self):
        checklist = read("docs/PUBLIC_RELEASE_CHECKLIST.md")
        sheet = read("docs/SHEETS_SYNC.md")
        self.assertIn("public and operational", checklist)
        self.assertIn("zero independent approvals", checklist)
        self.assertIn("ongoing", checklist.lower())
        self.assertNotIn("Before announcing it", checklist)
        self.assertNotIn("history-free snapshot", checklist)
        self.assertIn("**Operational status:**", sheet)
        self.assertIn("## Credential maintenance and recovery", sheet)
        self.assertIn("GOOGLE_SHEETS_CREDENTIALS_JSON", sheet)
        self.assertNotIn("Automatic synchronization is not live", sheet)
        self.assertNotIn("before changing GitHub visibility", sheet)

    def test_local_markdown_links_exist_for_changed_documents(self):
        for name in (
            "README.md",
            "CONTRIBUTING.md",
            "docs/DEVELOPMENT.md",
            "docs/PUBLIC_RELEASE_CHECKLIST.md",
            "docs/SHEETS_SYNC.md",
        ):
            content = read(name)
            for rel in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", content):
                if rel.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                if rel.startswith("<") and rel.endswith(">"):
                    continue
                dest = (ROOT / name).parent / rel.split("#", 1)[0]
                with self.subTest(document=name, link=rel):
                    self.assertTrue(dest.is_file(), f"Broken Markdown link {rel}")


if __name__ == "__main__":
    unittest.main()
