#!/usr/bin/env python3
"""
Complete Line Ranger Automation
1. Launch LDPlayer + Line Ranger (proven working)
2. Apply bypass if needed
3. Wait until in game
4. Use AI + OpenCV for gameplay automation
"""
import cv2
import numpy as np
import subprocess
import time
import os
import json
import base64
from datetime import datetime

class CompleteLineRangerBot:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.package = "com.linecorp.LGRGS"
        self.screenshot_path = "game_screen.png"
        
    def run_adb(self, cmd):
        try:
            full_cmd = f'"{self.adb_path}" -s {self.device} {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def run_ldconsole(self, cmd):
        try:
            full_cmd = f'cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def step1_ensure_ldplayer_running(self):
        """Step 1: Ensure LDPlayer is running"""
        print("🔄 Step 1: Checking LDPlayer status...")
        
        output, success = self.run_ldconsole("isrunning --index 0")
        if "running" in output:
            print("✅ LDPlayer already running")
            return True
        else:
            print("❌ LDPlayer not running - please start it first!")
            return False
    
    def step2_check_adb_connection(self):
        """Step 2: Check ADB connection"""
        print("🔄 Step 2: Checking ADB connection...")
        
        output, success = self.run_adb("devices")
        if "emulator-5554" in output and "device" in output:
            print("✅ ADB connected")
            return True
        else:
            print("❌ ADB not connected")
            return False
    
    def step3_launch_line_ranger(self):
        """Step 3: Launch Line Ranger if not running"""
        print("🔄 Step 3: Launching Line Ranger...")
        
        # Check if already running
        output, success = self.run_adb("shell dumpsys activity activities | findstr mResumedActivity")
        if self.package in output:
            print("✅ Line Ranger already running")
            return True
        
        # Launch Line Ranger
        self.run_ldconsole(f"runapp --index 0 --packagename {self.package}")
        print("🚀 Launch command sent, waiting...")
        
        # Wait for app to start
        for i in range(12):  # 2 minutes max
            time.sleep(10)
            output, success = self.run_adb("shell dumpsys activity activities | findstr mResumedActivity")
            if self.package in output:
                print(f"✅ Line Ranger started! ({(i+1)*10}s)")
                return True
            print(f"⏳ Waiting for Line Ranger... ({(i+1)*10}s)")
        
        print("❌ Line Ranger failed to start")
        return False
    
    def step4_wait_for_game_ready(self):
        """Step 4: Wait for game to be ready (past loading screens)"""
        print("🔄 Step 4: Waiting for game to be ready...")
        
        for i in range(18):  # 3 minutes max
            # Take screenshot to check
            self.run_adb("shell screencap -p /sdcard/check.png")
            subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/check.png", "check.png"], capture_output=True)
            
            try:
                # Check UI dump for game elements
                self.run_adb("shell uiautomator dump /sdcard/ui.xml")
                subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/ui.xml", "ui.xml"], capture_output=True)
                
                with open("ui.xml", "r", encoding="utf-8") as f:
                    ui_content = f.read()
                
                # Check for LIAPP ALERT
                if "LIAPP ALERT" in ui_content:
                    print("❌ LIAPP ALERT detected - need bypass!")
                    return False
                
                # Check for game UI elements (stage, battle, etc.)
                game_keywords = ["stage", "battle", "main", "lobby", "play", "start"]
                found_keywords = [kw for kw in game_keywords if kw.lower() in ui_content.lower()]
                
                if found_keywords:
                    print(f"✅ Game ready! Found: {found_keywords}")
                    return True
                
            except Exception as e:
                print(f"⚠️ Check error: {e}")
            
            time.sleep(10)
            print(f"⏳ Waiting for game UI... ({(i+1)*10}s)")
        
        print("❌ Game not ready after 3 minutes")
        return False
    
    def step5_opencv_analysis(self):
        """Step 5: Analyze screen with OpenCV"""
        print("🔄 Step 5: Analyzing screen with OpenCV...")
        
        # Take screenshot
        self.run_adb("shell screencap -p /sdcard/game.png")
        subprocess.run([self.adb_path, "-s", self.device, "pull", "/sdcard/game.png", self.screenshot_path], capture_output=True)
        
        img = cv2.imread(self.screenshot_path)
        if img is None:
            print("❌ Failed to load screenshot")
            return None
        
        print(f"✅ Screenshot loaded: {img.shape}")
        
        # OpenCV analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Find buttons
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < area < 80000:  # Button size range
                x, y, w, h = cv2.boundingRect(contour)
                if 0.2 < w/h < 5:  # Button aspect ratio
                    center_x, center_y = x + w//2, y + h//2
                    buttons.append({
                        "position": [center_x, center_y],
                        "size": [w, h],
                        "area": int(area)
                    })
        
        # Sort by area (largest first)
        buttons.sort(key=lambda x: x["area"], reverse=True)
        
        analysis = {
            "total_buttons": len(buttons),
            "top_buttons": buttons[:5],  # Top 5 largest buttons
            "resolution": f"{img.shape[1]}x{img.shape[0]}"
        }
        
        print(f"📊 Found {len(buttons)} buttons")
        return analysis
    
    def step6_ai_decision(self, analysis):
        """Step 6: Get AI decision for next action"""
        print("🔄 Step 6: Getting AI decision...")
        
        # Create simple context for AI
        context = f"""
Line Ranger game automation context:
- Screen resolution: {analysis['resolution']}
- Buttons detected: {analysis['total_buttons']}
- Top buttons by size: {analysis['top_buttons'][:3]}

Current task: Navigate to main stage and start a battle round.

Common Line Ranger UI elements:
- "Stage" or "스테이지" button for main stages
- "Battle" or "전투" button to start fights  
- "Start" or "시작" button to begin rounds
- Large central buttons are usually main actions

Suggest next action:
1. Which button to click (provide coordinates)
2. Or wait if loading
3. Keep response under 100 words

Top 3 button positions: {[btn['position'] for btn in analysis['top_buttons'][:3]]}
        """.strip()
        
        # Create AI interface
        with open(self.screenshot_path, "rb") as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Line Ranger AI Decision</title>
    <script src="https://js.puter.com/v2/"></script>
</head>
<body>
    <h2>🎮 Line Ranger AI Decision</h2>
    <img src="data:image/png;base64,{screenshot_base64}" style="max-width: 600px; border: 1px solid #ccc;">
    
    <h3>🔍 Analysis:</h3>
    <pre>{json.dumps(analysis, indent=2)}</pre>
    
    <h3>🤖 AI Decision:</h3>
    <div id="ai-output">Getting AI decision...</div>
    
    <script>
        const context = `{context}`;
        
        puter.ai.chat(context, {{
            model: "gpt-5-nano",
            max_tokens: 100,
            temperature: 0.3
        }}).then(response => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">' + 
                '<strong>🤖 AI Suggestion:</strong><br>' +
                response.replace(/\\n/g, '<br>') + 
                '</div>';
            
            // Extract coordinates if mentioned
            const coordMatch = response.match(/(\\d+),\\s*(\\d+)/);
            if (coordMatch) {{
                const x = parseInt(coordMatch[1]);
                const y = parseInt(coordMatch[2]);
                document.getElementById('ai-output').innerHTML += 
                    '<br><div style="background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px;">' +
                    '<strong>🎯 Suggested Click: (' + x + ', ' + y + ')</strong></div>';
            }}
        }}).catch(error => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="color: red; background: #ffebee; padding: 10px; border-radius: 5px;">Error: ' + error + '</div>';
        }});
    </script>
</body>
</html>
        """
        
        with open("ai_decision.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ AI decision interface created: ai_decision.html")
        
        # Fallback decision based on button analysis
        if analysis["top_buttons"]:
            largest_button = analysis["top_buttons"][0]
            decision = {
                "action": "click",
                "coordinates": largest_button["position"],
                "reason": f"Click largest button (area: {largest_button['area']})"
            }
        else:
            decision = {
                "action": "wait",
                "coordinates": None,
                "reason": "No clear buttons detected"
            }
        
        return decision
    
    def step7_execute_action(self, decision):
        """Step 7: Execute the decided action"""
        print(f"🔄 Step 7: Executing - {decision['reason']}")
        
        if decision["action"] == "click" and decision["coordinates"]:
            x, y = decision["coordinates"]
            self.run_adb(f"shell input tap {x} {y}")
            print(f"👆 Clicked at ({x}, {y})")
            time.sleep(3)
        else:
            print("⏳ Waiting...")
            time.sleep(5)
    
    def run_complete_automation(self):
        """Run complete automation workflow"""
        print("=" * 70)
        print("🚀 COMPLETE LINE RANGER AUTOMATION")
        print("=" * 70)
        
        # Step 1-4: Setup and launch
        if not self.step1_ensure_ldplayer_running():
            return False
        
        if not self.step2_check_adb_connection():
            return False
        
        if not self.step3_launch_line_ranger():
            return False
        
        if not self.step4_wait_for_game_ready():
            return False
        
        # Step 5-7: AI + OpenCV automation (repeat 5 times)
        print("\n🤖 Starting AI + OpenCV automation...")
        
        for cycle in range(5):
            print(f"\n🔄 Automation Cycle {cycle + 1}/5")
            
            analysis = self.step5_opencv_analysis()
            if analysis is None:
                continue
            
            decision = self.step6_ai_decision(analysis)
            self.step7_execute_action(decision)
        
        print("\n✅ Complete automation finished!")
        print("📁 Check 'ai_decision.html' for AI interface")

def main():
    bot = CompleteLineRangerBot()
    bot.run_complete_automation()

if __name__ == "__main__":
    main()