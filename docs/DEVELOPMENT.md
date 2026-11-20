# Local development

This is a static community directory, not an app store or an application
runtime. You can preview the website and validate contributions without
hardware, cloud accounts or a Google service-account key.

## Requirements

- Git
- Python 3.12 (the version used by GitHub Actions)
- Node.js 20 or newer for the JavaScript tests

The website has no npm dependencies or frontend build step. Python catalog
generation and validation use only the standard library.

## Get started

From a terminal:

```bash
git clone https://github.com/RBraga01/Raven_Prism-Community_App_Directory.git
cd Raven_Prism-Community_App_Directory

python scripts/validate_catalog.py
python -m http.server 8000 --directory docs
```

Open **http://localhost:8000/** in a browser. Stop the server with Ctrl+C.

Run a local server rather than opening `docs/index.html` with `file://`:
the site loads `docs/apps.json` and JavaScript modules from the same origin.

## Where to make changes

| Goal | Edit |
| --- | --- |
| Add or correct an application | `data/apps.json` |
| Update the website layout or copy | `docs/index.html` |
| Change interactive behavior | `docs/app.mjs` |
| Change search, sorting or insights | `docs/catalog-core.mjs` |
| Update contribution or editorial guidance | `CONTRIBUTING.md` or `docs/` |

**Only `data/apps.json` is the authoritative catalog.** When an application
changes, generate the derived files before committing:

```bash
python scripts/build_site.py
python scripts/validate_catalog.py
```

The generator sorts entries by application name and updates the catalog CSV,
the website JSON feed and the generated table in `README.md`. Do not manually
edit `docs/apps.json`, `data/apps.csv` or the section between the README's
generated-table markers.

## Run the checks

```bash
python -m unittest discover -s tests -v
node --check docs/catalog-core.mjs
node --check docs/app.mjs
node --test tests/catalog-ui.test.mjs
```

The required GitHub `catalog` check repeats catalog validation and tests,
then runs the generator to ensure all derived files were committed.

To review the files you changed before submitting:

```bash
git diff --check
git status --short
```

When testing website filters, check an unfiltered catalog, an individual
category, a combined filter and the return to **All categories**. Review
desktop/mobile layouts and keyboard operation when changing the UI.

## Contribute safely

Use a focused branch and a PR to `main`; do not push directly to the
protected branch. Explain changes and evidence for this directory only.

Never commit private repositories, unpublished projects, personal information,
third-party assets, API keys or service-account JSON. Catalog links must be
public sources that can be attributed to their original creators.

The Google Sheet is a read-only **mirror**, maintained by a trusted GitHub
Actions workflow. Local website development does not require Google access.
Do not run the sheet publisher against the public spreadsheet for testing
or commit credentials. See [Sheets synchronization](SHEETS_SYNC.md) for
maintainer operations and [CONTRIBUTING.md](../CONTRIBUTING.md) for editorial
criteria.
