#!/usr/bin/env python3
"""
Smart Line Ranger AI - Detects loading vs lobby, then automates gameplay
"""
import cv2
import numpy as np
import subprocess
import time
import os
import json
import base64
from datetime import datetime

class SmartLineRangerAI:
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "current_game.png"
        
        # Load reference images for detection
        self.loading_template = None
        self.lobby_template = None
        self.load_reference_images()
    
    def load_reference_images(self):
        """Load reference images for screen detection"""
        try:
            loading_path = "C:\\Users\\bimap\\OneDrive\\Desktop\\Ku\\ranger\\loading_awal_masuk_game.png"
            lobby_path = "C:\\Users\\bimap\\OneDrive\\Desktop\\Ku\\ranger\\lobby.png"
            
            if os.path.exists(loading_path):
                self.loading_template = cv2.imread(loading_path)
                print("✅ Loading screen template loaded")
            
            if os.path.exists(lobby_path):
                self.lobby_template = cv2.imread(lobby_path)
                print("✅ Lobby screen template loaded")
                
        except Exception as e:
            print(f"⚠️ Could not load templates: {e}")
    
    def safe_screenshot(self):
        """Take screenshot safely"""
        try:
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
                return img
            return None
        except:
            return None
    
    def detect_screen_type(self, img):
        """Detect if current screen is loading or lobby"""
        screen_type = "unknown"
        confidence = 0.0
        
        # Convert to different formats for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Method 1: Text detection for loading screen
        # Look for loading indicators
        loading_indicators = {
            "progress_bar": self.detect_progress_bar(img),
            "loading_text": self.detect_loading_text(img),
            "percentage": self.detect_percentage(img)
        }
        
        # Method 2: UI elements detection for lobby
        lobby_indicators = {
            "main_stage_button": self.detect_main_stage_button(img),
            "bottom_menu": self.detect_bottom_menu(img),
            "top_ui": self.detect_top_ui(img),
            "rangers": self.detect_rangers(img)
        }
        
        # Scoring system
        loading_score = sum([1 for indicator in loading_indicators.values() if indicator])
        lobby_score = sum([1 for indicator in lobby_indicators.values() if indicator])
        
        if loading_score >= 2:
            screen_type = "loading"
            confidence = loading_score / 3.0
        elif lobby_score >= 2:
            screen_type = "lobby"
            confidence = lobby_score / 4.0
        
        return {
            "type": screen_type,
            "confidence": confidence,
            "loading_indicators": loading_indicators,
            "lobby_indicators": lobby_indicators,
            "loading_score": loading_score,
            "lobby_score": lobby_score
        }
    
    def detect_progress_bar(self, img):
        """Detect yellow progress bar (loading screen)"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Yellow color range for progress bar
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        
        mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for horizontal bar-like shapes
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 200 and h < 50 and w/h > 5:  # Long horizontal bar
                return True
        return False
    
    def detect_loading_text(self, img):
        """Detect loading text patterns"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Look for text regions in center area
        center_y = img.shape[0] // 2
        center_region = gray[center_y-100:center_y+100, :]
        
        # Simple text detection using edge density
        edges = cv2.Canny(center_region, 50, 150)
        text_density = np.sum(edges) / edges.size
        
        return text_density > 0.02  # Threshold for text presence
    
    def detect_percentage(self, img):
        """Detect percentage indicator (loading screen)"""
        # Look for yellow text in bottom right (where percentage usually is)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Yellow text color range
        yellow_lower = np.array([20, 50, 200])
        yellow_upper = np.array([30, 255, 255])
        
        # Bottom right region
        h, w = img.shape[:2]
        bottom_right = hsv[int(h*0.8):h, int(w*0.8):w]
        
        mask = cv2.inRange(bottom_right, yellow_lower, yellow_upper)
        return np.sum(mask) > 1000
    
    def detect_main_stage_button(self, img):
        """Detect MAIN STAGE button (lobby screen)"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Look for red/brown colors of MAIN STAGE button
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([20, 255, 255])
        
        mask = cv2.inRange(hsv, red_lower, red_upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for large central button
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # Large button
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w//2
                if abs(center_x - img.shape[1]//2) < 100:  # Near center
                    return True
        return False
    
    def detect_bottom_menu(self, img):
        """Detect bottom menu bar (lobby screen)"""
        # Look for brown menu buttons at bottom
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Brown color range for menu buttons
        brown_lower = np.array([10, 50, 50])
        brown_upper = np.array([20, 255, 150])
        
        # Bottom region
        h = img.shape[0]
        bottom_region = hsv[int(h*0.7):h, :]
        
        mask = cv2.inRange(bottom_region, brown_lower, brown_upper)
        return np.sum(mask) > 15000  # Significant brown area
    
    def detect_top_ui(self, img):
        """Detect top UI elements (lobby screen)"""
        # Look for level badge and energy/gems
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Yellow color for level badge and coins
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        
        # Top region
        h = img.shape[0]
        top_region = hsv[0:int(h*0.2), :]
        
        mask = cv2.inRange(top_region, yellow_lower, yellow_upper)
        return np.sum(mask) > 5000
    
    def detect_rangers(self, img):
        """Detect ranger characters (lobby screen)"""
        # Look for circular platforms with characters
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Use HoughCircles to detect circular platforms
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 50,
            param1=50, param2=30, minRadius=20, maxRadius=80
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            return len(circles) >= 3  # At least 3 ranger platforms
        return False
    
    def wait_for_lobby(self, max_wait=300):
        """Wait for game to reach lobby screen"""
        print("⏳ Waiting for game to reach lobby...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            img = self.safe_screenshot()
            if img is None:
                time.sleep(5)
                continue
            
            detection = self.detect_screen_type(img)
            elapsed = int(time.time() - start_time)
            
            if detection["type"] == "loading":
                print(f"📱 Loading screen detected (confidence: {detection['confidence']:.2f}) - {elapsed}s")
                print(f"   Indicators: {[k for k, v in detection['loading_indicators'].items() if v]}")
                
            elif detection["type"] == "lobby":
                print(f"🎮 Lobby detected! (confidence: {detection['confidence']:.2f}) - {elapsed}s")
                print(f"   Indicators: {[k for k, v in detection['lobby_indicators'].items() if v]}")
                return True
                
            else:
                print(f"❓ Unknown screen - {elapsed}s")
            
            time.sleep(5)
        
        print("❌ Timeout waiting for lobby")
        return False
    
    def analyze_lobby_for_gameplay(self, img):
        """Analyze lobby screen for gameplay automation"""
        analysis = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "main_stage_button": None,
            "clickable_elements": []
        }
        
        # Find MAIN STAGE button specifically
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([20, 255, 255])
        mask = cv2.inRange(hsv, red_lower, red_upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # Large button
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w//2, y + h//2
                
                # Check if it's in center area (likely MAIN STAGE)
                if abs(center_x - img.shape[1]//2) < 150:
                    analysis["main_stage_button"] = {
                        "position": [center_x, center_y],
                        "size": [w, h],
                        "area": int(area)
                    }
                    break
        
        # Find other clickable elements
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < area < 50000:  # Button-like size
                x, y, w, h = cv2.boundingRect(contour)
                if 0.3 < w/h < 3:  # Button-like aspect ratio
                    center_x, center_y = x + w//2, y + h//2
                    analysis["clickable_elements"].append({
                        "position": [center_x, center_y],
                        "size": [w, h],
                        "area": int(area)
                    })
        
        # Sort by area (largest first)
        analysis["clickable_elements"].sort(key=lambda x: x["area"], reverse=True)
        analysis["clickable_elements"] = analysis["clickable_elements"][:10]
        
        return analysis
    
    def create_gameplay_ai_interface(self, analysis):
        """Create AI interface for gameplay decisions"""
        with open(self.screenshot_path, "rb") as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()
        
        context = f"""
Line Ranger Lobby - Gameplay Automation:

Current Analysis:
- Time: {analysis['timestamp']}
- Main Stage Button: {analysis['main_stage_button'] is not None}
- Clickable Elements: {len(analysis['clickable_elements'])}

MAIN STAGE Button: {analysis['main_stage_button']}
Other Elements: {analysis['clickable_elements'][:3]}

Task: Start main stage gameplay
1. Click MAIN STAGE button to enter stages
2. Then navigate through stage selection
3. Start a battle round

Suggest next action with coordinates.
        """.strip()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Line Ranger Gameplay AI</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .screenshot {{ max-width: 100%; border: 2px solid #333; border-radius: 8px; }}
        .analysis {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .ai-response {{ background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50; }}
        .button-target {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎮 Line Ranger Gameplay AI</h2>
        
        <div>
            <h3>📸 Current Lobby Screen:</h3>
            <img src="data:image/png;base64,{screenshot_base64}" class="screenshot">
        </div>
        
        <div class="analysis">
            <h3>🔍 Lobby Analysis:</h3>
            <strong>Time:</strong> {analysis['timestamp']}<br>
            <strong>Main Stage Button Found:</strong> {'✅ Yes' if analysis['main_stage_button'] else '❌ No'}<br>
            <strong>Clickable Elements:</strong> {len(analysis['clickable_elements'])}<br>
            {f"<strong>Main Stage Position:</strong> {analysis['main_stage_button']['position']}<br>" if analysis['main_stage_button'] else ""}
        </div>
        
        <div id="ai-decision">
            <h3>🤖 AI Gameplay Decision:</h3>
            <div id="ai-output">🎯 Analyzing lobby for next action...</div>
        </div>
    </div>
    
    <script>
        const context = `{context}`;
        
        puter.ai.chat(context, {{
            model: "gpt-5-nano",
            max_tokens: 60,
            temperature: 0.1
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
                    '<div class="button-target">' +
                    '<strong>🎯 Target: (' + x + ', ' + y + ')</strong>' +
                    '</div>';
            }}
        }}).catch(error => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="color: red;">❌ AI Error: ' + error + '</div>';
        }});
    </script>
</body>
</html>
        """
        
        with open("lobby_ai.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ Lobby AI interface created: lobby_ai.html")
    
    def safe_click(self, x, y):
        """Safe click"""
        try:
            subprocess.run([
                self.adb_path, "-s", self.device,
                "shell", "input", "tap", str(x), str(y)
            ], capture_output=True, timeout=5)
            print(f"👆 Clicked at ({x}, {y})")
            return True
        except:
            return False
    
    def run_smart_automation(self):
        """Run complete smart automation"""
        print("=" * 70)
        print("🧠 SMART LINE RANGER AI AUTOMATION")
        print("=" * 70)
        
        # Phase 1: Wait for lobby
        if not self.wait_for_lobby():
            print("❌ Could not reach lobby")
            return
        
        # Phase 2: Lobby gameplay automation
        print("\n🎮 Starting lobby gameplay automation...")
        
        for cycle in range(10):
            print(f"\n🔄 Gameplay Cycle {cycle + 1}/10")
            
            img = self.safe_screenshot()
            if img is None:
                print("❌ Screenshot failed")
                time.sleep(5)
                continue
            
            # Check if still in lobby or moved to other screen
            detection = self.detect_screen_type(img)
            print(f"📱 Screen: {detection['type']} (confidence: {detection['confidence']:.2f})")
            
            if detection["type"] == "lobby":
                # Analyze lobby for gameplay
                analysis = self.analyze_lobby_for_gameplay(img)
                self.create_gameplay_ai_interface(analysis)
                
                # Execute action
                if analysis["main_stage_button"]:
                    x, y = analysis["main_stage_button"]["position"]
                    print(f"🎯 Clicking MAIN STAGE at ({x}, {y})")
                    self.safe_click(x, y)
                elif analysis["clickable_elements"]:
                    largest = analysis["clickable_elements"][0]
                    x, y = largest["position"]
                    print(f"🎯 Clicking largest element at ({x}, {y})")
                    self.safe_click(x, y)
                else:
                    print("⏳ No clear targets, waiting...")
            
            elif detection["type"] == "loading":
                print("⏳ Loading screen, waiting...")
            
            else:
                print("❓ Unknown screen, trying center click")
                self.safe_click(640, 360)
            
            time.sleep(8)
        
        print("\n✅ Smart automation completed!")

def main():
    ai = SmartLineRangerAI()
    ai.run_smart_automation()

if __name__ == "__main__":
    main()