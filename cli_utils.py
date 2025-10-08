"""
CLI utility functions for parsing command line arguments and resolving objectives.
"""


def parse_objective_args(argv_tail):
    """Flatten a list of tokens that may include comma-separated ids into a list of ids."""
    ids = []
    for token in argv_tail:
        if not token:
            continue
        if ',' in token:
            ids.extend([p.strip() for p in token.split(',') if p.strip()])
        else:
            t = token.strip()
            if t:
                ids.append(t)
    return ids or None


def resolve_app_for_objective(config, objective_id):
    """Return app name for a given objective id by scanning the JSON objectives."""
    try:
        from objectives.json_parser import parse_json_objectives
    except Exception:
        return None
    
    try:
        all_objs = parse_json_objectives(config)
    except Exception:
        return None
    
    for o in all_objs:
        if o.get('id') == objective_id:
            return o.get('app')
    return None
