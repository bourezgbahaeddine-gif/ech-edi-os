#!/usr/bin/env python3
"""
Import OPML feed list into `sources` table.

Usage:
  python scripts/import_opml_to_sources.py \
    --opml-url http://news.bbc.co.uk/rss/feeds.opml \
    --db-url postgresql://echorouk:PASS@127.0.0.1:5433/echorouk_db

  python scripts/import_opml_to_sources.py \
    --opml-file ./freshrss_master_clean.opml \
    --db-url postgresql://echorouk:PASS@127.0.0.1:5433/echorouk_db
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import psycopg2
from psycopg2.extras import execute_values


def _clean_text(value: str | None, fallback: str = "") -> str:
    return (value or fallback).strip()


def _walk_outlines(element: ET.Element, category: str | None = None) -> list[dict[str, str]]:
    feeds: list[dict[str, str]] = []
    for outline in element.findall("outline"):
        xml_url = outline.attrib.get("xmlUrl")
        if xml_url:
            title = (
                outline.attrib.get("title")
                or outline.attrib.get("text")
                or urlparse(xml_url).netloc
            )
            feeds.append(
                {
                    "title": _clean_text(title, urlparse(xml_url).netloc),
                    "xml_url": _clean_text(xml_url),
                    "html_url": _clean_text(outline.attrib.get("htmlUrl")),
                    "language": _clean_text(outline.attrib.get("language")),
                    "priority": _clean_text(outline.attrib.get("priority")),
                    "category": _clean_text(category, "general"),
                }
            )
            continue

        next_category = (
            outline.attrib.get("text")
            or outline.attrib.get("title")
            or category
            or "general"
        )
        feeds.extend(_walk_outlines(outline, next_category))
    return feeds


def parse_opml_content(content: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(content)
    body = root.find("body")
    feeds = _walk_outlines(body if body is not None else root, "general")
    uniq: dict[str, dict[str, str]] = {}
    for feed in feeds:
        uniq[feed["xml_url"]] = feed
    return list(uniq.values())


def parse_opml_url(url: str) -> list[dict[str, str]]:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return parse_opml_content(resp.content)


def parse_opml_file(path: str) -> list[dict[str, str]]:
    return parse_opml_content(Path(path).read_bytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--opml-url")
    source.add_argument("--opml-file")
    ap.add_argument("--db-url", required=True)
    ap.add_argument("--prefix", default="")
    ap.add_argument("--default-language", default="ar")
    ap.add_argument("--default-priority", type=int, default=5)
    ap.add_argument("--default-category", default="general")
    args = ap.parse_args()

    feeds = parse_opml_url(args.opml_url) if args.opml_url else parse_opml_file(args.opml_file)
    if not feeds:
        print("No feeds found in OPML.")
        return 1

    rows = []
    now = datetime.utcnow()
    for feed in feeds:
        title = feed["title"]
        xml_url = feed["xml_url"]
        prefix = f"{args.prefix} - " if args.prefix else ""
        name = f"{prefix}{title}"[:255]
        language = feed["language"] or args.default_language
        category = (feed["category"] or args.default_category).strip().lower().replace(" ", "_")
        try:
            priority = int(feed["priority"]) if feed["priority"] else args.default_priority
        except ValueError:
            priority = args.default_priority
        rows.append(
            (
                name,
                "rss",
                xml_url,
                xml_url,
                category,
                language,
                "aggregator",
                "medium",
                priority,
                True,
                now,
                now,
            )
        )

    conn = psycopg2.connect(args.db_url)
    try:
        with conn, conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO sources
                (name, method, url, rss_url, category, language, source_type, credibility, priority, enabled, created_at, updated_at)
                VALUES %s
                ON CONFLICT (url) DO UPDATE
                SET
                    name = EXCLUDED.name,
                    rss_url = EXCLUDED.rss_url,
                    category = EXCLUDED.category,
                    language = EXCLUDED.language,
                    priority = EXCLUDED.priority,
                    enabled = true,
                    updated_at = now()
                """,
                rows,
            )
        print(f"Imported/updated {len(rows)} feeds.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
