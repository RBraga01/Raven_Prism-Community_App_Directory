#!/usr/bin/env python3
"""Validate sources, generated views and safe publishing invariants."""
import csv
import json
from pathlib import Path

from catalog_lib import FIELDS, load_apps, render_markdown_table

ROOT = Path(__file__).resolve().parents[1]
apps = load_apps(ROOT / "data/apps.json")

site = json.loads((ROOT / "docs/apps.json").read_text(encoding="utf-8"))
if site != apps:
    raise ValueError("docs/apps.json differs from the approved catalog")

with (ROOT / "data/apps.csv").open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    if reader.fieldnames != list(FIELDS):
        raise ValueError("CSV headers disagree with the catalog schema")
    rows = list(reader)
if rows != apps:
    raise ValueError("CSV rows disagree with approved data, values or order")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
begin, end = "<!-- BEGIN GENERATED APPS -->", "<!-- END GENERATED APPS -->"
if readme.count(begin) != 1 or readme.count(end) != 1:
    raise ValueError("README is missing a unique generated table region")
actual = readme.split(begin, 1)[1].split(end, 1)[0].strip()
expected = render_markdown_table(apps)
if actual != expected:
    raise ValueError("README table differs from escaped canonical output")

print(f"PASS: {len(apps)} entries; sources, safe text and generated views verified")
