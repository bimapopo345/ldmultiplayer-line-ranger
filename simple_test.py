#!/usr/bin/env python3
"""
Simple test to verify images can be loaded and basic detection works
"""
import cv2
import numpy as np

def test_image(img_path):
    print(f"Testing: {img_path}")
    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Could not load {img_path}")
        return
    
    print(f"✅ Loaded {img_path} - Shape: {img.shape}")
    
    # Convert to HSV for color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Check for yellow (progress bar in loading screen)
    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    yellow_pixels = cv2.countNonZero(yellow_mask)
    
    # Check for purple/blue (loading screen background)
    purple_lower = np.array([120, 50, 50])
    purple_upper = np.array([150, 255, 255])
    purple_mask = cv2.inRange(hsv, purple_lower, purple_upper)
    purple_pixels = cv2.countNonZero(purple_mask)
    
    # Check for brown/orange (lobby UI)
    brown_lower = np.array([10, 100, 50])
    brown_upper = np.array([20, 255, 200])
    brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
    brown_pixels = cv2.countNonZero(brown_mask)
    
    print(f"   Yellow pixels: {yellow_pixels}")
    print(f"   Purple pixels: {purple_pixels}")
    print(f"   Brown pixels: {brown_pixels}")
    
    # Simple detection logic
    if yellow_pixels > 5000 and purple_pixels > 50000:
        screen_type = "LOADING SCREEN"
    elif brown_pixels > 10000:
        screen_type = "LOBBY SCREEN"
    else:
        screen_type = "UNKNOWN"
    
    print(f"   🎯 Detected: {screen_type}")
    print()

if __name__ == "__main__":
    print("🧪 Simple Screen Detection Test")
    print("=" * 40)
    
    test_image("loading_awal_masuk_game.png")
    test_image("lobby.png")
    
    print("✅ Test completed!")