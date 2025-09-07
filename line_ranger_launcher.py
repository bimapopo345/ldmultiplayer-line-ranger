#!/usr/bin/env python3
"""
Line Ranger Launcher - Clean & Simple
"""
import subprocess
import time
import os

def print_step(step, message):
    print(f"[{step}] {message}")

def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.stdout.strip(), result.returncode == 0
    except:
        return "", False

def main():
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
            return
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
        return
    
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
        return
    
    # Step 4: Launch Line Ranger
    print_step("4", "Launching Line Ranger...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe runapp --index 0 --packagename com.linecorp.LGRGS')
    
    if success:
        print_step("4", "✅ Line Ranger launched!")
        print_step("4", "⏳ Waiting for app to load...")
        time.sleep(20)
        print_step("4", "🎉 DONE!")
    else:
        print_step("4", "❌ Failed to launch Line Ranger!")
        return
    
    print("\n" + "=" * 50)
    print("🎮 Line Ranger should now be running!")
    print("📱 Check your LDPlayer window")
    print("=" * 50)

if __name__ == "__main__":
    main()