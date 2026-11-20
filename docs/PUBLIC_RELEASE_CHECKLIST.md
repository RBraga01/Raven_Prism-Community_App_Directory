# Public-release checklist

**Release scope:** This new repository was initialized from a reviewed history-free snapshot. Before announcing it, the owner must activate and verify the administrative protections, workflow credentials, security settings and website deployment listed below.

This independent community directory may be shared only after verifying all
publication gates. Maintaining the catalog does not certify linked software.

## Security and privacy

- [ ] Review all current files, branches, reachable commit history and Actions
  logs for personal information, private data, credentials and third-party assets.
- [ ] Confirm every public listing links to a source that is publicly accessible.
- [ ] Confirm the directory does not ship the proprietary Raven SDK.
- [ ] Confirm GitHub Actions run only approved code when secrets are available.
- [ ] Run the adversarial catalog, sync and website tests on the final commit.
- [ ] Confirm PRs cannot bypass a maintainer review, including generated changes.
- [ ] Configure branch protection or rulesets on main: require PR reviews (ideally
  CODEOWNER review), require passing checks, prevent force pushes and deletion.
  CODEOWNERS alone does not enforce these conditions.
- [ ] Inspect repository visibility-conversion effects and re-enable any
  previously active push protections.

## Public presentation

- [ ] Verify the GitHub README and data files agree and are alphabetical.
- [ ] Enable GitHub Pages from docs/ and verify search/filter and every footer link.
- [ ] Verify the Google Sheet has Anyone-with-link Viewer, never public Editor.
- [ ] Check the Sheet with a browser not logged into the owner's account; note
  that Google's sharing UI can expose the document owner's public identity.
- [ ] Configure a dedicated Google Sheets service account and test a successful
  automatic synchronization on a reviewed catalog update.
- [ ] Confirm live short hyperlinks, alphabetical order and no duplicate/stale
  rows after subsequent syncs.
- [ ] Confirm unreviewed issues and PRs appear only as numeric references in
  the pending tab, never their raw titles.

## Operations

- [ ] Monitor GitHub Actions failures; missing credentials must fail visibly.
- [ ] Review Dependabot updates before merging.
- [ ] Maintain a recovery plan for Google credentials and API availability.
- [ ] Publish only with the repository owner's explicit approval.

If any gate is unverified, report the limitation; do not imply release readiness.
