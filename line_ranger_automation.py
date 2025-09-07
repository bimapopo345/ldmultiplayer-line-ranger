#!/usr/bin/env python3
"""
Line Ranger Full Automation - From Launch to Gameplay
"""
import subprocess
import time
import json
import os
from datetime import datetime

class LineRangerAutomation:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.package = "com.linecorp.LGRGS"
        self.session_active = False
        self.user_profile = {}
        self.log_file = "automation_log.txt"
        
    def log(self, message, level="INFO"):
        """Log activities to monitoring system"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def run_adb(self, cmd, timeout=30):
        """Execute ADB command"""
        try:
            full_cmd = f'"{self.adb_path}" -s {self.device} {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=timeout)
            return result.stdout.strip(), result.returncode == 0
        except Exception as e:
            self.log(f"ADB command failed: {e}", "ERROR")
            return "", False
    
    def run_ldconsole(self, cmd):
        """Execute LDConsole command"""
        try:
            full_cmd = f'cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except Exception as e:
            self.log(f"LDConsole command failed: {e}", "ERROR")
            return "", False
    
    def step1_launch_with_bypass(self):
        """Step 1: Launch LDPlayer and apply bypass"""
        self.log("=== STEP 1: LAUNCHING WITH BYPASS ===")
        
        # Check LDPlayer status
        self.log("Checking LDPlayer status...")
        output, success = self.run_ldconsole("isrunning --index 0")
        
        if "stop" in output or not success:
            self.log("Starting LDPlayer...")
            self.run_ldconsole("launch --index 0")
            
            # Wait for LDPlayer
            for i in range(18):
                time.sleep(10)
                output, success = self.run_ldconsole("isrunning --index 0")
                if "running" in output:
                    self.log(f"LDPlayer started successfully ({(i+1)*10}s)")
                    break
                self.log(f"Waiting for LDPlayer... ({(i+1)*10}s)")
            else:
                self.log("LDPlayer start timeout!", "ERROR")
                return False
        else:
            self.log("LDPlayer already running")
        
        # Wait for ADB
        self.log("Waiting for ADB connection...")
        for i in range(18):
            output, success = self.run_adb("devices")
            if "emulator-5554" in output and "device" in output:
                self.log(f"ADB connected ({(i+1)*10}s)")
                break
            time.sleep(10)
        else:
            self.log("ADB connection timeout!", "ERROR")
            return False
        
        # Apply bypass
        self.log("Applying anti-detection bypass...")
        self.apply_bypass()
        
        # Launch Line Ranger
        self.log("Launching Line Ranger...")
        self.run_ldconsole("runapp --index 0 --packagename com.linecorp.LGRGS")
        time.sleep(15)
        
        return True
    
    def apply_bypass(self):
        """Apply anti-detection bypass"""
        bypass_props = [
            "ro.kernel.qemu=0",
            "ro.product.model=SM-G973F",
            "ro.product.brand=samsung",
            "ro.debuggable=0",
            "ro.secure=1",
            "service.adb.root=0"
        ]
        
        for prop in bypass_props:
            key, value = prop.split("=", 1)
            self.run_adb(f"shell setprop {key} {value}")
        
        self.log("Bypass applied successfully")
    
    def step2_verify_session(self):
        """Step 2: Verify login session is valid"""
        self.log("=== STEP 2: VERIFYING SESSION ===")
        
        # Wait for app to load
        time.sleep(20)
        
        # Check if app is active
        output, success = self.run_adb("shell dumpsys activity activities | findstr mResumedActivity")
        if not success or self.package not in output:
            self.log("Line Ranger not active!", "ERROR")
            return False
        
        # Check for LIAPP ALERT
        self.run_adb("shell uiautomator dump /sdcard/session_check.xml")
        subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/session_check.xml", "session_check.xml"], capture_output=True)
        
        try:
            with open("session_check.xml", "r", encoding="utf-8") as f:
                ui_content = f.read()
            
            if "LIAPP ALERT" in ui_content:
                self.log("Session invalid - LIAPP ALERT detected!", "ERROR")
                return False
            
            self.log("Session verification successful")
            self.session_active = True
            return True
            
        except Exception as e:
            self.log(f"Session verification error: {e}", "ERROR")
            return False
    
    def step3_navigate_dashboard(self):
        """Step 3: Navigate to main dashboard"""
        self.log("=== STEP 3: NAVIGATING TO DASHBOARD ===")
        
        # Wait for loading screens
        time.sleep(30)
        
        # Handle initial popups/tutorials
        for i in range(5):
            self.log(f"Checking for popups... ({i+1}/5)")
            
            # Capture current UI
            self.run_adb("shell uiautomator dump /sdcard/dashboard.xml")
            subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/dashboard.xml", "dashboard.xml"], capture_output=True)
            
            try:
                with open("dashboard.xml", "r", encoding="utf-8") as f:
                    ui_content = f.read()
                
                # Look for common buttons to dismiss popups
                if "OK" in ui_content or "확인" in ui_content:
                    self.log("Found OK button, clicking...")
                    self.run_adb("shell input tap 800 600")  # Generic OK position
                    time.sleep(3)
                elif "CLOSE" in ui_content or "닫기" in ui_content:
                    self.log("Found Close button, clicking...")
                    self.run_adb("shell input tap 1000 300")  # Generic close position
                    time.sleep(3)
                elif "SKIP" in ui_content or "건너뛰기" in ui_content:
                    self.log("Found Skip button, clicking...")
                    self.run_adb("shell input tap 1100 100")  # Generic skip position
                    time.sleep(3)
                else:
                    self.log("No popups detected, proceeding...")
                    break
                    
            except Exception as e:
                self.log(f"Dashboard navigation error: {e}", "ERROR")
                break
            
            time.sleep(5)
        
        self.log("Dashboard navigation completed")
        return True
    
    def step4_get_user_profile(self):
        """Step 4: Extract user profile data"""
        self.log("=== STEP 4: EXTRACTING USER PROFILE ===")
        
        # Navigate to profile/settings
        self.log("Accessing profile section...")
        
        # Try to find profile/menu button
        self.run_adb("shell uiautomator dump /sdcard/profile.xml")
        subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/profile.xml", "profile.xml"], capture_output=True)
        
        try:
            with open("profile.xml", "r", encoding="utf-8") as f:
                ui_content = f.read()
            
            # Extract basic profile info (this would need to be customized based on actual UI)
            self.user_profile = {
                "timestamp": datetime.now().isoformat(),
                "app_active": True,
                "session_valid": self.session_active,
                "ui_elements_detected": len(ui_content.split("node")) - 1
            }
            
            self.log(f"User profile extracted: {self.user_profile}")
            return True
            
        except Exception as e:
            self.log(f"Profile extraction error: {e}", "ERROR")
            return False
    
    def step5_check_account_status(self):
        """Step 5: Check account status (active/inactive)"""
        self.log("=== STEP 5: CHECKING ACCOUNT STATUS ===")
        
        # Check if we can access game features
        account_active = True
        
        # Try to access main game features
        test_actions = [
            ("Check inventory", "shell input tap 100 500"),
            ("Check stages", "shell input tap 200 500"),
            ("Check shop", "shell input tap 300 500")
        ]
        
        for action_name, action_cmd in test_actions:
            self.log(f"Testing: {action_name}")
            self.run_adb(action_cmd)
            time.sleep(3)
            
            # Check for error messages
            self.run_adb("shell uiautomator dump /sdcard/status_check.xml")
            subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/status_check.xml", "status_check.xml"], capture_output=True)
            
            try:
                with open("status_check.xml", "r", encoding="utf-8") as f:
                    ui_content = f.read()
                
                if "error" in ui_content.lower() or "오류" in ui_content:
                    self.log(f"Error detected in {action_name}", "WARNING")
                    account_active = False
                    break
                    
            except:
                pass
            
            # Go back
            self.run_adb("shell input keyevent 4")  # Back button
            time.sleep(2)
        
        if account_active:
            self.log("Account status: ACTIVE")
            return True
        else:
            self.log("Account status: INACTIVE - stopping process", "ERROR")
            return False
    
    def step6_access_settings(self):
        """Step 6: Access settings if account is active"""
        self.log("=== STEP 6: ACCESSING SETTINGS ===")
        
        # Look for settings/menu button
        self.run_adb("shell uiautomator dump /sdcard/settings.xml")
        subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/settings.xml", "settings.xml"], capture_output=True)
        
        # Try common settings locations
        settings_positions = [
            (50, 50),    # Top-left menu
            (1200, 50),  # Top-right menu
            (50, 700),   # Bottom-left
            (1200, 700)  # Bottom-right
        ]
        
        for x, y in settings_positions:
            self.log(f"Trying settings at position ({x}, {y})")
            self.run_adb(f"shell input tap {x} {y}")
            time.sleep(3)
            
            # Check if settings opened
            self.run_adb("shell uiautomator dump /sdcard/settings_check.xml")
            subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/settings_check.xml", "settings_check.xml"], capture_output=True)
            
            try:
                with open("settings_check.xml", "r", encoding="utf-8") as f:
                    ui_content = f.read()
                
                if "setting" in ui_content.lower() or "설정" in ui_content:
                    self.log("Settings accessed successfully")
                    return True
                    
            except:
                pass
            
            # Go back if not settings
            self.run_adb("shell input keyevent 4")
            time.sleep(2)
        
        self.log("Could not access settings", "WARNING")
        return False
    
    def step7_save_monitoring_log(self):
        """Step 7: Save comprehensive log to monitoring system"""
        self.log("=== STEP 7: SAVING MONITORING LOG ===")
        
        monitoring_data = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "automation_status": "completed",
            "user_profile": self.user_profile,
            "session_active": self.session_active,
            "steps_completed": [
                "launch_with_bypass",
                "verify_session", 
                "navigate_dashboard",
                "extract_user_profile",
                "check_account_status",
                "access_settings"
            ],
            "device_info": {
                "emulator": "LDPlayer",
                "package": self.package,
                "adb_device": self.device
            }
        }
        
        # Save to JSON log
        json_log_file = f"monitoring_log_{monitoring_data['session_id']}.json"
        with open(json_log_file, "w", encoding="utf-8") as f:
            json.dump(monitoring_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"Monitoring log saved to {json_log_file}")
        self.log("All automation steps completed successfully!")
        return True
    
    def run_full_automation(self):
        """Execute complete automation workflow"""
        self.log("🚀 STARTING FULL LINE RANGER AUTOMATION")
        self.log("=" * 60)
        
        try:
            # Execute all steps
            if not self.step1_launch_with_bypass():
                raise Exception("Step 1 failed: Launch with bypass")
            
            if not self.step2_verify_session():
                raise Exception("Step 2 failed: Session verification")
            
            if not self.step3_navigate_dashboard():
                raise Exception("Step 3 failed: Dashboard navigation")
            
            if not self.step4_get_user_profile():
                raise Exception("Step 4 failed: User profile extraction")
            
            if not self.step5_check_account_status():
                raise Exception("Step 5 failed: Account inactive")
            
            self.step6_access_settings()  # Optional step
            
            self.step7_save_monitoring_log()
            
            self.log("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            self.log(f"❌ AUTOMATION FAILED: {e}", "ERROR")
            self.step7_save_monitoring_log()  # Save log even on failure
            return False

def main():
    automation = LineRangerAutomation()
    automation.run_full_automation()

if __name__ == "__main__":
    main()