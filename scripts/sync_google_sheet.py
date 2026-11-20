#!/usr/bin/env python3
"""Mirror approved public catalog entries from GitHub to a Google Sheet.

The repository's data/apps.json is authoritative. GitHub issues and PRs
appear only as clearly unverified suggestions, and only once the repository
itself is public. No private repository data or test reports are exported.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/apps.json"
REPO = "RBraga01/Raven_Prism-Community_App_Directory"
SHEET_ID = "1zpmI-z8rMLl50vsgDA0O8s4FfXIWPjRvKly5hzH-t14"
APPS_TAB = "Apps"
SUGGESTIONS_TAB = "Community suggestions"
APP_HEADERS = [
    "Application", "Category", "Creator", "Public description",
    "Source", "Demo", "Availability",
]
SUGGESTION_HEADERS = ["Proposed application", "Origin", "Status", "Public link"]


def alpha_key(name: str) -> str:
    return name.casefold()


def linked(label: str, url: str = "") -> dict:
    """Display a short label; retain the original URL as a proper Sheets link."""
    result = {"userEnteredValue": {"stringValue": str(label)}}
    if url:
        if not url.startswith("https://") or "\n" in url or "\r" in url:
            raise ValueError("Invalid public HTTPS URL")
        result["userEnteredFormat"] = {"textFormat": {"link": {"uri": url}}}
    return result


def demo_label(url: str) -> str:
    if not url:
        return "—"
    if "youtu.be/" in url or "youtube.com/" in url:
        return "Video"
    if "/releases/" in url:
        return "Release"
    return "Demo"


def public_apps() -> list[dict]:
    records = json.loads(CATALOG.read_text(encoding="utf-8"))
    if not records or not isinstance(records, list):
        raise ValueError("Refusing to publish an empty catalog")
    return sorted(records, key=lambda a: alpha_key(a["name"]))


def app_rows(apps: list[dict]) -> list[dict]:
    return [
        {"values": [
            linked(a["name"]), linked(a["category"]), linked(a["developer"]),
            linked(a["description"]), linked("GitHub", a["source_url"]),
            linked(demo_label(a["demo_url"]), a["demo_url"]),
            linked(a["availability"]),
        ]}
        for a in apps
    ]


def github_get(path: str, token: str) -> object:
    if not path.startswith("/repos/" + REPO):
        raise ValueError("Unexpected GitHub API path")
    req = Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RavenCommunityDirectorySheetMirror",
        },
    )
    with urlopen(req, timeout=25) as response:
        return json.load(response)


def github_list(path: str, token: str, maximum_pages: int = 10) -> list:
    """Bounded pagination; refuse to silently publish incomplete results."""
    results = []
    for page in range(1, maximum_pages + 1):
        params = urlencode({"per_page": 100, "page": page})
        separator = "&" if "?" in path else "?"
        part = github_get(path + separator + params, token)
        if not isinstance(part, list):
            raise ValueError("GitHub API returned an unexpected type")
        results.extend(part)
        if len(part) < 100:
            return results
    raise RuntimeError("GitHub suggestions exceed scan limit; no partial sync")


def community_suggestions(token: str) -> list[dict]:
    """Expose only numeric public issue/PR identifiers, never raw user titles.

    A title may contain sensitive or abusive text even in a public GitHub issue.
    Unreviewed suggestions are not approved listings.
    """
    if not token:
        return []
    metadata = github_get("/repos/" + REPO, token)
    if metadata.get("private", True):
        return []
    suggestions = []
    issues = github_list("/repos/" + REPO + "/issues?state=open", token)
    for issue in issues:
        if "pull_request" in issue:
            continue
        labels = {x.get("name", "") for x in issue.get("labels", [])}
        title = str(issue.get("title", ""))
        if "app-suggestion" not in labels and not title.lower().startswith("[app]"):
            continue
        number = issue.get("number")
        if not isinstance(number, int) or number < 1:
            continue
        suggestions.append({
            "name": f"Issue #{number}",
            "origin": "Issue",
            "url": f"https://github.com/{REPO}/issues/{number}",
        })
    prs = github_list("/repos/" + REPO + "/pulls?state=open", token)
    for pr in prs:
        number = pr.get("number")
        if not isinstance(number, int) or number < 1:
            continue
        changed = github_list(
            "/repos/" + REPO + f"/pulls/{number}/files", token
        )
        if not any(x.get("filename") == "data/apps.json" for x in changed):
            continue
        suggestions.append({
            "name": f"PR #{number}",
            "origin": "Pull request",
            "url": f"https://github.com/{REPO}/pull/{number}",
        })
    return sorted(suggestions, key=lambda s: (s["origin"], int(s["name"].split("#")[1])))

def suggestion_rows(suggestions: list[dict]) -> list[dict]:
    return [
        {"values": [
            linked(s["name"]), linked(s["origin"]),
            linked("Awaiting review"), linked(s["origin"], s["url"]),
        ]}
        for s in suggestions
    ]


def replace_tab(sheet_id: int, headers: list[str], records: list[dict],
                previous_count: int, grid_rows: int, has_filter: bool = False) -> list[dict]:
    """Overwrite the entire previous table; clear links left by removed rows."""
    width = len(headers)
    count = max(previous_count, len(records))
    end = count + 1
    rows = [{"values": [linked(h) for h in headers]}] + records
    rows += [{"values": [linked("") for _ in headers]} for _ in range(count - len(records))]
    requests = []
    if end > grid_rows:
        requests.append({
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"rowCount": end + 50}},
                "fields": "gridProperties.rowCount",
            }
        })
    if has_filter:
        requests.append({"clearBasicFilter": {"sheetId": sheet_id}})
    requests.extend([
        {"updateCells": {
            "range": {
                "sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": end,
                "startColumnIndex": 0, "endColumnIndex": width,
            },
            "rows": rows,
            "fields": "userEnteredValue,userEnteredFormat.textFormat.link",
        }},
        {"updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }},
    ])
    if records:
        requests.append({"setBasicFilter": {"filter": {"range": {
            "sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": len(records) + 1,
            "startColumnIndex": 0, "endColumnIndex": width,
        }}}})
    return requests


def main() -> None:
    approved = public_apps()
    secret = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
    if not secret:
        raise SystemExit("Missing Google Sheets service account credentials. See docs/SHEETS_SYNC.md")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credential = service_account.Credentials.from_service_account_info(
        json.loads(secret),
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=credential, cache_discovery=False)
    api = service.spreadsheets()
    metadata = api.get(
        spreadsheetId=SHEET_ID,
        fields="sheets(properties(sheetId,title,gridProperties(rowCount)),basicFilter)",
    ).execute()
    sheets = {s["properties"]["title"]: s for s in metadata["sheets"]}
    suggestions = community_suggestions(os.environ.get("GITHUB_TOKEN", ""))

    # Create the separate suggestions tab if not already present.
    if SUGGESTIONS_TAB not in sheets:
        result = api.batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": SUGGESTIONS_TAB}}}]},
        ).execute()
        sheets[SUGGESTIONS_TAB] = {"properties": result["replies"][0]["addSheet"]["properties"]}

    if APPS_TAB not in sheets:
        raise RuntimeError("Apps tab does not exist; refusing to modify another tab")
    requests = []
    for title, headers, records in [
        (APPS_TAB, APP_HEADERS, app_rows(approved)),
        (SUGGESTIONS_TAB, SUGGESTION_HEADERS, suggestion_rows(suggestions)),
    ]:
        tab = sheets[title]
        prop = tab["properties"]
        current = api.values().get(
            spreadsheetId=SHEET_ID,
            range="'" + title.replace("'", "''") + "'!A:A",
        ).execute().get("values", [])
        previous_count = max(0, len(current) - 1)
        requests += replace_tab(
            prop["sheetId"], headers, records, previous_count,
            prop["gridProperties"]["rowCount"], has_filter=bool(tab.get("basicFilter")),
        )

    api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": requests}).execute()

    # Check the actual published order, not merely a successful write response.
    readback = api.values().get(
        spreadsheetId=SHEET_ID, range="'Apps'!A1:A" + str(len(approved) + 1),
    ).execute().get("values", [])
    names = [r[0] for r in readback[1:] if r]
    expected = [a["name"] for a in approved]
    if not readback or readback[0] != ["Application"] or names != expected:
        raise RuntimeError("Google Sheets Apps order differs from GitHub catalog")
    print(f"SYNC_OK: {len(approved)} approved apps A–Z; "
          f"{len(suggestions)} public pending suggestions; GitHub is authoritative")


if __name__ == "__main__":
    main()
