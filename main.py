import sys
from config import load_config, get_app_config
from workflow import WorkflowManager
from utils import print_banner


def main():
    """Main entry point using modular structure"""
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
    
    # Create workflow manager
    workflow_manager = WorkflowManager(config)
    
    # Check if objectives were specified
    objective_ids = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    
    # If no objectives specified, just prepare app and exit
    if not objective_ids:
        if workflow_manager.prepare_application(app_name, app_config):
            print_banner("PREPARATION COMPLETE - App is ready")
            print(f"\nTo execute objectives, use: python main.py {app_name} <objective_ids>")
            return True
        else:
            print("[FAIL] Application preparation failed")
            return False
    
    # Execute workflow with specified objectives
    if workflow_manager.execute_workflow(app_name, app_config, objective_ids):
        return True
    else:
        print("[FAIL] Workflow execution failed")
        return False


if __name__ == "__main__":
    main()
