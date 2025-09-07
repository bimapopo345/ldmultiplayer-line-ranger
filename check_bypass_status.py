#!/usr/bin/env python3
"""
Check if bypass worked - detect LIAPP ALERT or normal lobby
"""
import subprocess
import time

def run_adb(cmd):
    try:
        full_cmd = f'"C:\\LDPlayer\\LDPlayer9\\adb.exe" -s emulator-5554 {cmd}'
        result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
        return result.stdout.strip(), result.returncode == 0
    except:
        return "", False

def check_current_status():
    print("🔍 Checking current Line Ranger status...")
    
    # Get UI dump
    print("📱 Capturing UI state...")
    run_adb("shell uiautomator dump /sdcard/ui_check.xml")
    subprocess.run([
        "C:\\LDPlayer\\LDPlayer9\\adb.exe", "-s", "emulator-5554", 
        "pull", "/sdcard/ui_check.xml", "ui_check.xml"
    ], capture_output=True)
    
    try:
        with open("ui_check.xml", "r", encoding="utf-8") as f:
            ui_content = f.read()
        
        # Check for LIAPP ALERT
        if "LIAPP ALERT" in ui_content:
            print("❌ BYPASS FAILED - LIAPP ALERT still detected!")
            print("🚨 Memory Attack detection still active")
            
            # Check for specific error messages
            if "Memory Attack" in ui_content:
                print("   - Memory Attack detected")
            if "Mattack-ldr" in ui_content:
                print("   - Loader attack detected")
            
            return False
            
        elif "lobby" in ui_content.lower() or "main" in ui_content.lower():
            print("✅ BYPASS SUCCESS - In lobby/main menu!")
            return True
            
        elif "loading" in ui_content.lower():
            print("⏳ App is loading...")
            return None
            
        else:
            print("❓ Unknown state - checking activity...")
            
            # Check current activity
            output, success = run_adb("shell dumpsys activity activities | findstr mResumedActivity")
            if "com.linecorp.LGRGS" in output:
                print("✅ Line Ranger is active")
                print(f"   Activity: {output}")
                return True
            else:
                print("❌ Line Ranger not active")
                return False
                
    except Exception as e:
        print(f"❌ Error reading UI: {e}")
        return False

def main():
    print("=" * 50)
    print("🕵️ BYPASS STATUS CHECKER")
    print("=" * 50)
    
    # Wait a bit for app to fully load
    print("⏳ Waiting 10 seconds for app to stabilize...")
    time.sleep(10)
    
    # Check status
    status = check_current_status()
    
    if status is True:
        print("\n🎉 SUCCESS! Bypass worked!")
        print("📱 Line Ranger is running normally")
    elif status is False:
        print("\n💀 FAILED! Need stronger bypass")
        print("🔧 Anti-cheat detection is still active")
    else:
        print("\n⏳ UNCERTAIN - App might still be loading")
        print("🔄 Try checking again in a few minutes")

if __name__ == "__main__":
    main()