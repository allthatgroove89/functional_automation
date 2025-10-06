#!/usr/bin/env python3
"""
Simple test script for click actions operations
"""

import time
import os
import pyautogui
from actions import execute_action, ACTION_HANDLERS
import ui_detection
import verification


def test_basic_functionality():
    """Test basic click functionality"""
    print("Testing Basic Click Actions")
    print("-" * 40)
    
    results = []
    
    # Test 1: Action handlers are registered
    print("1. Testing action handlers registration...")
    expected_handlers = ['click_image', 'click_text', 'close_window']
    missing = [h for h in expected_handlers if h not in ACTION_HANDLERS]
    success = len(missing) == 0
    print(f"   [{'PASS' if success else 'FAIL'}] Handlers registered: {success}")
    results.append(("Action Handlers", success))
    
    # Test 2: Screenshot functionality
    print("2. Testing screenshot functionality...")
    try:
        screenshot_path = ui_detection.take_screenshot("test_screenshot.png")
        success = os.path.exists(screenshot_path)
        print(f"   [{'PASS' if success else 'FAIL'}] Screenshot taken: {success}")
        results.append(("Screenshot", success))
    except Exception as e:
        print(f"   [FAIL] Screenshot failed: {e}")
        results.append(("Screenshot", False))
    
    # Test 3: Screen size detection
    print("3. Testing screen size detection...")
    try:
        width, height = ui_detection.get_screen_size()
        success = width > 0 and height > 0
        print(f"   [{'PASS' if success else 'FAIL'}] Screen size: {width}x{height}")
        results.append(("Screen Size", success))
    except Exception as e:
        print(f"   [FAIL] Screen size failed: {e}")
        results.append(("Screen Size", False))
    
    # Test 4: Coordinate clicking
    print("4. Testing coordinate clicking...")
    try:
        # Get screen center
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        
        # Take screenshot before click
        ui_detection.take_screenshot("before_click.png")
        
        # Click at center (safe location)
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # Take screenshot after click
        ui_detection.take_screenshot("after_click.png")
        
        print(f"   [PASS] Clicked at ({center_x}, {center_y})")
        results.append(("Coordinate Click", True))
    except Exception as e:
        print(f"   [FAIL] Coordinate click failed: {e}")
        results.append(("Coordinate Click", False))
    
    # Test 5: Screen stability check
    print("5. Testing screen stability check...")
    try:
        stable = verification.verify_screen_stable(timeout=2)
        print(f"   [{'PASS' if stable else 'FAIL'}] Screen stable: {stable}")
        results.append(("Screen Stability", stable))
    except Exception as e:
        print(f"   [FAIL] Stability check failed: {e}")
        results.append(("Screen Stability", False))
    
    # Test 6: Error handling
    print("6. Testing error handling...")
    try:
        # Test with invalid action
        invalid_action = {'type': 'nonexistent_action'}
        result = execute_action(invalid_action)
        print(f"   [PASS] Invalid action handled gracefully: {result}")
        results.append(("Error Handling", True))
    except Exception as e:
        print(f"   [FAIL] Error handling failed: {e}")
        results.append(("Error Handling", False))
    
    return results


def test_click_actions():
    """Test specific click actions"""
    print("\nTesting Click Actions")
    print("-" * 40)
    
    # Test click_text action
    print("1. Testing click_text action...")
    action = {
        'type': 'click_text',
        'text': 'File'  # Common menu item
    }
    
    try:
        result = execute_action(action)
        print(f"   [{'PASS' if result else 'FAIL'}] Click text result: {result}")
        text_success = result
    except Exception as e:
        print(f"   [FAIL] Click text failed: {e}")
        text_success = False
    
    # Test click_image action
    print("2. Testing click_image action...")
    action = {
        'type': 'click_image',
        'template': 'nonexistent_template.png',
        'confidence': 0.8
    }
    
    try:
        result = execute_action(action)
        print(f"   [{'PASS' if result else 'FAIL'}] Click image result: {result}")
        image_success = result
    except Exception as e:
        print(f"   [FAIL] Click image failed: {e}")
        image_success = False
    
    # Test close_window action
    print("3. Testing close_window action...")
    action = {
        'type': 'close_window',
        'app_name': 'Calculator'  # Try to close calculator if open
    }
    
    try:
        result = execute_action(action)
        print(f"   [{'PASS' if result else 'FAIL'}] Close window result: {result}")
        close_success = result
    except Exception as e:
        print(f"   [FAIL] Close window failed: {e}")
        close_success = False
    
    return [text_success, image_success, close_success]


def run_tests():
    """Run all tests"""
    print("Click Actions Test Suite")
    print("=" * 50)
    
    # Disable pyautogui failsafe for testing
    pyautogui.FAILSAFE = False
    
    # Run basic tests
    basic_results = test_basic_functionality()
    
    # Run action tests
    action_results = test_click_actions()
    
    # Re-enable pyautogui failsafe
    pyautogui.FAILSAFE = True
    
    # Calculate results
    basic_passed = sum(1 for _, success in basic_results if success)
    basic_total = len(basic_results)
    
    action_passed = sum(1 for result in action_results if result)
    action_total = len(action_results)
    
    total_passed = basic_passed + action_passed
    total_tests = basic_total + action_total
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Test Results: {total_passed}/{total_tests} tests passed")
    
    print(f"\nBasic Tests: {basic_passed}/{basic_total}")
    for test_name, success in basic_results:
        status = "PASS" if success else "FAIL"
        print(f"   [{status}] {test_name}")
    
    print(f"\nAction Tests: {action_passed}/{action_total}")
    print(f"   [{'PASS' if action_results[0] else 'FAIL'}] Click Text")
    print(f"   [{'PASS' if action_results[1] else 'FAIL'}] Click Image")
    print(f"   [{'PASS' if action_results[2] else 'FAIL'}] Close Window")
    
    if total_passed == total_tests:
        print("\nAll tests passed!")
    else:
        print(f"\n{total_tests - total_passed} test(s) failed")
    
    return total_passed == total_tests


def main():
    """Main test runner"""
    print("Click Actions Test")
    print("This will test basic click action functionality")
    print("\nWARNING: This test will perform mouse clicks")
    print("Make sure no important applications are open.")
    
    response = input("\nContinue with tests? (y/N): ").strip().lower()
    if response != 'y':
        print("Test cancelled by user")
        return
        
    success = run_tests()
    
    if success:
        print("\nClick action tests completed successfully!")
    else:
        print("\nSome tests failed. Check the results above.")


if __name__ == "__main__":
    main()
