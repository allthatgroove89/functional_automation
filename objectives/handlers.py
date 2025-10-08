"""
Objective handlers: high-level function counterparts for JSON objective IDs.
Each handler receives (objective, config, session_id) and should return True/False.
Handlers here delegate to the existing executor for now but provide a central place
to implement custom behavior when needed.
"""
from workflow.workflow_executor import execute_single_objective_no_dispatch as execute_single_objective_internal


def spotify_play(objective, config, session_id=None):
    """Handler for 'spotify_play' objective.

    First check whether Spotify process is running. If not, attempt to launch it
    via the app_preparation launcher. After Spotify is confirmed running, delegate
    to the default single-objective executor to perform the objective actions.
    """
    print("[HANDLER] spotify_play invoked - checking subprocess")

    app_name = objective.get('app', 'Spotify')

    try:
        from app_preparation.app_launcher import is_spotify_running, launch_application
        from config import get_app_config
        app_cfg = None
        try:
            app_cfg = get_app_config(config, app_name)
        except Exception:
            app_cfg = None

        running = False
        try:
            running = is_spotify_running()
        except Exception as e:
            print(f"  [WARN] is_spotify_running check failed: {e}")

        if not running:
            print("  [INFO] Spotify subprocess not running - attempting launch")
            launched = False
            try:
                launched = launch_application(app_name, app_cfg)
            except Exception as e:
                print(f"  [ERROR] Failed to launch Spotify: {e}")
                launched = False

            if not launched:
                print("  [FAIL] Could not ensure Spotify is running")
                return False
        else:
            print("  [OK] Spotify subprocess already running")

    except Exception as e:
        print(f"  [WARN] Spotify launch-check skipped due to import error: {e}")

    # Delegate to the existing single-objective executor
    return execute_single_objective_internal(objective, config, session_id)


def spotify_pause(objective, config, session_id=None):
    print("[HANDLER] spotify_pause invoked")
    return execute_single_objective_internal(objective, config, session_id)


def spotify_next_track(objective, config, session_id=None):
    print("[HANDLER] spotify_next_track invoked")
    return execute_single_objective_internal(objective, config, session_id)


def spotify_previous_track(objective, config, session_id=None):
    print("[HANDLER] spotify_previous_track invoked")
    return execute_single_objective_internal(objective, config, session_id)
