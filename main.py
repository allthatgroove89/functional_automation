import sys
from datetime import datetime
from config import load_config, get_objectives
from notifications import notify_unsupported, notify_error
from window_ops import find_window, launch_app, focus_window, maximize_window, is_window_maximized
from workflow import execute_objective
from state import save_checkpoint


def main():
    """Main entry point"""
    print("Starting automation...")
    
    # Load config
    config = load_config()
    
    # Get app name
    app_name = sys.argv[1] if len(sys.argv) > 1 else config['default_app']
    
    # Get app config
    app_config = None
    for app in config['apps']:
        if app['name'] == app_name:
            app_config = app
            break
    
    if not app_config:
        print(f"App {app_name} not found in config")
        return False
    
    # Prepare app (always happens)
    max_retries = 3
    if not prepare_application_with_retry(app_name, app_config, max_retries):
        print("Failed to prepare application after 3 attempts")
        notify_error("Failed to launch/prepare application after 3 retries", app_name)
        return False
    
    print(f"✓ {app_name} prepared successfully (launched, maximized, focused)")
    
    # Check if objectives were specified
    objective_ids = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    
    # If no objectives specified, just exit after preparation (leave app open)
    if not objective_ids:
        print("\n" + "="*60)
        print("PREPARATION COMPLETE - App is ready")
        print("="*60)
        print(f"\nTo execute objectives, use: python main.py {app_name} <objective_ids>")
        return True
    
    # Objectives specified - get and execute them
    supported, unsupported = get_objectives(config, objective_ids)
    
    # Notify about unsupported objectives
    if unsupported:
        notify_unsupported(unsupported)
    
    # No supported objectives to run
    if not supported:
        print("\n" + "="*60)
        print("No supported objectives to execute")
        print("="*60)
        return True
    
    # Execute objectives
    print("\n" + "="*60)
    print(f"Executing {len(supported)} objective(s)...")
    print("="*60)
    
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, objective in enumerate(supported):
        print(f"\n[{i+1}/{len(supported)}] Starting: {objective['name']}")
        
        # Save checkpoint
        save_checkpoint(session_id, objective['id'], i, [])
        
        # Execute objective - sends email only if action fails after 3 retries
        if not execute_objective(objective, config):
            notify_error(f"Objective failed after 3 retry attempts", objective['name'])
            return False
    
    print("\n" + "="*60)
    print("✓ Automation complete!")
    print("="*60)
    return True


def prepare_application_with_retry(app_name, app_config, max_retries=3):
    """Prepare application with retry logic"""
    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt}/{max_retries} to prepare {app_name}...")
        
        if prepare_application(app_name, app_config):
            print(f"✓ Preparation successful on attempt {attempt}")
            return True
        
        if attempt < max_retries:
            print(f"✗ Preparation failed, retrying...")
            import time
            time.sleep(2)
    
    return False


def prepare_application(app_name, app_config):
    """Prepare application for automation"""
    # Sub-step 1: Check if app is already open
    window = find_window(app_name)
    
    # App not open, launch it
    if not window:
        print(f"  → Launching {app_name}...")
        launch_app(
            app_config['path'], 
            app_config.get('startup_delay', 2),
            app_config.get('args')
        )
        window = find_window(app_name)
    else:
        print(f"  → Found existing {app_name} window")
    
    if not window:
        print(f"  ✗ Could not find window")
        return False
    
    # Sub-step 2: Focus the window (bring to foreground)
    print(f"  → Focusing window...")
    if not focus_window(window):
        print(f"  ✗ Could not focus window")
        return False
    
    print(f"  → Maximizing window...")
    if not maximize_window(window):
        print(f"  ✗ Could not maximize window")
        return False
    
    if not is_window_maximized(window):
        print(f"  ✗ Window not fully maximized")
        return False
    
    return True


if __name__ == "__main__":
    main()
