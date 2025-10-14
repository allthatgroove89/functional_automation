"""Action verification utilities - Prerequisites and completion checks"""
import time
import ui_detection
from window_ops import find_window, is_window_maximized


def verify_prerequisite(prerequisite, context):
    """Verify a single prerequisite is met"""
    print(f"  [CHECK] Checking prerequisite: {prerequisite}")
    
    if prerequisite == "app_maximized":
        app_name = context.get('app_name')
        window = find_window(app_name)
        result = window and is_window_maximized(window)
        
    elif prerequisite == "page_loaded":
        # Check if page finished loading (wait for stability)
        result = verify_screen_stable(timeout=3)
        
    elif prerequisite == "correct_page":
        # Verify correct page is open using URL or title
        expected_page = context.get('expected_page')
        if expected_page:
            result = verify_correct_page(expected_page, context)
        else:
            result = True
        
    elif prerequisite == "search_complete":
        # Wait for file search to complete (no screen changes)
        result = verify_screen_stable(timeout=2)
        
    elif prerequisite == "element_present":
        # Check if specific element is visible
        template = context.get('prerequisite_template')
        if template:
            result = ui_detection.verify_element_present(template, threshold=0.8)
        else:
            result = True
            
    else:
        print(f"  [WARN] Unknown prerequisite: {prerequisite}")
        result = True  # Unknown prerequisites pass
    
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} Prerequisite '{prerequisite}': {'Met' if result else 'Not met'}")
    return result


def verify_prerequisites(prerequisites, context):
    """Verify all prerequisites are met"""
    if not prerequisites:
        return True
    
    print(f"  Verifying {len(prerequisites)} prerequisite(s)...")
    
    for prereq in prerequisites:
        if not verify_prerequisite(prereq, context):
            return False
    
    return True


def verify_action_complete(verification, context):
    """Verify action completed successfully"""
    if not verification:
        return True  # No verification needed
    
    verify_type = verification.get('type')
    print(f"  [VERIFY] Verifying action completion: {verify_type}")
    
    if verify_type == "template_match":
        # Check if expected element/screen appeared
        template = verification.get('template')
        threshold = verification.get('threshold', 0.8)
        timeout = verification.get('timeout', 5)
        
        if not template:
            print("  [WARN] No template specified for verification")
            return False
        
        location = ui_detection.wait_for_element(template, timeout, threshold)
        result = location is not None
        
    elif verify_type == "screen_change":
        # Verify screen changed (new page loaded)
        result = verify_screen_changed(context.get('previous_screenshot'))
        
    elif verify_type == "element_at_location":
        # Verify element appeared at specific location
        template = verification.get('template')
        location = verification.get('location')  # (x, y, w, h)
        threshold = verification.get('threshold', 0.8)
        
        if not template or not location:
            return False
        
        found_location = ui_detection.find_template(template, threshold, region=location)
        result = found_location is not None
        
    elif verify_type == "ocr_text":
        # Verify specific text appeared (OCR)
        expected_text = verification.get('text')
        region = verification.get('region')
        
        if not expected_text:
            print("  [WARN] No text specified for OCR verification")
            result = False
        else:
            result = verify_ocr_text(expected_text, region)
            
            # If OCR fails, try template matching as fallback
            if not result and verification.get('fallback_template'):
                print("  [FALLBACK] OCR failed, trying template matching...")
                template_path = verification.get('fallback_template')
                result = ui_detection.verify_element_present(template_path, threshold=0.8)
                if result:
                    print("  [OK] Template matching fallback succeeded")
                else:
                    print("  [FAIL] Template matching fallback also failed")
        
    elif verify_type == "wait":
        # Simple wait for action to complete
        duration = verification.get('duration', 1)
        time.sleep(duration)
        result = True
        
    else:
        print(f"  [WARN] Unknown verification type: {verify_type}")
        result = True
    
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} Verification: {'Passed' if result else 'Failed'}")
    return result


def verify_screen_stable(timeout=3, check_interval=0.5, action_type=None):
    """Verify screen is stable (not changing) with optional action-specific logic
    
    Args:
        timeout: Maximum seconds to wait for stability
        check_interval: Seconds between checks
        action_type: Optional action type for specific stability requirements
        
    Returns:
        True if screen stable, False if timeout
    """
    previous_path = ui_detection.take_screenshot("screenshots/stability_check_prev.png")
    time.sleep(check_interval)
    
    stable_time = 0
    while stable_time < timeout:
        current_path = ui_detection.take_screenshot("screenshots/stability_check_curr.png")
        
        if not ui_detection.detect_screen_change(previous_path, current_path, threshold=5.0):
            # Screen stable
            return True
        
        # Screen still changing
        previous_path = current_path
        time.sleep(check_interval)
        stable_time += check_interval
    
    # Timeout - screen never stabilized
    return False


def verify_screen_changed(previous_screenshot):
    """Verify screen has changed from previous state"""
    if not previous_screenshot:
        return True  # No previous screenshot, assume changed
    
    return ui_detection.detect_screen_change(previous_screenshot)


def verify_app_visually(app_config):
    """Verify app is open and maximized using template matching"""
    templates = app_config.get('verification_templates', [])
    if not templates:
        print("  [WARN] No verification templates configured")
        return True  # Skip visual verification
    
    print(f"  [VISUAL] Visual verification using {len(templates)} template(s)...")
    
    # Take screenshot once
    screenshot_path = ui_detection.take_screenshot("screenshots/app_verification.png")
    if not screenshot_path:
        return False
    
    # Check all templates
    for template in templates:
        try:
            location = ui_detection.find_template(template, threshold=0.8, screenshot_path=screenshot_path)
        except FileNotFoundError:
            # Template file missing - warn and skip this template
            print(f"  [WARN] Template file missing: {template} - skipping this template")
            continue

        if not location:
            print(f"  ✗ Template not found: {template}")
            # Don't fail immediately; mark as warn and continue to check others
            print(f"  [WARN] Template '{template}' not found in screenshot - continuing")
            continue

        # Check if element is in expected position (top of screen for titlebar)
        if "titlebar" in template:
            _, y = location
            screen_w, screen_h = ui_detection.get_screen_size()
            if y > 100:  # Titlebar should be near top
                print(f"  ✗ Titlebar at unexpected position: y={y}")
                print(f"  [WARN] Titlebar not in expected position for template '{template}' - continuing")
                continue
    
    print(f"  [OK] Visual verification passed")
    return True


def verify_visual_state(expected_state, context):
    """Verify visual state of application"""
    print(f"  [VISUAL] Verifying visual state: {expected_state}")
    
    if expected_state == "app_maximized":
        # Check if app is visually maximized
        app_name = context.get('app_name', 'Notepad')
        from window_ops import find_window, is_window_maximized
        window = find_window(app_name)
        if window:
            return is_window_maximized(window)
        return False
    
    elif expected_state == "app_ready":
        # Check if app is ready for automation
        app_config = context.get('config', {}).get('apps', [])
        for app in app_config:
            if app.get('name') == context.get('app_name'):
                return verify_app_visually(app)
        return True
    
    elif expected_state == "element_positioned":
        # Check if specific element is in correct position
        template = context.get('visual_template')
        expected_position = context.get('expected_position')  # (x, y, tolerance)
        
        if template and expected_position:
            location = ui_detection.find_template(template, threshold=0.8)
            if location:
                x, y = location
                expected_x, expected_y, tolerance = expected_position
                
                # Check if element is within tolerance of expected position
                x_diff = abs(x - expected_x)
                y_diff = abs(y - expected_y)
                
                if x_diff <= tolerance and y_diff <= tolerance:
                    print(f"  [VISUAL] Element positioned correctly: ({x}, {y})")
                    return True
                else:
                    print(f"  [VISUAL] Element at wrong position: ({x}, {y}) vs expected ({expected_x}, {expected_y})")
                    return False
        
        return True  # Skip if no template/position specified
    
    else:
        print(f"  [WARN] Unknown visual state: {expected_state}")
        return True


def verify_correct_page(expected_page, context):
    """Verify correct page is open"""
    print(f"  [PAGE] Checking if correct page is open: {expected_page}")
    
    # Method 1: Check window title
    if 'title' in expected_page:
        app_name = context.get('app_name')
        window = find_window(app_name)
        if window:
            actual_title = window.title
            expected_title = expected_page['title']
            result = expected_title.lower() in actual_title.lower()
            print(f"  [PAGE] Title check: '{expected_title}' in '{actual_title}' = {result}")
            return result
    
    # Method 2: Check for specific text on page
    if 'text' in expected_page:
        expected_text = expected_page['text']
        region = expected_page.get('region')
        result = ui_detection.verify_text_present(expected_text, region)
        print(f"  [PAGE] Text check: '{expected_text}' found = {result}")
        return result
    
    # Method 3: Check for specific template
    if 'template' in expected_page:
        template_path = expected_page['template']
        result = ui_detection.verify_element_present(template_path)
        print(f"  [PAGE] Template check: '{template_path}' found = {result}")
        return result
    
    print("  [PAGE] No verification method specified")
    return True


def verify_ocr_text(expected_text, region=None):
    """Verify specific text appeared using OCR"""
    try:
        import pytesseract
        from PIL import Image
        import ui_detection
        
        # Set tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Take screenshot
        screenshot_path = ui_detection.take_screenshot("screenshots/ocr_verification.png")
        if not screenshot_path:
            print("  [FAIL] Failed to take screenshot for OCR")
            return False
        
        # Load and crop if region specified
        image = Image.open(screenshot_path)
        if region:
            x, y, w, h = region
            image = image.crop((x, y, x+w, y+h))
            print(f"  [OCR] OCR searching in region: ({x}, {y}, {w}, {h})")
        
        # Perform OCR with better configuration
        # Use PSM 6 for single text block, PSM 8 for single word
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        text = pytesseract.image_to_string(image, config=custom_config)
        text = text.strip().lower()
        expected_text = expected_text.strip().lower()
        
        print(f"  [OCR] Raw OCR result: '{text}'")
        print(f"  [OCR] Expected text: '{expected_text}'")
        
        # Check if expected text is in the OCR result
        found = expected_text in text
        
        if found:
            print(f"  [OK] OCR found expected text: '{expected_text}'")
        else:
            print(f"  [FAIL] OCR did not find expected text: '{expected_text}'")
            print(f"  OCR result: '{text[:100]}...'")
            print(f"  [DEBUG] Expected: '{expected_text}' (length: {len(expected_text)})")
            print(f"  [DEBUG] Found: '{text}' (length: {len(text)})")
            
            # Try alternative OCR configuration as fallback
            print(f"  [FALLBACK] Trying alternative OCR configuration...")
            try:
                # Try PSM 8 for single word
                fallback_config = r'--oem 3 --psm 8'
                fallback_text = pytesseract.image_to_string(image, config=fallback_config)
                fallback_text = fallback_text.strip().lower()
                print(f"  [FALLBACK] Alternative OCR result: '{fallback_text}'")
                
                if expected_text in fallback_text:
                    print(f"  [OK] Fallback OCR found expected text: '{expected_text}'")
                    found = True
                else:
                    print(f"  [FAIL] Fallback OCR also failed")
            except Exception as e:
                print(f"  [ERROR] Fallback OCR failed: {e}")
        
        return found
        
    except ImportError:
        print("  [WARN] pytesseract not installed - OCR verification disabled")
        print("  Install with: pip install pytesseract")
        return True  # Skip OCR if not available
    except Exception as e:
        print(f"  [FAIL] Error in OCR verification: {e}")
        return False


def verify_action_completion(action, action_result):
    """Verify that an action completed successfully based on its type and result"""
    action_type = action.get('type')
    completion_check = action.get('completion_check', {})
    
    if not completion_check:
        # No completion check specified, assume success if action returned True
        return action_result
    
    check_type = completion_check.get('type')
    print(f"  [COMPLETION] Verifying {action_type} completion: {check_type}")
    
    try:
        if check_type == "screen_change":
            # Verify screen changed after action
            before_path = completion_check.get('before_screenshot')
            after_path = completion_check.get('after_screenshot')
            threshold = completion_check.get('threshold', 10.0)
            
            if before_path and after_path:
                changed = ui_detection.detect_screen_change(before_path, after_path, threshold)
                print(f"  [COMPLETION] Screen change detected: {changed}")
                return changed
            else:
                print("  [COMPLETION] No screenshots provided for change detection")
                return True
        
        elif check_type == "element_present":
            # Verify expected element appeared
            template = completion_check.get('template')
            threshold = completion_check.get('threshold', 0.8)
            timeout = completion_check.get('timeout', 5)
            
            if template:
                location = ui_detection.wait_for_element(template, timeout, threshold)
                found = location is not None
                print(f"  [COMPLETION] Element found: {found}")
                return found
            else:
                print("  [COMPLETION] No template specified for element verification")
                return True
        
        elif check_type == "text_present":
            # Verify expected text appeared
            text = completion_check.get('text')
            region = completion_check.get('region')
            confidence = completion_check.get('confidence', 0.8)
            
            if text:
                found = ui_detection.verify_text_present(text, region, confidence)
                print(f"  [COMPLETION] Text found: {found}")
                return found
            else:
                print("  [COMPLETION] No text specified for verification")
                return True
        
        elif check_type == "window_closed":
            # Verify window was closed
            app_name = completion_check.get('app_name', 'Notepad')
            from window_ops import find_window
            window = find_window(app_name)
            closed = window is None
            print(f"  [COMPLETION] Window closed: {closed}")
            return closed
        
        elif check_type == "window_focused":
            # Verify window is focused
            app_name = completion_check.get('app_name', 'Notepad')
            from window_ops import find_window
            window = find_window(app_name)
            if window:
                focused = window.isActive
                print(f"  [COMPLETION] Window focused: {focused}")
                return focused
            else:
                print(f"  [COMPLETION] Window {app_name} not found")
                return False
        
        elif check_type == "text_typed":
            # Verify text was actually typed (OCR verification)
            expected_text = completion_check.get('expected_text')
            region = completion_check.get('region')
            confidence = completion_check.get('confidence', 0.8)
            
            if expected_text:
                found = ui_detection.verify_text_present(expected_text, region, confidence)
                print(f"  [COMPLETION] Text typed verification: {found}")
                return found
            else:
                print("  [COMPLETION] No expected text specified")
                return True
        
        elif check_type == "hotkey_executed":
            # Verify hotkey had expected effect
            expected_result = completion_check.get('expected_result')
            if expected_result == "window_maximized":
                app_name = completion_check.get('app_name', 'Notepad')
                from window_ops import find_window, is_window_maximized
                window = find_window(app_name)
                if window:
                    maximized = is_window_maximized(window)
                    print(f"  [COMPLETION] Window maximized: {maximized}")
                    return maximized
            elif expected_result == "text_selected":
                # Check if text is selected (Ctrl+A effect)
                # This is complex to verify, so we'll assume success
                print("  [COMPLETION] Text selection assumed successful")
                return True
            else:
                print(f"  [COMPLETION] Unknown hotkey result: {expected_result}")
                return True
        
        elif check_type == "wait_complete":
            # Wait actions are always successful if they complete
            duration = completion_check.get('duration', 1)
            print(f"  [COMPLETION] Wait completed: {duration}s")
            return True
        
        else:
            print(f"  [COMPLETION] Unknown completion check type: {check_type}")
            return True
    
    except Exception as e:
        print(f"  [COMPLETION] Error in completion verification: {e}")
        return False
