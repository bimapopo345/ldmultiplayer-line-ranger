#!/usr/bin/env python3
import time
from CBAutoHelper import LDPlayer

def auto_open_line_ranger():
    print("=== Auto Open Line Ranger ===")
    
    try:
        # Initialize LDPlayer
        ld = LDPlayer()
        
        # Get devices
        devices = ld.GetDevices2()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device['name']} (index: {device['index']})")
        
        # Find LDPlayer device
        ldplayer_device = None
        for device in devices:
            if device['name'] == 'LDPlayer':
                ldplayer_device = device
                break
        
        if not ldplayer_device:
            print("❌ Device 'LDPlayer' not found!")
            return
        
        print(f"✅ Selected device: {ldplayer_device['name']}")
        
        # Set device info
        ld.Info('name', ldplayer_device['name'])
        
        # Check if already running
        if ld.IsDevice_Running():
            print("📱 LDPlayer already running")
        else:
            print("🚀 Starting LDPlayer...")
            ld.Start()
            print("⏳ Waiting for LDPlayer to start...")
            time.sleep(10)  # Wait for LDPlayer to fully start
        
        # Open Line Ranger
        print("🎮 Opening Line Ranger...")
        
        # Try different package names for Line Ranger
        line_ranger_packages = [
            "com.linecorp.LGRGS",  # Line Rangers Global
            "jp.naver.LGRJP",      # Line Rangers Japan
            "com.linecorp.LGRKR",  # Line Rangers Korea
            "com.nhnent.SKLINELGR" # Line Rangers (alternative)
        ]
        
        for package in line_ranger_packages:
            try:
                print(f"Trying package: {package}")
                ld.OpenApp(package)
                print(f"✅ Successfully opened Line Ranger with package: {package}")
                break
            except Exception as e:
                print(f"Failed with {package}: {e}")
                continue
        else:
            print("❌ Could not open Line Ranger with any known package name")
            print("💡 You may need to install Line Ranger first or check the package name")
        
        print("🎉 Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    auto_open_line_ranger()