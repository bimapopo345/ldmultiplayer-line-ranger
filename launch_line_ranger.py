#!/usr/bin/env python3
"""
Auto Launch Line Ranger Script
Membuka LDPlayer dan menjalankan Line Ranger dengan timeout yang cukup
"""

import time
import subprocess
import sys
from CBAutoHelper import LDPlayer

class LineRangerLauncher:
    def __init__(self):
        self.ld = LDPlayer()
        self.device_name = "LDPlayer"
        self.device_index = "0"
        self.line_ranger_package = "com.linecorp.LGRGS"
        self.max_wait_time = 300  # 5 menit
        
    def print_status(self, message, status="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WAIT": "⏳", "START": "🚀"}
        print(f"[{timestamp}] {symbols.get(status, 'ℹ️')} {message}")
    
    def check_ldplayer_running(self):
        """Cek apakah LDPlayer sudah running"""
        try:
            result = subprocess.run([
                "C:\\LDPlayer\\LDPlayer9\\ldconsole.exe", 
                "isrunning", "--index", self.device_index
            ], capture_output=True, text=True, timeout=10)
            
            return "running" in result.stdout.lower()
        except Exception as e:
            self.print_status(f"Error checking LDPlayer status: {e}", "ERROR")
            return False
    
    def start_ldplayer(self):
        """Start LDPlayer dengan timeout"""
        self.print_status("Starting LDPlayer...", "START")
        
        try:
            # Launch LDPlayer
            subprocess.run([
                "C:\\LDPlayer\\LDPlayer9\\ldconsole.exe", 
                "launch", "--index", self.device_index
            ], timeout=30)
            
            # Wait for LDPlayer to start (max 5 minutes)
            start_time = time.time()
            while time.time() - start_time < self.max_wait_time:
                if self.check_ldplayer_running():
                    elapsed = int(time.time() - start_time)
                    self.print_status(f"LDPlayer started successfully in {elapsed} seconds!", "SUCCESS")
                    return True
                
                elapsed = int(time.time() - start_time)
                self.print_status(f"Waiting for LDPlayer to start... ({elapsed}s/{self.max_wait_time}s)", "WAIT")
                time.sleep(10)
            
            self.print_status("Timeout waiting for LDPlayer to start", "ERROR")
            return False
            
        except Exception as e:
            self.print_status(f"Error starting LDPlayer: {e}", "ERROR")
            return False
    
    def wait_for_android_boot(self):
        """Wait for Android system to fully boot"""
        self.print_status("Waiting for Android system to boot...", "WAIT")
        
        for attempt in range(60):  # 60 attempts, 10 seconds each = 10 minutes max
            try:
                # Check if ADB devices shows the emulator
                result = subprocess.run([
                    "C:\\LDPlayer\\LDPlayer9\\adb.exe", "devices"
                ], capture_output=True, text=True, timeout=10)
                
                if "emulator-5554" not in result.stdout:
                    self.print_status(f"Waiting for emulator to appear... (attempt {attempt + 1}/60)", "WAIT")
                    time.sleep(10)
                    continue
                
                # Check if Android boot is complete
                boot_result = subprocess.run([
                    "C:\\LDPlayer\\LDPlayer9\\adb.exe", 
                    "-s", "emulator-5554",
                    "shell", "getprop", "sys.boot_completed"
                ], capture_output=True, text=True, timeout=15)
                
                if "1" in boot_result.stdout.strip():
                    # Additional check: can we access package manager?
                    pm_result = subprocess.run([
                        "C:\\LDPlayer\\LDPlayer9\\adb.exe", 
                        "-s", "emulator-5554",
                        "shell", "pm", "list", "packages", "|", "head", "-1"
                    ], capture_output=True, text=True, timeout=15)
                    
                    if pm_result.returncode == 0:
                        elapsed = (attempt + 1) * 10
                        self.print_status(f"Android system fully booted! ({elapsed}s)", "SUCCESS")
                        return True
                
                elapsed = (attempt + 1) * 10
                self.print_status(f"Android still booting... ({elapsed}s/600s)", "WAIT")
                    
            except Exception as e:
                self.print_status(f"Boot check error: {e}", "WAIT")
            
            time.sleep(10)
        
        self.print_status("Android boot timeout (10 minutes)", "ERROR")
        return False
    
    def check_app_installed(self):
        """Cek apakah Line Ranger terinstall"""
        try:
            # Use direct ADB command instead of ldconsole
            result = subprocess.run([
                "C:\\LDPlayer\\LDPlayer9\\adb.exe", 
                "-s", "emulator-5554",
                "shell", "pm", "list", "packages"
            ], capture_output=True, text=True, timeout=30)
            
            return self.line_ranger_package in result.stdout
        except Exception as e:
            self.print_status(f"Error checking app installation: {e}", "ERROR")
            return False
    
    def launch_line_ranger(self):
        """Launch Line Ranger"""
        self.print_status("Launching Line Ranger...", "START")
        
        try:
            # Check if app is installed
            if not self.check_app_installed():
                self.print_status("Line Ranger not installed!", "ERROR")
                return False
            
            # Launch the app
            subprocess.run([
                "C:\\LDPlayer\\LDPlayer9\\ldconsole.exe", 
                "runapp", "--index", self.device_index, 
                "--packagename", self.line_ranger_package
            ], timeout=30)
            
            self.print_status("Line Ranger launch command sent!", "SUCCESS")
            
            # Wait a bit for app to start
            self.print_status("Waiting for Line Ranger to load...", "WAIT")
            time.sleep(15)
            
            return True
            
        except Exception as e:
            self.print_status(f"Error launching Line Ranger: {e}", "ERROR")
            return False
    
    def get_device_info(self):
        """Get device information"""
        try:
            devices = self.ld.GetDevices2()
            self.print_status(f"Found {len(devices)} LDPlayer devices:", "INFO")
            
            for device in devices:
                status = "🟢 Selected" if device['name'] == self.device_name else "⚪"
                self.print_status(f"  {status} {device['name']} (index: {device['index']})", "INFO")
            
            return len(devices) > 0
        except Exception as e:
            self.print_status(f"Error getting device info: {e}", "ERROR")
            return False
    
    def run(self):
        """Main execution function"""
        self.print_status("=== LINE RANGER AUTO LAUNCHER ===", "START")
        self.print_status("Max wait time: 5 minutes", "INFO")
        
        # Step 1: Get device info
        if not self.get_device_info():
            self.print_status("Failed to get device information", "ERROR")
            return False
        
        # Step 2: Check if LDPlayer is already running
        if self.check_ldplayer_running():
            self.print_status("LDPlayer is already running!", "SUCCESS")
        else:
            # Step 3: Start LDPlayer
            if not self.start_ldplayer():
                self.print_status("Failed to start LDPlayer", "ERROR")
                return False
        
        # Step 4: Wait for Android to fully boot
        if not self.wait_for_android_boot():
            self.print_status("Failed to wait for Android boot", "ERROR")
            return False
        
        # Step 5: Launch Line Ranger
        if not self.launch_line_ranger():
            self.print_status("Failed to launch Line Ranger", "ERROR")
            return False
        
        self.print_status("=== ALL DONE! ===", "SUCCESS")
        self.print_status("Line Ranger should now be running in LDPlayer", "SUCCESS")
        return True

def main():
    """Main function"""
    try:
        launcher = LineRangerLauncher()
        success = launcher.run()
        
        if success:
            print("\n🎉 SUCCESS! Line Ranger is now running!")
        else:
            print("\n❌ FAILED! Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()