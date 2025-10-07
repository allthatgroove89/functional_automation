"""
JSON Parser Module
Handles reading JSON file and creating actions
"""

import json


def parse_json_objectives(config):
    """
    Parse the JSON file for objectives
    
    Args:
        config: Configuration object containing instructions file path
    
    Returns:
        list: List of all objectives from the JSON file
    """
    print("Reading JSON file and creating actions...")
    
    # Load instructions from path in config
    instructions_path = config.get('instructions_file', 'config/instructions.json')
    
    try:
        with open(instructions_path, 'r') as f:
            instructions = json.load(f)
        
        objectives = instructions.get('objectives', [])
        print(f"[OK] Loaded {len(objectives)} objectives from {instructions_path}")
        return objectives
        
    except FileNotFoundError:
        print(f"[ERROR] Instructions file not found: {instructions_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in instructions file: {str(e)}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load instructions: {str(e)}")
        return []


def parse_objective_actions(objective):
    """
    Parse actions from a single objective
    
    Args:
        objective: Single objective dictionary
    
    Returns:
        list: List of actions for the objective
    """
    return objective.get('actions', [])


def parse_objective_prerequisites(objective):
    """
    Parse prerequisites from a single objective
    
    Args:
        objective: Single objective dictionary
    
    Returns:
        list: List of prerequisites for the objective
    """
    return objective.get('prerequisites', [])
