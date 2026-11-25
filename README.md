# FOST Paris 2026 Agenda Data

Extract of the full list of events and speakers of [FOST Paris 2026](https://joinfost.io/events/paris#agenda) (1-3 December 2026) as JSON and Markdown files.

> **Last update:** 2026-11-25T16:22:30+01:00

## Data files

| File                             | Content                                                                                             |
|:---------------------------------|:----------------------------------------------------------------------------------------------------|
| [`events.json`](events.json)     | All events (talks, workshops, keynotes, panels, breaks, etc.) as extracted from the original source |
| [`events.md`](events.md)         | The most important data in `events.json` converted to Markdown                                      |
| [`speakers.json`](speakers.json) | All speakers as extracted from the original source                                                  |
| [`speakers.md`](speakers.md)     | The most important data in `speakers.json` converted to Markdown                                    |

> Note: the JSON files are suited to agents that process the data with code, the Markdown files to agents that process the data as text.

## Data sources

The data is extracted from two iframes served by <https://portal.joinfost.io>, one for the events and one for the speakers:

- **Events:** <https://portal.joinfost.io/embed/5e27c773-7fa8-4169-b6a7-93494701212a/program/5e27c773-7fa8-4169-b6a7-93494701212a?style=fost>
- **Speakers:** <https://portal.joinfost.io/embed/5e27c773-7fa8-4169-b6a7-93494701212a/speakers?program=5e27c773-7fa8-4169-b6a7-93494701212a&style=fost>

## Extraction

The extraction consists of two steps, each done by a script in `scripts/`:

- [`fetch.py`](scripts/fetch.py): fetches the agenda from the website and writes `events.json` and `speakers.json`
- [`format.py`](scripts/format.py): generates `events.md` and `speakers.md` from `events.json` and `speakers.json`

No browser is needed for the first step, even though the agenda is rendered by JavaScript, because both iframe pages embed their data directly in the HTML: the events page contains a `<script>` block with a JSON object holding all sessions, and the speakers page contains one HTML-escaped JSON attribute per speaker. `fetch.py` downloads both pages, extracts the embedded data and writes it to `events.json` and `speakers.json`, together with the source URL and the time of the extraction.

> Note: changes made to the source data (such as converting timestamps to local Paris dates and times and renaming some fields) are documented in the `fetch.py` script as comments.

There is also an [`update.py`](scripts/update.py) script that combines both of the above steps: it runs `fetch.py` and `format.py` and also sets the "Last update" line at the top of this README.

## Usage

The most straightforward usage is to run the `update.py` script to re-fetch the data from the source and generate all of the JSON and Markdown files in a single step:

```bash
python3 scripts/update.py
```

Since the agenda data is gradually being completed as the conference approaches, the data should be repeatedly re-extracted.
