import time
import pyautogui
from window_ops import find_window
import ui_detection


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
    
    """Wait for screen stability before clicking"""
    from verification import verify_screen_stable
    if not verify_screen_stable(timeout=2):
        print("Screen is not stable, skipping click")

    # Use ui_detection module
    return ui_detection.find_and_click_template(
        template_path,
        threshold=confidence,
        offset_x=offset_x,
        offset_y=offset_y
    )


def execute_click_text(action):
    """Find and click on text using OCR"""
    text = action.get('text')
    region = action.get('region')  # Optional region to search
    use_smart_crop = action.get('use_smart_crop', True)  # Enable smart cropping by default
    text_hint = action.get('text_hint')  # Optional hint about text location
    confidence_threshold = action.get('confidence', 0.8)
    
    if not text:
        print("No text specified for click_text action")
        return False
    
    try:
        # Use OCR-based text detection with smart cropping
        return ui_detection.find_and_click_text(
            text=text,
            region=region,
            use_smart_crop=use_smart_crop,
            text_hint=text_hint,
            confidence_threshold=confidence_threshold,
            delay=0.5
        )
            
    except Exception as e:
        print(f"Error in click_text: {e}")
        return False


def execute_verify_text(action):
    """Verify text is present on screen using OCR"""
    text = action.get('text')
    region = action.get('region')
    confidence_threshold = action.get('confidence', 0.8)
    
    if not text:
        print("No text specified for verify_text action")
        return False
    
    try:
        # Use OCR to verify text presence
        return ui_detection.verify_text_present(
            text=text,
            region=region,
            confidence_threshold=confidence_threshold
        )
        
    except Exception as e:
        print(f"Error in verify_text: {e}")
        return False


def execute_wait_for_text(action):
    """Wait for text to appear using OCR"""
    text = action.get('text')
    timeout = action.get('timeout', 10)
    region = action.get('region')
    confidence_threshold = action.get('confidence', 0.8)
    check_interval = action.get('check_interval', 0.5)
    
    if not text:
        print("No text specified for wait_for_text action")
        return False
    
    try:
        # Use OCR to wait for text
        return ui_detection.wait_for_text(
            text=text,
            timeout=timeout,
            region=region,
            confidence_threshold=confidence_threshold,
            check_interval=check_interval
        )
        
    except Exception as e:
        print(f"Error in wait_for_text: {e}")
        return False


def execute_close_window(action):
    """Close window by clicking the X button"""
    app_name = action.get('app_name', 'Notepad')
    
    # Find the window
    window = find_window(app_name)
    if not window:
        print(f"Window {app_name} not found")
        return False
    
    try:
        # Get window position and size
        x, y, width = window.left, window.top, window.width
        
        # X button is typically at top-right corner
        # Offset from right edge: ~15px, from top: ~15px
        close_x = x + width - 15
        close_y = y + 15
        
        print(f"Clicking close button at ({close_x}, {close_y})")
        pyautogui.click(close_x, close_y)
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"Error in close_window: {e}")
        return False


# Action dispatcher using dictionary
ACTION_HANDLERS = {
    'type_text': execute_type_text,
    'hotkey': execute_hotkey,
    'key_press': execute_key_press,
    'wait': execute_wait,
    'click_image': execute_click_image,
    'click_text': execute_click_text,
    'verify_text': execute_verify_text,
    'wait_for_text': execute_wait_for_text,
    'close_window': execute_close_window,
}

def execute_action(action):
    """Execute any action type"""
    action_type = action.get('type')
    handler = ACTION_HANDLERS.get(action_type)
    
    if handler:
        return handler(action)
    
    print(f"Unknown action type: {action_type}")
    return False

