#!/usr/bin/env python3
"""
Test script to verify screen detection works with the loading and lobby images
"""
import cv2
import numpy as np
import json
from datetime import datetime

def detect_screen_type(img_path):
    """Test the screen detection logic"""
    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Could not load image: {img_path}")
        return None
    
    print(f"📸 Testing image: {img_path} - Shape: {img.shape}")
    
    # Convert to different formats for analysis
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Look for yellow progress bar (loading screen)
    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    yellow_pixels = cv2.countNonZero(yellow_mask)
    
    # Look for the purple/blue background of loading screen
    purple_lower = np.array([120, 50, 50])
    purple_upper = np.array([150, 255, 255])
    purple_mask = cv2.inRange(hsv, purple_lower, purple_upper)
    purple_pixels = cv2.countNonZero(purple_mask)
    
    # Look for "MAIN STAGE" button (lobby screen)
    # Check for brown/orange UI elements typical of lobby
    brown_lower = np.array([10, 100, 50])
    brown_upper = np.array([20, 255, 200])
    brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
    brown_pixels = cv2.countNonZero(brown_mask)
    
    # Look for multiple character platforms (lobby)
    # Detect circular/platform shapes
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=20, maxRadius=100)
    circle_count = len(circles[0]) if circles is not None else 0
    
    # Decision logic
    if yellow_pixels > 5000 and purple_pixels > 50000:
        screen_type = "loading"
        confidence = "high"
    elif brown_pixels > 20000 and circle_count >= 3:
        screen_type = "lobby" 
        confidence = "high"
    elif brown_pixels > 10000:
        screen_type = "lobby"
        confidence = "medium"
    elif purple_pixels > 30000:
        screen_type = "loading"
        confidence = "medium"
    else:
        screen_type = "unknown"
        confidence = "low"
    
    detection_info = {
        "image": img_path,
        "screen_type": screen_type,
        "confidence": confidence,
        "yellow_pixels": int(yellow_pixels),
        "purple_pixels": int(purple_pixels), 
        "brown_pixels": int(brown_pixels),
        "circles_detected": circle_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"🔍 Detection Result:")
    print(f"   Screen Type: {screen_type} ({confidence} confidence)")
    print(f"   Yellow pixels: {yellow_pixels}")
    print(f"   Purple pixels: {purple_pixels}")
    print(f"   Brown pixels: {brown_pixels}")
    print(f"   Circles detected: {circle_count}")
    print()
    
    return detection_info

def find_clickable_elements(img_path):
    """Find potential clickable elements in the image"""
    img = cv2.imread(img_path)
    if img is None:
        return []
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, width = img.shape[:2]
    
    clickable_elements = []
    
    # Find MAIN STAGE button area (for lobby)
    if "lobby" in img_path.lower():
        main_stage_pos = (width // 2, height // 2 - 100)
        clickable_elements.append({
            "type": "main_stage_button",
            "position": main_stage_pos,
            "description": "MAIN STAGE button"
        })
    
    # Find yellow round buttons
    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 1000 < area < 20000:  # Button-sized areas
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w//2, y + h//2
            clickable_elements.append({
                "type": "yellow_button",
                "position": (center_x, center_y),
                "area": int(area),
                "description": f"Yellow button at ({center_x}, {center_y})"
            })
    
    # Find green buttons (START/GO buttons)
    green_lower = np.array([40, 50, 50])
    green_upper = np.array([80, 255, 255])
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    
    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 2000 < area < 50000:  # Button-sized
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w//2, y + h//2
            clickable_elements.append({
                "type": "green_button",
                "position": (center_x, center_y),
                "area": int(area),
                "description": f"Green button (START/GO) at ({center_x}, {center_y})"
            })
    
    return clickable_elements

def main():
    """Test screen detection with the provided images"""
    print("🧪 TESTING SCREEN DETECTION")
    print("=" * 50)
    
    test_images = [
        "loading_awal_masuk_game.png",
        "lobby.png"
    ]
    
    results = []
    
    for img_path in test_images:
        print(f"\n📋 Testing: {img_path}")
        print("-" * 30)
        
        # Test screen detection
        detection_result = detect_screen_type(img_path)
        if detection_result:
            results.append(detection_result)
        
        # Find clickable elements
        clickable = find_clickable_elements(img_path)
        print(f"🎯 Found {len(clickable)} clickable elements:")
        for element in clickable:
            print(f"   - {element['description']}")
        print()
    
    # Save results
    with open("screen_detection_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Test completed!")
    print("📁 Results saved to: screen_detection_test_results.json")
    
    # Summary
    print("\n📊 SUMMARY:")
    for result in results:
        print(f"   {result['image']}: {result['screen_type']} ({result['confidence']})")

if __name__ == "__main__":
    main()