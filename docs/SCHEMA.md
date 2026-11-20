# Catalog record format

Source of truth: `data/apps.json`. An array of records, each containing:

| Field | Type | Requirement |
| --- | --- | --- |
| `id` | string | Unique lowercase slug |
| `name` | string | Public project name |
| `category` | string | Descriptive category |
| `developer` | string | Public creator name/handle |
| `description` | string | Original, factual short description |
| `source_url` | URL | Primary public source, HTTPS |
| `demo_url` | URL or empty string | Public example/demo when verified |
| `availability` | enum | `Source code`, `Official example`, `Downloadable release` |

No secret or internal metadata, device performance scores or unpublished claims. Each named project must have a public source.

Run `python scripts/build_site.py` after changing `data/apps.json` and commit the generated README table, `docs/apps.json` and CSV together.

New URL hosts need explicit maintainer approval in scripts/catalog_lib.py.
Catalog text is validated against control-character, formula-injection and
Markdown-table injection risks. To regenerate public views, run the builder
before the validator.

Publication dates and per-entry verification timestamps are intentionally omitted from the public directory. Use Git commit history to review changes without maintaining dates for every entry.
