#!/usr/bin/env python3
"""
Enhanced Safe Line Ranger AI Automation
1. Detect loading screen vs lobby screen
2. Wait for loading to complete
3. Navigate to main stage and automate gameplay
4. Log all actions and screen states
"""
import cv2
import numpy as np
import subprocess
import time
import os
import json
import base64
from datetime import datetime

def print_step(step, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{step}] {message}")

def log_action(action, details=""):
    """Log all actions with timestamp"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details
    }
    
    # Append to log file
    log_file = "line_ranger_automation_log.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except:
        pass
    
    print_step("LOG", f"{action}: {details}")

def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.stdout.strip(), result.returncode == 0
    except:
        return "", False

def launch_line_ranger():
    """Proven launcher code - no debugging to avoid LIAPP ALERT"""
    print("=" * 50)
    print("🚀 LINE RANGER LAUNCHER")
    print("=" * 50)
    
    # Step 1: Check LDPlayer
    print_step("1", "Checking LDPlayer status...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe isrunning --index 0')
    
    if "stop" in output or not success:
        print_step("1", "LDPlayer not running. Starting...")
        run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe launch --index 0')
        
        # Wait for LDPlayer to start
        for i in range(18):  # 3 minutes max
            time.sleep(10)
            output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe isrunning --index 0')
            if "running" in output:
                print_step("1", f"✅ LDPlayer started! ({(i+1)*10}s)")
                break
            print_step("1", f"⏳ Waiting for LDPlayer... ({(i+1)*10}s)")
        else:
            print_step("1", "❌ LDPlayer start timeout!")
            return False
    else:
        print_step("1", "✅ LDPlayer already running!")
    
    # Step 2: Wait for ADB
    print_step("2", "Waiting for ADB connection...")
    for i in range(18):  # 3 minutes max
        output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe devices')
        if "emulator-5554" in output and "device" in output:
            print_step("2", f"✅ ADB connected! ({(i+1)*10}s)")
            break
        time.sleep(10)
        print_step("2", f"⏳ Waiting for ADB... ({(i+1)*10}s)")
    else:
        print_step("2", "❌ ADB connection timeout!")
        return False
    
    # Step 3: Wait for Android boot
    print_step("3", "Waiting for Android system...")
    for i in range(18):  # 3 minutes max
        output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell getprop sys.boot_completed')
        if "1" in output:
            print_step("3", f"✅ Android ready! ({(i+1)*10}s)")
            break
        time.sleep(10)
        print_step("3", f"⏳ Waiting for Android... ({(i+1)*10}s)")
    else:
        print_step("3", "❌ Android boot timeout!")
        return False
    
    # Step 4: Launch Line Ranger
    print_step("4", "Launching Line Ranger...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe runapp --index 0 --packagename com.linecorp.LGRGS')
    
    if success:
        print_step("4", "✅ Line Ranger launched!")
        log_action("GAME_LAUNCHED", "Line Ranger app started successfully")
        print_step("4", "⏳ Waiting for app to load...")
        time.sleep(20)
        print_step("4", "🎉 DONE!")
    else:
        print_step("4", "❌ Failed to launch Line Ranger!")
        return False
    
    print("\n" + "=" * 50)
    print("🎮 Line Ranger should now be running!")
    print("📱 Check your LDPlayer window")
    print("=" * 50)
    return True

class EnhancedGameplayAI:
    """Enhanced AI with screen detection and smart automation"""
    
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "current_screen.png"
        self.game_state = "unknown"
        
    def safe_screenshot(self):
        """Take screenshot safely - minimal ADB usage"""
        try:
            # Only use screencap - no debugging commands
            subprocess.run([
                self.adb_path, "-s", self.device, 
                "shell", "screencap", "-p", "/sdcard/game.png"
            ], capture_output=True, timeout=10)
            
            subprocess.run([
                self.adb_path, "-s", self.device, 
                "pull", "/sdcard/game.png", self.screenshot_path
            ], capture_output=True, timeout=10)
            
            img = cv2.imread(self.screenshot_path)
            if img is not None:
                print_step("SCREENSHOT", f"Captured: {img.shape}")
                return img
            return None
        except:
            print_step("ERROR", "Screenshot failed")
            return None
    
    def detect_screen_type(self, img):
        """Detect if we're on loading screen or lobby"""
        if img is None:
            return "unknown"
        
        # Convert to different formats for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Check for loading screen indicators
        loading_indicators = [
            "Loading game data",  # Text detection would be complex, so we use color/shape
            "Use items strategically",
            "18%"  # Progress percentage
        ]
        
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
            "screen_type": screen_type,
            "confidence": confidence,
            "yellow_pixels": int(yellow_pixels),
            "purple_pixels": int(purple_pixels), 
            "brown_pixels": int(brown_pixels),
            "circles_detected": circle_count
        }
        
        log_action("SCREEN_DETECTED", f"{screen_type} ({confidence} confidence)")
        print_step("DETECT", f"Screen: {screen_type} ({confidence}) - Yellow:{yellow_pixels}, Purple:{purple_pixels}, Brown:{brown_pixels}, Circles:{circle_count}")
        
        return screen_type, detection_info
    
    def find_main_stage_button(self, img):
        """Find the MAIN STAGE button in lobby"""
        if img is None:
            return None
            
        # Look for the large central button area
        height, width = img.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # MAIN STAGE button is typically in upper-center area
        # Based on the lobby image, it's around coordinates (640, 280)
        main_stage_area = {
            "x": center_x - 100,
            "y": center_y - 150,
            "width": 200,
            "height": 100
        }
        
        return (center_x, center_y - 100)  # Approximate MAIN STAGE button position
    
    def find_yellow_round_button(self, img):
        """Find yellow round/stage selection buttons"""
        if img is None:
            return []
            
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Look for yellow/gold buttons
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        # Find contours of yellow areas
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        yellow_buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 20000:  # Button-sized areas
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w//2, y + h//2
                yellow_buttons.append((center_x, center_y))
        
        return yellow_buttons
    
    def safe_click(self, x, y):
        """Safe click - minimal ADB usage"""
        try:
            subprocess.run([
                self.adb_path, "-s", self.device,
                "shell", "input", "tap", str(x), str(y)
            ], capture_output=True, timeout=5)
            log_action("CLICK", f"Tapped at ({x}, {y})")
            print_step("CLICK", f"👆 Clicked at ({x}, {y})")
            return True
        except:
            print_step("ERROR", "Click failed")
            return False
    
    def wait_for_lobby(self, max_wait=120):
        """Wait for loading to complete and reach lobby"""
        print_step("WAIT", "Waiting for loading to complete...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            img = self.safe_screenshot()
            if img is not None:
                screen_type, info = self.detect_screen_type(img)
                
                if screen_type == "lobby":
                    log_action("LOBBY_REACHED", f"Loading completed in {int(time.time() - start_time)}s")
                    print_step("SUCCESS", "🎉 Reached lobby!")
                    return True
                elif screen_type == "loading":
                    print_step("WAIT", f"Still loading... ({int(time.time() - start_time)}s)")
                else:
                    print_step("WAIT", f"Unknown screen, continuing... ({int(time.time() - start_time)}s)")
            
            time.sleep(5)
        
        print_step("TIMEOUT", "❌ Lobby wait timeout!")
        return False
    
    def automate_main_stage_flow(self):
        """Automate the main stage gameplay flow"""
        print_step("AUTOMATION", "Starting main stage automation...")
        
        # Step 1: Click MAIN STAGE button
        img = self.safe_screenshot()
        if img is not None:
            main_stage_pos = self.find_main_stage_button(img)
            if main_stage_pos:
                print_step("ACTION", "Clicking MAIN STAGE button")
                self.safe_click(main_stage_pos[0], main_stage_pos[1])
                time.sleep(3)
        
        # Step 2: Look for and click yellow round buttons (stage selection)
        for attempt in range(3):
            img = self.safe_screenshot()
            if img is not None:
                yellow_buttons = self.find_yellow_round_button(img)
                if yellow_buttons:
                    # Click the first yellow button found
                    x, y = yellow_buttons[0]
                    print_step("ACTION", f"Clicking yellow round button at ({x}, {y})")
                    self.safe_click(x, y)
                    time.sleep(3)
                    break
            time.sleep(2)
        
        # Step 3: Look for START/NEXT buttons and click them
        for step in range(5):  # Multiple next/start clicks
            img = self.safe_screenshot()
            if img is not None:
                # Look for green buttons (typically START/GO buttons)
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                green_lower = np.array([40, 50, 50])
                green_upper = np.array([80, 255, 255])
                green_mask = cv2.inRange(hsv, green_lower, green_upper)
                
                contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 2000 < area < 50000:  # Button-sized
                        x, y, w, h = cv2.boundingRect(contour)
                        center_x, center_y = x + w//2, y + h//2
                        print_step("ACTION", f"Clicking green button (START/NEXT) at ({center_x}, {center_y})")
                        self.safe_click(center_x, center_y)
                        time.sleep(4)
                        break
                else:
                    # If no green button, click center of screen
                    height, width = img.shape[:2]
                    center_x, center_y = width // 2, height // 2
                    print_step("ACTION", f"Clicking center screen at ({center_x}, {center_y})")
                    self.safe_click(center_x, center_y)
                    time.sleep(3)
            
            time.sleep(2)
        
        log_action("AUTOMATION_COMPLETE", "Main stage automation sequence finished")
        print_step("COMPLETE", "✅ Main stage automation completed!")
    
    def run_full_automation(self):
        """Run the complete automation flow"""
        print("\n" + "=" * 60)
        print("🤖 ENHANCED LINE RANGER AI AUTOMATION")
        print("=" * 60)
        
        # Phase 1: Wait for lobby
        if not self.wait_for_lobby():
            print_step("ERROR", "Failed to reach lobby")
            return False
        
        # Phase 2: Automate main stage flow
        self.automate_main_stage_flow()
        
        # Phase 3: Continue monitoring and automation
        print_step("MONITOR", "Starting continuous monitoring...")
        for cycle in range(10):
            print_step("CYCLE", f"Monitoring cycle {cycle + 1}/10")
            
            img = self.safe_screenshot()
            if img is not None:
                screen_type, info = self.detect_screen_type(img)
                
                if screen_type == "lobby":
                    print_step("STATUS", "Back in lobby - could restart automation")
                    # Could restart main stage flow here
                elif screen_type == "loading":
                    print_step("STATUS", "Loading screen detected - waiting...")
                else:
                    print_step("STATUS", "In game or unknown screen")
                    # Look for any clickable elements and interact
                    yellow_buttons = self.find_yellow_round_button(img)
                    if yellow_buttons:
                        x, y = yellow_buttons[0]
                        print_step("ACTION", f"Clicking yellow button at ({x}, {y})")
                        self.safe_click(x, y)
            
            time.sleep(10)
        
        print_step("COMPLETE", "🎉 Full automation completed!")
        return True

def main():
    """Main automation workflow"""
    print("🚀 ENHANCED SAFE LINE RANGER AI AUTOMATION")
    print("=" * 60)
    
    # Phase 1: Launch Line Ranger safely (proven method)
    print("📱 Phase 1: Launching Line Ranger...")
    if not launch_line_ranger():
        print("❌ Failed to launch Line Ranger")
        return
    
    # Phase 2: Enhanced AI automation with screen detection
    print("\n🤖 Phase 2: Starting enhanced AI automation...")
    gameplay_ai = EnhancedGameplayAI()
    gameplay_ai.run_full_automation()
    
    print("\n🎉 AUTOMATION COMPLETE!")
    print("📱 Check 'line_ranger_automation_log.json' for detailed logs")

if __name__ == "__main__":
    main()