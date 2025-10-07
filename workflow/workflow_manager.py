"""
Workflow Manager Module
Handles overall workflow management and coordination
"""

from datetime import datetime
from .workflow_executor import execute_workflow_sequence
from objectives import parse_json_objectives, filter_supported_objectives, notify_unsupported_objectives
from app_preparation import launch_application, maximize_application, verify_application_ready
from window_ops import find_window, focus_window
from notifications import notify_error
from utils import print_banner


class WorkflowManager:
    """
    Manages the complete workflow process
    """
    
    def __init__(self, config):
        """
        Initialize workflow manager with configuration
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def prepare_application(self, app_name, app_config, max_retries=3):
        """
        Prepare application for automation
        
        Args:
            app_name: Name of the application
            app_config: Configuration for the application
            max_retries: Maximum number of retry attempts
        
        Returns:
            bool: True if application is ready, False otherwise
        """
        print(f"Preparing {app_name} for automation...")
        
        # Step 1: Launch application
        if not launch_application(app_name, app_config, max_retries):
            print(f"[FAIL] Failed to launch {app_name}")
            return False
        
        # Step 2: Maximize application
        if not maximize_application(app_name, max_retries):
            print(f"[FAIL] Failed to maximize {app_name}")
            return False
        
        # Step 3: Verify application is ready
        if not verify_application_ready(app_name):
            print(f"[FAIL] {app_name} is not ready")
            return False
        
        print(f"[OK] {app_name} prepared successfully")
        return True
    
    def get_objectives_ready(self, objective_ids=None):
        """
        Get objectives ready for execution
        
        Args:
            objective_ids: Optional list of specific objective IDs
        
        Returns:
            tuple: (supported_objectives, unsupported_objectives)
        """
        print("Getting objectives ready for execution...")
        
        # Step 1: Parse JSON objectives
        all_objectives = parse_json_objectives(self.config)
        if not all_objectives:
            print("[ERROR] No objectives found in JSON file")
            return [], []
        
        # Step 2: Filter supported/unsupported objectives
        supported, unsupported = filter_supported_objectives(all_objectives, objective_ids)
        
        # Step 3: Notify about unsupported objectives
        if unsupported:
            notify_unsupported_objectives(unsupported)
        
        return supported, unsupported
    
    def execute_workflow(self, app_name, app_config, objective_ids=None):
        """
        Execute complete workflow process
        
        Args:
            app_name: Name of the application
            app_config: Configuration for the application
            objective_ids: Optional list of specific objective IDs
        
        Returns:
            bool: True if workflow completed successfully, False otherwise
        """
        print("Starting complete workflow process...")
        
        # Step 1: Prepare application
        if not self.prepare_application(app_name, app_config):
            print("[FAIL] Application preparation failed")
            return False
        
        # Step 2: Get objectives ready
        supported, unsupported = self.get_objectives_ready(objective_ids)
        
        # Step 3: Check if there are supported objectives
        if not supported:
            print_banner("No supported objectives to execute")
            return True
        
        # Step 4: Execute objectives in sequence
        print_banner(f"Executing {len(supported)} objective(s)...")
        
        if not execute_workflow_sequence(supported, self.config, self.session_id):
            print("[FAIL] Workflow execution failed")
            return False
        
        print_banner("[OK] Workflow complete!")
        return True
    
    def execute_single_objective(self, app_name, app_config, objective_id):
        """
        Execute a single objective
        
        Args:
            app_name: Name of the application
            app_config: Configuration for the application
            objective_id: ID of the objective to execute
        
        Returns:
            bool: True if objective executed successfully, False otherwise
        """
        print(f"Executing single objective: {objective_id}")
        
        # Step 1: Prepare application
        if not self.prepare_application(app_name, app_config):
            print("[FAIL] Application preparation failed")
            return False
        
        # Step 2: Get objectives ready
        supported, unsupported = self.get_objectives_ready([objective_id])
        
        # Step 3: Check if objective is supported
        if not supported:
            print(f"[FAIL] Objective '{objective_id}' not found or not supported")
            return False
        
        # Step 4: Execute the single objective
        print_banner(f"Executing 1 objective...")
        
        if not execute_workflow_sequence(supported, self.config, self.session_id):
            print("[FAIL] Objective execution failed")
            return False
        
        print_banner("[OK] Objective complete!")
        return True
