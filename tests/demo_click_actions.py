#!/usr/bin/env python3
"""
Demo script for click actions operations
Demonstrates click action functionality without user interaction
"""

import time
import os
import pyautogui
from actions import execute_action, ACTION_HANDLERS
import ui_detection
import verification


def demo_click_actions():
    """Demonstrate click actions functionality"""
    print("Click Actions Operations Demo")
    print("=" * 50)
    
    # 1. Show available action handlers
    print("\n1. Available Click Action Handlers:")
    print("-" * 40)
    click_handlers = [name for name in ACTION_HANDLERS.keys() if 'click' in name or name == 'close_window']
    for handler in click_handlers:
        print(f"   - {handler}")
    
    # 2. Test screenshot functionality
    print("\n2. Testing Screenshot Functionality:")
    print("-" * 40)
    try:
        screenshot_path = ui_detection.take_screenshot("demo_screenshot.png")
        if os.path.exists(screenshot_path):
            print(f"   [SUCCESS] Screenshot saved: {screenshot_path}")
        else:
            print("   [FAILED] Screenshot not saved")
    except Exception as e:
        print(f"   [ERROR] Screenshot failed: {e}")
    
    # 3. Test screen size detection
    print("\n3. Screen Size Detection:")
    print("-" * 40)
    try:
        width, height = ui_detection.get_screen_size()
        print(f"   [SUCCESS] Screen size: {width}x{height}")
    except Exception as e:
        print(f"   [ERROR] Screen size detection failed: {e}")
    
    # 4. Test coordinate clicking (safe location)
    print("\n4. Testing Coordinate Clicking:")
    print("-" * 40)
    try:
        # Get screen center
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        
        print(f"   [INFO] Screen center: ({center_x}, {center_y})")
        
        # Take screenshot before
        ui_detection.take_screenshot("before_click_demo.png")
        
        # Click at center
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # Take screenshot after
        ui_detection.take_screenshot("after_click_demo.png")
        
        print("   [SUCCESS] Coordinate click performed")
    except Exception as e:
        print(f"   [ERROR] Coordinate click failed: {e}")
    
    # 5. Test screen stability
    print("\n5. Testing Screen Stability:")
    print("-" * 40)
    try:
        stable = verification.verify_screen_stable(timeout=2)
        print(f"   [SUCCESS] Screen stable: {stable}")
    except Exception as e:
        print(f"   [ERROR] Stability check failed: {e}")
    
    # 6. Test click_text action
    print("\n6. Testing Click Text Action:")
    print("-" * 40)
    action = {
        'type': 'click_text',
        'text': 'File'  # Common menu item
    }
    
    try:
        result = execute_action(action)
        print(f"   [RESULT] Click text action: {result}")
    except Exception as e:
        print(f"   [ERROR] Click text failed: {e}")
    
    # 7. Test click_image action
    print("\n7. Testing Click Image Action:")
    print("-" * 40)
    action = {
        'type': 'click_image',
        'template': 'nonexistent_template.png',
        'confidence': 0.8
    }
    
    try:
        result = execute_action(action)
        print(f"   [RESULT] Click image action: {result}")
    except Exception as e:
        print(f"   [ERROR] Click image failed: {e}")
    
    # 8. Test close_window action
    print("\n8. Testing Close Window Action:")
    print("-" * 40)
    action = {
        'type': 'close_window',
        'app_name': 'Calculator'
    }
    
    try:
        result = execute_action(action)
        print(f"   [RESULT] Close window action: {result}")
    except Exception as e:
        print(f"   [ERROR] Close window failed: {e}")
    
    # 9. Test error handling
    print("\n9. Testing Error Handling:")
    print("-" * 40)
    try:
        invalid_action = {'type': 'nonexistent_action'}
        result = execute_action(invalid_action)
        print(f"   [SUCCESS] Invalid action handled: {result}")
    except Exception as e:
        print(f"   [ERROR] Error handling failed: {e}")
    
    # 10. Show UI detection capabilities
    print("\n10. UI Detection Capabilities:")
    print("-" * 40)
    try:
        # Test template finding (will fail without real template)
        template_path = "nonexistent_template.png"
        location = ui_detection.find_template(template_path, threshold=0.8)
        print(f"   [INFO] Template finding: {location}")
        
        # Test screen change detection
        before_path = ui_detection.take_screenshot("stability_before.png")
        time.sleep(1)
        after_path = ui_detection.take_screenshot("stability_after.png")
        
        change_detected = ui_detection.detect_screen_change(before_path, after_path)
        print(f"   [INFO] Screen change detected: {change_detected}")
        
    except Exception as e:
        print(f"   [ERROR] UI detection test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Click Actions Demo Complete!")
    print("Check the screenshots/ directory for generated images.")


def show_click_action_examples():
    """Show examples of click action configurations"""
    print("\nClick Action Configuration Examples:")
    print("-" * 50)
    
    examples = [
        {
            "name": "Click Image/Template",
            "action": {
                "type": "click_image",
                "template": "button_template.png",
                "confidence": 0.8,
                "offset_x": 0,
                "offset_y": 0
            }
        },
        {
            "name": "Click Text (OCR)",
            "action": {
                "type": "click_text",
                "text": "Submit"
            }
        },
        {
            "name": "Close Window",
            "action": {
                "type": "close_window",
                "app_name": "Notepad"
            }
        },
        {
            "name": "Coordinate Click",
            "action": {
                "type": "click_image",  # Using click_image with coordinates
                "template": "any_template.png",
                "offset_x": 100,
                "offset_y": 200
            }
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        print(f"  Action: {example['action']}")


if __name__ == "__main__":
    # Disable pyautogui failsafe for demo
    pyautogui.FAILSAFE = False
    
    try:
        demo_click_actions()
        show_click_action_examples()
    finally:
        # Re-enable pyautogui failsafe
        pyautogui.FAILSAFE = True
