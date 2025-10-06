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
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

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
