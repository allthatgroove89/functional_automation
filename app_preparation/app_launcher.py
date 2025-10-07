"""
App Launcher Module
Handles checking if application is open and launching if needed
"""

import time
from window_ops import find_window, launch_app
from notifications import notify_error


def launch_application(app_name, app_config, max_retries=3):
    """
    Check if application is already open, if not open it (iterate until open)
    
    Args:
        app_name: Name of the application
        app_config: Configuration for the application
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        bool: True if application is successfully launched, False otherwise
    """
    print(f"Checking if {app_name} is already open...")
    
    # Check if already open
    window = find_window(app_name)
    if window:
        print(f"[OK] {app_name} is already open")
        return True
    
    # Not open, try to launch
    print(f"{app_name} not found, launching...")
    
    for attempt in range(1, max_retries + 1):
        print(f"  Launch attempt {attempt}/{max_retries}")
        
        try:
            # Launch the application
            launch_app(
                app_config['path'], 
                app_config.get('startup_delay', 2), 
                app_config.get('args')
            )
            
            # Wait a moment for startup
            time.sleep(app_config.get('startup_delay', 2))
            
            # Check if it's now open
            window = find_window(app_name)
            if window:
                print(f"[OK] {app_name} successfully launched on attempt {attempt}")
                return True
            else:
                print(f"[FAIL] {app_name} not found after launch attempt {attempt}")
                
        except Exception as e:
            print(f"[ERROR] Launch attempt {attempt} failed: {str(e)}")
        
        # Wait before retry
        if attempt < max_retries:
            print(f"  Waiting 2 seconds before retry...")
            time.sleep(2)
    
    # All attempts failed
    print(f"[FAIL] Failed to launch {app_name} after {max_retries} attempts")
    notify_error(f"Failed to launch {app_name} after {max_retries} attempts", app_name)
    return False
