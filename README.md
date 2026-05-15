# Dialogue Reviewer

A Python CLI tool that reviews game dialogue lines for character-voice consistency, powered by Claude.

## Overview

Game projects often accumulate thousands of dialogue lines across multiple writers, contractors, and localisation passes. Keeping each character's voice consistent — their register, vocabulary, rhythm, speech patterns — becomes hard to do by eye. Dialogue Reviewer reads dialogue from a Gridly project or a local CSV/XLSX/JSON file, reviews each line against a per-character "voice bible" using Claude, and produces a filterable HTML report of issues.

## Features (implemented)

- Input from Gridly REST API or local CSV / XLSX / JSON files

## Features (planned)

- Claude-generated character bibles, output as editable JSON so writers can review and refine before a full run
- Per-line review with surrounding context, returning structured severity / category / explanation
- Self-contained HTML report, filterable by character, severity, and category
- Profanity & sensitivity pass (follow-on extension)

## Status

In active development. Not yet production-ready.

## Requirements

- Python 3.13
- An Anthropic API key (for Claude integration)
- A Gridly API key and View ID (only if wanting to import dialogue from Gridly)

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

CLI is still being built — usage instructions will land here once we are at that stage of the project. Currently `main.py` is just used for testing the importers are working as expected.

## Licence

MIT — see [LICENSE](LICENSE).
