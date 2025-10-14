"""Spotify objective handlers (clean, single-copy).

This module provides four simple handlers that delegate to the core
executor where appropriate. The previous-track handler includes a layered
strategy (template -> approximate click -> configured actions -> final
media-key fallback) and saves diagnostic screenshots when fallbacks are
used.
"""

import time


def _run_configured_actions(objective, config, session_id):
    """Run the objective's configured action list via the core executor.

    Uses execute_single_objective_no_dispatch to avoid re-dispatching back
    into handlers (prevents recursion).
    """
    try:
        from workflow.workflow_executor import execute_single_objective_no_dispatch
        return execute_single_objective_no_dispatch(objective, config, session_id)
    except Exception as e:
        print(f"  [ERROR] Unable to run configured actions: {e}")
        return False


def spotify_play(objective, config, session_id=None):
    return _run_configured_actions(objective, config, session_id)


def spotify_pause(objective, config, session_id=None):
    return _run_configured_actions(objective, config, session_id)


def spotify_next_track(objective, config, session_id=None):
    return _run_configured_actions(objective, config, session_id)


def spotify_previous_track(objective, config, session_id=None):
    """Attempt to trigger Spotify previous track with multiple strategies.

    Returns True on success, False otherwise.
    """
    try:
        import ui_detection
        import pyautogui
        from window_ops import find_window, focus_window
    except Exception:
        print("  [ERROR] UI modules unavailable for spotify_previous_track")
        return False

    app_name = objective.get('app', 'Spotify')
    before_win = find_window(app_name)
    before_title = before_win.title if before_win else None

    # 1) Template click
    try:
        if ui_detection.find_and_click_template('templates/spotify_previous_button.png', threshold=0.6, delay=0.25):
            time.sleep(0.18)
            after_win = find_window(app_name)
            after_title = after_win.title if after_win else None
            if before_title and after_title and before_title != after_title:
                return True
    except Exception:
        pass

    # 2) Approximate window-relative click (save diagnostics)
    try:
        win = find_window(app_name)
        if win:
            focus_window(win)
            time.sleep(0.06)
            left, top, w, h = win.left, win.top, win.width, win.height
            x = int(left + w / 2 - 45)
            y = int(top + h - 70)
            ui_detection.take_screenshot('screenshots/prev_click_before.png')
            pyautogui.click(x, y)
            time.sleep(0.18)
            ui_detection.take_screenshot('screenshots/prev_click_after.png')
            after_win = find_window(app_name)
            after_title = after_win.title if after_win else None
            if before_title and after_title and before_title != after_title:
                return True
    except Exception as e:
        print(f"  [WARN] Approximate UI click failed: {e}")

    # 3) Run configured actions (treat success as success to avoid false-negatives)
    try:
        ran = _run_configured_actions(objective, config, session_id)
        if ran:
            print("  [INFO] Configured actions executed; treating as success")
            return True
    except Exception as e:
        print(f"  [WARN] Running configured actions failed: {e}")

    # 4) Final fallback: send extra media 'previous_track' (twice) and save debug screenshots
    try:
        from actions import execute_action
        ui_detection.take_screenshot('screenshots/prev_debug_before.png')
        # Some players restart the current song on first 'previous' press — send it twice
        print("  [INFO] Final fallback: sending 'previous_track' hotkey twice")
        execute_action({'type': 'hotkey', 'keys': ['previous_track']})
        time.sleep(0.12)
        execute_action({'type': 'hotkey', 'keys': ['previous_track']})
        time.sleep(0.25)
        ui_detection.take_screenshot('screenshots/prev_debug_after.png')
        final_win = find_window(app_name)
        final_title = final_win.title if final_win else None
        if before_title and final_title and before_title != final_title:
            return True
        print("  [WARN] previous did not appear to change; saved debug screenshots")
        return False
    except Exception as e:
        print(f"  [ERROR] Final fallback failed: {e}")
        return False


