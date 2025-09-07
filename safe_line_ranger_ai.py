#!/usr/bin/env python3
"""
Safe Line Ranger AI Automation
1. Use proven launcher to get into game safely
2. Then use OpenCV + AI for gameplay (no ADB debugging)
"""
import cv2
import numpy as np
import subprocess
import time
import os
import json
import base64
from datetime import datetime

def print_step(step, message):
    print(f"[{step}] {message}")

def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.stdout.strip(), result.returncode == 0
    except:
        return "", False

def launch_line_ranger():
    """Proven launcher code - no debugging to avoid LIAPP ALERT"""
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
            return False
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
        return False
    
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
        return False
    
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
        return False
    
    print("\n" + "=" * 50)
    print("🎮 Line Ranger should now be running!")
    print("📱 Check your LDPlayer window")
    print("=" * 50)
    return True

class SafeGameplayAI:
    """AI + OpenCV for gameplay - NO ADB debugging to stay safe"""
    
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "gameplay.png"
    
    def safe_screenshot(self):
        """Take screenshot safely - minimal ADB usage"""
        try:
            # Only use screencap - no debugging commands
            subprocess.run([
                self.adb_path, "-s", self.device, 
                "shell", "screencap", "-p", "/sdcard/game.png"
            ], capture_output=True, timeout=10)
            
            subprocess.run([
                self.adb_path, "-s", self.device, 
                "pull", "/sdcard/game.png", self.screenshot_path
            ], capture_output=True, timeout=10)
            
            img = cv2.imread(self.screenshot_path)
            if img is not None:
                print(f"📸 Screenshot: {img.shape}")
                return img
            return None
        except:
            print("❌ Screenshot failed")
            return None
    
    def analyze_gameplay_screen(self, img):
        """Analyze screen for gameplay elements"""
        analysis = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "resolution": f"{img.shape[1]}x{img.shape[0]}",
            "buttons": [],
            "colors": []
        }
        
        # Convert to different formats
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Find clickable elements (buttons)
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 3000 < area < 100000:  # Game button size
                x, y, w, h = cv2.boundingRect(contour)
                if 0.2 < w/h < 5:  # Button-like shape
                    center_x, center_y = x + w//2, y + h//2
                    analysis["buttons"].append({
                        "pos": [center_x, center_y],
                        "size": [w, h],
                        "area": int(area)
                    })
        
        # Sort buttons by size (largest first)
        analysis["buttons"].sort(key=lambda x: x["area"], reverse=True)
        analysis["buttons"] = analysis["buttons"][:8]  # Top 8 buttons
        
        # Detect important colors
        color_ranges = {
            "green": ([40, 50, 50], [80, 255, 255]),    # Start/Go buttons
            "blue": ([100, 50, 50], [130, 255, 255]),   # Info/Menu buttons  
            "red": ([0, 50, 50], [20, 255, 255]),       # Attack/Battle buttons
            "yellow": ([20, 50, 50], [40, 255, 255]),   # Rewards/Gold
            "orange": ([10, 50, 50], [25, 255, 255])    # Special buttons
        }
        
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            pixels = cv2.countNonZero(mask)
            if pixels > 8000:  # Significant presence
                analysis["colors"].append({
                    "color": color_name,
                    "pixels": int(pixels)
                })
        
        return analysis
    
    def create_ai_interface(self, analysis):
        """Create AI decision interface"""
        with open(self.screenshot_path, "rb") as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()
        
        # Create focused context for Line Ranger gameplay
        context = f"""
Line Ranger Mobile Game - Gameplay Decision:

Current Screen Analysis:
- Time: {analysis['timestamp']}
- Buttons found: {len(analysis['buttons'])}
- Colors detected: {[c['color'] for c in analysis['colors']]}
- Top 3 button positions: {[btn['pos'] for btn in analysis['buttons'][:3]]}

Line Ranger Game Context:
You are helping automate Line Ranger gameplay. Common actions:
1. "Stage" or "스테이지" - Enter main stages
2. "Battle" or "전투" - Start battles  
3. "Start" or "시작" - Begin rounds
4. Green buttons usually mean "Go/Start"
5. Red buttons usually mean "Attack/Battle"
6. Large central buttons are main actions

Current Task: Navigate to main stage and start a battle round.

Suggest ONE specific action:
- Click button at coordinates (x, y) 
- Or wait if loading screen
- Explain reasoning in 1-2 sentences

Button options: {analysis['buttons'][:3]}
        """.strip()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Line Ranger Gameplay AI</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .screenshot {{ max-width: 500px; border: 2px solid #333; border-radius: 8px; }}
        .analysis {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .ai-response {{ background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50; }}
        .button-info {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <h2>🎮 Line Ranger Gameplay AI</h2>
    
    <div>
        <h3>📸 Current Game Screen:</h3>
        <img src="data:image/png;base64,{screenshot_base64}" class="screenshot">
    </div>
    
    <div class="analysis">
        <h3>🔍 Screen Analysis:</h3>
        <strong>Time:</strong> {analysis['timestamp']}<br>
        <strong>Buttons:</strong> {len(analysis['buttons'])}<br>
        <strong>Colors:</strong> {', '.join([c['color'] for c in analysis['colors']])}<br>
        <strong>Top Buttons:</strong> {[btn['pos'] for btn in analysis['buttons'][:3]]}
    </div>
    
    <div id="ai-decision">
        <h3>🤖 AI Decision:</h3>
        <div id="ai-output">🤔 Analyzing gameplay...</div>
    </div>
    
    <script>
        const context = `{context}`;
        
        puter.ai.chat(context, {{
            model: "gpt-5-nano",
            max_tokens: 80,
            temperature: 0.2
        }}).then(response => {{
            document.getElementById('ai-output').innerHTML = 
                '<div class="ai-response">' +
                '<strong>🎯 AI Decision:</strong><br>' +
                response.replace(/\\n/g, '<br>') + 
                '</div>';
            
            // Extract coordinates
            const coordMatch = response.match(/(\\d+),\\s*(\\d+)/);
            if (coordMatch) {{
                const x = parseInt(coordMatch[1]);
                const y = parseInt(coordMatch[2]);
                document.getElementById('ai-output').innerHTML += 
                    '<div class="button-info">' +
                    '<strong>🎯 Click Target: (' + x + ', ' + y + ')</strong>' +
                    '</div>';
                window.clickTarget = {{x: x, y: y}};
            }}
        }}).catch(error => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="color: red;">❌ AI Error: ' + error + '</div>';
        }});
    </script>
</body>
</html>
        """
        
        with open("gameplay_ai.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ AI interface created: gameplay_ai.html")
    
    def safe_click(self, x, y):
        """Safe click - minimal ADB usage"""
        try:
            subprocess.run([
                self.adb_path, "-s", self.device,
                "shell", "input", "tap", str(x), str(y)
            ], capture_output=True, timeout=5)
            print(f"👆 Clicked at ({x}, {y})")
            return True
        except:
            print("❌ Click failed")
            return False
    
    def gameplay_automation_cycle(self, cycles=5):
        """Run gameplay automation cycles"""
        print("\n" + "=" * 60)
        print("🤖 STARTING SAFE GAMEPLAY AI AUTOMATION")
        print("=" * 60)
        
        for cycle in range(cycles):
            print(f"\n🔄 Gameplay Cycle {cycle + 1}/{cycles}")
            
            # Take screenshot
            img = self.safe_screenshot()
            if img is None:
                print("❌ Screenshot failed, skipping cycle")
                time.sleep(5)
                continue
            
            # Analyze screen
            analysis = self.analyze_gameplay_screen(img)
            print(f"📊 Found {len(analysis['buttons'])} buttons, colors: {[c['color'] for c in analysis['colors']]}")
            
            # Create AI interface
            self.create_ai_interface(analysis)
            
            # Simple fallback decision
            if analysis["buttons"]:
                # Click largest button
                largest_button = analysis["buttons"][0]
                x, y = largest_button["pos"]
                print(f"🎯 Clicking largest button at ({x}, {y})")
                self.safe_click(x, y)
            else:
                print("⏳ No buttons found, waiting...")
            
            # Wait before next cycle
            time.sleep(8)
        
        print("\n✅ Gameplay automation completed!")
        print("📁 Check 'gameplay_ai.html' for AI decisions")

def main():
    """Main automation workflow"""
    print("🚀 SAFE LINE RANGER AI AUTOMATION")
    print("=" * 60)
    
    # Phase 1: Launch Line Ranger safely (proven method)
    print("📱 Phase 1: Launching Line Ranger...")
    if not launch_line_ranger():
        print("❌ Failed to launch Line Ranger")
        return
    
    # Wait for game to fully load
    print("\n⏳ Waiting 30 seconds for game to fully load...")
    time.sleep(30)
    
    # Phase 2: AI + OpenCV gameplay automation
    print("\n🤖 Phase 2: Starting AI gameplay automation...")
    gameplay_ai = SafeGameplayAI()
    gameplay_ai.gameplay_automation_cycle(cycles=5)
    
    print("\n🎉 AUTOMATION COMPLETE!")
    print("📱 Line Ranger should be running with AI assistance")

if __name__ == "__main__":
    main()