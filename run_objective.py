import sys
import os
import json

# Ensure project root on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import load_config, load_instructions, get_app_config
from workflow import WorkflowManager


def run_objective_cli(argv=None):
    """Run a single objective from the instructions file.

    argv: optional list of arguments (defaults to sys.argv)
    Returns an exit code integer.
    """
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        # No CLI argument allowed for actions per user request.
        # Prompt the user to type the objective id exactly as listed in config/instructions.json
        try:
            objective_id = input("Enter objective id (as in config/instructions.json): ").strip()
        except Exception:
            objective_id = None

        if not objective_id:
            print("No objective id provided.")
            print("Example id: spotify_play")
            return 1
    else:
        objective_id = argv[1]
    cfg = load_config()
    instructions = load_instructions(cfg)
    objectives = instructions.get('objectives', [])

    # Find objective
    objective = None
    for o in objectives:
        if o.get('id') == objective_id:
            objective = o
            break

    if not objective:
        print(f"Objective '{objective_id}' not found in instructions.json")
        return 2

    app_name = objective.get('app')

    if not app_name:
        print(f"Objective '{objective_id}' has no 'app' field")
        return 3

    try:
        app_cfg = get_app_config(cfg, app_name)
    except Exception as e:
        print(f"Failed to get app config for '{app_name}': {e}")
        return 4

    wm = WorkflowManager(cfg)

    print(f"Executing objective '{objective_id}' for app '{app_name}'...\n")
    try:
        ok = wm.execute_single_objective(app_name, app_cfg, objective_id)
        print(f"Execution returned: {ok}")
        return 0 if ok else 5
    except Exception as e:
        print(f"Execution failed with exception: {e}")
        return 6


if __name__ == '__main__':
    sys.exit(run_objective_cli())
