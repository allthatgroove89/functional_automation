import sys
from datetime import datetime
from config import load_config, get_objectives, get_app_config
from notifications import notify_unsupported, notify_error
from window_ops import find_window, launch_app, focus_window, maximize_window, is_window_maximized
from workflow import execute_objective
from state import save_checkpoint
from utils import print_banner


def main():
    """Main entry point"""
    print("Starting automation...")
    
    # Load config
    config = load_config()
    
    # Get app name
    app_name = config['default_app']
    
    # Get app config
    try:
        app_config = get_app_config(config, app_name)
    except ValueError as e:
        print(str(e))
        return False
    
    # Prepare app (always happens)
    max_retries = 3
    if not prepare_application_with_retry(app_name, app_config, max_retries):
        print("Failed to prepare application after 3 attempts")
        notify_error("Failed to launch/prepare application after 3 retries", app_name)
        return False
    
    print(f"[OK] {app_name} prepared successfully (launched, maximized, focused)")
    
    # Check if objectives were specified
    objective_ids = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    
    # If no objectives specified, just exit after preparation (leave app open)
    if not objective_ids:
        print_banner("PREPARATION COMPLETE - App is ready")
        print(f"\nTo execute objectives, use: python main.py {app_name} <objective_ids>")
        return True
    
    # Objectives specified - get and execute them
    supported, unsupported = get_objectives(config, objective_ids)
    
    # Notify about unsupported objectives
    if unsupported:
        notify_unsupported(unsupported)
    
    # No supported objectives to run
    if not supported:
        print_banner("No supported objectives to execute")
        return True
    
    # Execute objectives
    print_banner(f"Executing {len(supported)} objective(s)...")
    
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, objective in enumerate(supported):
        print(f"\n[{i+1}/{len(supported)}] Starting: {objective['name']}")
        
        # Save checkpoint
        save_checkpoint(session_id, objective['id'], i, [])
        
        # Execute objective - sends email only if action fails after 3 retries
        if not execute_objective(objective, config, session_id):
            notify_error(f"Objective failed after 3 retry attempts", objective['name'])
            return False
    
    print_banner("[OK] Automation complete!")
    return True

# Prepare application with retry logic
def prepare_application_with_retry(app_name, app_config, max_retries=3):
    """Prepare application with retry logic"""
    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt}/{max_retries} to prepare {app_name}...")
        
        if prepare_application(app_name, app_config):
            print(f"[OK] Preparation successful on attempt {attempt}")
            return True
        
        if attempt < max_retries:
            print(f"[FAIL] Preparation failed, retrying...")
            import time
            time.sleep(2)
        else:
            print(f"[FAIL] All {max_retries} preparation attempts failed for {app_name}")
            
    return False

# Launch and prepare application
def prepare_application(app_name, app_config):
    """Prepare application for automation"""
    # Find or launch window
    window = find_window(app_name)
    if not window:
        launch_app(app_config['path'], app_config.get('startup_delay', 2), app_config.get('args'))
        window = find_window(app_name)
    
    # Verify window exists and is ready
    if not window:
        return False
    
    return (focus_window(window) and 
            maximize_window(window) and 
            is_window_maximized(window))


if __name__ == "__main__":
    main()
