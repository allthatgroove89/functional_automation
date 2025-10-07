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
    """Focus a window with enhanced reliability"""
    if not window:
        return False
    try:
        # Method 1: Try window.activate()
        window.activate()
        time.sleep(0.5)
        
        # Method 2: Verify focus by checking if window is active
        if window.isActive:
            print(f"  [FOCUS] Window '{window.title}' is now active")
            return True
        else:
            print(f"  [WARN] Window activation may have failed, trying alternative method...")
            # Method 3: Click on window to force focus
            pyautogui.click(window.left + 10, window.top + 10)
            time.sleep(0.5)
            return True
            
    except Exception as e:
        print(f"  [ERROR] Failed to focus window: {e}")
        # Fallback: Try clicking on window
        try:
            pyautogui.click(window.left + 10, window.top + 10)
            time.sleep(0.5)
            return True
        except:
            return False


def maximize_window(window):
    """Maximize window with visual verification"""
    if not window:
        return False
    try:
        window.maximize()
        time.sleep(0.5)
        
        # Visual verification of maximization
        if is_window_maximized(window):
            print(f"  [VISUAL] Window '{window.title}' successfully maximized")
            return True
        else:
            print(f"  [WARN] Maximization may have failed, trying fallback...")
            # Fallback to keyboard shortcut
            pyautogui.hotkey('win', 'up')
            time.sleep(0.5)
            return is_window_maximized(window)
            
    except Exception as e:
        print(f"Failed to maximize window: {e}")
        # Fallback to keyboard shortcut
        pyautogui.hotkey('win', 'up')
        time.sleep(0.5)
        return is_window_maximized(window)


def is_window_maximized(window):
    """Check if window is maximized with visual verification"""
    if not window:
        return False
    
    screen_w, screen_h = pyautogui.size()
    """ gets the rectangle information of the window """
    rect = window._rect

    # Calculate window ratio
    width_ratio = rect.width / screen_w
    height_ratio = rect.height / screen_h
    
    is_maximized = width_ratio >= 0.8 and height_ratio >= 0.8
    
    if is_maximized:
        print(f"  [VISUAL] Window maximization verified: {width_ratio:.2f}x{height_ratio:.2f}")
    else:
        print(f"  [VISUAL] Window not maximized: {width_ratio:.2f}x{height_ratio:.2f}")
    
    return is_maximized


def maximize_window_with_retry(window, max_attempts=3):
    """Maximize window with retry and visual verification"""
    if not window:
        return False
    
    for attempt in range(max_attempts):
        print(f"  [MAXIMIZE] Attempt {attempt + 1}/{max_attempts}")
        
        # Try to maximize
        if maximize_window(window):
            # Verify visually
            if is_window_maximized(window):
                print(f"  [VISUAL] Window '{window.title}' successfully maximized on attempt {attempt + 1}")
                return True
            else:
                print(f"  [WARN] Maximization attempt {attempt + 1} failed visual verification")
        else:
            print(f"  [WARN] Maximization attempt {attempt + 1} failed")
        
        if attempt < max_attempts - 1:
            print(f"  [RETRY] Waiting 1 second before retry...")
            time.sleep(1)
    
    print(f"  [FAIL] Failed to maximize window after {max_attempts} attempts")
    return False

