"""
App Launcher Module
Handles checking if application is open and launching if needed
Following clean workflow steps with proper error handling
"""

import time
import subprocess
import psutil
import shutil
import os
from window_ops import find_window, launch_app
from notifications import notify_error
import pyautogui


def is_spotify_running():
    """Check if Spotify process is running"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and 'spotify' in proc.info['name'].lower():
                return True
        return False
    except Exception as e:
        print(f"  [WARN] Error checking Spotify process: {e}")
        return False


def resolve_app_path(app_path):
    """Resolve an application path: expand vars, check existence, which/where lookup."""
    if not app_path:
        return None

    try:
        # Expand env vars and user
        expanded = os.path.expandvars(os.path.expanduser(app_path))
        if os.path.isabs(expanded) and os.path.exists(expanded):
            return expanded

        # Try shutil.which for executables in PATH
        which_found = shutil.which(app_path)
        if which_found:
            return which_found

        # On Windows try 'where' as a last resort
        try:
            res = subprocess.run(['where', app_path], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout:
                first = res.stdout.splitlines()[0].strip()
                if os.path.exists(first):
                    return first
        except Exception:
            pass

    except Exception as e:
        print(f"  [WARN] Error resolving app path: {e}")

    return None


def is_process_running_for_path(exec_path):
    """Check running processes to find one matching exec_path (by absolute path or basename)."""
    if not exec_path:
        return False

    try:
        norm_target = None
        if os.path.isabs(exec_path):
            try:
                norm_target = os.path.normcase(os.path.abspath(exec_path))
            except Exception:
                norm_target = None

        target_basename = os.path.basename(exec_path).lower()

        for proc in psutil.process_iter(['pid', 'exe', 'cmdline', 'name']):
            try:
                exe = proc.info.get('exe')
                if exe:
                    try:
                        exe_norm = os.path.normcase(os.path.abspath(exe))
                    except Exception:
                        exe_norm = None
                    if norm_target and exe_norm == norm_target:
                        return True
                    if os.path.basename(exe).lower() == target_basename:
                        return True

                # Fallback: check cmdline[0]
                cmd = proc.info.get('cmdline')
                if cmd and len(cmd) > 0:
                    cmd0 = cmd[0]
                    if os.path.isabs(cmd0):
                        try:
                            cmd0_norm = os.path.normcase(os.path.abspath(cmd0))
                        except Exception:
                            cmd0_norm = None
                        if norm_target and cmd0_norm == norm_target:
                            return True
                    if os.path.basename(cmd0).lower() == target_basename:
                        return True

                # Last resort: compare process name
                name = proc.info.get('name')
                if name and name.lower() == target_basename:
                    return True

            except Exception:
                continue
    except Exception as e:
        print(f"  [WARN] Error scanning processes: {e}")

    return False


def click_spotify_icon():
    """Open Spotify using Windows search - SIMPLE"""
    try:
        print("  [INFO] Opening Spotify via Windows search...")
        # Use Windows key + search (most reliable)
        pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.typewrite('spotify', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(4)  # Give it time to launch
        return True
    except Exception as e:
        print(f"  [WARN] Windows search method failed: {e}")
        return False


def safe_find_window(app_name):
    """Safely find window with error handling"""
    if not app_name or not isinstance(app_name, str):
        print(f"  [WARN] Invalid app_name provided: {app_name}")
        return None
    
    try:
        window = find_window(app_name)
        return window
    except Exception as e:
        print(f"  [WARN] Window search failed for '{app_name}': {e}")
        return None


def launch_application(app_name, app_config, max_retries=3):
    """Get Application ready for action - with proper error handling.

    Returns True if the application is ready (either already open or launched successfully),
    or False if it could not be ensured running.
    """

    # Validate inputs
    if not app_name or not isinstance(app_name, str):
        print(f"[ERROR] Invalid app_name provided")
        return False

    print(f"Checking if {app_name} is already open...")

    # Resolve path from config
    resolved_path = None
    if app_config and app_config.get('path'):
        try:
            resolved_path = resolve_app_path(app_config.get('path'))
            if resolved_path:
                print(f"  [INFO] Resolved app path: {resolved_path}")
        except Exception as e:
            print(f"  [WARN] Could not resolve path: {e}")
            resolved_path = None

    # Quick window check - is it already open?
    window = safe_find_window(app_name)
    if window:
        print(f"[OK] {app_name} is already open - reusing existing instance")
        return True

    # Check if process is running (might be open but window not detected)
    if resolved_path:
        print(f"  [INFO] Checking for running process...")
        if is_process_running_for_path(resolved_path):
            print(f"  [OK] Found running process for {app_name}")
            # Give it a few chances to find the window
            for i in range(3):
                time.sleep(1)
                window = safe_find_window(app_name)
                if window:
                    print(f"[OK] {app_name} window found after {i+1} check(s)")
                    return True
            # If the process is running but window wasn't found, only treat as available
            # if the app_config indicates process presence is sufficient.
            try:
                if isinstance(app_config, dict) and app_config.get('process_presence_sufficient', True):
                    print(f"  [WARN] Process running but window not visible - treating as available")
                    return True
                else:
                    print(f"  [WARN] Process running but window not visible - will attempt to surface window")
            except Exception:
                print(f"  [WARN] Process running but window not visible - treating as available")
                return True

    # SPOTIFY SPECIFIC LAUNCH LOGIC
    if app_name.lower() == 'spotify':
        print(f"Opening Spotify...")

        # Decide whether process presence should be treated as sufficient.
        # This is configurable per-app via `process_presence_sufficient` in the app's config.
        # Default behavior: True (backwards compatible).
        process_presence_sufficient = True
        try:
            if isinstance(app_config, dict) and 'process_presence_sufficient' in app_config:
                process_presence_sufficient = bool(app_config.get('process_presence_sufficient'))
        except Exception:
            process_presence_sufficient = True

        # If process is already running and the config says that's sufficient, return True
        try:
            if process_presence_sufficient and is_spotify_running():
                print(f"  [INFO] Spotify process detected - treating process presence as sufficient")
                return True
        except Exception:
            pass

        # Attempts are fixed to 3 (no count configuration allowed)
        max_attempts = 3
        attempts_done = 0

        # Method 1: Try executable launch first, while we still have attempts left
        if resolved_path:
            while attempts_done < max_attempts:
                attempts_done += 1
                try:
                    print(f"  [ATTEMPT {attempts_done}/{max_attempts}] Launching via executable: {resolved_path}")
                    startup_delay = app_config.get('startup_delay', 3) if app_config else 3
                    launch_app(resolved_path, startup_delay)
                    # Wait for Spotify to start and surface a window
                    time.sleep(startup_delay)

                    for check in range(5):
                        window = safe_find_window('Spotify')
                        if window:
                            print(f"[OK] Spotify opened successfully via executable")
                            return True
                        time.sleep(1)

                    # If process exists now, treat as available only if toggle allows it
                    try:
                        if process_presence_sufficient and is_spotify_running():
                            print(f"  [OK] Spotify process started (no visible window) - treating as available")
                            return True
                    except Exception:
                        pass

                except Exception as e:
                    print(f"  [WARN] Executable launch attempt failed: {e}")

        # If still not available and we still have attempts left, try Windows search
        # Only attempt Windows search if no Spotify process exists (respect user preference)
        while attempts_done < max_attempts:
            try:
                if is_spotify_running():
                    # Honor the per-app toggle: only treat process presence as sufficient when allowed
                    if process_presence_sufficient:
                        print(f"  [INFO] Spotify process detected during attempts - treating as sufficient")
                        return True
                    else:
                        print(f"  [INFO] Spotify process detected during attempts - config requires window; continuing attempts")
            except Exception:
                pass

            attempts_done += 1
            print(f"  [ATTEMPT {attempts_done}/{max_attempts}] Using Windows search fallback...")
            if click_spotify_icon():
                for check in range(5):
                    window = safe_find_window('Spotify')
                    if window:
                        print(f"[OK] Spotify opened successfully via Windows search")
                        return True
                    time.sleep(1)

                try:
                    if process_presence_sufficient and is_spotify_running():
                        print(f"  [OK] Spotify process started after Windows search - treating as available")
                        return True
                except Exception:
                    pass

        # All attempts exhausted
        print(f"[FAIL] Could not open Spotify after {max_attempts} attempt(s)")
        notify_error(f"Failed to open Spotify after {max_attempts} attempt(s)", "support")
        return False

    # GENERIC APPLICATION LAUNCH (non-Spotify)
    print(f"{app_name} not found, launching...")
    
    for attempt in range(1, max_retries + 1):
        print(f"  Launch attempt {attempt}/{max_retries}")
        
        try:
            launch_path = resolved_path or (app_config.get('path') if app_config else None)
            launch_args = app_config.get('args') if app_config else None
            startup_delay = app_config.get('startup_delay', 2) if app_config else 2

            if not launch_path:
                print(f"[ERROR] No launch path available for {app_name}")
                break

            # Launch the application
            launch_app(launch_path, startup_delay, launch_args)
            
            # Wait for it to start
            time.sleep(startup_delay)
            
            # Check if window appeared (multiple attempts)
            for check in range(5):
                window = safe_find_window(app_name)
                if window:
                    print(f"[OK] {app_name} successfully launched on attempt {attempt}")
                    return True
                if check < 4:
                    time.sleep(1)
            
            print(f"[WARN] {app_name} not found after launch attempt {attempt}")

        except Exception as e:
            print(f"[ERROR] Launch attempt {attempt} failed: {str(e)}")

        # Wait before retry
        if attempt < max_retries:
            print(f"  Waiting before retry...")
            time.sleep(2)

    # All attempts exhausted
    print(f"[FAIL] Failed to launch {app_name} after {max_retries} attempts")
    notify_error(f"Failed to launch {app_name} after {max_retries} attempts", app_name)
    return False
