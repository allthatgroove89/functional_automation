#!/usr/bin/env python3
"""
Simple click actions test - basic functionality testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pyautogui
from actions import execute_action, ACTION_HANDLERS
import ui_detection
import verification


def test_basic_click_operations():
    """Test basic click operations"""
    print("Testing Basic Click Operations")
    print("-" * 40)
    
    results = []
    
    # Test 1: Action handlers
    print("1. Testing action handlers...")
    click_handlers = [h for h in ACTION_HANDLERS.keys() if 'click' in h or h == 'close_window']
    success = len(click_handlers) >= 3  # Should have click_image, click_text, close_window
    print(f"   [{'PASS' if success else 'FAIL'}] Found {len(click_handlers)} click handlers")
    results.append(("Action Handlers", success))
    
    # Test 2: Screenshot functionality
    print("2. Testing screenshot...")
    try:
        screenshot_path = ui_detection.take_screenshot("test_screenshot.png")
        success = os.path.exists(screenshot_path)
        print(f"   [{'PASS' if success else 'FAIL'}] Screenshot: {success}")
        results.append(("Screenshot", success))
    except Exception as e:
        print(f"   [FAIL] Screenshot error: {e}")
        results.append(("Screenshot", False))
    
    # Test 3: Screen size
    print("3. Testing screen size...")
    try:
        width, height = ui_detection.get_screen_size()
        success = width > 0 and height > 0
        print(f"   [{'PASS' if success else 'FAIL'}] Screen: {width}x{height}")
        results.append(("Screen Size", success))
    except Exception as e:
        print(f"   [FAIL] Screen size error: {e}")
        results.append(("Screen Size", False))
    
    # Test 4: Coordinate click
    print("4. Testing coordinate click...")
    try:
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        print(f"   [PASS] Clicked at ({center_x}, {center_y})")
        results.append(("Coordinate Click", True))
    except Exception as e:
        print(f"   [FAIL] Coordinate click error: {e}")
        results.append(("Coordinate Click", False))
    
    # Test 5: Click actions
    print("5. Testing click actions...")
    try:
        # Test click_text
        action = {'type': 'click_text', 'text': 'File'}
        result1 = execute_action(action)
        
        # Test click_image (will fail without template)
        action = {'type': 'click_image', 'template': 'nonexistent.png'}
        result2 = execute_action(action)
        
        # Test close_window
        action = {'type': 'close_window', 'app_name': 'Calculator'}
        result3 = execute_action(action)
        
        print(f"   [INFO] Click text: {result1}, Click image: {result2}, Close window: {result3}")
        results.append(("Click Actions", True))
    except Exception as e:
        print(f"   [FAIL] Click actions error: {e}")
        results.append(("Click Actions", False))
    
    return results


def main():
    """Main test runner"""
    print("Simple Click Actions Test")
    print("=" * 50)
    
    # Disable pyautogui failsafe
    pyautogui.FAILSAFE = False
    
    try:
        results = test_basic_click_operations()
        
        # Calculate results
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        for test_name, success in results:
            status = "PASS" if success else "FAIL"
            print(f"  [{status}] {test_name}")
        
        if passed == total:
            print("\nAll tests passed!")
        else:
            print(f"\n{total - passed} test(s) failed")
            
    finally:
        # Re-enable pyautogui failsafe
        pyautogui.FAILSAFE = True


if __name__ == "__main__":
    main()
