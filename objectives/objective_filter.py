"""
Objective Filter Module
Handles finding supported/unsupported objectives
"""


def filter_supported_objectives(objectives, objective_ids=None):
    """
    Find the list of objectives that are not supported/not defined already in the system
    
    Args:
        objectives: List of all objectives
        objective_ids: Optional list of specific objective IDs to filter
    
    Returns:
        tuple: (supported_objectives, unsupported_objectives)
    """
    print("Filtering supported and unsupported objectives...")
    
    # Filter by objective IDs if provided
    if objective_ids:
        filtered_objectives = []
        for objective in objectives:
            if objective.get('id') in objective_ids:
                filtered_objectives.append(objective)
        objectives = filtered_objectives
        print(f"Filtered to {len(objectives)} objectives by IDs")
    
    supported = []
    unsupported = []
    
    # Separate objectives into supported and unsupported lists
    for objective in objectives:
        if objective.get('supported', False):
            supported.append(objective)
        else:
            unsupported.append(objective)
    
    print(f"[OK] Found {len(supported)} supported objectives")
    print(f"[OK] Found {len(unsupported)} unsupported objectives")
    
    return supported, unsupported


def get_objective_by_id(objectives, objective_id):
    """
    Get a specific objective by its ID
    
    Args:
        objectives: List of all objectives
        objective_id: ID of the objective to find
    
    Returns:
        dict or None: The objective if found, None otherwise
    """
    for objective in objectives:
        if objective.get('id') == objective_id:
            return objective
    return None


def validate_objective_structure(objective):
    """
    Validate that an objective has the required structure
    
    Args:
        objective: Objective dictionary to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['id', 'name', 'actions']
    
    for field in required_fields:
        if field not in objective:
            print(f"[WARN] Objective missing required field: {field}")
            return False
    
    # Validate actions structure
    actions = objective.get('actions', [])
    if not isinstance(actions, list):
        print(f"[WARN] Objective actions must be a list")
        return False
    
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            print(f"[WARN] Action {i} must be a dictionary")
            return False
        
        if 'type' not in action:
            print(f"[WARN] Action {i} missing required field: type")
            return False
    
    return True
