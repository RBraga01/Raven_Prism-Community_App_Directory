"""Shared, dependency-free validation and safe Markdown output.

Catalog entries are untrusted contributor-controlled text.
"""
from __future__ import annotations

import json
import re
import unicodedata
from urllib.parse import urlsplit

FIELDS = (
    "id", "name", "category", "developer", "description",
    "source_url", "demo_url", "availability",
)
AVAILABILITY = {"Source code", "Official example", "Downloadable release"}
# New domains require a reviewed code change.
SOURCE_HOSTS = {
    "github.com", "www.github.com", "devpost.com", "raven.computer",
    "www.raven.computer", "itch.io", "www.itch.io",
}
DEMO_HOSTS = SOURCE_HOSTS | {
    "youtu.be", "youtube.com", "www.youtube.com", "vimeo.com", "www.vimeo.com",
}
FORBIDDEN_PUBLIC_TERMS = (
    "sk-proj-", "github_pat_", "ghp_", "authorization: bearer",
    "-----begin private key-----", "private lab", "internal report",
    
)


def fail(message: str) -> None:
    raise ValueError(message)


def verify_text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        fail(f"{label}: expected nonempty, trimmed text")
    if len(value) > maximum:
        fail(f"{label}: exceeds {maximum} characters")
    if any(unicodedata.category(c) in {"Cc", "Cf", "Cs"} for c in value):
        fail(f"{label}: control or direction-formatting character")
    if value[0] in "=+-@":
        fail(f"{label}: spreadsheet formula-like prefix")
    if any(term in value.casefold() for term in FORBIDDEN_PUBLIC_TERMS):
        fail(f"{label}: possibly sensitive text")
    return value


def verify_url(url: object, label: str, allowed_hosts: set[str], *, optional=False) -> str:
    if optional and url == "":
        return ""
    value = verify_text(url, label, 2048)
    if any(c.isspace() for c in value) or any(c in value for c in "<>\\[]()|" + chr(96)):
        fail(f"{label}: unsafe URL character")
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"{label}: invalid URL") from exc
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.hostname not in allowed_hosts
        or parts.username is not None
        or parts.password is not None
        or port not in (None, 443)
        or not parts.path.startswith("/")
    ):
        fail(f"{label}: HTTPS URL must point to a reviewed public host")
    return value


def validate_apps(apps: object, *, require_order=True) -> list[dict]:
    if not isinstance(apps, list) or not apps or len(apps) > 10000:
        fail("Catalog must be a nonempty array of at most 10000 entries")
    ids: set[str] = set()
    names: set[str] = set()
    for idx, app in enumerate(apps):
        if not isinstance(app, dict) or set(app) != set(FIELDS):
            fail(f"Entry {idx}: unknown or missing fields")
        identifier = app["id"]
        if not isinstance(identifier, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier
        ):
            fail(f"Entry {idx}: invalid ID")
        if identifier in ids:
            fail(f"Entry {idx}: duplicate ID")
        ids.add(identifier)
        name = verify_text(app["name"], "name", 120)
        if name.casefold() in names:
            fail(f"Entry {idx}: duplicate name")
        names.add(name.casefold())
        verify_text(app["category"], "category", 80)
        verify_text(app["developer"], "developer", 120)
        verify_text(app["description"], "description", 280)
        verify_url(app["source_url"], "source_url", SOURCE_HOSTS)
        verify_url(app["demo_url"], "demo_url", DEMO_HOSTS, optional=True)
        if app["availability"] not in AVAILABILITY:
            fail(f"Entry {idx}: invalid availability")
    if require_order and apps != sorted(apps, key=lambda a: a["name"].casefold()):
        fail("Entries must be ordered alphabetically A–Z by app name")
    return apps


def markdown_text(value: str) -> str:
    """Escape the delimiters that can break Markdown cells or link labels."""
    return (
        value.replace("\\", "\\\\").replace("|", "\\|")
        .replace("[", "\\[").replace("]", "\\]")
        .replace("<", "&lt;").replace(">", "&gt;")
    )


def render_markdown_table(apps: list[dict]) -> str:
    lines = [
        "| Application | Category | Developer | Public availability |",
        "| --- | --- | --- | --- |",
    ]
    for app in apps:
        lines.append(
            f"| [{markdown_text(app['name'])}](<{app['source_url']}>) | "
            f"{markdown_text(app['category'])} | "
            f"{markdown_text(app['developer'])} | "
            f"{markdown_text(app['availability'])} |"
        )
    return "\n".join(lines)


def load_apps(path, *, require_order=True) -> list[dict]:
    return validate_apps(json.loads(path.read_text(encoding="utf-8")),
                         require_order=require_order)
