#!/usr/bin/env python3
from CBAutoHelper import LDPlayer

print("=== Quick Line Ranger Launcher ===")

# Initialize and select LDPlayer device
ld = LDPlayer()
ld.Info('name', 'LDPlayer')

print("🚀 Starting LDPlayer...")
ld.Start()

print("⏳ Waiting 5 seconds...")
import time
time.sleep(5)

print("🎮 Trying to open Line Ranger...")
# Try the most common Line Ranger package
try:
    ld.RunApp("com.linecorp.LGRGS")
    print("✅ Line Ranger opened!")
except:
    print("❌ Line Ranger not found. Checking installed apps...")
    # Alternative: use ADB to check installed packages
    result = ld.AdbLd("shell pm list packages | findstr line")
    print(f"Line-related packages: {result}")

print("🎉 Done!")