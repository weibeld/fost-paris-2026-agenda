#!/usr/bin/env python3
"""Update all data files from the live website and set the "Last update" line in README.md.

Runs the following steps in the repository root (independent of the current directory):

1. fetch.py: writes sessions.json and speakers.json
2. format.py: writes sessions.md and speakers.md
3. sets the "> Last update: ..." line in README.md to the extraction time in sessions.json

Usage: python3 scripts/update.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
README = ROOT / "README.md"
# Matches "> Last update: ..." with or without the label in bold; group 1 is everything before the value
LAST_UPDATE = re.compile(r"^(> (?:\*\*)?Last update:(?:\*\*)? ).*$", flags=re.M)


def run(script, *args):
    """Run a script (its output goes straight to the terminal); stop on failure."""
    print(f"> Running {script}...", flush=True)
    result = subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"{script} failed with exit code {result.returncode}")


def update_readme():
    extracted_at = json.loads((ROOT / "sessions.json").read_text(encoding="utf-8"))["extracted_at"]
    readme = README.read_text(encoding="utf-8")
    if not LAST_UPDATE.search(readme):
        sys.exit(f"{README}: no '> Last update: ...' line found")
    # Keep the label as it is in the README (e.g. bold) and replace only the value
    README.write_text(LAST_UPDATE.sub(lambda m: m.group(1) + extracted_at, readme, count=1), encoding="utf-8")
    print(f'> Set "Last update" of {README.name} to {extracted_at}')


def main():
    run("fetch.py", ".")
    run("format.py", "sessions.json", "speakers.json")
    update_readme()


if __name__ == "__main__":
    main()
