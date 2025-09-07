#!/usr/bin/env python3
"""
Line Ranger OpenCV Automation
Visual-based automation using computer vision
"""
import cv2
import numpy as np
import subprocess
import time
import os
from PIL import Image

class LineRangerCV:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "screenshot.png"
        self.templates_dir = "templates"
        
        # Create templates directory
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def run_adb(self, cmd):
        """Execute ADB command"""
        try:
            full_cmd = f'"{self.adb_path}" -s {self.device} {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def take_screenshot(self):
        """Take screenshot from device"""
        print("📸 Taking screenshot...")
        
        # Take screenshot
        self.run_adb("shell screencap -p /sdcard/screenshot.png")
        
        # Pull to PC
        subprocess.run([
            self.adb_path, "-s", self.device, 
            "pull", "/sdcard/screenshot.png", self.screenshot_path
        ], capture_output=True)
        
        # Load image
        try:
            img = cv2.imread(self.screenshot_path)
            if img is not None:
                print(f"✅ Screenshot taken: {img.shape}")
                return img
            else:
                print("❌ Failed to load screenshot")
                return None
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
    
    def find_template(self, img, template_name, threshold=0.8):
        """Find template in image using template matching"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.png")
        
        if not os.path.exists(template_path):
            print(f"❌ Template {template_name} not found")
            return None
        
        template = cv2.imread(template_path)
        if template is None:
            print(f"❌ Could not load template {template_name}")
            return None
        
        # Template matching
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        if len(locations[0]) > 0:
            # Get best match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            print(f"✅ Found {template_name} at ({center_x}, {center_y}) confidence: {max_val:.2f}")
            return (center_x, center_y, max_val)
        else:
            print(f"❌ {template_name} not found (threshold: {threshold})")
            return None
    
    def click_at(self, x, y):
        """Click at coordinates"""
        print(f"👆 Clicking at ({x}, {y})")
        self.run_adb(f"shell input tap {x} {y}")
        time.sleep(1)
    
    def find_and_click(self, template_name, threshold=0.8):
        """Find template and click on it"""
        img = self.take_screenshot()
        if img is None:
            return False
        
        result = self.find_template(img, template_name, threshold)
        if result:
            x, y, confidence = result
            self.click_at(x, y)
            return True
        return False
    
    def detect_text_ocr(self, img, text_to_find):
        """Detect text using simple OCR (requires pytesseract)"""
        try:
            import pytesseract
            
            # Convert to PIL Image
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # Extract text
            text = pytesseract.image_to_string(img_pil)
            
            if text_to_find.lower() in text.lower():
                print(f"✅ Found text: {text_to_find}")
                return True
            else:
                print(f"❌ Text '{text_to_find}' not found")
                return False
                
        except ImportError:
            print("❌ pytesseract not installed. Install with: pip install pytesseract")
            return False
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return False
    
    def detect_colors(self, img, color_ranges):
        """Detect specific colors in image"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            pixels = cv2.countNonZero(mask)
            
            if pixels > 1000:  # Threshold for significant color presence
                print(f"✅ Detected {color_name} color ({pixels} pixels)")
                return color_name
        
        return None
    
    def wait_for_element(self, template_name, timeout=30, threshold=0.8):
        """Wait for element to appear"""
        print(f"⏳ Waiting for {template_name} (timeout: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            img = self.take_screenshot()
            if img is not None:
                result = self.find_template(img, template_name, threshold)
                if result:
                    return result
            
            time.sleep(2)
        
        print(f"❌ Timeout waiting for {template_name}")
        return None
    
    def create_template_from_screenshot(self, template_name, x1, y1, x2, y2):
        """Create template from current screenshot coordinates"""
        img = self.take_screenshot()
        if img is None:
            return False
        
        # Crop region
        template = img[y1:y2, x1:x2]
        
        # Save template
        template_path = os.path.join(self.templates_dir, f"{template_name}.png")
        cv2.imwrite(template_path, template)
        
        print(f"✅ Template '{template_name}' saved to {template_path}")
        return True
    
    def analyze_current_screen(self):
        """Analyze current screen and detect common elements"""
        print("🔍 Analyzing current screen...")
        
        img = self.take_screenshot()
        if img is None:
            return
        
        # Color detection for common UI elements
        color_ranges = {
            "blue_button": ([100, 50, 50], [130, 255, 255]),
            "green_button": ([40, 50, 50], [80, 255, 255]),
            "red_button": ([0, 50, 50], [20, 255, 255]),
            "yellow_text": ([20, 50, 50], [40, 255, 255])
        }
        
        detected_color = self.detect_colors(img, color_ranges)
        
        # Edge detection for buttons
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        button_candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 50000:  # Button-like size
                x, y, w, h = cv2.boundingRect(contour)
                if 0.3 < w/h < 3:  # Button-like aspect ratio
                    button_candidates.append((x + w//2, y + h//2, area))
        
        print(f"📊 Analysis results:")
        print(f"   - Detected color: {detected_color}")
        print(f"   - Button candidates: {len(button_candidates)}")
        
        # Save analyzed image
        analyzed_img = img.copy()
        for x, y, area in button_candidates:
            cv2.circle(analyzed_img, (x, y), 10, (0, 255, 0), 2)
        
        cv2.imwrite("analyzed_screen.png", analyzed_img)
        print("✅ Analysis saved to analyzed_screen.png")
    
    def simple_automation_demo(self):
        """Simple automation demo"""
        print("=" * 50)
        print("🎮 LINE RANGER OPENCV AUTOMATION")
        print("=" * 50)
        
        # Take initial screenshot
        self.analyze_current_screen()
        
        # Demo: Click on center of screen
        print("\n🎯 Demo: Clicking center of screen...")
        self.click_at(640, 360)  # Assuming 1280x720 resolution
        
        time.sleep(3)
        
        # Take another screenshot to see changes
        print("\n📸 Taking screenshot after click...")
        self.analyze_current_screen()
        
        print("\n✅ OpenCV automation demo completed!")
        print("📁 Check 'screenshot.png' and 'analyzed_screen.png'")
        print("📁 Templates can be saved in 'templates/' folder")

def main():
    cv_automation = LineRangerCV()
    cv_automation.simple_automation_demo()

if __name__ == "__main__":
    main()