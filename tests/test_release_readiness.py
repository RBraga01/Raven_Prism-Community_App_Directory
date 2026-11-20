"""Public-release safeguards that must remain true for community contributions."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseReadinessTests(unittest.TestCase):
    def test_mit_license_is_canonical_without_external_notices(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8").strip()
        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("Permission is hereby granted", license_text)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', license_text)
        self.assertTrue(license_text.endswith("SOFTWARE."))
        self.assertNotIn("This license applies only", license_text)
        self.assertIn("external", (ROOT / "NOTICE.md").read_text().lower())

    def test_public_security_reporting_and_conduct_exist(self):
        for name in ("SECURITY.md", "NOTICE.md", "CODE_OF_CONDUCT.md"):
            self.assertGreater((ROOT / name).stat().st_size, 300)
        self.assertIn("Advisories", (ROOT / "SECURITY.md").read_text())
        self.assertIn("third-party", (ROOT / "SECURITY.md").read_text().lower())

    def test_unverified_leads_have_no_uncited_hackathon_count(self):
        leads = (ROOT / "docs/UNVERIFIED_LEADS.md").read_text().lower()
        self.assertNotRegex(leads, r"\b55\s*(?:\+|reported|apps)")
        self.assertIn("primary", leads)

    def test_privileged_workflow_ignores_failed_pr_checks(self):
        workflow = (ROOT / ".github/workflows/sync-google-sheet.yml").read_text()
        self.assertNotIn("pull_request_target:", workflow)
        self.assertIn("workflow_run.conclusion == 'success'", workflow)
        self.assertIn("github.event.repository.default_branch", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("pull_request.head.sha", workflow)

    def test_ruleset_is_active_and_restricts_main(self):
        path = ROOT / "docs/release/main-ruleset.json"
        ruleset = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(ruleset["enforcement"], "active")
        self.assertEqual(ruleset["conditions"]["ref_name"]["include"],
                         ["refs/heads/main"])
        kinds = {r["type"] for r in ruleset["rules"]}
        self.assertTrue({"deletion", "non_fast_forward", "pull_request",
                         "required_status_checks", "required_linear_history"}
                        <= kinds)
        checks = next(r for r in ruleset["rules"]
                      if r["type"] == "required_status_checks")
        self.assertIn({"context": "catalog"},
                      checks["parameters"]["required_status_checks"])

    def test_pages_static_assets_exist(self):
        self.assertTrue((ROOT / "docs/index.html").is_file())
        self.assertTrue((ROOT / "docs/apps.json").is_file())
        self.assertTrue((ROOT / "docs/.nojekyll").is_file())


if __name__ == "__main__":
    unittest.main()
