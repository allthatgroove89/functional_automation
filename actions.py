import time
import pyautogui
import cv2
import numpy as np
from config import load_config
from window_ops import find_window, launch_app, focus_window, maximize_window


def execute_type_text(action):
    """Type text action"""
    text = action.get('text', '')
    pyautogui.typewrite(text)
    time.sleep(0.5)
    return True


def execute_hotkey(action):
    """Execute hotkey action"""
    keys = action.get('keys', [])
    if not keys:
        return False
    pyautogui.hotkey(*keys)
    time.sleep(0.5)
    return True


def execute_key_press(action):
    """Press single key"""
    key = action.get('key')
    if not key:
        return False
    pyautogui.press(key)
    time.sleep(0.5)
    return True


def execute_wait(action):
    """Wait/sleep for specified duration"""
    duration = action.get('duration', 1)
    time.sleep(duration)
    return True


def execute_click_image(action):
    """Find and click on an image/template"""
    template_path = action.get('template')
    confidence = action.get('confidence', 0.8)
    offset_x = action.get('offset_x', 0)
    offset_y = action.get('offset_y', 0)
    
    if not template_path:
        print("No template path specified")
        return False
    
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        
        # Load template
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Could not load template: {template_path}")
            return False
        
        # Match template
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            # Calculate center of matched region
            h, w = template.shape
            center_x = max_loc[0] + w // 2 + offset_x
            center_y = max_loc[1] + h // 2 + offset_y
            
            print(f"Found template at ({center_x}, {center_y}) with confidence {max_val:.2f}")
            
            # Click at the location
            pyautogui.click(center_x, center_y)
            time.sleep(0.5)
            return True
        else:
            print(f"Template not found. Best match confidence: {max_val:.2f}")
            return False
            
    except Exception as e:
        print(f"Error in click_image: {e}")
        return False


def execute_click_text(action):
    """Find and click on text using PyAutoGUI's locate functions"""
    text = action.get('text')
    
    if not text:
        print("No text specified for click_text action")
        return False
    
    try:
        # Try to locate the text on screen
        location = pyautogui.locateOnScreen(text, confidence=0.8)
        
        if location:
            # Click center of the found text
            center = pyautogui.center(location)
            pyautogui.click(center)
            time.sleep(0.5)
            return True
        else:
            print(f"Text '{text}' not found on screen")
            return False
            
    except Exception as e:
        print(f"Error in click_text: {e}")
        return False


def execute_close_window(action):
    """Close window by clicking the X button"""
    app_name = action.get('app_name', 'Notepad')
    handle_dialog = action.get('handle_dialog', True)
    
    # Find the window
    window = find_window(app_name)
    if not window:
        print(f"Window {app_name} not found")
        return False
    
    try:
        # Get window position and size
        x, y, width, height = window.left, window.top, window.width, window.height
        
        # X button is typically at top-right corner
        # Offset from right edge: ~15px, from top: ~15px
        close_x = x + width - 15
        close_y = y + 15
        
        print(f"Clicking close button at ({close_x}, {close_y})")
        pyautogui.click(close_x, close_y)
        time.sleep(0.5)
        
        # If handle_dialog is True, try to handle save dialog
        if handle_dialog:
            time.sleep(1)
            
            # Use keyboard shortcut Tab+Enter instead of clicking random position
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"Error in close_window: {e}")
        return False


def execute_switch_app(action):
    """Switch to another application"""
    app_name = action.get('app_name')
    if not app_name:
        print("No app_name specified for switch_app action")
        return False
    
    # Load config to get app details
    config = load_config()
    app_config = None
    for app in config['apps']:
        if app['name'] == app_name:
            app_config = app
            break
    
    if not app_config:
        print(f"App {app_name} not found in config")
        return False
    
    # Try to find existing window
    window = find_window(app_name)
    
    # Launch if not found
    if not window:
        print(f"Launching {app_name}...")
        launch_app(
            app_config['path'], 
            app_config.get('startup_delay', 2),
            app_config.get('args')
        )
        time.sleep(1)
        window = find_window(app_name)
    
    # Focus and maximize
    if window:
        focus_window(window)
        maximize_window(window)
        return True
    
    print(f"Could not find or launch {app_name}")
    return False


# Action dispatcher using dictionary
ACTION_HANDLERS = {
    'type_text': execute_type_text,
    'hotkey': execute_hotkey,
    'key_press': execute_key_press,
    'wait': execute_wait,
    'click_image': execute_click_image,
    'click_text': execute_click_text,
    'close_window': execute_close_window,
    'switch_app': execute_switch_app,
}


def execute_action(action):
    """Execute any action type"""
    action_type = action.get('type')
    handler = ACTION_HANDLERS.get(action_type)
    
    if handler:
        return handler(action)
    
    print(f"Unknown action type: {action_type}")
    return False

