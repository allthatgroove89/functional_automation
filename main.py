import sys
from datetime import datetime
from config import load_config, get_app_config
from workflow import WorkflowManager
from workflow.workflow_executor import WORKFLOW_SEQUENCES, execute_workflow_sequence_by_name
from utils import print_banner
from cli_utils import parse_objective_args, resolve_app_for_objective


def main():
    """Flexible CLI:
    - python main.py                     -> prepare default_app only
    - python main.py <objective_id>      -> auto-detect app & run single objective
    - python main.py <AppName> <obj...>  -> run one or multiple objectives
    """
    config = load_config()

    # No args: prepare default app
    if len(sys.argv) == 1:
        app_name = config.get('default_app')
        if not app_name:
            print('[ERROR] No default_app in config')
            return 1
        try:
            app_config = get_app_config(config, app_name)
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1
        wm = WorkflowManager(config)
        if wm.prepare_application(app_name, app_config):
            print_banner('PREPARATION COMPLETE - App is ready')
            print(f"\nTo execute objectives, use: python main.py {app_name} <objective_ids>")
            return 0
        print('[FAIL] Application preparation failed')
        return 2

    # One token: either objective id, sequence name, or app name
    if len(sys.argv) == 2:
        token = sys.argv[1].strip()
        
        # Check if it's a workflow sequence
        if token in WORKFLOW_SEQUENCES:
            print(f"[INFO] Detected workflow sequence: {token}")
            print(f"Sequence: {' -> '.join(WORKFLOW_SEQUENCES[token])}")
            
            # Determine app from sequence (assume Spotify for now)

            app_name = "Spotify"
            try:
                app_config = get_app_config(config, app_name)
                
            except Exception as e:
                print(f"[ERROR] {e}")
                return 1
            
            # Execute the sequence
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            ok = execute_workflow_sequence_by_name(token, app_config, session_id)
            return 0 if ok else 3
        
        # Try to resolve as objective
        app_name = resolve_app_for_objective(config, token)
        wm = WorkflowManager(config)
        if app_name:
            try:
                app_config = get_app_config(config, app_name)
            except Exception as e:
                print(f"[ERROR] {e}")
                return 1
            print(f"[INFO] Resolved objective '{token}' to app '{app_name}'")
            ok = wm.execute_single_objective(app_name, app_config, token)
            return 0 if ok else 3
        else:
            # token is app name -> prepare only
            app_name = token
            try:
                app_config = get_app_config(config, app_name)
            except Exception as e:
                print(f"[ERROR] {e}")
                return 1
            if wm.prepare_application(app_name, app_config):
                print_banner('PREPARATION COMPLETE - App is ready')
                return 0
            print('[FAIL] Application preparation failed')
            return 2

    # Multiple args: first is app name, rest are objectives
    app_name = sys.argv[1].strip()
    objective_ids = parse_objective_args(sys.argv[2:])
    try:
        app_config = get_app_config(config, app_name)
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    wm = WorkflowManager(config)
    if not objective_ids:
        if wm.prepare_application(app_name, app_config):
            print_banner('PREPARATION COMPLETE - App is ready')
            return 0
        print('[FAIL] Application preparation failed')
        return 2

    if len(objective_ids) == 1:
        ok = wm.execute_single_objective(app_name, app_config, objective_ids[0])
        return 0 if ok else 3

    ok = wm.execute_workflow(app_name, app_config, objective_ids)
    return 0 if ok else 4


if __name__ == "__main__":
    raise SystemExit(main())