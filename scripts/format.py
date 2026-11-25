#!/usr/bin/env python3
"""Render events.json and/or speakers.json (as written by fetch.py) as Markdown.

Each input file is written to a Markdown file of the same name next to it (events.json ->
events.md). The kind of file is detected from its top-level key ("events" or "speakers"), so
the files can be given in any order, and either one alone. Descriptions and biographies are
HTML and are passed through unchanged (Markdown allows inline HTML).

Usage: python3 scripts/format.py events.json speakers.json
"""

import json
import sys
from datetime import date
from pathlib import Path


def long_date(iso_date):
    return f"{date.fromisoformat(iso_date):%-d %B %Y}"


def header(title, extracted_at):
    return [f"# FOST Paris 2026: {title}", "", f"> Last update: {extracted_at}", "", "All times are local Paris time.", ""]


def render_events(events, extracted_at):
    lines = header("Events", extracted_at)
    day = None
    for e in events:
        if e["date"] != day:
            day = e["date"]
            lines += [f"## {long_date(day)}", ""]
        lines += [
            f"### {e['title']}",
            "",
            f"- Date: {long_date(e['date'])}",
            f"- Time: {e['start']}–{e['end']}",
        ]
        for label, key in (("Room", "rooms"), ("Conference", "conferences"), ("Track", "tracks")):
            if e[key]:
                lines.append(f"- {label}: {', '.join(e[key])}")
        lines.append(f"- Type: {e['type']}")
        if e["speakers"]:
            lines.append(f"- Speakers: {', '.join(s['name'] for s in e['speakers'])}")
        if e["description"]:
            lines += ["", e["description"]]
        lines.append("")
    return lines


def render_speakers(speakers, extracted_at):
    lines = header("Speakers", extracted_at)
    for s in speakers:
        lines += [f"### {s['name']}", ""]
        if s["jobtitle"]:
            lines.append(f"- Job title: {s['jobtitle']}")
        if s["company"]:
            lines.append(f"- Company: {s['company']}")
        if s["sessions"]:
            lines.append("- Sessions:")
            for session in s["sessions"]:
                lines.append(f"  - {session['title']} ({long_date(session['date'])}, {session['start']}–{session['end']})")
        if s["bio"]:
            lines += ["", s["bio"]]
        lines.append("")
    return lines


RENDERERS = {"events": render_events, "speakers": render_speakers}


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 scripts/format.py <events.json> <speakers.json>")
    for arg in sys.argv[1:]:
        path = Path(arg)
        data = json.loads(path.read_text(encoding="utf-8"))
        key = next((k for k in RENDERERS if k in data), None)
        if key is None:
            sys.exit(f"{path}: expected a top-level 'events' or 'speakers' key")
        output = path.with_suffix(".md")
        output.write_text("\n".join(RENDERERS[key](data[key], data["extracted_at"])), encoding="utf-8")
        print(f"Created {output} ({len(data[key])} {key})")


if __name__ == "__main__":
    main()
