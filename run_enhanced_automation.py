#!/usr/bin/env python3
"""
Main runner for the enhanced Line Ranger automation
This version focuses on the core automation without complex testing
"""
import subprocess
import time
import os
from datetime import datetime

def print_step(step, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{step}] {message}")

def main():
    print("🚀 ENHANCED LINE RANGER AUTOMATION")
    print("=" * 50)
    
    print_step("INFO", "This automation will:")
    print_step("INFO", "1. Launch Line Ranger safely")
    print_step("INFO", "2. Detect loading screen vs lobby")
    print_step("INFO", "3. Wait for loading to complete")
    print_step("INFO", "4. Navigate to MAIN STAGE")
    print_step("INFO", "5. Click yellow round buttons")
    print_step("INFO", "6. Automate next/start buttons")
    print_step("INFO", "7. Continue gameplay automation")
    
    print("\n" + "=" * 50)
    print("📋 FILES CREATED:")
    print("✅ enhanced_safe_line_ranger_ai.py - Main automation script")
    print("✅ test_screen_detection.py - Screen detection testing")
    print("✅ simple_test.py - Simple image testing")
    print("=" * 50)
    
    choice = input("\n🎮 Run the enhanced automation now? (y/n): ").lower().strip()
    
    if choice == 'y':
        print_step("START", "Starting enhanced automation...")
        try:
            # Run the enhanced automation
            result = subprocess.run([
                "python", "enhanced_safe_line_ranger_ai.py"
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print_step("SUCCESS", "✅ Automation completed successfully!")
            else:
                print_step("ERROR", "❌ Automation encountered an error")
                
        except Exception as e:
            print_step("ERROR", f"Failed to run automation: {e}")
    else:
        print_step("INFO", "Automation not started. You can run it manually with:")
        print_step("INFO", "python enhanced_safe_line_ranger_ai.py")
    
    print("\n📁 Log files will be created:")
    print("   - line_ranger_automation_log.json (detailed action log)")
    print("   - current_screen.png (latest screenshot)")

if __name__ == "__main__":
    main()