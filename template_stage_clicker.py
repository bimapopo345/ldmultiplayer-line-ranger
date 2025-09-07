#!/usr/bin/env python3
"""
Template Stage Clicker - Gunakan template matching untuk deteksi stage numbers
"""
import cv2
import numpy as np
import subprocess
import time
from datetime import datetime

def print_step(step, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{step}] {message}")

def safe_screenshot():
    try:
        adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        device = "emulator-5554"
        
        subprocess.run([adb_path, "-s", device, "shell", "screencap", "-p", "/sdcard/game.png"], capture_output=True, timeout=10)
        subprocess.run([adb_path, "-s", device, "pull", "/sdcard/game.png", "current_game.png"], capture_output=True, timeout=10)
        
        img = cv2.imread("current_game.png")
        if img is not None:
            print_step("SCREENSHOT", f"Screenshot: {img.shape}")
            return img
        return None
    except Exception as e:
        print_step("ERROR", f"Screenshot gagal: {e}")
        return None

def safe_click(x, y):
    try:
        adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        device = "emulator-5554"
        subprocess.run([adb_path, "-s", device, "shell", "input", "tap", str(x), str(y)], capture_output=True, timeout=5)
        print_step("CLICK", f"👆 Klik di ({x}, {y})")
        return True
    except:
        print_step("ERROR", "Klik gagal")
        return False

def load_stage_template():
    """Load template angka 3 dari logo_stage.png"""
    try:
        template = cv2.imread("logo_stage.png")
        if template is not None:
            print_step("TEMPLATE", f"Template loaded: {template.shape}")
            return template
        else:
            print_step("ERROR", "Template tidak bisa dimuat")
            return None
    except:
        print_step("ERROR", "Template file tidak ditemukan")
        return None

def find_stage_numbers_with_template(img, template):
    """Cari stage numbers menggunakan template matching"""
    if img is None or template is None:
        return []
    
    # Convert to grayscale for template matching
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Get template dimensions
    template_h, template_w = template_gray.shape
    
    # Perform template matching
    result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # Find locations where matching is good
    threshold = 0.6  # Adjust this threshold as needed
    locations = np.where(result >= threshold)
    
    matches = []
    for pt in zip(*locations[::-1]):  # Switch x and y coordinates
        x, y = pt
        center_x = x + template_w // 2
        center_y = y + template_h // 2
        confidence = result[y, x]
        
        matches.append({
            "pos": (center_x, center_y),
            "confidence": confidence,
            "bbox": (x, y, template_w, template_h)
        })
        print_step("MATCH", f"Template match at ({center_x}, {center_y}) confidence: {confidence:.3f}")
    
    # Sort by confidence (highest first)
    matches.sort(key=lambda m: m["confidence"], reverse=True)
    
    # Remove overlapping matches (non-maximum suppression)
    filtered_matches = []
    for match in matches:
        x1, y1 = match["pos"]
        is_duplicate = False
        
        for existing in filtered_matches:
            x2, y2 = existing["pos"]
            distance = np.sqrt((x1-x2)**2 + (y1-y2)**2)
            if distance < 50:  # Too close, likely duplicate
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_matches.append(match)
    
    return filtered_matches

def find_yellow_circular_stages(img):
    """Fallback: Cari stage numbers berdasarkan warna kuning dan bentuk circular"""
    if img is None:
        return []
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, width = img.shape[:2]
    
    # Yellow color range
    yellow_lower = np.array([15, 100, 100])
    yellow_upper = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    
    # Find contours
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    stage_candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 1000 < area < 10000:  # Stage number size
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check if roughly circular
            aspect_ratio = w / h
            if 0.7 < aspect_ratio < 1.3:
                center_x, center_y = x + w//2, y + h//2
                
                # Should be in stage path area
                if (width * 0.1 < center_x < width * 0.9 and 
                    height * 0.3 < center_y < height * 0.8):
                    
                    stage_candidates.append({
                        "pos": (center_x, center_y),
                        "area": area,
                        "method": "color_detection"
                    })
                    print_step("DETECT", f"Yellow circular stage at ({center_x}, {center_y})")
    
    return stage_candidates

def find_start_button(img):
    """Cari tombol START"""
    if img is None:
        return None
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Green color for START button
    green_lower = np.array([40, 50, 50])
    green_upper = np.array([80, 255, 255])
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    
    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 3000 < area < 50000:
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w//2, y + h//2
            print_step("DETECT", f"START button at ({center_x}, {center_y})")
            return (center_x, center_y)
    
    return None

def main():
    """Main template-based stage automation"""
    print("🎯 TEMPLATE STAGE CLICKER")
    print("=" * 50)
    
    # Load template
    template = load_stage_template()
    if template is None:
        print_step("ERROR", "Tidak bisa load template, exit")
        return
    
    for cycle in range(15):
        print_step("CYCLE", f"Cycle {cycle + 1}/15")
        
        # Take screenshot
        img = safe_screenshot()
        if img is None:
            time.sleep(3)
            continue
        
        # Method 1: Template matching
        template_matches = find_stage_numbers_with_template(img, template)
        
        if template_matches:
            # Click best template match
            best_match = template_matches[0]
            x, y = best_match["pos"]
            confidence = best_match["confidence"]
            print_step("ACTION", f"Klik template match di ({x}, {y}) confidence: {confidence:.3f}")
            safe_click(x, y)
            time.sleep(5)
            
            # Look for START button after clicking stage
            img2 = safe_screenshot()
            if img2 is not None:
                start_pos = find_start_button(img2)
                if start_pos:
                    sx, sy = start_pos
                    print_step("ACTION", f"Klik START button di ({sx}, {sy})")
                    safe_click(sx, sy)
                    time.sleep(8)
        else:
            # Method 2: Fallback to color detection
            print_step("FALLBACK", "Template tidak match, coba color detection")
            yellow_stages = find_yellow_circular_stages(img)
            
            if yellow_stages:
                # Click first yellow stage
                x, y = yellow_stages[0]["pos"]
                print_step("ACTION", f"Klik yellow stage di ({x}, {y})")
                safe_click(x, y)
                time.sleep(5)
                
                # Look for START button
                img2 = safe_screenshot()
                if img2:
                    start_pos = find_start_button(img2)
                    if start_pos:
                        sx, sy = start_pos
                        print_step("ACTION", f"Klik START button di ({sx}, {sy})")
                        safe_click(sx, sy)
                        time.sleep(8)
            else:
                # Method 3: Look for START button directly
                start_pos = find_start_button(img)
                if start_pos:
                    sx, sy = start_pos
                    print_step("ACTION", f"Klik START button langsung di ({sx}, {sy})")
                    safe_click(sx, sy)
                    time.sleep(8)
                else:
                    print_step("WAIT", "Tidak ada stage atau START button, tunggu...")
        
        time.sleep(3)
    
    print_step("COMPLETE", "Template automation selesai!")

if __name__ == "__main__":
    main()