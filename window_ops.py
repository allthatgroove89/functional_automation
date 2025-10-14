import subprocess
import time
import pyautogui
import pygetwindow as gw


def launch_app(app_path, startup_delay=2, args=None):
    """Launch application and wait"""
    cmd = [app_path]
    if args:
        cmd.extend(args)
    # Use shell=False for safety; cmd should be a list (path + args)
    subprocess.Popen(cmd, shell=False)
    time.sleep(startup_delay)
    return True


def find_window(app_name):
    """Find window by title with enhanced debugging"""
    print(f"  [SEARCH] Looking for window: '{app_name}'")
    if app_name.lower() == "spotify":
        all_windows = gw.getAllWindows()
        primary_screen_width, primary_screen_height = pyautogui.size()

        print(f"  [DEBUG] Scanning {len(all_windows)} windows for '{app_name}'...")

        # First: prefer PID-based detection. Some Spotify windows don't include 'Spotify' in
        # the title (they show track names). Gather Spotify PIDs and try to find any top-level
        # window owned by those processes.
        try:
            import psutil
            import ctypes
            spotify_pids = set()
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    pid_val = proc.info.get('pid')
                    name = (proc.info.get('name') or '')
                    exe = (proc.info.get('exe') or '')
                    cmdline = proc.info.get('cmdline') or []
                    cmdline_str = ' '.join(cmdline) if isinstance(cmdline, (list, tuple)) else str(cmdline)

                    # Match on process name, executable path, or command line containing 'spotify'
                    if ('spotify' in name.lower()) or ('spotify' in exe.lower()) or ('spotify' in cmdline_str.lower()):
                        try:
                            spotify_pids.add(int(pid_val))
                        except Exception:
                            # some pid values may be None or non-int - skip
                            continue
                except Exception:
                    continue

            if spotify_pids:
                for window in all_windows:
                    try:
                        hwnd = getattr(window, '_hWnd', None) or getattr(window, 'hWnd', None)
                        if not hwnd:
                            continue
                        pid = ctypes.c_ulong()
                        ctypes.windll.user32.GetWindowThreadProcessId(int(hwnd), ctypes.byref(pid))
                        if pid.value in spotify_pids:
                            # Favor visible/top-level windows
                            try:
                                title = (window.title or '').strip()
                            except Exception:
                                title = ''
                            try:
                                safe_title = title.encode('utf-8', errors='replace').decode('utf-8') if title else '<no-title>'
                            except Exception:
                                safe_title = title or '<no-title>'
                            print(f"  [FOUND] {app_name} window by PID match: '{safe_title}' (pid={pid.value})")
                            return window
                    except Exception:
                        continue
        except Exception:
            # If psutil/ctypes not available or something went wrong, fall back to title heuristics
            pass

        for window in all_windows:
            # Only consider windows that have a non-empty title
            try:
                title = (window.title or '').strip()
            except Exception:
                title = ''

            if not title:
                continue

            lower_title = title.lower()

            # Direct title match first
            if 'spotify' in lower_title or 'spotify premium' in lower_title:
                try:
                    safe_title = title.encode('utf-8', errors='replace').decode('utf-8')
                except Exception:
                    safe_title = title
                print(f"  [FOUND] {app_name} window: '{safe_title}'")

                try:
                    print(f"  [DEBUG] Window dimensions: {window.width}x{window.height}, minimized: {window.isMinimized}")
                    print(f"  [DEBUG] Window position: left={window.left}, top={window.top}")
                    print(f"  [DEBUG] Primary screen: {primary_screen_width}x{primary_screen_height}")

                    if window.isMinimized:
                        print(f"  [RESTORE] {app_name} window is minimized, restoring...")
                        try:
                            window.restore()
                            time.sleep(1)
                            updated = gw.getWindowsWithTitle('Spotify Premium')
                            if updated:
                                window = updated[0]
                                print(f"  [DEBUG] After restore - dimensions: {window.width}x{window.height}, minimized: {window.isMinimized}")
                        except Exception as e:
                            print(f"  [ERROR] Failed to restore window: {e}")

                    # If window within expected size and on primary monitor, return it
                    if getattr(window, 'width', 0) > 200 and getattr(window, 'height', 0) > 200 and not getattr(window, 'isMinimized', False):
                        if (getattr(window, 'left', 0) >= 0 and getattr(window, 'left', 0) < primary_screen_width and 
                            getattr(window, 'top', 0) >= 0 and getattr(window, 'top', 0) < primary_screen_height):
                            print(f"  [OK] {app_name} window found on primary monitor")
                            return window
                        else:
                            print(f"  [MOVE] Moving {app_name} window to primary monitor")
                            try:
                                window.moveTo(100, 100)
                                time.sleep(0.5)
                            except Exception:
                                pass
                            return window
                    else:
                        print(f"  [FALLBACK] Returning {app_name} window (doesn't meet size/minimized criteria)")
                        return window
                except Exception as e:
                    print(f"  [ERROR] Failed to process {app_name} window: {e}")
                    return None

            # Some Spotify windows show track titles like 'Artist - Song' and don't include the word
            # 'spotify' in the title. As a fallback, detect windows with a ' - ' pattern and verify
            # the owning process is Spotify to avoid false positives.
            if ' - ' in title and len(title) > 6:
                hwnd = None
                try:
                    hwnd = getattr(window, '_hWnd', None) or getattr(window, 'hWnd', None)
                    if hwnd:
                        try:
                            import ctypes
                            pid = ctypes.c_ulong()
                            ctypes.windll.user32.GetWindowThreadProcessId(int(hwnd), ctypes.byref(pid))
                            proc = None
                            try:
                                import psutil
                                proc = psutil.Process(pid.value)
                            except Exception:
                                proc = None

                            proc_name = ''
                            if proc:
                                try:
                                    proc_name = proc.name() or ''
                                except Exception:
                                    proc_name = ''

                            if 'spotify' in proc_name.lower():
                                try:
                                    safe_title = title.encode('utf-8', errors='replace').decode('utf-8')
                                except Exception:
                                    safe_title = title
                                print(f"  [FOUND] {app_name} window by process match: '{safe_title}' (pid={pid.value})")
                                return window
                        except Exception:
                            # Can't determine process id - skip this heuristic
                            pass
                except Exception:
                    pass

        print(f"  [NOT FOUND] No {app_name} window found")
        return None
    else:
        windows = gw.getWindowsWithTitle(app_name)
        return windows[0] if windows else None

def focus_window(window):
    """Focus a window - CLEAN AND SIMPLE"""
    if not window or not window.title:
        return False
    
    # Check for Spotify patterns (including track titles)
    title = window.title.lower()
    is_spotify = ("spotify" in title or "spotify premium" in title or 
                  (" - " in title and len(title) > 10 and not any(x in title for x in ['cursor', 'code', 'editor', 'functional_automation'])))  # Track title pattern
    
    if not is_spotify:
        return False
    
    try:
        window.activate()
        time.sleep(0.2)
        return window.isActive
    except:
        return False


def maximize_window(window):
    """Maximize window with enhanced reliability for Spotify Premium"""
    if not window or not window.title:
        return False
    
    # Check for Spotify patterns (including track titles)
    title = window.title.lower()
    is_spotify = ("spotify" in title or "spotify premium" in title or 
                  (" - " in title and len(title) > 10 and not any(x in title for x in ['cursor', 'code', 'editor', 'functional_automation'])))  # Track title pattern
    
    if not is_spotify:
        return False
    
    try:
        # Handle Unicode safely for display
        try:
            safe_title = window.title.encode('utf-8', errors='replace').decode('utf-8')
        except:
            safe_title = "Spotify"
        print(f"  [MAXIMIZE] Attempting to maximize: '{safe_title}'")
        
        # Method 1: Standard maximize
        window.activate()
        time.sleep(0.3)
        window.maximize()
        time.sleep(0.8)
        
        if is_window_maximized(window):
            print(f"  [OK] Window maximized successfully")
            return True
        
        # Method 2: Windows shortcut (Win + Up)
        print(f"  [FALLBACK] Trying Win+Up shortcut...")
        pyautogui.hotkey('win', 'up')
        time.sleep(0.8)
        
        if is_window_maximized(window):
            print(f"  [OK] Window maximized via Win+Up")
            return True
        
    # Method 3: Double-click title bar simulation
        print(f"  [FALLBACK] Trying double-click title bar...")
        try:
            # Click on title bar area to focus, then double-click
            pyautogui.click(window.left + window.width//2, window.top + 10)
            time.sleep(0.2)
            pyautogui.doubleClick(window.left + window.width//2, window.top + 10)
            time.sleep(0.8)
            
            if is_window_maximized(window):
                print(f"  [OK] Window maximized via double-click")
                return True
        except:
            pass

        # Method 4: Win32 ShowWindow / SetWindowPos fallback (Windows only)
        try:
            hwnd = None
            if hasattr(window, '_hWnd') and window._hWnd:
                try:
                    hwnd = int(window._hWnd)
                except Exception:
                    hwnd = None
            elif hasattr(window, 'hWnd') and window.hWnd:
                try:
                    hwnd = int(window.hWnd)
                except Exception:
                    hwnd = None

            if hwnd:
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    SW_MAXIMIZE = 3
                    # Try ShowWindow
                    res = user32.ShowWindow(hwnd, SW_MAXIMIZE)
                    time.sleep(0.5)
                    # Also attempt to force size with SetWindowPos
                    screen_w, screen_h = pyautogui.size()
                    SWP_NOZORDER = 0x4
                    SWP_NOACTIVATE = 0x10
                    # Set to full primary screen (may overlap taskbar slightly)
                    user32.SetWindowPos(hwnd, 0, 0, 0, screen_w, screen_h, SWP_NOZORDER | SWP_NOACTIVATE)
                    time.sleep(0.6)
                    if is_window_maximized(window):
                        print(f"  [OK] Window maximized via Win32 ShowWindow/SetWindowPos")
                        return True
                    else:
                        print(f"  [WARN] Win32 ShowWindow attempted but visual verification failed")
                except Exception as we:
                    # Provide more detailed Windows error if available
                    try:
                        import ctypes as _ct
                        err = _ct.GetLastError()
                    except Exception:
                        err = None
                    print(f"  [ERROR] Win32 maximize attempt failed: {we} (GetLastError={err})")
        except Exception:
            pass

        print(f"  [FAIL] All maximization methods failed")
        return False
        
    except Exception as e:
        print(f"  [ERROR] Maximization failed: {e}")
        return False


def is_window_maximized(window):
    """Check if window is maximized with visual verification"""
    if not window:
        return False
    
    screen_w, screen_h = pyautogui.size()

    # Try multiple ways to get window rectangle depending on pygetwindow/versions
    try:
        rect = getattr(window, '_rect', None)
        if rect is None:
            # Some versions expose left/top/width/height directly
            left = getattr(window, 'left', None)
            top = getattr(window, 'top', None)
            width = getattr(window, 'width', None)
            height = getattr(window, 'height', None)
            if None not in (left, top, width, height):
                # Help static type checkers: width/height are not None here
                assert width is not None and height is not None
                # Ensure numeric types
                try:
                    width_ratio = float(width) / float(screen_w)
                    height_ratio = float(height) / float(screen_h)
                except Exception:
                    width_ratio = 0.0
                    height_ratio = 0.0
            else:
                # Last resort: try window.size() or bounding box
                width_ratio = getattr(window, 'width', 0) / screen_w
                height_ratio = getattr(window, 'height', 0) / screen_h
        else:
            width_ratio = rect.width / screen_w
            height_ratio = rect.height / screen_h
    except Exception:
        # If any attribute access fails, assume not maximized
        print("  [WARN] Unable to get window rect - assuming not maximized")
        return False
    
    # Require full maximization (0.95 or higher to account for taskbar)
    is_maximized = width_ratio >= 0.95 and height_ratio >= 0.95
    
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
                safe_title = window.title.encode('utf-8', errors='replace').decode('utf-8')
                print(f"  [VISUAL] Window '{safe_title}' successfully maximized on attempt {attempt + 1}")
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

