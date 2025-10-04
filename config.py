import json


def load_config(config_path="config/config.json"):
    """Load main config"""
    with open(config_path, 'r') as f:
        return json.load(f)


def load_instructions(config):
    """Load instructions from path in config"""
    instructions_path = config.get('instructions_file', 'config/instructions.json')
    with open(instructions_path, 'r') as f:
        return json.load(f)


def get_objectives(config, objective_ids=None):
    """Get objectives"""
    instructions = load_instructions(config)
    objectives = instructions['objectives']
    
    if objective_ids:
        objectives = [o for o in objectives if o['id'] in objective_ids]
    
    supported = [o for o in objectives if o.get('supported')]
    unsupported = [o for o in objectives if not o.get('supported')]
    
    return supported, unsupported

