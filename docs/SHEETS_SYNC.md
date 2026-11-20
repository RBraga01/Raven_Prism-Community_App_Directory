# Google Sheets synchronization — operating contract

**One authoritative design:** GitHub is the editable source; a dedicated Google
service account writes the public read-only Google Sheet. Do not also use
IMPORTDATA on the same table.

Source catalog: [data/apps.json](../data/apps.json)
Public Sheet: https://docs.google.com/spreadsheets/d/1zpmI-z8rMLl50vsgDA0O8s4FfXIWPjRvKly5hzH-t14/edit

**Operational status:** The GitHub Actions publisher has been configured and
has completed successful synchronization runs. GitHub is the editable source;
the public Sheet remains a read-only mirror. For freshness or incident checks,
inspect the most recent relevant [sync workflow](https://github.com/RBraga01/Raven_Prism-Community_App_Directory/actions/workflows/sync-google-sheet.yml)
run and confirm `SYNC_OK`. A previous success does not guarantee every
future run will succeed.

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
Private forks may suppress pending issue/PR metadata; this published directory accepts public suggestions.
Individual app verification dates are intentionally omitted.

## Credential maintenance and recovery

The dedicated Google service-account credential is managed by the repository
owner and is stored **only** as the GitHub Actions secret
`GOOGLE_SHEETS_CREDENTIALS_JSON`. Never commit the JSON, post it in an issue
or PR, or copy it into CI logs.

If the credential must be replaced or rotated:

1. Create or rotate a dedicated service-account key in the owner's Google
   Cloud project. The Google Sheets API must remain enabled.
2. Keep the service account's **Editor** access scoped to this spreadsheet
   only. Keep anonymous visitors at **Viewer**, not Editor.
3. Replace the GitHub Actions secret at
   **Settings → Secrets and variables → Actions** using the exact name
   `GOOGLE_SHEETS_CREDENTIALS_JSON`. Never paste its value into discussions.
4. Manually run **Actions → Sync community directory to Google Sheets**.
   Confirm `SYNC_OK`, alphabetical entries and working source hyperlinks.
5. After successful verification, deactivate the superseded key.

If the secret is absent or invalid, synchronization **fails visibly**.
The source catalog in GitHub remains authoritative and should not be edited
through Google Sheets.

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
Before wider promotion or an ownership change, inspect anonymous access and
confirm the visible identity is acceptable. Changing the account must not
silently grant public editing access.
