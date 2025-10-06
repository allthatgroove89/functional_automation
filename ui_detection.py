"""UI Detection utilities - Template matching, screenshots, and verification"""
import time
import cv2
import numpy as np
import pyautogui
import os


def take_screenshot(save_path="screenshots/screen.png"):
    """Take screenshot and save to file
    
    Args:
        save_path: Path to save screenshot
        
    Returns:
        Path to saved screenshot, or empty string on error
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        print(f"Screenshot saved: {save_path}")
        return save_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return ""


def find_template(template_path, threshold=0.8, region=None, screenshot_path=None):
    """Find template image on screen using OpenCV template matching
    
    Args:
        template_path: Path to template image file
        threshold: Confidence threshold (0.0 - 1.0)
        region: Optional region to search (x, y, width, height)
        screenshot_path: Use existing screenshot instead of taking new one
        
    Returns:
        (x, y) center coordinates if found, None otherwise
    """
    if not os.path.exists(template_path):
        print(f"Template file not found: {template_path}")
        return None

    try:
        # Take screenshot if not provided
        if not screenshot_path:
            screenshot_path = take_screenshot()
        if not screenshot_path:
            return None

        # Load images
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)

        if screenshot is None or template is None:
            print("Error loading images for template matching")
            return None

        # Crop to region if specified
        region_offset_x, region_offset_y = 0, 0
        if region:
            x, y, w, h = region
            screenshot = screenshot[y:y+h, x:x+w]
            region_offset_x, region_offset_y = x, y

        # Convert to grayscale
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Template matching
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # Calculate center of matched region
            template_h, template_w = template_gray.shape
            center_x = max_loc[0] + template_w // 2 + region_offset_x
            center_y = max_loc[1] + template_h // 2 + region_offset_y

            print(f"Template found at ({center_x}, {center_y}) with confidence {max_val:.2f}")
            return (center_x, center_y)
        else:
            print(f"Template not found (confidence: {max_val:.2f}, threshold: {threshold})")
            return None

    except Exception as e:
        print(f"Error in template matching: {e}")
        return None


def click_at_location(location, delay=0.5):
    """Click at specified screen coordinates
    
    Args:
        location: (x, y) coordinates
        delay: Delay after clicking
        
    Returns:
        True if successful, False otherwise
    """
    try:
        x, y = location
        pyautogui.click(x, y)
        time.sleep(delay)
        print(f"Clicked at ({x}, {y})")
        return True
    except Exception as e:
        print(f"Error clicking at location: {e}")
        return False


def find_and_click_template(template_path, threshold=0.8, offset_x=0, offset_y=0, delay=0.5):
    """Find template and click it
    
    Args:
        template_path: Path to template image
        threshold: Confidence threshold
        offset_x: X offset from center
        offset_y: Y offset from center
        delay: Delay after clicking
        
    Returns:
        True if found and clicked, False otherwise
    """
    location = find_template(template_path, threshold)
    if location:
        adjusted_location = (location[0] + offset_x, location[1] + offset_y)
        return click_at_location(adjusted_location, delay)
    return False


def verify_element_present(template_path, threshold=0.8):
    """Check if element is present on screen
    
    Args:
        template_path: Path to template image
        threshold: Confidence threshold
        
    Returns:
        True if element found, False otherwise
    """
    location = find_template(template_path, threshold)
    return location is not None


def wait_for_element(template_path, timeout=10, threshold=0.8, check_interval=0.5):
    """Wait for element to appear on screen
    
    Args:
        template_path: Path to template image
        timeout: Maximum seconds to wait
        threshold: Confidence threshold
        check_interval: Seconds between checks
        
    Returns:
        (x, y) coordinates if found, None if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        location = find_template(template_path, threshold)
        if location:
            elapsed = time.time() - start_time
            print(f"Element found after {elapsed:.1f} seconds")
            return location
        time.sleep(check_interval)

    print(f"Element not found within {timeout} seconds")
    return None


def find_multiple_templates(template_paths, threshold=0.8):
    """Find multiple templates in single screenshot
    
    Args:
        template_paths: List of template image paths
        threshold: Confidence threshold
        
    Returns:
        List of (template_name, (x, y)) tuples for found templates
    """
    # Take one screenshot for all searches
    screenshot_path = take_screenshot()
    if not screenshot_path:
        return []

    results = []
    for template_path in template_paths:
        location = find_template(template_path, threshold, screenshot_path=screenshot_path)
        if location:
            template_name = os.path.basename(template_path)
            results.append((template_name, location))

    return results


def detect_screen_change(previous_screenshot_path, current_screenshot_path=None, threshold=10.0):
    """Detect if screen has changed between two screenshots
    
    Args:
        previous_screenshot_path: Path to previous screenshot
        current_screenshot_path: Path to current screenshot (takes new one if None)
        threshold: Difference threshold to consider as change
        
    Returns:
        True if screen changed, False otherwise
    """
    try:
        # Take current screenshot if not provided
        if not current_screenshot_path:
            current_screenshot_path = take_screenshot("screenshots/screen_current.png")
        
        if not current_screenshot_path or not os.path.exists(previous_screenshot_path):
            return True

        # Load images
        current = cv2.imread(current_screenshot_path)
        previous = cv2.imread(previous_screenshot_path)

        if current is None or previous is None:
            return True

        # Calculate difference
        diff = cv2.absdiff(current, previous)
        mean_diff = np.mean(diff)

        has_changed = mean_diff > threshold

        if has_changed:
            print(f"Screen change detected (diff: {mean_diff:.2f})")
        else:
            print(f"No significant screen change (diff: {mean_diff:.2f})")

        return has_changed

    except Exception as e:
        print(f"Error detecting screen change: {e}")
        return True


def crop_region(screenshot_path, region, save_path=None):
    """Crop region from screenshot
    
    Args:
        screenshot_path: Path to screenshot
        region: (x, y, width, height) to crop
        save_path: Path to save cropped image (optional)
        
    Returns:
        Path to cropped image if saved, None otherwise
    """
    try:
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            return None

        x, y, w, h = region
        cropped = screenshot[y:y+h, x:x+w]

        if save_path:
            cv2.imwrite(save_path, cropped)
            print(f"Cropped image saved: {save_path}")
            return save_path

        return None

    except Exception as e:
        print(f"Error cropping region: {e}")
        return None


def cleanup_screenshots(screenshot_dir="screenshots", patterns=None):
    """Clean up screenshot files
    
    Args:
        screenshot_dir: Directory containing screenshots
        patterns: List of filename patterns to delete (defaults to common patterns)
    """
    if patterns is None:
        patterns = [
            "screen.png",
            "screen_*.png",
            "app_verification.png",
            "template_match.png",
            "screenshot.png",
            "ocr_region.png",
            "cropped_*.png"
        ]

    try:
        deleted_count = 0

        # Handle both direct files and patterns
        for pattern in patterns:
            if '*' in pattern:
                # Pattern matching
                import glob
                files = glob.glob(os.path.join(screenshot_dir, pattern))
                for file in files:
                    if os.path.exists(file):
                        os.remove(file)
                        deleted_count += 1
                        print(f"Deleted: {file}")
            else:
                # Direct file
                file_path = os.path.join(screenshot_dir, pattern) if screenshot_dir else pattern
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted: {file_path}")

        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} screenshot file(s)")
        else:
            print("No screenshot files to clean up")

    except Exception as e:
        print(f"Error cleaning up screenshots: {e}")


def get_screen_size():
    """Get screen dimensions
    
    Returns:
        (width, height) of screen
    """
    return pyautogui.size()


def verify_templates_exist(template_paths):
    """Verify which template files exist
    
    Args:
        template_paths: List of template paths to check
        
    Returns:
        Tuple of (existing_paths, missing_paths)
    """
    existing = []
    missing = []

    for path in template_paths:
        if os.path.exists(path):
            existing.append(path)
        else:
            missing.append(path)

    return existing, missing


def wait_for_screen_stability(timeout=5, check_interval=0.5):
    """Wait for screen to become stable (no changes)
    
    Args:
        timeout: Maximum seconds to wait for stability
        check_interval: Seconds between checks
        
    Returns:
        True if screen stable, False if timeout
    """
    from verification import verify_screen_stable
    return verify_screen_stable(timeout, check_interval)


def detect_action_success(action_type, before_screenshot, after_screenshot):
    """Detect if action was successful based on screen changes
    
    Args:
        action_type: Type of action performed
        before_screenshot: Path to screenshot before action
        after_screenshot: Path to screenshot after action
        
    Returns:
        True if action likely successful, False otherwise
    """
    if action_type in ['click_image', 'click_text', 'close_window']:
        # These actions should cause screen changes
        return detect_screen_change(before_screenshot, after_screenshot)
    elif action_type in ['type_text', 'hotkey']:
        # These might not cause visible changes
        return True
    else:
        return True


def wait_for_element_appeared(template_path, timeout=10, threshold=0.8):
    """Wait for element to appear on screen after action
    
    Args:
        template_path: Path to template image
        timeout: Maximum seconds to wait
        threshold: Confidence threshold
        
    Returns:
        True if element appeared, False if timeout
    """
    return wait_for_element(template_path, timeout, threshold) is not None


def verify_screen_ready_for_action(action_type, timeout=3):
    """Verify screen is ready for specific action type
    
    Args:
        action_type: Type of action to perform
        timeout: Maximum seconds to wait
        
    Returns:
        True if screen ready, False otherwise
    """
    if action_type in ['click_image', 'click_text']:
        # For click actions, ensure screen is stable
        return wait_for_screen_stability(timeout)
    elif action_type in ['type_text', 'hotkey']:
        # For input actions, basic stability check
        return wait_for_screen_stability(1)
    else:
        return True


def find_text_with_bounding_boxes(text, region=None, confidence_threshold=0.8, save_debug=False):
    """Find text using OCR and return bounding boxes for precise clicking
    
    Args:
        text: Text to search for
        region: Optional region to search (x, y, width, height)
        confidence_threshold: Minimum confidence for text detection
        save_debug: Save debug images for troubleshooting
        
    Returns:
        List of dicts with 'text', 'bbox', 'confidence' for each match
        Format: [{'text': 'found_text', 'bbox': (x, y, w, h), 'confidence': 0.95}]
    """
    try:
        import pytesseract
        from PIL import Image, ImageDraw
        import re
        
        # Set tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Take screenshot using existing function
        screenshot_path = take_screenshot("screenshots/ocr_search.png")
        if not screenshot_path:
            return []
        
        # Load and crop if region specified
        image = Image.open(screenshot_path)
        if region:
            x, y, w, h = region
            image = image.crop((x, y, x+w, y+h))
            print(f"[OCR] Searching in region: ({x}, {y}, {w}, {h})")
        
        # Get detailed OCR data with bounding boxes
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        matches = []
        text_lower = text.lower()
        
        # Process each detected text element
        for i in range(len(ocr_data['text'])):
            detected_text = ocr_data['text'][i].strip()
            confidence = int(ocr_data['conf'][i]) / 100.0
            
            if detected_text and confidence >= confidence_threshold:
                # Check if our target text is in this detected text
                if text_lower in detected_text.lower():
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    # Adjust coordinates if we cropped the image
                    if region:
                        x += region[0]
                        y += region[1]
                    
                    match = {
                        'text': detected_text,
                        'bbox': (x, y, w, h),
                        'confidence': confidence,
                        'center': (x + w//2, y + h//2)
                    }
                    matches.append(match)
        
        if save_debug and matches:
            # Draw bounding boxes on image for debugging
            debug_image = image.copy()
            draw = ImageDraw.Draw(debug_image)
            for match in matches:
                x, y, w, h = match['bbox']
                if region:
                    x -= region[0]
                    y -= region[1]
                draw.rectangle([x, y, x+w, y+h], outline='red', width=2)
                draw.text((x, y-20), f"{match['confidence']:.2f}", fill='red')
            
            debug_path = "screenshots/ocr_debug.png"
            debug_image.save(debug_path)
            print(f"[DEBUG] OCR debug image saved: {debug_path}")
        
        print(f"[OCR] Found {len(matches)} match(es) for '{text}'")
        return matches
        
    except ImportError:
        print("[WARN] pytesseract not installed - OCR with bounding boxes disabled")
        return []
    except Exception as e:
        print(f"[ERROR] OCR with bounding boxes failed: {e}")
        return []


def smart_crop_for_ocr(image_path, text_hint=None, min_text_size=20):
    """Intelligently crop image for better OCR accuracy
    
    Args:
        image_path: Path to image file
        text_hint: Optional hint about text location ('top', 'bottom', 'center', 'left', 'right')
        min_text_size: Minimum text size to detect
        
    Returns:
        List of cropped image paths for OCR processing
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for better text detection
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Find contours (potential text regions)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and aspect ratio
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size
            if w < min_text_size or h < min_text_size:
                continue
            
            # Filter by aspect ratio (text is usually wider than tall)
            aspect_ratio = w / h
            if aspect_ratio < 0.1 or aspect_ratio > 10:
                continue
            
            text_regions.append((x, y, w, h))
        
        # Sort regions by position based on hint
        if text_hint == 'top':
            text_regions.sort(key=lambda r: r[1])
        elif text_hint == 'bottom':
            text_regions.sort(key=lambda r: r[1], reverse=True)
        elif text_hint == 'left':
            text_regions.sort(key=lambda r: r[0])
        elif text_hint == 'right':
            text_regions.sort(key=lambda r: r[0], reverse=True)
        else:
            # Default: sort by area (largest first)
            text_regions.sort(key=lambda r: r[2] * r[3], reverse=True)
        
        # Create cropped images
        cropped_paths = []
        for i, (x, y, w, h) in enumerate(text_regions[:5]):  # Limit to top 5 regions
            # Add padding around text
            padding = 10
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(image.shape[1], x + w + padding)
            y_end = min(image.shape[0], y + h + padding)
            
            # Crop the region
            cropped = image[y_start:y_end, x_start:x_end]
            
            # Save cropped image
            cropped_path = f"screenshots/cropped_ocr_{i}.png"
            cv2.imwrite(cropped_path, cropped)
            cropped_paths.append(cropped_path)
            
            print(f"[CROP] Created cropped region {i}: {cropped_path} ({w}x{h})")
        
        return cropped_paths
        
    except Exception as e:
        print(f"[ERROR] Smart cropping failed: {e}")
        return []


def find_text_precise(text, region=None, use_smart_crop=True, text_hint=None):
    """Find text with enhanced accuracy using smart cropping and bounding boxes
    
    Args:
        text: Text to search for
        region: Optional region to search (x, y, width, height)
        use_smart_crop: Use intelligent cropping for better OCR
        text_hint: Hint about text location for cropping
        
    Returns:
        Dict with 'found', 'location', 'confidence', 'bbox' if found
    """
    try:
        # Take initial screenshot using existing function
        screenshot_path = take_screenshot("screenshots/ocr_precise.png")
        if not screenshot_path:
            return {'found': False, 'error': 'Failed to take screenshot'}
        
        # If smart cropping enabled, try cropping first
        if use_smart_crop:
            cropped_paths = smart_crop_for_ocr(screenshot_path, text_hint)
            
            # Search in each cropped region
            for i, cropped_path in enumerate(cropped_paths):
                matches = find_text_with_bounding_boxes(text, save_debug=True)
                if matches:
                    # Return the best match
                    best_match = max(matches, key=lambda m: m['confidence'])
                    return {
                        'found': True,
                        'location': best_match['center'],
                        'confidence': best_match['confidence'],
                        'bbox': best_match['bbox'],
                        'text': best_match['text'],
                        'method': 'smart_crop'
                    }
        
        # Fallback to regular search
        matches = find_text_with_bounding_boxes(text, region, save_debug=True)
        if matches:
            best_match = max(matches, key=lambda m: m['confidence'])
            return {
                'found': True,
                'location': best_match['center'],
                'confidence': best_match['confidence'],
                'bbox': best_match['bbox'],
                'text': best_match['text'],
                'method': 'regular'
            }
        
        return {'found': False, 'error': 'Text not found'}
        
    except Exception as e:
        return {'found': False, 'error': f'OCR search failed: {e}'}


def click_text_precise(text, region=None, use_smart_crop=True, text_hint=None):
    """Click on text with enhanced precision using bounding boxes
    
    Args:
        text: Text to click on
        region: Optional region to search (x, y, width, height)
        use_smart_crop: Use intelligent cropping for better OCR
        text_hint: Hint about text location for cropping
        
    Returns:
        True if clicked successfully, False otherwise
    """
    try:
        result = find_text_precise(text, region, use_smart_crop, text_hint)
        
        if not result['found']:
            print(f"[FAIL] Text '{text}' not found: {result.get('error', 'Unknown error')}")
            return False
        
        # Click at the center of the bounding box
        x, y = result['location']
        confidence = result['confidence']
        bbox = result['bbox']
        
        print(f"[CLICK] Clicking text '{text}' at ({x}, {y}) with confidence {confidence:.2f}")
        print(f"[CLICK] Bounding box: {bbox}")
        
        # Perform the click
        pyautogui.click(x, y)
        
        # Small delay after click
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Precise text clicking failed: {e}")
        return False


def find_and_click_text(text, region=None, use_smart_crop=True, text_hint=None, delay=0.5):
    """Find text using OCR and click it (convenience function)
    
    Args:
        text: Text to find and click
        region: Optional region to search (x, y, width, height)
        use_smart_crop: Use intelligent cropping for better OCR
        text_hint: Hint about text location for cropping
        delay: Delay after clicking
        
    Returns:
        True if found and clicked, False otherwise
    """
    return click_text_precise(text, region, use_smart_crop, text_hint)


def verify_text_present(text, region=None, confidence_threshold=0.8):
    """Check if text is present on screen using OCR
    
    Args:
        text: Text to search for
        region: Optional region to search (x, y, width, height)
        confidence_threshold: Minimum confidence for text detection
        
    Returns:
        True if text found, False otherwise
    """
    matches = find_text_with_bounding_boxes(text, region, confidence_threshold)
    return len(matches) > 0


def wait_for_text(text, timeout=10, region=None, confidence_threshold=0.8, check_interval=0.5):
    """Wait for text to appear on screen
    
    Args:
        text: Text to wait for
        timeout: Maximum seconds to wait
        region: Optional region to search (x, y, width, height)
        confidence_threshold: Minimum confidence for text detection
        check_interval: Seconds between checks
        
    Returns:
        True if text found, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if verify_text_present(text, region, confidence_threshold):
            elapsed = time.time() - start_time
            print(f"Text '{text}' found after {elapsed:.1f} seconds")
            return True
        time.sleep(check_interval)
    
    print(f"Text '{text}' not found within {timeout} seconds")
    return False