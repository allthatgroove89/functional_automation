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
    
    # Get objectives
    objective_ids = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    supported, unsupported = get_objectives(config, objective_ids)
    
    # Notify about unsupported
    if unsupported:
        notify_unsupported(unsupported)
    
    # Prepare app
    if not prepare_application(app_name, app_config):
        print("Failed to prepare application")
        return False
    
    # Execute objectives
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, objective in enumerate(supported):
        # Save checkpoint
        save_checkpoint(session_id, objective['id'], i, [])
        
        # Execute
        if not execute_objective(objective, config):
            notify_error(f"Objective failed", objective['name'])
            return False
    
    print("Automation complete!")
    return True


def prepare_application(app_name, app_config):
    """Prepare application for automation"""
    # Launch if needed
    window = find_window(app_name)
    if not window:
        launch_app(
            app_config['path'], 
            app_config.get('startup_delay', 2),
            app_config.get('args')
        )
        window = find_window(app_name)
    
    if not window:
        return False
    
    # Focus and maximize
    if not focus_window(window):
        return False
    
    if not maximize_window(window):
        return False
    
    return is_window_maximized(window)


if __name__ == "__main__":
    main()

