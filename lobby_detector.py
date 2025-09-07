#!/usr/bin/env python3
"""
Line Ranger Lobby Detector & API Bypass Research
"""
import subprocess
import time
import json
import requests
from PIL import Image
import cv2
import numpy as np

class LobbyDetector:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
    
    def run_adb(self, cmd):
        """Run ADB command"""
        try:
            full_cmd = f'"{self.adb_path}" -s {self.device} {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def check_app_activity(self):
        """Check current activity of Line Ranger"""
        print("🔍 Checking current app activity...")
        output, success = self.run_adb("shell dumpsys activity activities | findstr mResumedActivity")
        if success and "com.linecorp.LGRGS" in output:
            print(f"✅ Line Ranger is active: {output}")
            return True, output
        return False, output
    
    def get_current_activity(self):
        """Get detailed current activity"""
        print("📱 Getting current activity details...")
        output, success = self.run_adb("shell dumpsys activity top | findstr ACTIVITY")
        if success:
            print(f"Current activity: {output}")
            return output
        return ""
    
    def check_network_traffic(self):
        """Monitor network traffic for API calls"""
        print("🌐 Checking network connections...")
        output, success = self.run_adb("shell netstat -an | findstr :80")
        if success:
            print(f"HTTP connections: {output}")
        
        output2, success2 = self.run_adb("shell netstat -an | findstr :443")
        if success2:
            print(f"HTTPS connections: {output2}")
    
    def capture_screen(self):
        """Capture screen for visual analysis"""
        print("📸 Capturing screen...")
        # Take screenshot
        self.run_adb("shell screencap -p /sdcard/screenshot.png")
        # Pull to PC
        subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/screenshot.png", "screenshot.png"], 
                      capture_output=True)
        
        try:
            # Analyze screenshot
            img = cv2.imread("screenshot.png")
            if img is not None:
                height, width = img.shape[:2]
                print(f"✅ Screenshot captured: {width}x{height}")
                return True
            else:
                print("❌ Failed to load screenshot")
                return False
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return False
    
    def detect_lobby_elements(self):
        """Detect lobby UI elements"""
        print("🎯 Detecting lobby elements...")
        
        # Check for common lobby text/buttons
        lobby_indicators = [
            "shell uiautomator dump /sdcard/ui.xml",
        ]
        
        for cmd in lobby_indicators:
            output, success = self.run_adb(cmd)
            if success:
                # Pull UI dump
                subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/ui.xml", "ui.xml"], 
                              capture_output=True)
                
                try:
                    with open("ui.xml", "r", encoding="utf-8") as f:
                        ui_content = f.read()
                        
                    # Look for lobby indicators
                    lobby_keywords = ["lobby", "main", "menu", "start", "play", "battle", "stage"]
                    found_keywords = []
                    
                    for keyword in lobby_keywords:
                        if keyword.lower() in ui_content.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"✅ Lobby indicators found: {found_keywords}")
                        return True, found_keywords
                    else:
                        print("❌ No lobby indicators found")
                        return False, []
                        
                except Exception as e:
                    print(f"❌ UI analysis error: {e}")
                    return False, []
        
        return False, []
    
    def check_app_processes(self):
        """Check Line Ranger processes and memory"""
        print("⚙️ Checking app processes...")
        
        # Get process info
        output, success = self.run_adb("shell ps | findstr linecorp")
        if success:
            print(f"Line Ranger processes: {output}")
        
        # Get memory usage
        output2, success2 = self.run_adb("shell dumpsys meminfo com.linecorp.LGRGS")
        if success2:
            lines = output2.split('\n')[:10]  # First 10 lines
            print("Memory usage:")
            for line in lines:
                if line.strip():
                    print(f"  {line}")
    
    def monitor_logcat(self, duration=10):
        """Monitor logcat for API calls and network activity"""
        print(f"📋 Monitoring logcat for {duration} seconds...")
        
        # Clear logcat first
        self.run_adb("logcat -c")
        
        # Monitor for specific time
        try:
            cmd = f'"{self.adb_path}" -s {self.device} logcat -v time | findstr -i "http\\|api\\|network\\|login\\|lobby"'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            start_time = time.time()
            logs = []
            
            while time.time() - start_time < duration:
                line = process.stdout.readline()
                if line:
                    logs.append(line.strip())
                    print(f"📋 {line.strip()}")
                time.sleep(0.1)
            
            process.terminate()
            return logs
            
        except Exception as e:
            print(f"❌ Logcat error: {e}")
            return []
    
    def full_lobby_check(self):
        """Complete lobby detection routine"""
        print("=" * 60)
        print("🕵️ LOBBY DETECTION & API ANALYSIS")
        print("=" * 60)
        
        # 1. Check if app is running
        is_active, activity_info = self.check_app_activity()
        if not is_active:
            print("❌ Line Ranger not active!")
            return False
        
        # 2. Get current activity details
        current_activity = self.get_current_activity()
        
        # 3. Capture and analyze screen
        screen_captured = self.capture_screen()
        
        # 4. Detect lobby UI elements
        lobby_detected, keywords = self.detect_lobby_elements()
        
        # 5. Check processes and memory
        self.check_app_processes()
        
        # 6. Monitor network traffic
        self.check_network_traffic()
        
        # 7. Monitor logcat for API calls
        api_logs = self.monitor_logcat(15)
        
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"App Active: {'✅' if is_active else '❌'}")
        print(f"Screen Captured: {'✅' if screen_captured else '❌'}")
        print(f"Lobby Detected: {'✅' if lobby_detected else '❌'}")
        print(f"Keywords Found: {keywords}")
        print(f"API Logs Captured: {len(api_logs)} entries")
        
        return lobby_detected

def main():
    detector = LobbyDetector()
    detector.full_lobby_check()

if __name__ == "__main__":
    main()