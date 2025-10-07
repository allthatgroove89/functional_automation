import time
import pyautogui
from actions import execute_action
from verification import verify_prerequisites, verify_action_complete
from notifications import notify_error


def execute_objective(objective, config):
    """Execute single objective with prerequisite checks and error handling"""
    print(f"Executing: {objective['name']}")
    
    # Create context for prerequisites
    context = {
        'app_name': objective.get('app', 'Notepad'),
        'objective_name': objective['name'],
        'config': config
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
    
    print(f"[OK] Objective '{objective['name']}' completed successfully")
    return True


def execute_action_with_retry(action, max_retries=3, context=None):
    """Execute action with retry logic, screen stability, and error handling"""
    if context is None:
        context = {}
    
    for attempt in range(max_retries):
        print(f"  Attempt {attempt + 1}/{max_retries}")
        
        # Check screen stability before action
        from verification import verify_screen_stable
        if not verify_screen_stable(timeout=2):
            print("  Screen not stable, waiting...")
            time.sleep(1)
        
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
    return False


def handle_action_failure(action, history, failure_reason):
    """Handle action failure with error strategies"""
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
    if history:
        previous_action = history[-1]
        print(f"  Retrying: {previous_action['type']}")
        return execute_action_with_retry(previous_action, max_retries=1)
    return False


def handle_email_dev_strategy(action, history, failure_reason):
    """Error strategy: Email developer and continue"""
    print("  [STRATEGY] Notifying developer...")
    notify_error(f"Action failed: {failure_reason}", action.get('type', 'Unknown'))
    return False


def handle_rollback_all_strategy(action, history, failure_reason):
    """Error strategy: Rollback all actions and notify"""
    print("  [STRATEGY] Rolling back all actions...")
    rollback_actions(history)
    notify_error(f"Objective failed after rollback: {failure_reason}", action.get('type', 'Unknown'))
    return False


def rollback_actions(history):
    """Rollback completed actions"""
    print(f"Rolling back {len(history)} actions")
    
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

