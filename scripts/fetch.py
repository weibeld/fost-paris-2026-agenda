#!/usr/bin/env python3
"""Fetch the FOST Paris 2026 programme and write it to sessions.json and speakers.json.

The agenda on https://joinfost.io/events/paris is rendered from two iframes served by
portal.joinfost.io. Both pages embed their data directly in the HTML:

- program page: a <script> block holding a JSON object with all sessions
- speakers page: one HTML-escaped JSON attribute per speaker (including biography)

Changes compared to the source data:

- whitespace in titles, names, job titles, companies, rooms, conferences and tracks is collapsed
- line endings in descriptions and biographies are normalised to LF (some source biographies use CRLF)
- UNIX timestamps are converted to local Paris date ("2026-12-01") and times ("09:00")
- fields are renamed: uuid -> id, type_label -> type, places -> rooms, calendars -> conferences,
  tags -> tracks
- internal fields are dropped: position, new_slot, the IDs of rooms, conferences and tracks,
  track colours, and speaker photos within sessions
- the speakers' session lists ("Tue, Dec 1 · 9:00 AM – 9:20 AM" text in the source) are
  rebuilt from the sessions data as title, date, start and end
- sessions are sorted by start time, speakers by name

Usage: python3 scripts/fetch.py [output_dir]
"""

import html
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

EVENT_ID = "5e27c773-7fa8-4169-b6a7-93494701212a"
BASE_URL = f"https://portal.joinfost.io/embed/{EVENT_ID}"
PROGRAM_URL = f"{BASE_URL}/program/{EVENT_ID}?style=fost"
SPEAKERS_URL = f"{BASE_URL}/speakers?program={EVENT_ID}&style=fost"
SOURCE_URL = "https://joinfost.io/events/paris#agenda"
TIMEZONE = ZoneInfo("Europe/Paris")


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def squash(value):
    """Collapse all whitespace runs into single spaces."""
    return " ".join((value or "").split())


def normalize_newlines(value):
    """Convert Windows (CRLF) and old Mac (CR) line endings to LF and strip surrounding whitespace."""
    return (value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def to_local(timestamp):
    return datetime.fromtimestamp(timestamp, TIMEZONE)


def load_sessions():
    page = fetch(PROGRAM_URL)
    for script in re.findall(r"<script[^>]*>(.*?)</script>", page, flags=re.S):
        script = script.strip()
        if script.startswith('{"event"'):
            return json.loads(script)["sessions"]
    raise RuntimeError("Session data not found in program page")


def load_speakers():
    page = fetch(SPEAKERS_URL)
    speakers = [json.loads(html.unescape(a)) for a in re.findall(r'="(\{&quot;name&quot;[^"]*)"', page)]
    if not speakers:
        raise RuntimeError("Speaker data not found in speakers page")
    return speakers


def convert_session(session):
    start, end = to_local(session["date_start"]), to_local(session["date_end"])
    return {
        "id": session["uuid"],
        "title": squash(session["title"]),
        "type": session["type_label"],
        "date": start.strftime("%Y-%m-%d"),
        "start": start.strftime("%H:%M"),
        "end": end.strftime("%H:%M"),
        "rooms": [squash(x["title"]) for x in session["places"]],
        "conferences": [squash(x["title"]) for x in session["calendars"]],
        "tracks": [squash(x["title"]) for x in session["tags"]],
        "speakers": [
            {"name": squash(s["name"]), "jobtitle": squash(s.get("jobtitle")), "company": squash(s.get("company"))}
            for s in session["speakers"]
        ],
        "description": normalize_newlines(session["description"]),
    }


def convert_speaker(speaker, sessions_by_speaker):
    name = squash(speaker["name"])
    return {
        "name": name,
        "jobtitle": squash(speaker.get("jobtitle")),
        "company": squash(speaker.get("company")),
        "bio": normalize_newlines(speaker.get("bio")),
        "avatar": speaker.get("avatar"),
        "sessions": sessions_by_speaker.get(name, []),
    }


def write_json(path, items, key):
    data = {
        "source": SOURCE_URL,
        "extracted_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
        "timezone": str(TIMEZONE),
        key: items,
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_sessions = sorted(load_sessions(), key=lambda s: (s["date_start"], s["date_end"], squash(s["title"])))
    sessions = [convert_session(s) for s in raw_sessions]

    sessions_by_speaker = {}
    for session in sessions:
        summary = {key: session[key] for key in ("title", "date", "start", "end")}
        for speaker in session["speakers"]:
            sessions_by_speaker.setdefault(speaker["name"], []).append(summary)

    raw_speakers = sorted(load_speakers(), key=lambda s: squash(s["name"]).casefold())
    speakers = [convert_speaker(s, sessions_by_speaker) for s in raw_speakers]

    sessions_path, speakers_path = output_dir / "sessions.json", output_dir / "speakers.json"
    write_json(sessions_path, sessions, "sessions")
    print(f"Created {sessions_path} ({len(sessions)} sessions)")
    write_json(speakers_path, speakers, "speakers")
    print(f"Created {speakers_path} ({len(speakers)} speakers)")


if __name__ == "__main__":
    main()
