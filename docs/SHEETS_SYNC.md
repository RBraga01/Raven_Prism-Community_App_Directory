# Google Sheets synchronization — operating contract

**One authoritative design:** GitHub is the editable source; a dedicated Google
service account writes the public read-only Google Sheet. Do not also use
IMPORTDATA on the same table.

Source catalog: [data/apps.json](../data/apps.json)
Public Sheet: https://docs.google.com/spreadsheets/d/1zpmI-z8rMLl50vsgDA0O8s4FfXIWPjRvKly5hzH-t14/edit

**Automatic synchronization is not live until the one-time account setup succeeds.**
Until a real workflow run reports SYNC_OK, do not claim a working scheduled mirror.

## Events

| Event | Outcome |
| --- | --- |
| Approved merge to main | Apps tab rebuilt alphabetically A–Z with short clickable links |
| Public app-suggestion issue | Numeric Issue #N in a separate pending tab |
| PR touching the catalog | Numeric PR #N after read-only validation completes |
| Daily 07:19 UTC | Full reconciliation |
| Manual workflow_dispatch | Full reconciliation when the owner requests it |

Unverified suggestions do NOT become approved entries until merged.
Issue/PR titles are never mirrored into the public spreadsheet.
When the GitHub repository is private, pending issue/PR metadata is not exported.
Individual app verification dates are intentionally omitted.

## One-time setup required from the repository owner

The current GitHub connector cannot set GitHub Actions secrets, and the owner
must approve an external service account receiving Editor access to the Sheet.

1. In a Google Cloud project, enable the Google Sheets API and create a
   dedicated service account. It needs no project-wide IAM roles.
2. Create a JSON credential. Keep the key strictly private.
3. Share only this spreadsheet with that service account's client_email as
   **Editor**. Keep public Anyone-with-link sharing as **Viewer**.
4. In GitHub: Settings → Secrets and variables → Actions → New repository secret.
   Set the exact name GOOGLE_SHEETS_CREDENTIALS_JSON and paste the JSON.
5. Run Actions → Sync community directory to Google Sheets → Run workflow.
   Confirm SYNC_OK and verify the Apps tab and source hyperlinks.
6. Review the repository history, rules and CI before changing GitHub visibility.

Without step 4, the sync workflow **fails visibly** instead of pretending success.

## Security model

- No pull_request_target trigger.
- PR validation is read-only and cannot access Google secrets.
- A workflow_run notification from CI can launch the trusted publisher. It
  checks out the default branch exclusively and never downloads or executes
  PR head code or artifacts.
- The publisher uses read-only GitHub issue/PR metadata and publishes only
  numeric public references, never arbitrary user-supplied titles.
- Google Sheets access is limited to the specified spreadsheet, whose public
  audience has Viewer permission.
- Any upload error or mismatching order/readback fails the job.
- Changes to automation, catalog or policy require maintainer review; the
  CODEOWNERS file is not sufficient without enforced branch protection.
- GitHub Actions use immutable commit hashes. Direct and transitive Python
  dependencies are fully pinned with SHA-256 hashes in
  requirements-sheet-sync.lock, regenerated deliberately and reviewed before
  deployment.

## Why not IMPORTDATA?

Google Sheets' IMPORTDATA periodically refreshes a public CSV, but does not
guarantee updates on GitHub event completion or precise daily reconciliation.
It also does not automatically produce short, linked label cells or handle
separate moderated suggestions. To meet the original requirements, this
project uses the service-account writer as its **only** sync implementation.

## Public document identity

Even Viewer-only documents may display their owner's public Google profile.
For identity separation, use a publication account before promoting the
directory widely. Anonymous browser verification is still required.
