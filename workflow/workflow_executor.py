"""
Workflow Executor Module
Handles executing objectives in sequence
"""

import time
from datetime import datetime
from actions import execute_action
from verification import verify_prerequisites, verify_action_complete
from notifications import notify_error
from state import save_checkpoint


# Predefined workflow sequences
WORKFLOW_SEQUENCES = {
    "spotify_music_session": [
        "spotify_search_artist_name",
        "spotify_play", 
        "spotify_next_track",
        "spotify_search_artist_name",
        "spotify_play",
        "spotify_pause",
        "spotify_close"
    ],
    "spotify_quick_play": [
        "spotify_play",
        "spotify_next_track", 
        "spotify_pause"
    ],
    "spotify_search_and_play": [
        "spotify_search_artist_name",
        "spotify_play",
        "spotify_pause",
        "spotify_close"
    ],
    "spotify_volume_control": [
        "spotify_volume_up",
        "spotify_volume_down",
        "spotify_mute"
    ],
    "spotify_filter_browse": [
        "spotify_filter_artists",
        "spotify_filter_albums", 
        "spotify_filter_songs",
        "spotify_filter_all"
    ],
    "spotify_music_journey": [
        "spotify_search_metallica",
        "spotify_play",
        "spotify_next_track",
        "spotify_search_iron_maiden", 
        "spotify_play",
        "spotify_search_ozzy_osbourne",
        "spotify_play",
        "spotify_pause",
        "spotify_close"
    ],
    "spotify_simple_test": [
        "spotify_search_metallica",
        "spotify_play",
        "spotify_pause"
    ]
}


def execute_workflow_sequence_by_name(sequence_name, config, session_id=None):
    """
    Execute a predefined workflow sequence by name
    
    Args:
        sequence_name: Name of the predefined sequence
        config: Configuration object
        session_id: Optional session ID for checkpointing
    
    Returns:
        bool: True if sequence completed successfully, False otherwise
    """
    if sequence_name not in WORKFLOW_SEQUENCES:
        print(f"[ERROR] Unknown workflow sequence: {sequence_name}")
        print(f"Available sequences: {list(WORKFLOW_SEQUENCES.keys())}")
        return False
    
    sequence_objectives = WORKFLOW_SEQUENCES[sequence_name]
    print(f"Executing workflow sequence: {sequence_name}")
    print(f"Sequence: {' -> '.join(sequence_objectives)}")
    
    # First, prepare the application (Spotify)
    print("Preparing Spotify for automation...")
    from app_preparation import launch_application, maximize_application, verify_application_ready
    from config import load_config, get_app_config
    
    app_name = "Spotify"
    try:
        # Load the full config
        full_config = load_config()
        app_config = get_app_config(full_config, app_name)
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    # Launch, maximize, and verify Spotify
    if not launch_application(app_name, app_config, max_retries=3):
        print(f"[FAIL] Failed to launch {app_name}")
        return False
    
    if not maximize_application(app_name, max_retries=3):
        print(f"[FAIL] Failed to maximize {app_name}")
        return False
    
    if not verify_application_ready(app_name):
        print(f"[FAIL] {app_name} is not ready")
        return False
    
    print(f"[OK] {app_name} prepared successfully")
    
    # Convert objective IDs to full objective objects
    from objectives import parse_json_objectives, filter_supported_objectives
    all_objectives = parse_json_objectives(config)
    supported, unsupported = filter_supported_objectives(all_objectives, sequence_objectives)
    
    if not supported:
        print(f"[ERROR] No supported objectives found in sequence '{sequence_name}'")
        return False
    
    if unsupported:
        print(f"[WARN] Some objectives in sequence are not supported: {[obj['id'] for obj in unsupported]}")
    
    return execute_workflow_sequence(supported, config, session_id)


def execute_workflow_sequence(supported_objectives, config, session_id=None):
    """
    For each of the objectives that are supported, start a workflow process to complete them in sequence
    
    Args:
        supported_objectives: List of supported objectives to execute
        config: Configuration object
        session_id: Optional session ID for checkpointing
    
    Returns:
        bool: True if all objectives completed successfully, False otherwise
    """
    if not supported_objectives:
        print("No supported objectives to execute")
        return True
    
    print(f"Starting workflow process for {len(supported_objectives)} objectives...")
    
    # Generate session ID if not provided
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Execute each objective in sequence
    for i, objective in enumerate(supported_objectives):
        print(f"\n[{i+1}/{len(supported_objectives)}] Starting: {objective['name']}")
        
        # Save checkpoint before starting objective
        save_checkpoint(session_id, objective['id'], i, [])
        
        # Execute the objective
        if not execute_single_objective(objective, config, session_id):
            print(f"[FAIL] Objective '{objective['name']}' failed")
            notify_error(f"Objective failed after 3 retry attempts", objective['name'])
            return False
        
        print(f"[OK] Objective '{objective['name']}' completed successfully")
    
    print(f"[OK] All {len(supported_objectives)} objectives completed successfully")
    return True


def execute_single_objective(objective, config, session_id=None):
    """
    Execute a single objective with prerequisite checks and error handling
    
    Args:
        objective: Single objective to execute
        config: Configuration object
        session_id: Optional session ID for checkpointing
    
    Returns:
        bool: True if objective completed successfully, False otherwise
    """
    print(f"Executing: {objective['name']}")

    # If objective has a registered handler, delegate to it.
    try:
        from objectives.mapping import get_handler_for_objective_id
        handler = get_handler_for_objective_id(objective.get('id'))
        if handler:
            print(f"  [DISPATCH] Found handler for objective id '{objective.get('id')}' - delegating")
            return handler(objective, config, session_id)
    except Exception:
        # If mapping import fails, continue with default flow
        pass

    # No handler registered -- run the non-dispatching executor
    return execute_single_objective_no_dispatch(objective, config, session_id)


def execute_single_objective_no_dispatch(objective, config, session_id=None):
    """
    Core executor for a single objective that does NOT perform handler dispatch.
    This is intended for internal use by handlers that need to run the default
    action loop without being re-routed back into handlers (avoids recursion).
    """
    # Create context for prerequisites
    context = {
        'app_name': objective.get('app', 'Notepad'),
        'objective_name': objective['name'],
        'config': config,
        'session_id': session_id,
        'history': [],  # Initialize history for error handling
        # Context data for element_positioned prerequisite
        'visual_template': 'templates/notepad_titlebar.png',  # Template image for element detection
        'expected_position': [50, 10, 5]  # [x, y, tolerance] - expected position with 5 pixel tolerance
    }

    actions = objective.get('actions', [])
    history = []

    for i, action in enumerate(actions):
        print(f"Action {i+1}/{len(actions)}: {action['type']}")

        # Check prerequisites before action
        prerequisites = action.get('prerequisites', [])
        if prerequisites:
            print(f"  Checking {len(prerequisites)} prerequisite(s)...")
            if not verify_prerequisites(prerequisites, context):
                print(f"  [FAIL] Prerequisites not met for action: {action['type']}")
                return handle_action_failure(action, history, "prerequisites_not_met")

        # Execute with retry and error handling
        success = execute_action_with_retry(action, max_retries=3, context=context)

        if not success:
            return handle_action_failure(action, history, "execution_failed")

        history.append(action)
        context['history'] = history  # Update context with current history

        # Save checkpoint after each successful action
        if session_id:
            save_checkpoint(session_id, objective['id'], i + 1, history)
            print(f"  [CHECKPOINT] Saved progress: {len(history)} action(s) completed")

    print(f"[OK] Objective '{objective['name']}' completed successfully")
    return True


def execute_action_with_retry(action, max_retries=3, context=None):
    """
    Execute action with retry logic, screen stability, and error handling
    
    Args:
        action: Action to execute
        max_retries: Maximum number of retry attempts
        context: Context object for prerequisites
    
    Returns:
        bool: True if action completed successfully, False otherwise
    """
    if context is None:
        context = {}
    
    for attempt in range(max_retries):
        print(f"  Attempt {attempt + 1}/{max_retries}")
        
        # Check screen stability before action
        from verification import verify_screen_stable
        if not verify_screen_stable(timeout=2):
            print("  Screen not stable, waiting...")
            time.sleep(1)
        
        # Ensure correct window is focused before action
        app_name = context.get('app_name', 'Notepad')
        from window_ops import find_window, focus_window
        window = find_window(app_name)
        if window:
            print(f"  [FOCUS] Ensuring '{app_name}' window is focused...")
            focus_window(window)
            time.sleep(0.5)  # Give time for focus to take effect
        else:
            print(f"  [WARN] Window '{app_name}' not found - proceeding anyway")
        
        # Take screenshot before action for change detection
        from ui_detection import take_screenshot
        before_screenshot = take_screenshot("screenshots/before_action.png")
        
        # Execute the action
        action_success = execute_action(action)
        
        if action_success:
            # Take screenshot after action
            after_screenshot = take_screenshot("screenshots/after_action.png")
            
            # Verify screen changed for click actions
            if action.get('type') in ['click_image', 'click_text', 'close_window']:
                from ui_detection import detect_screen_change
                if detect_screen_change(before_screenshot, after_screenshot):
                    print("  [OK] Screen change detected - action successful")
                else:
                    print("  [WARN] No screen change detected")
            
            # Check for action completion verification
            verification = action.get('verification')
            if verification:
                context['previous_screenshot'] = before_screenshot
                if not verify_action_complete(verification, context):
                    print(f"  [FAIL] Action verification failed: {action['type']}")
                    if attempt < max_retries - 1:
                        print(f"  Retrying due to verification failure...")
                        time.sleep(2)
                        continue
                    return False
            
            print(f"  [OK] Action '{action['type']}' completed successfully")
            return True
        
        print(f"  [FAIL] Action failed on attempt {attempt + 1}")
        if attempt < max_retries - 1:
            print(f"  Retrying in 2 seconds...")
            time.sleep(2)
    
    print(f"  [FAIL] Action '{action['type']}' failed after {max_retries} attempts")
    return handle_action_failure(action, context.get('history', []), "execution_failed")


def handle_action_failure(action, history, failure_reason):
    """
    Handle action failure with error strategies
    
    Args:
        action: The failed action
        history: History of completed actions
        failure_reason: Reason for failure
    
    Returns:
        bool: False (always fails)
    """
    print(f"[ERROR] Action failure: {failure_reason}")
    
    # Get error strategy from action or use default
    error_strategy = action.get('error_strategy', 'rollback_all')
    
    if error_strategy == 'retry_previous':
        return handle_retry_previous_strategy(action, history)
    elif error_strategy == 'email_dev':
        return handle_email_dev_strategy(action, history, failure_reason)
    elif error_strategy == 'rollback_all':
        return handle_rollback_all_strategy(action, history, failure_reason)
    else:
        print(f"Unknown error strategy: {error_strategy}")
        return False


def handle_retry_previous_strategy(action, history):
    """Error strategy: Retry previous action"""
    print("  [STRATEGY] Retrying previous action...")
    print(f"  [INFO] Current action '{action.get('type', 'Unknown')}' failed, retrying previous")
    if history:
        previous_action = history[-1]
        print(f"  Retrying: {previous_action['type']}")
        # Create minimal context for retry
        context = {'history': history}
        return execute_action_with_retry(previous_action, max_retries=1, context=context)
    else:
        print("  [WARN] No previous action to retry")
        return False


def handle_email_dev_strategy(action, history, failure_reason):
    """Error strategy: Email developer and continue"""
    print("  [STRATEGY] Notifying developer...")
    print(f"  [INFO] History contains {len(history)} completed actions")
    notify_error(f"Action failed: {failure_reason}", action.get('type', 'Unknown'))
    return False


def handle_rollback_all_strategy(action, history, failure_reason):
    """Error strategy: Rollback all actions and notify"""
    print("  [STRATEGY] Rolling back all actions...")
    rollback_actions(history)
    notify_error(f"Objective failed after rollback: {failure_reason}", action.get('type', 'Unknown'))
    return False


def rollback_actions(history):
    """
    Rollback completed actions
    
    Args:
        history: List of completed actions to rollback
    """
    print(f"Rolling back {len(history)} actions")
    
    import pyautogui
    
    for action in reversed(history):
        action_type = action.get('type')
        print(f"  Rolling back: {action_type}")
        
        if action_type == 'type_text':
            # Undo typing
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('backspace')
        elif action_type == 'hotkey':
            # Try undo
            pyautogui.hotkey('ctrl', 'z')
        elif action_type == 'click_image' or action_type == 'click_text':
            # For click actions, try to click back or use escape
            pyautogui.press('escape')
        elif action_type == 'close_window':
            # For close window, try to reopen (this is complex)
            print("  [WARN] Cannot automatically reopen closed window")
        
        time.sleep(0.5)  # Small delay between rollback actions
