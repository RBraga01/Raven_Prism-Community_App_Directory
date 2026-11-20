# Contributing

Thanks for helping others discover software for Raven Prism.

## Suggest a listing
Use the GitHub **Suggest an app** issue form, or open a pull request adding/editing exactly one catalog record in `data/apps.json`.

Include:
1. The application's public name and creator.
2. A public primary source (GitHub repository, creator-maintained page or official project page).
3. A short **original** description of what the application does.
4. A public video or release link, if available.
5. The correct availability label: `Source code`, `Official example`, or `Downloadable release`.

The public directory and Google Sheet are **always alphabetical by application name**. Run `python scripts/build_site.py` after changing the JSON; it rewrites the canonical JSON, CSV, README table, and website data in A–Z order.

Submit suggestions through issues or PRs; **do not edit Google Sheets**. A public issue/PR can appear in the Sheet's separate *Community suggestions* tab as awaiting review after synchronization is configured. The approved *Apps* tab updates only when a validated catalog change is merged into `main`.

Only add items for Raven Prism or explicit Raven Framework projects. A clone, fork or rewrite is not automatically a different app. Where multiple distinct experiences live in one repository, they may be listed separately.

## PR and issue descriptions

Describe the specific change, the factual reason for it and its test evidence.
Keep the public discussion self-contained and focused on this directory.
Do **not** cite, compare or attribute the directory's design choices to
unrelated repositories or websites consulted as examples.

This rule does not prohibit source citations for a new application: its
creator's public project link and accurate attribution are required for
catalog verification. Do not include private research notes or unsupported
claims in discussions.

## Public links and safe formatting

Only reviewed HTTPS destinations can enter the catalog. If a legitimate
project uses a new domain, submit the source in an issue; the maintainer can
review and extend the allowlist in scripts/catalog_lib.py before merging.
The builder escapes Markdown-sensitive text, and CI rejects control characters
and spreadsheet formulas. Never bypass those checks.

## Accuracy rules
- Public source code does not mean compatible with actual hardware or publicly installable.
- Do not attribute private or simulated tests to physical hardware.
- Do not submit misleading compatibility claims, invented demo links, or unsupported ratings.
- Do not post credentials, device data, internal project documents, private repositories, personal contacts, or copyrighted assets.
- Do not add proprietary SDK files or downloadable copyrighted comics.

## Review
The maintainer verifies sources, duplicate entries, availability wording and potential licensing issues before merging. Submission does not guarantee listing. Reviews and removal requests are welcome.

## Refresh generated files
```bash
python scripts/build_site.py
python scripts/validate_catalog.py
```

Please include generated changes and keep the directory independent from Raven Resonance.
