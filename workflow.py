import time
import pyautogui
from actions import execute_action


def execute_objective(objective, config):
    """Execute single objective"""
    print(f"Executing: {objective['name']}")
    
    actions = objective.get('actions', [])
    history = []
    
    for i, action in enumerate(actions):
        print(f"Action {i+1}/{len(actions)}: {action['type']}")
        
        # Execute with retry
        success = execute_action_with_retry(action, max_retries=3)
        
        if not success:
            print(f"Action failed: {action['type']}")
            rollback_actions(history)
            return False
        
        history.append(action)
    
    return True


def execute_action_with_retry(action, max_retries=3):
    """Execute action with retry logic and screen stability"""
    for attempt in range(max_retries):
        # Check screen stability before action
        from verification import verify_screen_stable
        if not verify_screen_stable(timeout=2):
            print("Screen not stable, waiting...")
            time.sleep(1)
        
        # Take screenshot before action for change detection
        from ui_detection import take_screenshot
        before_screenshot = take_screenshot("screenshots/before_action.png")
        
        if execute_action(action):
            # Take screenshot after action
            after_screenshot = take_screenshot("screenshots/after_action.png")
            
            # Verify screen changed for click actions
            if action.get('type') in ['click_image', 'click_text', 'close_window']:
                from ui_detection import detect_screen_change
                if detect_screen_change(before_screenshot, after_screenshot):
                    print("[OK] Screen change detected - action successful")
                else:
                    print("[WARN] No screen change detected")
            
            # Check for action verification
            verification = action.get('verification')
            if verification:
                from verification import verify_action_complete
                context = {'previous_screenshot': before_screenshot}
                if not verify_action_complete(verification, context):
                    print(f"[FAIL] Action verification failed: {action['type']}")
                    return False
            
            return True
        
        print(f"Retry {attempt + 1}/{max_retries}")
        time.sleep(2)
    
    return False


def rollback_actions(history):
    """Rollback completed actions"""
    print(f"Rolling back {len(history)} actions")
    
    for action in reversed(history):
        action_type = action.get('type')
        
        if action_type == 'type_text':
            # Undo typing
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('backspace')
        elif action_type == 'hotkey':
            # Try undo
            pyautogui.hotkey('ctrl', 'z')

