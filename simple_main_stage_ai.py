#!/usr/bin/env python3
"""
Simple Main Stage AI - Fokus pada MAIN STAGE detection yang akurat
"""
import cv2
import numpy as np
import subprocess
import time
import os
from datetime import datetime

def print_step(step, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{step}] {message}")

def safe_screenshot():
    """Ambil screenshot"""
    try:
        adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        device = "emulator-5554"
        
        subprocess.run([
            adb_path, "-s", device, 
            "shell", "screencap", "-p", "/sdcard/game.png"
        ], capture_output=True, timeout=10)
        
        subprocess.run([
            adb_path, "-s", device, 
            "pull", "/sdcard/game.png", "test_screen.png"
        ], capture_output=True, timeout=10)
        
        img = cv2.imread("test_screen.png")
        if img is not None:
            print_step("SCREENSHOT", f"Screenshot berhasil: {img.shape}")
            return img
        return None
    except Exception as e:
        print_step("ERROR", f"Screenshot gagal: {e}")
        return None

def safe_click(x, y):
    """Safe click"""
    try:
        adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        device = "emulator-5554"
        
        subprocess.run([
            adb_path, "-s", device,
            "shell", "input", "tap", str(x), str(y)
        ], capture_output=True, timeout=5)
        print_step("CLICK", f"👆 Klik di ({x}, {y})")
        return True
    except:
        print_step("ERROR", "Klik gagal")
        return False

def find_main_stage_precise(img):
    """Cari MAIN STAGE dengan presisi tinggi"""
    if img is None:
        return None
    
    height, width = img.shape[:2]
    print_step("DETECT", f"Screen size: {width}x{height}")
    
    # Berdasarkan screenshot lobby yang kita lihat sebelumnya:
    # MAIN STAGE button ada di tengah, sekitar koordinat (640, 280) untuk resolusi 900x1600
    
    # Define MAIN STAGE area yang aman (tengah layar, hindari shop)
    main_stage_x = width // 2  # Center horizontally
    main_stage_y = int(height * 0.35)  # About 35% from top
    
    # Area pencarian MAIN STAGE (kotak di sekitar posisi yang diperkirakan)
    search_area = {
        "x1": int(width * 0.25),   # 25% from left
        "x2": int(width * 0.75),   # 75% from left  
        "y1": int(height * 0.25),  # 25% from top
        "y2": int(height * 0.45)   # 45% from top
    }
    
    print_step("DETECT", f"MAIN STAGE search area: ({search_area['x1']}, {search_area['y1']}) to ({search_area['x2']}, {search_area['y2']})")
    
    # Extract search region
    search_region = img[search_area["y1"]:search_area["y2"], search_area["x1"]:search_area["x2"]]
    
    # Convert to HSV for color detection
    hsv_region = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
    
    # Look for red/brown colors (MAIN STAGE button)
    red_lower = np.array([0, 50, 50])
    red_upper = np.array([20, 255, 255])
    red_mask = cv2.inRange(hsv_region, red_lower, red_upper)
    
    # Find contours
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    largest_area = 0
    best_position = None
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5000:  # Minimum size for MAIN STAGE button
            x, y, w, h = cv2.boundingRect(contour)
            
            # Convert back to full image coordinates
            full_x = search_area["x1"] + x + w//2
            full_y = search_area["y1"] + y + h//2
            
            if area > largest_area:
                largest_area = area
                best_position = (full_x, full_y)
                print_step("DETECT", f"Found red area: {area} pixels at ({full_x}, {full_y})")
    
    if best_position:
        print_step("SUCCESS", f"MAIN STAGE detected at {best_position}")
        return best_position
    else:
        # Fallback to center of search area
        fallback_x = (search_area["x1"] + search_area["x2"]) // 2
        fallback_y = (search_area["y1"] + search_area["y2"]) // 2
        print_step("FALLBACK", f"Using fallback position ({fallback_x}, {fallback_y})")
        return (fallback_x, fallback_y)

def main():
    """Test MAIN STAGE detection"""
    print("🎯 SIMPLE MAIN STAGE AI TEST")
    print("=" * 50)
    
    for test in range(5):
        print_step("TEST", f"Test {test + 1}/5")
        
        # Take screenshot
        img = safe_screenshot()
        if img is None:
            print_step("ERROR", "Screenshot failed")
            time.sleep(3)
            continue
        
        # Find MAIN STAGE
        main_stage_pos = find_main_stage_precise(img)
        if main_stage_pos:
            x, y = main_stage_pos
            print_step("ACTION", f"Akan klik MAIN STAGE di ({x}, {y})")
            
            # Click MAIN STAGE
            safe_click(x, y)
            
            # Wait and see result
            time.sleep(5)
        else:
            print_step("ERROR", "MAIN STAGE tidak ditemukan")
        
        time.sleep(3)
    
    print_step("COMPLETE", "Test selesai!")

if __name__ == "__main__":
    main()