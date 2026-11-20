"""Guard public contribution narratives and retired automation removal."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContributionPolicyTests(unittest.TestCase):
    def test_no_retired_branch_cleanup_workflow(self):
        self.assertFalse(
            (ROOT / ".github/workflows/cleanup-merged-branches.yml").exists()
        )

    def test_pr_template_requires_self_contained_evidence(self):
        template = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("self-contained", template)
        self.assertIn("no comparisons", template)
        self.assertIn("Required `catalog` CI checks pass", template)

    def test_app_source_citation_is_still_supported(self):
        docs = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("public project link", docs)
        self.assertIn("catalog verification", docs)
        self.assertIn("unrelated repositories", docs)


if __name__ == "__main__":
    unittest.main()
