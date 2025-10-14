# Internship Automation Framework

A Python-based desktop automation framework focused on robust app preparation, visual verification (OpenCV), OCR-based interactions (Tesseract), and configurable objective sequences.

---

## Table of contents
- Overview
- Quick links
- Requirements
- Quick start
- Configuration
- Templates
- Testing
- Troubleshooting
- Contributing

---

## Overview

Top-level layout (important files and folders):

internship_automation/

- main.py — entry point and orchestration
- config.py — configuration management (loads config/config.json & instructions)
- workflow.py — objective execution engine (executes actions and handles retries/checkpoints)
- actions.py — action handlers (type, click, hotkey, verify)
- ui_detection.py — UI detection, template-matching, screenshots, OCR helpers
- verification.py — prerequisites & completion verification utilities
- window_ops.py — window management helpers (pygetwindow wrappers)
- notifications.py — email/notification helpers (dotenv + SMTP fallback)
- state.py — checkpoint and state management
- utils.py — small utilities (print_banner, etc.)
- cli_utils.py — CLI parsing helpers
- run_objective.py — utility script to run a single objective
- show_spotify_actions.py — utility script / debugging helpers for Spotify
- DOCUMENTATION.md — project documentation
- requirements.txt — dependencies for the project
- PROJECT_STATUS_OCTOBER_8_2025.md — project status notes

Packages:

- app_preparation/ — app launch/verification helpers
- objectives/ — objective parsing, handlers, mapping
- workflow/ — workflow manager & executor
- config/ — config files (config.json, instructions.json)
- tests/ — test suite and reports
- screenshots/ — runtime screenshots used by UI detection
- checkpoints/ — checkpoint JSON files created during runs
- __pycache__/ — compiled python files

---

## Quick links

- Config: `config/config.json`
- Objectives: `config/instructions.json`
- Main entrypoint: `main.py`
- Actions: `actions.py`
- Verification: `verification.py`
- Window ops: `window_ops.py`
- Tests: `tests/`

---

## Requirements

- Python 3.8+
- Windows 10/11 (desktop automation)
- Tesseract OCR (for OCR features)

Install dependencies:

```powershell
pip install -r requirements.txt
```

Install Tesseract (Windows):

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR\`
- Add to PATH or set `pytesseract.pytesseract.tesseract_cmd` in code

---

## Quick start

1. Clone the repo:

```powershell
git clone https://github.com/allthatgroove89/internship_automation
cd internship_automation
```

2. Edit `config/config.json` to add your app(s) and set `default_app`.
3. Edit `config/instructions.json` to define objectives and actions.

### Run examples

- Prepare the app only:

```powershell
python main.py Spotify
```

- Run a specific objective:

```powershell
python main.py Spotify spotify_search_metallica
```

- Run all objectives for an app:

```powershell
python main.py Spotify all
```

---

## Configuration

- The `config/config.json` file describes apps and global settings (retry policy, screenshot/log directories).
- Per-app config supports `process_presence_sufficient` to control whether a running process is treated as sufficient for preparing the app.

---

## Templates

- Visual verification templates are expected in `templates/` (e.g., `templates/spotify_titlebar.png`).
- You can use screenshots from `screenshots/` to craft templates.

---

## Testing

- Run the test suite:

```powershell
python tests/test_framework.py
```

- Run subsets with pytest:

```powershell
python -m pytest tests/ -k "app_preparation"
```

---

## Troubleshooting

- If templates are not found, verify paths in `config/config.json` and confirm PNG files exist under `templates/`.
- If Tesseract is not found, set the path in code or add to PATH.
- If windows are not detected reliably, the framework uses PID-first detection and an optional Windows Search fallback controlled by per-app config.

---

## Contributing

- Follow PEP8 and add tests for new features.
- Update `DOCUMENTATION.md` when changing behavior.

---

For more details, see `DOCUMENTATION.md` in the repo.
