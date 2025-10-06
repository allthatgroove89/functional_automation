#!/usr/bin/env python3
"""
Quick test script for click actions operations
Simple tests that can be run immediately
"""

import time
import os
import pyautogui
from actions import execute_action, ACTION_HANDLERS
import ui_detection
import verification


def test_basic_click_actions():
    """Test basic click actions without complex setup"""
    print("Testing Basic Click Actions")
    print("-" * 40)
    
    results = []
    
    # Test 1: Action handlers are registered
    print("1. Testing action handlers registration...")
    expected_handlers = ['click_image', 'click_text', 'close_window']
    missing = [h for h in expected_handlers if h not in ACTION_HANDLERS]
    success = len(missing) == 0
    print(f"   {'✅' if success else '❌'} Handlers registered: {success}")
    results.append(("Action Handlers", success))
    
    # Test 2: Screenshot functionality
    print("2. Testing screenshot functionality...")
    try:
        screenshot_path = ui_detection.take_screenshot("test_screenshot.png")
        success = os.path.exists(screenshot_path)
        print(f"   {'✅' if success else '❌'} Screenshot taken: {success}")
        results.append(("Screenshot", success))
    except Exception as e:
        print(f"   ❌ Screenshot failed: {e}")
        results.append(("Screenshot", False))
    
    # Test 3: Screen size detection
    print("3. Testing screen size detection...")
    try:
        width, height = ui_detection.get_screen_size()
        success = width > 0 and height > 0
        print(f"   {'✅' if success else '❌'} Screen size: {width}x{height}")
        results.append(("Screen Size", success))
    except Exception as e:
        print(f"   ❌ Screen size failed: {e}")
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
        
        print(f"   ✅ Clicked at ({center_x}, {center_y})")
        results.append(("Coordinate Click", True))
    except Exception as e:
        print(f"   ❌ Coordinate click failed: {e}")
        results.append(("Coordinate Click", False))
    
    # Test 5: Screen stability check
    print("5. Testing screen stability check...")
    try:
        stable = verification.verify_screen_stable(timeout=2)
        print(f"   {'✅' if stable else '❌'} Screen stable: {stable}")
        results.append(("Screen Stability", stable))
    except Exception as e:
        print(f"   ❌ Stability check failed: {e}")
        results.append(("Screen Stability", False))
    
    # Test 6: Error handling
    print("6. Testing error handling...")
    try:
        # Test with invalid action
        invalid_action = {'type': 'nonexistent_action'}
        result = execute_action(invalid_action)
        print(f"   ✅ Invalid action handled gracefully: {result}")
        results.append(("Error Handling", True))
    except Exception as e:
        print(f"   ❌ Error handling failed: {e}")
        results.append(("Error Handling", False))
    
    return results


def test_click_text_action():
    """Test click_text action specifically"""
    print("\n🔍 Testing Click Text Action")
    print("-" * 40)
    
    # Test click_text action with common UI text
    action = {
        'type': 'click_text',
        'text': 'File'  # Common menu item
    }
    
    try:
        print("Testing click_text action...")
        result = execute_action(action)
        print(f"   {'✅' if result else '❌'} Click text result: {result}")
        return result
    except Exception as e:
        print(f"   ❌ Click text failed: {e}")
        return False


def test_click_image_action():
    """Test click_image action specifically"""
    print("\n🔍 Testing Click Image Action")
    print("-" * 40)
    
    # Test click_image action (will likely fail without real template)
    action = {
        'type': 'click_image',
        'template': 'nonexistent_template.png',
        'confidence': 0.8
    }
    
    try:
        print("Testing click_image action...")
        result = execute_action(action)
        print(f"   {'✅' if result else '❌'} Click image result: {result}")
        return result
    except Exception as e:
        print(f"   ❌ Click image failed: {e}")
        return False


def test_close_window_action():
    """Test close_window action specifically"""
    print("\n🔍 Testing Close Window Action")
    print("-" * 40)
    
    # Test close_window action
    action = {
        'type': 'close_window',
        'app_name': 'Calculator'  # Try to close calculator if open
    }
    
    try:
        print("Testing close_window action...")
        result = execute_action(action)
        print(f"   {'✅' if result else '❌'} Close window result: {result}")
        return result
    except Exception as e:
        print(f"   ❌ Close window failed: {e}")
        return False


def run_quick_tests():
    """Run all quick tests"""
    print("Quick Click Actions Test Suite")
    print("=" * 50)
    
    # Disable pyautogui failsafe for testing
    pyautogui.FAILSAFE = False
    
    # Run basic tests
    basic_results = test_basic_click_actions()
    
    # Run specific action tests
    text_result = test_click_text_action()
    image_result = test_click_image_action()
    close_result = test_close_window_action()
    
    # Re-enable pyautogui failsafe
    pyautogui.FAILSAFE = True
    
    # Calculate results
    basic_passed = sum(1 for _, success in basic_results if success)
    basic_total = len(basic_results)
    
    action_results = [text_result, image_result, close_result]
    action_passed = sum(1 for result in action_results if result)
    action_total = len(action_results)
    
    total_passed = basic_passed + action_passed
    total_tests = basic_total + action_total
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {total_passed}/{total_tests} tests passed")
    
    print(f"\n📋 Basic Tests: {basic_passed}/{basic_total}")
    for test_name, success in basic_results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n📋 Action Tests: {action_passed}/{action_total}")
    print(f"   {'✅' if text_result else '❌'} Click Text")
    print(f"   {'✅' if image_result else '❌'} Click Image")
    print(f"   {'✅' if close_result else '❌'} Close Window")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
    
    return total_passed == total_tests


def main():
    """Main test runner"""
    print("Quick Click Actions Test")
    print("This will test basic click action functionality")
    print("\n⚠️  WARNING: This test will perform mouse clicks")
    print("Make sure no important applications are open.")
    
    response = input("\nContinue with tests? (y/N): ").strip().lower()
    if response != 'y':
        print("Test cancelled by user")
        return
        
    success = run_quick_tests()
    
    if success:
        print("\n🎉 Quick click action tests completed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check the results above.")


if __name__ == "__main__":
    main()
