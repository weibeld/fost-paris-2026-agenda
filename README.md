# FOST Paris 2026 Agenda Data

Extract of the full agenda of [FOST Paris 2026](https://joinfost.io/events/paris#agenda) (1–3 December 2026): all events (talks, workshops, keynotes, panels, etc.) and all speakers.

The data is meant to be used with an LLM agent so that it can answer questions about the agenda.

## Contents

- **`events.json`, `speakers.json`:** the data extracted from the original source (suited to agents that process the data with code)
- **`events.md`, `speakers.md`:** the same data as in the JSON files converted to a more compact Markdown format (suited to agents that process the data as text)
- **`scripts/fetch.py`:** fetches the agenda from the website and writes `events.json` and `speakers.json`
- **`scripts/format.py`:** renders `events.json` and `speakers.json` in Markdown as `events.md` and `speakers.md`

## How it works

The agenda on the FOST website is rendered by JavaScript inside two iframes served by `portal.joinfost.io`, one for the agenda and one for the speakers. No browser is needed, however, because both iframe pages embed their data directly in the HTML. `fetch.py` downloads both pages, extracts the embedded data and writes it to `events.json` and `speakers.json`. The few changes made to the source data, such as converting timestamps to local Paris dates and times, are documented at the top of `fetch.py`.

`format.py` takes one or both JSON files in any order and writes a Markdown file of the same name next for each one.

## Usage

> Requires Python 3.9 or later (no other dependencies).

To regenerate all data from the live website:

```bash
python3 scripts/fetch.py                               # writes events.json and speakers.json
python3 scripts/format.py events.json speakers.json    # writes events.md and speakers.md
```

Programme data may still change before the conference, so re-run the above scripts occasionally, in order to pick up agenda changes.
