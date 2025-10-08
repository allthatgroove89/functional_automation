#!/usr/bin/env python3
"""
Show supported and unsupported Spotify actions
"""

import json
from config import load_config
from objectives.json_parser import parse_json_objectives
from objectives.objective_filter import filter_supported_objectives

def show_spotify_actions():
    """Show all Spotify actions categorized by supported/unsupported"""
    
    print("SPOTIFY AUTOMATION ACTIONS")
    print("=" * 50)
    
    # Load config and parse objectives
    config = load_config()
    all_objectives = parse_json_objectives(config)
    
    # Also load mock unsupported objectives directly from JSON
    import json
    instructions_path = config.get('instructions_file', 'config/instructions.json')
    try:
        with open(instructions_path, 'r') as f:
            instructions = json.load(f)
        mock_unsupported = instructions.get('mock_unsupported_objectives', [])
    except Exception as e:
        print(f"ERROR loading mock objectives: {e}")
        mock_unsupported = []
    
    if not all_objectives:
        print("ERROR: No objectives found in JSON file")
        return
    
    # Filter for Spotify objectives
    spotify_objectives = [obj for obj in all_objectives if obj.get('app', '').lower() == 'spotify']
    
    if not spotify_objectives:
        print("ERROR: No Spotify objectives found")
        return
    
    # Get supported and unsupported from regular objectives
    supported, unsupported = filter_supported_objectives(spotify_objectives)
    
    # Add mock unsupported objectives to the unsupported list
    unsupported.extend(mock_unsupported)
    
    print(f"SUMMARY: {len(supported)} supported, {len(unsupported)} unsupported")
    print()
    
    # Show supported actions
    print("SUPPORTED ACTIONS:")
    print("-" * 30)
    for obj in supported:
        status = "[OK]" if obj.get('supported', False) else "[FAIL]"
        print(f"{status} {obj.get('id', 'unknown')}")
        print(f"   Name: {obj.get('name', 'No name')}")
        if obj.get('reason'):
            print(f"   Note: {obj.get('reason')}")
        print()
    
    # Show unsupported actions
    if unsupported:
        print("UNSUPPORTED ACTIONS:")
        print("-" * 30)
        for obj in unsupported:
            print(f"[FAIL] {obj.get('id', 'unknown')}")
            print(f"   Name: {obj.get('name', 'No name')}")
            if obj.get('reason'):
                print(f"   Reason: {obj.get('reason')}")
            print()
    
    # Show action types breakdown
    print("ACTION TYPES BREAKDOWN:")
    print("-" * 30)
    
    action_types = {}
    for obj in spotify_objectives:
        actions = obj.get('actions', [])
        for action in actions:
            action_type = action.get('type', 'unknown')
            action_types[action_type] = action_types.get(action_type, 0) + 1
    
    for action_type, count in sorted(action_types.items()):
        print(f"   {action_type}: {count} actions")
    
    print()
    print("QUICK COMMANDS:")
    print("-" * 30)
    for obj in supported:
        if obj.get('supported', False):
            print(f"python main.py Spotify {obj.get('id')}")

if __name__ == "__main__":
    show_spotify_actions()
