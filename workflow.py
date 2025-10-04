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
    """Execute action with retry logic"""
    for attempt in range(max_retries):
        if execute_action(action):
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

