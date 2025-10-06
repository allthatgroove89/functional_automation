import subprocess
import time
import pyautogui
import pygetwindow as gw


def launch_app(app_path, startup_delay=2, args=None):
    """Launch application and wait"""
    cmd = [app_path]
    if args:
        cmd.extend(args)
    subprocess.Popen(cmd)
    time.sleep(startup_delay)
    return True


def find_window(app_name):
    """Find window by title"""
    windows = gw.getWindowsWithTitle(app_name)
    return windows[0] if windows else None


def focus_window(window):
    """Focus a window"""
    if not window:
        return False
    try:
        window.activate()
        time.sleep(0.5)
        return True
    except:
        return False


def maximize_window(window):
    """Maximize window"""
    if not window:
        return False
    try:
        window.maximize()
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Failed to maximize window: {e}")
        # Fallback to keyboard shortcut
        pyautogui.hotkey('win', 'up')
        time.sleep(0.5)
        return True


def is_window_maximized(window):
    """Check if window is maximized"""
    if not window:
        return False
    
    screen_w, screen_h = pyautogui.size()
    """ gets the rectangle information of the window """
    rect = window._rect

    # Calculate window ratio
    width_ratio = rect.width / screen_w
    height_ratio = rect.height / screen_h
    
    return width_ratio >= 0.8 and height_ratio >= 0.8

