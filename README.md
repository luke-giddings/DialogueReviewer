# Dialogue Reviewer

A Python CLI tool that reviews game dialogue lines for character-voice consistency, powered by Claude.

## Overview

Game projects often accumulate thousands of dialogue lines across multiple writers, contractors, and localisation passes. Keeping each character's voice consistent — their register, vocabulary, rhythm, speech patterns — becomes hard to do by eye. Dialogue Reviewer reads dialogue from a Gridly project or a local CSV/XLSX file, reviews each line against a per-character "voice bible" using Claude, and produces a filterable HTML report of issues.

## Features (planned)

- Input from Gridly REST API or local CSV / XLSX files
- Claude-generated character bibles, output as editable JSON so writers can review and refine before a full run
- Per-line review with surrounding context, returning structured severity / category / explanation
- Self-contained HTML report, filterable by character, severity, and category
- Profanity & sensitivity pass (follow-on extension)

## Status

In active development. Not yet production-ready.

## Requirements

- Python 3.13
- An Anthropic API key (for Claude integration)
- A Gridly API key (only if using the Gridly reader)

## Setup

```bash
# Clone
git clone https://github.com/<your-username>/<repo>.git
cd <repo>

# Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Dependencies
pip install -r requirements.txt

# Environment variables
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
# Then edit .env with your real keys.
```

## Usage

CLI is still being built — usage instructions will land here once `main.py` is in place.

## Licence

MIT — see [LICENSE](LICENSE).
