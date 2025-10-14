# 🚀 Internship Automation Framework - Complete Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Testing Framework](#testing-framework)
8. [Error Handling](#error-handling)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## 🎯 Project Overview

The Functional Automation Framework is a comprehensive Python-based automation system designed to automate desktop applications with robust error handling, verification systems, and intelligent UI detection.

### ✨ Key Features
- **Multi-Action Support**: Text typing, clicking, hotkeys, OCR-based interactions
- **Template Matching**: OpenCV-based image recognition
- **OCR Integration**: Text detection and interaction using Tesseract
- **Prerequisite System**: Action dependencies and verification
- **Error Handling**: Multiple error strategies with rollback capabilities
- **Email Notifications**: Automated failure reporting
- **Testing Framework**: Comprehensive test suite
- **Configuration-Driven**: JSON-based objective definitions

## 🏗️ Architecture

### Core Components

```
functional_automation/
├── main.py                 # Entry point and orchestration
├── config.py              # Configuration management
├── workflow.py             # Objective execution engine
├── actions.py              # Action handlers
├── ui_detection.py         # UI detection and OCR
├── verification.py         # Prerequisites and completion verification
├── window_ops.py           # Window management
├── notifications.py        # Email notification system
├── state.py                # Checkpoint and state management
├── utils.py                # Utility functions
├── config/
│   ├── config.json         # Application settings
│   └── instructions.json   # Objectives and actions
└── tests/
    ├── test_framework.py   # Comprehensive testing
    └── [other test files]
```

### Data Flow

```
1. Configuration Loading → 2. App Preparation → 3. Objective Execution → 4. Action Processing → 5. Verification → 6. Error Handling
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Windows 10/11 (for window operations)
- Tesseract OCR (for text detection)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/allthatgroove89/internship_automation
cd functional_automation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Tesseract OCR**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- Add to PATH or update `pytesseract.pytesseract.tesseract_cmd` in code

4. **Configure email settings** (optional)
```bash
# Create .env file
FROM_EMAIL=your-email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
TO_EMAIL=recipient@example.com
```

## ⚙️ Configuration

### Application Configuration (`config/config.json`)

```json
{
  "apps": [
    {
      "name": "Spotify",
      "path": "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe",
      "startup_delay": 3,
      "max_retries": 3,
      "verification_templates": [
        "templates/spotify_titlebar.png"
      ]
    }
  ],
  "default_app": "Spotify",
  "instructions_file": "config/instructions.json",
  "settings": {
    "screenshot_dir": "screenshots",
    "log_dir": "logs",
    "checkpoint_dir": "checkpoints",
    "email": {
      "enabled": true,
      "to": "user@example.com"
    },
    "retry": {
      "max_attempts": 3,
      "delay_seconds": 2
    }
  }
}
```

### Objectives Configuration (`config/instructions.json`)

```json
{
  "objectives": [
    {
      "id": "spotify_search_metallica",
      "name": "Spotify Search Metallica",
      "app": "Spotify",
      "actions": [
        {
          "type": "click_image",
          "template": "templates/spotify_search_box.png",
          "description": "Click search box",
          "prerequisites": ["app_maximized"],
          "error_strategy": "email_dev"
        },
        {
          "type": "type_text",
          "text": "Metallica",
          "description": "Type artist name into search",
          "prerequisites": [],
          "verification": {
            "type": "ocr_text",
            "text": "Metallica",
            "region": [200, 100, 600, 200]
          },
          "error_strategy": "rollback_all"
        },
        {
          "type": "click_image",
          "template": "templates/spotify_first_result.png",
          "description": "Click first search result",
          "prerequisites": [],
          "error_strategy": "email_dev"
        }
      ],
      "supported": true
    }
  ]
}
```

## 📖 Usage Guide

### Basic Usage

```bash
# Prepare app only
python main.py Notepad

# Execute specific objectives
python main.py Notepad notepad_basic_typing,notepad_delete_and_close

# Execute all objectives
python main.py Notepad all
```

### Advanced Usage

```python
from main import main
from config import load_config, get_objectives
from workflow import execute_objective

# Load configuration
config = load_config()

# Get objectives
supported, unsupported = get_objectives(config, ['notepad_basic_typing'])

# Execute objective
if supported:
    result = execute_objective(supported[0], config)
    print(f"Objective completed: {result}")
```

## 🔧 API Reference

### Core Functions

#### `main.py`
- `main()`: Main entry point
- `prepare_application(app_name, app_config)`: Prepare application
- `prepare_application_with_retry(app_name, app_config, max_retries)`: Prepare with retry logic

#### `workflow.py`
- `execute_objective(objective, config)`: Execute single objective
- `execute_action_with_retry(action, max_retries, context)`: Execute action with retry
- `handle_action_failure(action, history, failure_reason)`: Handle action failures
- `rollback_actions(history)`: Rollback completed actions

#### `actions.py`
- `execute_action(action)`: Execute any action type
- `execute_type_text(action)`: Type text
- `execute_click_text(action)`: Click on text using OCR
- `execute_click_image(action)`: Click on image template
- `execute_hotkey(action)`: Execute keyboard shortcuts

#### `ui_detection.py`
- `find_template(template_path, threshold, region, screenshot_path)`: Find template image
- `find_and_click_text(text, region, use_smart_crop, text_hint)`: Find and click text
- `take_screenshot(save_path)`: Take screenshot
- `detect_screen_change(previous_screenshot, current_screenshot)`: Detect screen changes

#### `verification.py`
- `verify_prerequisites(prerequisites, context)`: Verify action prerequisites
- `verify_action_complete(verification, context)`: Verify action completion
- `verify_screen_stable(timeout, check_interval)`: Verify screen stability
- `verify_ocr_text(expected_text, region)`: Verify text using OCR

### Action Types

| Action Type | Description | Parameters |
|-------------|-------------|------------|
| `type_text` | Type text | `text` |
| `hotkey` | Keyboard shortcut | `keys` (array) |
| `key_press` | Single key | `key` |
| `click_text` | Click on text | `text`, `region`, `confidence` |
| `click_image` | Click on image | `template`, `confidence`, `offset_x`, `offset_y` |
| `close_window` | Close window | `app_name` |
| `wait` | Wait/delay | `duration` |
| `verify_text` | Verify text present | `text`, `region`, `confidence` |
| `wait_for_text` | Wait for text | `text`, `timeout`, `region` |

### Prerequisites

| Prerequisite | Description |
|--------------|-------------|
| `app_maximized` | App window is maximized |
| `page_loaded` | Page finished loading |
| `search_complete` | Search operation complete |
| `element_present` | Specific element visible |

### Verification Types

| Verification Type | Description | Parameters |
|-------------------|-------------|------------|
| `template_match` | Template image found | `template`, `threshold`, `timeout` |
| `screen_change` | Screen changed | `previous_screenshot` |
| `ocr_text` | Text found via OCR | `text`, `region` |
| `element_at_location` | Element at specific location | `template`, `location`, `threshold` |
| `wait` | Simple wait | `duration` |

### Error Strategies

| Strategy | Description |
|----------|-------------|
| `retry_previous` | Retry previous action |
| `email_dev` | Email developer and continue |
| `rollback_all` | Rollback all actions and notify |

## 🧪 Testing Framework

### Running Tests

```bash
# Run comprehensive test suite
python tests/test_framework.py

# Run specific test categories
python -m pytest tests/ -k "app_preparation"
python -m pytest tests/ -k "action_execution"
```

### Test Categories

1. **App Preparation Testing**
   - App launches successfully (1st attempt)
   - App fails twice, succeeds on 3rd attempt
   - App fails all 3 attempts → Email sent

2. **Action Execution Testing**
   - All actions execute successfully
   - Action fails, retries succeed
   - Action fails all 3 attempts → Rollback + Email

3. **Objective Workflow Testing**
   - Single objective execution
   - Multiple objectives in sequence
   - Mixed supported/unsupported objectives

4. **Error Strategy Testing**
   - Strategy A: retry_previous
   - Strategy B: email_dev
   - Strategy C: rollback_all

5. **Email Notification Testing**
   - App preparation failure (3 attempts)
   - Action execution failure (3 attempts)
   - Unsupported objectives notification

### Test Report

Tests generate detailed JSON reports with:
- Test results and status
- Success/failure rates
- Error details
- Performance metrics
- Timestamp information

## 🚨 Error Handling

### Error Strategies

The framework supports three error handling strategies:

1. **retry_previous**: Retry the previous action
2. **email_dev**: Email developer and continue
3. **rollback_all**: Rollback all actions and notify

### Error Scenarios

- **App Preparation Failures**: Retry logic with email notifications
- **Action Execution Failures**: Multiple retry attempts with rollback
- **Prerequisite Failures**: Early detection and graceful handling
- **Verification Failures**: Retry with different verification methods

### Rollback Capabilities

- **Text Actions**: Undo typing with Ctrl+A + Backspace
- **Hotkey Actions**: Undo with Ctrl+Z
- **Click Actions**: Escape key to cancel
- **Window Actions**: Attempt to reopen (complex)

## 🔧 Troubleshooting

### Common Issues

1. **Tesseract Not Found**
   ```
   Error: pytesseract not installed
   Solution: Install Tesseract OCR and set path
   ```

2. **Template Not Found**
   ```
   Error: Template file not found
   Solution: Check template file paths in config
   ```

3. **Window Not Found**
   ```
   Error: Window 'AppName' not found
   Solution: Verify app is running and window title is correct
   ```

4. **OCR Accuracy Issues**
   ```
   Problem: Low OCR confidence
   Solution: Use smart cropping, adjust confidence thresholds
   ```

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Screenshot Debugging

Screenshots are automatically saved to `screenshots/` directory:
- `before_action.png`: Before action execution
- `after_action.png`: After action execution
- `stability_check_*.png`: Screen stability checks
- `ocr_*.png`: OCR processing images

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Update documentation
6. Submit pull request

### Code Standards

- Follow PEP 8 style guide
- Add docstrings to all functions
- Include type hints where possible
- Write comprehensive tests
- Update documentation

### Testing Requirements

- All new features must have tests
- Maintain >90% test coverage
- Include error scenario testing
- Update test documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review test reports for debugging
- Consult the API reference

---

**🎉 Congratulations! You now have a complete, production-ready automation framework with comprehensive testing, error handling, and documentation!**
