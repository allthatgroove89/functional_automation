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
        
    elif prerequisite == "search_complete":
        # Wait for search to complete (no screen changes)
        result = verify_screen_stable(timeout=2)
        
    elif prerequisite == "element_present":
        # Check if specific element is visible
        template = context.get('prerequisite_template')
        if template:
            result = ui_detection.verify_element_present(template, threshold=0.8)
        else:
            result = True
            
    else:
        print(f"  ⚠ Unknown prerequisite: {prerequisite}")
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
            print("  ⚠ No template specified for verification")
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
            print("  ⚠ No text specified for OCR verification")
            result = False
        else:
            result = verify_ocr_text(expected_text, region)
        
    elif verify_type == "wait":
        # Simple wait for action to complete
        duration = verification.get('duration', 1)
        time.sleep(duration)
        result = True
        
    else:
        print(f"  ⚠ Unknown verification type: {verify_type}")
        result = True
    
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} Verification: {'Passed' if result else 'Failed'}")
    return result


def verify_screen_stable(timeout=3, check_interval=0.5):
    """Verify screen is stable (not changing)"""
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
        print("  ⚠ No verification templates configured")
        return True  # Skip visual verification
    
    print(f"  [VISUAL] Visual verification using {len(templates)} template(s)...")
    
    # Take screenshot once
    screenshot_path = ui_detection.take_screenshot("screenshots/app_verification.png")
    if not screenshot_path:
        return False
    
    # Check all templates
    for template in templates:
        location = ui_detection.find_template(template, threshold=0.8, screenshot_path=screenshot_path)
        if not location:
            print(f"  ✗ Template not found: {template}")
            return False
        
        # Check if element is in expected position (top of screen for titlebar)
        if "titlebar" in template:
            _, y = location
            screen_w, screen_h = ui_detection.get_screen_size()
            if y > 100:  # Titlebar should be near top
                print(f"  ✗ Titlebar at unexpected position: y={y}")
                return False
    
    print(f"  [OK] Visual verification passed")
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
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        text = text.strip().lower()
        expected_text = expected_text.strip().lower()
        
        # Check if expected text is in the OCR result
        found = expected_text in text
        
        if found:
            print(f"  [OK] OCR found expected text: '{expected_text}'")
        else:
            print(f"  [FAIL] OCR did not find expected text: '{expected_text}'")
            print(f"  OCR result: '{text[:100]}...'")
        
        return found
        
    except ImportError:
        print("  [WARN] pytesseract not installed - OCR verification disabled")
        print("  Install with: pip install pytesseract")
        return True  # Skip OCR if not available
    except Exception as e:
        print(f"  [FAIL] Error in OCR verification: {e}")
        return False
