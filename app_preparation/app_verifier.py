"""
App Verifier Module
Handles checking if application is open and maximized
"""

from window_ops import find_window, is_window_maximized
from ui_detection import find_template


def verify_application_ready(app_name, template_path=None):
    """
    Check if the application is open and maximized
    
    Args:
        app_name: Name of the application
        template_path: Optional template path for visual verification
    
    Returns:
        bool: True if application is ready, False otherwise
    """
    print(f"Verifying {app_name} is ready...")
    
    # Check if window exists
    window = find_window(app_name)
    if not window:
        print(f"[FAIL] {app_name} window not found")
        return False
    
    # Check if maximized
    if not is_window_maximized(window):
        print(f"[FAIL] {app_name} is not maximized")
        return False
    
    # Optional visual verification with template
    if template_path:
        if not verify_application_maximized_visually(app_name, template_path):
            print(f"[FAIL] {app_name} visual verification failed")
            return False
    
    print(f"[OK] {app_name} is ready (open and maximized)")
    return True


def verify_application_maximized_visually(app_name, template_path):
    """
    Use icon/image template to check visually if the application is maximized
    
    Args:
        app_name: Name of the application
        template_path: Path to template image for verification
    
    Returns:
        bool: True if application appears maximized visually, False otherwise
    """
    print(f"  [VISUAL] Checking if {app_name} is maximized visually...")
    
    # Try to find the template
    result = find_template(template_path, threshold=0.8)
    if result:
        print(f"  [VISUAL] Template found at position: {result}")
        return True
    else:
        print(f"  [VISUAL] Template not found - application may not be maximized")
        return False

