#!/usr/bin/env python3
"""
Stage Number Clicker - Klik stage numbers (1, 2, 3) yang kuning
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
        subprocess.run([adb_path, "-s", device, "pull", "/sdcard/game.png", "stage_screen.png"], capture_output=True, timeout=10)
        
        img = cv2.imread("stage_screen.png")
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

def find_stage_numbers(img):
    """Cari stage numbers kuning (1, 2, 3)"""
    if img is None:
        return []
    
    height, width = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Yellow/gold color range untuk stage numbers
    yellow_lower = np.array([15, 100, 100])
    yellow_upper = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    
    # Find contours
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    stage_numbers = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 800 < area < 8000:  # Stage number size
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check if it's roughly circular (stage numbers are circular)
            aspect_ratio = w / h
            if 0.6 < aspect_ratio < 1.4:  # Roughly circular
                center_x, center_y = x + w//2, y + h//2
                
                # Stage numbers should be in the path area (center-bottom of screen)
                if (width * 0.2 < center_x < width * 0.8 and 
                    height * 0.3 < center_y < height * 0.8):
                    
                    stage_numbers.append({
                        "pos": (center_x, center_y),
                        "area": area,
                        "size": (w, h)
                    })
                    print_step("DETECT", f"Stage number found at ({center_x}, {center_y}), area: {area}")
    
    # Sort by position (left to right, then top to bottom)
    stage_numbers.sort(key=lambda s: (s["pos"][1], s["pos"][0]))
    
    return stage_numbers

def find_start_button(img):
    """Cari tombol START setelah pilih stage"""
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
        if 3000 < area < 50000:  # START button size
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w//2, y + h//2
            print_step("DETECT", f"START button found at ({center_x}, {center_y})")
            return (center_x, center_y)
    
    return None

def main():
    """Main stage number automation"""
    print("🎯 STAGE NUMBER CLICKER")
    print("=" * 40)
    
    for cycle in range(10):
        print_step("CYCLE", f"Cycle {cycle + 1}/10")
        
        # Take screenshot
        img = safe_screenshot()
        if img is None:
            time.sleep(3)
            continue
        
        # Look for stage numbers first
        stage_numbers = find_stage_numbers(img)
        if stage_numbers:
            # Click first available stage number
            pos = stage_numbers[0]["pos"]
            x, y = pos
            print_step("ACTION", f"Klik stage number di ({x}, {y})")
            safe_click(x, y)
            time.sleep(4)
            
            # After clicking stage, look for START button
            img2 = safe_screenshot()
            if img2:
                start_pos = find_start_button(img2)
                if start_pos:
                    sx, sy = start_pos
                    print_step("ACTION", f"Klik START button di ({sx}, {sy})")
                    safe_click(sx, sy)
                    time.sleep(6)
                else:
                    print_step("INFO", "START button tidak ditemukan, lanjut...")
        else:
            # Look for START button if no stage numbers
            start_pos = find_start_button(img)
            if start_pos:
                sx, sy = start_pos
                print_step("ACTION", f"Klik START button di ({sx}, {sy})")
                safe_click(sx, sy)
                time.sleep(6)
            else:
                print_step("INFO", "Tidak ada stage numbers atau START button, tunggu...")
        
        time.sleep(3)
    
    print_step("COMPLETE", "Stage automation selesai!")

if __name__ == "__main__":
    main()