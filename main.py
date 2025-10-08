import sys
from config import load_config, get_app_config
from workflow import WorkflowManager
from utils import print_banner

try:
    from objectives.json_parser import parse_json_objectives
except Exception:
    parse_json_objectives = None  # Fallback if import path differs


def def_main():
    """Legacy named entry preserved at top as requested."""
    return main()


def _parse_objective_args(argv_tail):
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


def _resolve_app_for_objective(config, objective_id):
    """Return app name for a given objective id by scanning the JSON objectives."""
    if not parse_json_objectives:
        return None
    try:
        all_objs = parse_json_objectives(config)
    except Exception:
        return None
    for o in all_objs:
        if o.get('id') == objective_id:
            return o.get('app')
    return None


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

    # One token: either objective id or app name
    if len(sys.argv) == 2:
        token = sys.argv[1].strip()
        app_name = _resolve_app_for_objective(config, token)
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
    objective_ids = _parse_objective_args(sys.argv[2:])
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