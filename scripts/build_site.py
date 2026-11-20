#!/usr/bin/env python3
"""Deterministically generate public views from the approved JSON catalog."""
import csv
import json
from pathlib import Path

from catalog_lib import FIELDS, load_apps, render_markdown_table

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data/apps.json"
apps = sorted(load_apps(source, require_order=False),
              key=lambda a: a["name"].casefold())
source.write_text(json.dumps(apps, indent=2, ensure_ascii=False) + "\n",
                  encoding="utf-8")
(ROOT / "docs/apps.json").write_text(
    json.dumps(apps, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
with (ROOT / "data/apps.csv").open("w", newline="", encoding="utf-8") as out:
    writer = csv.DictWriter(out, fieldnames=FIELDS, quoting=csv.QUOTE_ALL,
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(apps)

readme = ROOT / "README.md"
content = readme.read_text(encoding="utf-8")
begin, end = "<!-- BEGIN GENERATED APPS -->", "<!-- END GENERATED APPS -->"
if content.count(begin) != 1 or content.count(end) != 1:
    raise ValueError("README requires exactly one generated region")
prefix, remaining = content.split(begin, 1)
_, suffix = remaining.split(end, 1)
readme.write_text(
    prefix + begin + "\n" + render_markdown_table(apps) + "\n" + end + suffix,
    encoding="utf-8",
)
print(f"Generated views for {len(apps)} approved public entries")
