#!/usr/bin/env python3
"""
Line Ranger Anti-Detection Bypass
"""
import subprocess
import time
import os

class AntiDetectionBypass:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
    
    def run_adb(self, cmd, silent=True):
        try:
            full_cmd = f'"{self.adb_path}" -s {self.device} {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            if not silent:
                print(f"CMD: {cmd}")
                print(f"OUT: {result.stdout.strip()}")
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def hide_emulator_properties(self):
        """Hide emulator properties that trigger detection"""
        print("🔧 Hiding emulator properties...")
        
        # Common emulator properties to hide/change
        props_to_hide = [
            "ro.kernel.qemu=0",
            "ro.bootmode=unknown", 
            "ro.hardware=goldfish",
            "ro.product.model=SM-G973F",  # Change to real device
            "ro.product.brand=samsung",
            "ro.product.name=beyond1lte",
            "ro.build.fingerprint=samsung/beyond1ltexx/beyond1:10/QP1A.190711.020/G973FXXU3BTIB:user/release-keys"
        ]
        
        for prop in props_to_hide:
            key, value = prop.split("=", 1)
            self.run_adb(f"shell setprop {key} {value}")
        
        print("✅ Emulator properties hidden")
    
    def disable_debugging_detection(self):
        """Disable debugging detection"""
        print("🔧 Disabling debugging detection...")
        
        # Hide debugging flags
        debug_props = [
            "ro.debuggable=0",
            "ro.secure=1", 
            "service.adb.root=0",
            "ro.build.type=user"
        ]
        
        for prop in debug_props:
            key, value = prop.split("=", 1)
            self.run_adb(f"shell setprop {key} {value}")
        
        print("✅ Debugging detection disabled")
    
    def hide_root_detection(self):
        """Hide root detection"""
        print("🔧 Hiding root detection...")
        
        # Remove common root files/paths
        root_paths = [
            "/system/bin/su",
            "/system/xbin/su", 
            "/sbin/su",
            "/system/app/Superuser.apk",
            "/system/app/SuperSU.apk"
        ]
        
        for path in root_paths:
            self.run_adb(f"shell rm -f {path}")
        
        print("✅ Root detection hidden")
    
    def spoof_device_info(self):
        """Spoof device information"""
        print("🔧 Spoofing device information...")
        
        # Spoof to Samsung Galaxy S10
        device_props = [
            "ro.product.manufacturer=samsung",
            "ro.product.model=SM-G973F",
            "ro.product.brand=samsung", 
            "ro.product.name=beyond1lte",
            "ro.product.device=beyond1",
            "ro.build.product=beyond1lte",
            "ro.build.model=SM-G973F",
            "ro.build.brand=samsung",
            "ro.build.manufacturer=samsung"
        ]
        
        for prop in device_props:
            key, value = prop.split("=", 1)
            self.run_adb(f"shell setprop {key} {value}")
        
        print("✅ Device info spoofed to Samsung Galaxy S10")
    
    def disable_memory_protection(self):
        """Try to disable memory protection"""
        print("🔧 Disabling memory protection...")
        
        # Kill Line Ranger first
        self.run_adb("shell am force-stop com.linecorp.LGRGS")
        time.sleep(2)
        
        # Disable memory protection features
        memory_props = [
            "ro.config.knox=0",
            "ro.boot.warranty_bit=0",
            "ro.warranty_bit=0",
            "ro.fmp_config=0",
            "ro.boot.fmp_config=0"
        ]
        for prop in memory_props:
            key, value = prop.split("=", 1)
            self.run_adb(f"shell setprop {key} {value}")
        
        print("✅ Memory protection disabled")
    
    def restart_app_safely(self):
        """Restart Line Ranger with bypass"""
        print("🚀 Restarting Line Ranger with bypass...")
        
        # Force stop first
        self.run_adb("shell am force-stop com.linecorp.LGRGS")
        time.sleep(3)
        
        # Clear app data (optional - removes detection cache)
        # self.run_adb("shell pm clear com.linecorp.LGRGS")
        
        # Start app
        self.run_adb("shell monkey -p com.linecorp.LGRGS -c android.intent.category.LAUNCHER 1")
        
        print("✅ Line Ranger restarted")
    
    def full_bypass(self):
        """Execute full bypass routine"""
        print("=" * 60)
        print("🛡️ LINE RANGER ANTI-DETECTION BYPASS")
        print("=" * 60)
        
        # Step 1: Hide emulator
        self.hide_emulator_properties()
        time.sleep(1)
        
        # Step 2: Disable debugging
        self.disable_debugging_detection() 
        time.sleep(1)
        
        # Step 3: Hide root
        self.hide_root_detection()
        time.sleep(1)
        
        # Step 4: Spoof device
        self.spoof_device_info()
        time.sleep(1)
        
        # Step 5: Disable memory protection
        self.disable_memory_protection()
        time.sleep(3)
        
        # Step 6: Restart app
        self.restart_app_safely()
        
        print("\n" + "=" * 60)
        print("✅ BYPASS COMPLETE!")
        print("🎮 Try launching Line Ranger now")
        print("=" * 60)

def main():
    bypass = AntiDetectionBypass()
    bypass.full_bypass()

if __name__ == "__main__":
    main()