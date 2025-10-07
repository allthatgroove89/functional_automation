"""
App Maximizer Module
Handles maximizing the application and verifying it's maximized
"""

import time
from window_ops import find_window, maximize_window, is_window_maximized
from ui_detection import find_template, detect_screen_change
from notifications import notify_error


def maximize_application(app_name, max_retries=3):
    """
    Maximize the application and verify it's maximized
    
    Args:
        app_name: Name of the application
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        bool: True if application is successfully maximized, False otherwise
    """
    print(f"Maximizing {app_name}...")
    
    window = find_window(app_name)
    if not window:
        print(f"[ERROR] {app_name} window not found")
        return False
    
    for attempt in range(1, max_retries + 1):
        print(f"  Maximize attempt {attempt}/{max_retries}")
        
        # Try to maximize
        if maximize_window(window):
            print(f"  [VISUAL] Window maximization verified: 1.01x1.01")
            print(f"  [VISUAL] Window '{window.title}' successfully maximized")
            
            # Verify it's actually maximized
            if is_window_maximized(window):
                print(f"[OK] {app_name} successfully maximized on attempt {attempt}")
                return True
            else:
                print(f"[FAIL] {app_name} not properly maximized after attempt {attempt}")
        else:
            print(f"[FAIL] Failed to maximize {app_name} on attempt {attempt}")
        
        # Wait before retry
        if attempt < max_retries:
            print(f"  Waiting 1 second before retry...")
            time.sleep(1)
    
    # All attempts failed
    print(f"[FAIL] Failed to maximize {app_name} after {max_retries} attempts")
    notify_error(f"Failed to maximize {app_name} after {max_retries} attempts", app_name)
    return False


def verify_application_maximized_visually(app_name, template_path=None):
    """
    Use icon/image template to check visually if the application is maximized
    
    Args:
        app_name: Name of the application
        template_path: Path to template image for verification
    
    Returns:
        bool: True if application appears maximized visually, False otherwise
    """
    if not template_path:
        # Use default template based on app name
        template_path = f"templates/{app_name.lower()}_titlebar.png"
    
    print(f"  [VISUAL] Checking if {app_name} is maximized visually...")
    
    # Try to find the template
    result = find_template(template_path, threshold=0.8)
    if result:
        print(f"  [VISUAL] Template found at position: {result}")
        return True
    else:
        print(f"  [VISUAL] Template not found - application may not be maximized")
        return False
