# Public directory — ongoing readiness checklist

The Community App Directory is **public and operational**. This is an ongoing
checklist for significant catalog, website, workflow or governance changes;
it is **not** an incomplete pre-launch checklist or a certificate that every
listed third-party application is safe.

Check only what is relevant to the proposed change. Keep evidence in the
related PR or GitHub Actions run, and report unverified checks without
marking them complete.

## Changes to public content

- [ ] New or updated entries have publicly accessible primary sources and
  accurate creator attribution, category and availability labels.
- [ ] No private information, credentials, personal/device logs, proprietary
  SDK components or third-party media are being republished.
- [ ] Changes to `data/apps.json` have regenerated the approved README table,
  `data/apps.csv` and `docs/apps.json`; entries remain alphabetical.
- [ ] The required `catalog` CI passes, including website, spreadsheet and
  adversarial validation tests.
- [ ] For a UI change, review search and filters (including **All categories**),
  mobile layout, keyboard accessibility and public external links.
- [ ] Public PR descriptions are self-contained and discuss changes to this
  directory, not unrelated examples used during design.

## GitHub and public-site operations

- [ ] Verify the actual GitHub `main` ruleset is active: PR required,
  `catalog` check required, force pushes and branch deletion blocked.
- [ ] Confirm the reviewer policy matches the available team. The current
  single-maintainer configuration requires **zero independent approvals**;
  requiring CODEOWNER review is appropriate only when another trusted
  maintainer is available. `CODEOWNERS` alone is not an enforcement rule.
- [ ] Verify GitHub Pages deploys the reviewed `main/docs` content and can
  be opened anonymously without unexpected errors.
- [ ] Review Actions permissions and triggers before changing workflows.
  Untrusted PR code or PR artifacts must not execute with Google credentials.
- [ ] Review Dependabot changes and rerun CI before merging.
- [ ] Verify available repository security settings after relevant changes,
  including vulnerability reporting and secret/push protection as supported.

## Google Sheets mirror

- [ ] Confirm the latest relevant synchronization run reports `SYNC_OK`.
- [ ] Verify the public Google Sheet is **Viewer** for visitors, not Editor,
  and the dedicated service account retains only the necessary access.
- [ ] Check approved applications, alphabetical order, clickable short links
  and absence of duplicate or stale spreadsheet rows.
- [ ] Verify unreviewed issues and PRs appear only as numeric identifiers
  in the suggestions tab, not unreviewed titles or descriptions.
- [ ] When sharing more widely, check the Sheet anonymously for the owner's
  public profile information and confirm that this disclosure is acceptable.
- [ ] If a key is lost or suspected exposed, rotate the credential, update
  the GitHub secret and test synchronization without publishing the key.

## Community continuity

- [ ] Keep [CONTRIBUTING.md](../CONTRIBUTING.md) and
  [the local development guide](DEVELOPMENT.md) usable for new contributors.
- [ ] Welcome interested volunteer maintainers and document any actual role
  delegation; do not promise additional reviewers until available.
- [ ] Handle removal/correction requests using the public editorial policy;
  handle vulnerability details privately via [SECURITY.md](../SECURITY.md).
- [ ] Obtain explicit repository-owner authorization before exposing any
  non-public content or changing access to a private resource.

The directory links to external software but does not independently certify
its performance, safety, privacy or compatibility.
