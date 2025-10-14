# Functional Automation Framework

A Python-based desktop automation framework focused on robust app preparation, visual verification (OpenCV), OCR-based interactions (Tesseract), and configurable objective sequences.

internship_automation/
├── main.py                      Entry point and orchestration
├── config.py                    Configuration management (loads config/config.json & instructions)
├── workflow.py                  Objective execution engine (executes actions and handles retries/checkpoints)
├── actions.py                   Action handlers (type, click, hotkey, verify)
├── ui_detection.py              UI detection, template-matching, screenshots, OCR helpers
├── verification.py              Prerequisites & completion verification utilities
├── window_ops.py                Window management helpers (pygetwindow wrappers)
├── notifications.py             Email/notification helpers (dotenv + SMTP fallback)
├── state.py                     Checkpoint and state management
├── utils.py                     Small utilities (print_banner, etc.)
├── cli_utils.py                 CLI parsing helpers
├── run_objective.py             Utility script to run a single objective
├── show_spotify_actions.py      Utility script / debugging helpers for Spotify
├── DOCUMENTATION.md             Project documentation
├── README.md                    Project README
├── requirements.txt             Dependencies for the project
├── PROJECT_STATUS_OCTOBER_8_2025.md
├── app_preparation/             Package: app launch/verification helpers
│   ├── __init__.py
│   ├── app_launcher.py
│   ├── app_maximizer.py
│   └── app_verifier.py
├── objectives/                  Package: objective parsing, handlers, mapping
│   ├── __init__.py
│   ├── handlers.py
│   ├── json_parser.py
│   ├── mapping.py
│   ├── objective_filter.py
│   └── objective_notifier.py
├── workflow/                    Package: workflow manager & executor
│   ├── __init__.py
│   ├── workflow_manager.py
│   └── workflow_executor.py
├── config/                      Configuration files
│   ├── config.json              Application settings (apps list, defaults)
│   └── instructions.json        Objectives and action sequences
├── tests/                       Test suite and reports
│   ├── test_framework.py        Comprehensive test harness
│   ├── simple_click_test.py
│   ├── simple_click_actions.py
│   ├── quick_click_test.py
│   ├── demo_click_actions.py
│   ├── run_spotify_objective.py
│   ├── test_spotify_open.py
│   ├── test_report_20251007_121801.json
│   ├── test_report_20251013_214404.json
│   └── test_report_20251013_214438.json
├── screenshots/                 Runtime screenshots used by UI detection
├── checkpoints/                 Checkpoint JSON files created during runs
└── __pycache__/                 Compiled Python files

## Quick links
- Config: `config/config.json`
- Objectives: `config/instructions.json`
- Main entrypoint: `main.py`
- Actions: `actions.py`
- Verification: `verification.py`
- Window ops: `window_ops.py`
- Tests: `tests/`

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

## Configuration
- The `config/config.json` file describes apps and global settings (retry policy, screenshot/log directories).
- Per-app config supports `process_presence_sufficient` to control whether a running process is treated as sufficient for preparing the app.

## Templates
- Visual verification templates are expected in `templates/` (e.g., `templates/spotify_titlebar.png`).
- You can use screenshots from `screenshots/` to craft templates.

## Testing
- Run the test suite:

```powershell
python tests/test_framework.py
```

- Run subsets with pytest:

```powershell
python -m pytest tests/ -k "app_preparation"
```

## Troubleshooting
- If templates are not found, verify paths in `config/config.json` and confirm PNG files exist under `templates/`.
- If Tesseract is not found, set the path in code or add to PATH.
- If windows are not detected reliably, the framework uses PID-first detection and an optional Windows Search fallback controlled by per-app config.

## Contributing
- Follow PEP8 and add tests for new features.
- Update `DOCUMENTATION.md` when changing behavior.

---

For more details, see `DOCUMENTATION.md` in the repo.
