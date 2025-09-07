#!/usr/bin/env python3
"""
Line Ranger AI + OpenCV Integration
AI-powered automation that learns from screenshots
"""
import cv2
import numpy as np
import subprocess
import time
import os
import json
import base64
from datetime import datetime

class LineRangerAI:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "current_screen.png"
        self.ai_decisions_log = "ai_decisions.json"
        self.context_limit = 4500  # Keep under 5000 tokens
        
    def run_adb(self, cmd):
        """Execute ADB command"""
        try:
            full_cmd = f'"{self.adb_path}" -s {self.device} {cmd}'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def take_screenshot(self):
        """Take screenshot and return OpenCV image"""
        print("📸 Taking screenshot...")
        
        self.run_adb("shell screencap -p /sdcard/screenshot.png")
        subprocess.run([
            self.adb_path, "-s", self.device, 
            "pull", "/sdcard/screenshot.png", self.screenshot_path
        ], capture_output=True)
        
        img = cv2.imread(self.screenshot_path)
        if img is not None:
            print(f"✅ Screenshot: {img.shape}")
            return img
        return None
    
    def analyze_screen_opencv(self, img):
        """Analyze screen using OpenCV"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "resolution": f"{img.shape[1]}x{img.shape[0]}",
            "elements": []
        }
        
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Detect buttons using edge detection
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 50000:  # Button-like size
                x, y, w, h = cv2.boundingRect(contour)
                if 0.3 < w/h < 3:  # Button aspect ratio
                    center_x, center_y = x + w//2, y + h//2
                    buttons.append({
                        "type": "button",
                        "position": [center_x, center_y],
                        "size": [w, h],
                        "area": int(area)
                    })
        
        # Detect colors
        color_ranges = {
            "blue": ([100, 50, 50], [130, 255, 255]),
            "green": ([40, 50, 50], [80, 255, 255]),
            "red": ([0, 50, 50], [20, 255, 255]),
            "yellow": ([20, 50, 50], [40, 255, 255])
        }
        
        dominant_colors = []
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            pixels = cv2.countNonZero(mask)
            if pixels > 5000:  # Significant presence
                dominant_colors.append({
                    "color": color_name,
                    "pixels": int(pixels)
                })
        
        analysis["elements"] = buttons[:10]  # Limit to 10 buttons
        analysis["colors"] = dominant_colors[:5]  # Top 5 colors
        analysis["total_buttons"] = len(buttons)
        
        return analysis
    
    def create_ai_web_interface(self, analysis, screenshot_base64):
        """Create HTML interface for AI analysis"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Line Ranger AI Analysis</title>
    <script src="https://js.puter.com/v2/"></script>
</head>
<body>
    <h2>🎮 Line Ranger AI Analysis</h2>
    
    <div id="screenshot">
        <h3>📸 Current Screenshot:</h3>
        <img src="data:image/png;base64,{screenshot_base64}" style="max-width: 400px; border: 1px solid #ccc;">
    </div>
    
    <div id="analysis">
        <h3>🔍 OpenCV Analysis:</h3>
        <pre>{json.dumps(analysis, indent=2)}</pre>
    </div>
    
    <div id="ai-response">
        <h3>🤖 AI Decision:</h3>
        <div id="ai-output">Analyzing...</div>
    </div>
    
    <script>
        // Prepare context for AI (keep under 5000 tokens)
        const context = `
Line Ranger Game Analysis:
- Resolution: {analysis.get('resolution', 'unknown')}
- Buttons detected: {analysis.get('total_buttons', 0)}
- Colors: {', '.join([c['color'] for c in analysis.get('colors', [])])}
- Elements: {len(analysis.get('elements', []))} interactive elements

Current screen shows a mobile game interface. Analyze and suggest next action.
Rules:
1. If you see buttons, suggest which to click
2. If loading screen, suggest wait
3. If popup/dialog, suggest dismiss
4. Keep response under 200 words
5. Provide specific coordinates if possible

Elements found: {json.dumps(analysis.get('elements', [])[:3])}
        `.trim();
        
        // Call AI for decision
        puter.ai.chat(context, {{
            model: "gpt-5-nano",
            max_tokens: 150,
            temperature: 0.3
        }}).then(response => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="background: #f0f8ff; padding: 10px; border-radius: 5px;">' + 
                response.replace(/\\n/g, '<br>') + 
                '</div>';
            
            // Save decision to parent process
            window.aiDecision = response;
            
            // Try to extract coordinates from AI response
            const coordMatch = response.match(/\\((\\d+),\\s*(\\d+)\\)/);
            if (coordMatch) {{
                const x = parseInt(coordMatch[1]);
                const y = parseInt(coordMatch[2]);
                document.getElementById('ai-output').innerHTML += 
                    '<br><strong>🎯 Suggested click: (' + x + ', ' + y + ')</strong>';
                window.suggestedClick = {{x: x, y: y}};
            }}
        }}).catch(error => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="color: red;">Error: ' + error + '</div>';
        }});
    </script>
</body>
</html>
        """
        
        return html_content
    
    def get_ai_decision(self, analysis):
        """Get AI decision using web interface"""
        print("🤖 Getting AI decision...")
        
        # Convert screenshot to base64
        with open(self.screenshot_path, "rb") as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()
        
        # Create HTML file
        html_content = self.create_ai_web_interface(analysis, screenshot_base64)
        
        with open("ai_analysis.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ AI analysis interface created: ai_analysis.html")
        print("🌐 Open ai_analysis.html in browser to see AI decision")
        
        # Simulate AI decision for automation (fallback)
        fallback_decision = self.create_fallback_decision(analysis)
        return fallback_decision
    
    def create_fallback_decision(self, analysis):
        """Create fallback decision based on OpenCV analysis"""
        decision = {
            "action": "wait",
            "reason": "No clear action detected",
            "confidence": 0.5,
            "coordinates": None
        }
        
        # Simple rule-based decisions
        if analysis["total_buttons"] > 0:
            # Click on largest button
            largest_button = max(analysis["elements"], key=lambda x: x["area"])
            decision = {
                "action": "click",
                "reason": f"Click largest button (area: {largest_button['area']})",
                "confidence": 0.8,
                "coordinates": largest_button["position"]
            }
        
        elif any(color["color"] == "green" for color in analysis["colors"]):
            # Green usually means "go" or "start"
            decision = {
                "action": "click",
                "reason": "Green color detected - likely start/go button",
                "confidence": 0.7,
                "coordinates": [640, 360]  # Center screen
            }
        
        return decision
    
    def execute_decision(self, decision):
        """Execute AI decision"""
        print(f"🎯 Executing: {decision['action']} - {decision['reason']}")
        
        if decision["action"] == "click" and decision["coordinates"]:
            x, y = decision["coordinates"]
            self.run_adb(f"shell input tap {x} {y}")
            print(f"👆 Clicked at ({x}, {y})")
            
        elif decision["action"] == "wait":
            print("⏳ Waiting...")
            time.sleep(3)
        
        # Log decision
        self.log_decision(decision)
    
    def log_decision(self, decision):
        """Log AI decision for learning"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        }
        
        try:
            if os.path.exists(self.ai_decisions_log):
                with open(self.ai_decisions_log, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 50 decisions to manage file size
            logs = logs[-50:]
            
            with open(self.ai_decisions_log, "w") as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"❌ Logging error: {e}")
    
    def run_ai_automation_cycle(self, cycles=5):
        """Run AI automation cycle"""
        print("=" * 60)
        print("🤖 LINE RANGER AI + OPENCV AUTOMATION")
        print("=" * 60)
        
        for cycle in range(cycles):
            print(f"\n🔄 Cycle {cycle + 1}/{cycles}")
            
            # Take screenshot
            img = self.take_screenshot()
            if img is None:
                print("❌ Failed to take screenshot")
                continue
            
            # Analyze with OpenCV
            analysis = self.analyze_screen_opencv(img)
            print(f"📊 Found {analysis['total_buttons']} buttons, {len(analysis['colors'])} colors")
            
            # Get AI decision
            decision = self.get_ai_decision(analysis)
            
            # Execute decision
            self.execute_decision(decision)
            
            # Wait before next cycle
            time.sleep(5)
        
        print("\n✅ AI automation cycle completed!")
        print("📁 Check 'ai_analysis.html' for AI interface")
        print("📁 Check 'ai_decisions.json' for decision log")

def main():
    ai_automation = LineRangerAI()
    ai_automation.run_ai_automation_cycle(cycles=3)

if __name__ == "__main__":
    main()