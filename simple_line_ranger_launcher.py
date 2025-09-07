#!/usr/bin/env python3
"""
Simple Line Ranger Launcher - Step by step dengan bypass
"""
import subprocess
import time

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=30)
        return result.stdout.strip(), result.returncode == 0
    except:
        return "", False

def print_step(step, message):
    print(f"[{step}] {message}")

def main():
    print("=" * 50)
    print("🚀 SIMPLE LINE RANGER LAUNCHER")
    print("=" * 50)
    
    # Step 1: Check LDPlayer
    print_step("1", "Checking LDPlayer...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe isrunning --index 0')
    if "running" in output:
        print_step("1", "✅ LDPlayer is running")
    else:
        print_step("1", "❌ LDPlayer not running!")
        return
    
    # Step 2: Check ADB
    print_step("2", "Checking ADB connection...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe devices')
    if "emulator-5554" in output:
        print_step("2", "✅ ADB connected")
    else:
        print_step("2", "❌ ADB not connected!")
        return
    
    # Step 3: Apply bypass
    print_step("3", "Applying bypass...")
    bypass_commands = [
        'cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell setprop ro.kernel.qemu 0',
        'cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell setprop ro.debuggable 0',
        'cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell setprop ro.product.model SM-G973F',
        'cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell am force-stop com.linecorp.LGRGS'
    ]
    
    for cmd in bypass_commands:
        run_cmd(cmd)
        time.sleep(1)
    
    print_step("3", "✅ Bypass applied")
    
    # Step 4: Launch Line Ranger
    print_step("4", "Launching Line Ranger...")
    run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe runapp --index 0 --packagename com.linecorp.LGRGS')
    print_step("4", "✅ Launch command sent")
    
    # Step 5: Wait and check
    print_step("5", "Waiting 20 seconds for app to load...")
    time.sleep(20)
    
    # Step 6: Check if app is running
    print_step("6", "Checking app status...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell dumpsys activity activities | findstr mResumedActivity')
    
    if "com.linecorp.LGRGS" in output:
        print_step("6", "✅ Line Ranger is running!")
        print_step("6", f"   Activity: {output}")
    else:
        print_step("6", "❌ Line Ranger not detected")
        print_step("6", f"   Output: {output}")
    
    # Step 7: Check for LIAPP ALERT
    print_step("7", "Checking for LIAPP ALERT...")
    run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell uiautomator dump /sdcard/check.xml')
    run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 pull /sdcard/check.xml check.xml')
    
    try:
        with open("check.xml", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "LIAPP ALERT" in content:
            print_step("7", "❌ LIAPP ALERT detected - bypass failed!")
            if "Memory Attack" in content:
                print_step("7", "   - Memory Attack detected")
        else:
            print_step("7", "✅ No LIAPP ALERT - bypass successful!")
            
    except Exception as e:
        print_step("7", f"❌ Could not check UI: {e}")
    
    print("\n" + "=" * 50)
    print("🎮 Check your LDPlayer window now!")
    print("=" * 50)

if __name__ == "__main__":
    main()