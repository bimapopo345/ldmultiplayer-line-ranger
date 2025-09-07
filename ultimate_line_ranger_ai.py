#!/usr/bin/env python3
"""
Ultimate Line Ranger AI - Gabungan smart detection + Puter AI
1. Smart check LDPlayer/Line Ranger status
2. Deteksi loading vs lobby dengan akurat
3. Gunakan Puter AI untuk gameplay decisions
4. Log semua aksi dengan detail
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
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{step}] {message}")

def log_action(action, details=""):
    """Log semua aksi dengan timestamp"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details
    }
    
    log_file = "ultimate_automation_log.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except:
        pass
    
    print_step("LOG", f"{action}: {details}")

def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.stdout.strip(), result.returncode == 0
    except:
        return "", False

def check_ldplayer_status():
    """Cek apakah LDPlayer sudah jalan"""
    print_step("CHECK", "Mengecek status LDPlayer...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe isrunning --index 0')
    
    if "running" in output and success:
        print_step("CHECK", "✅ LDPlayer sudah jalan!")
        log_action("LDPLAYER_STATUS", "Already running")
        return True
    else:
        print_step("CHECK", "❌ LDPlayer belum jalan")
        log_action("LDPLAYER_STATUS", "Not running")
        return False

def start_ldplayer():
    """Start LDPlayer jika belum jalan"""
    print_step("START", "Memulai LDPlayer...")
    run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe launch --index 0')
    
    for i in range(18):  # 3 menit max
        time.sleep(10)
        output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe isrunning --index 0')
        if "running" in output:
            print_step("START", f"✅ LDPlayer berhasil dimulai! ({(i+1)*10}s)")
            log_action("LDPLAYER_STARTED", f"Started in {(i+1)*10}s")
            return True
        print_step("START", f"⏳ Menunggu LDPlayer... ({(i+1)*10}s)")
    
    print_step("START", "❌ LDPlayer gagal dimulai!")
    return False

def check_adb_connection():
    """Cek koneksi ADB"""
    print_step("ADB", "Mengecek koneksi ADB...")
    for i in range(18):  # 3 menit max
        output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe devices')
        if "emulator-5554" in output and "device" in output:
            print_step("ADB", f"✅ ADB terhubung! ({(i+1)*10}s)")
            log_action("ADB_CONNECTED", f"Connected in {(i+1)*10}s")
            return True
        time.sleep(10)
        print_step("ADB", f"⏳ Menunggu ADB... ({(i+1)*10}s)")
    
    print_step("ADB", "❌ ADB gagal terhubung!")
    return False

def check_android_ready():
    """Cek Android sudah siap"""
    print_step("ANDROID", "Mengecek sistem Android...")
    for i in range(18):  # 3 menit max
        output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell getprop sys.boot_completed')
        if "1" in output:
            print_step("ANDROID", f"✅ Android siap! ({(i+1)*10}s)")
            log_action("ANDROID_READY", f"Ready in {(i+1)*10}s")
            return True
        time.sleep(10)
        print_step("ANDROID", f"⏳ Menunggu Android... ({(i+1)*10}s)")
    
    print_step("ANDROID", "❌ Android gagal siap!")
    return False

def check_line_ranger_running():
    """Cek apakah Line Ranger sudah jalan"""
    print_step("GAME", "Mengecek apakah Line Ranger sudah jalan...")
    
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && adb.exe -s emulator-5554 shell "ps | grep line"')
    
    if "linecorp" in output.lower() or "lgrgs" in output.lower():
        print_step("GAME", "✅ Line Ranger sudah jalan!")
        log_action("GAME_STATUS", "Already running")
        return True
    else:
        print_step("GAME", "❌ Line Ranger belum jalan")
        log_action("GAME_STATUS", "Not running")
        return False

def launch_line_ranger():
    """Launch Line Ranger"""
    print_step("LAUNCH", "Meluncurkan Line Ranger...")
    output, success = run_cmd('cd "C:\\LDPlayer\\LDPlayer9" && ldconsole.exe runapp --index 0 --packagename com.linecorp.LGRGS')
    
    if success:
        print_step("LAUNCH", "✅ Line Ranger diluncurkan!")
        log_action("GAME_LAUNCHED", "Line Ranger started")
        print_step("LAUNCH", "⏳ Menunggu game memuat...")
        time.sleep(20)
        return True
    else:
        print_step("LAUNCH", "❌ Gagal meluncurkan Line Ranger!")
        return False

class UltimateGameplayAI:
    """Ultimate AI dengan smart detection + Puter AI"""
    
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "ultimate_screen.png"
        
    def safe_screenshot(self):
        """Ambil screenshot dengan aman"""
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
                print_step("SCREENSHOT", f"Screenshot berhasil: {img.shape}")
                return img
            return None
        except Exception as e:
            print_step("ERROR", f"Screenshot gagal: {e}")
            return None
    
    def detect_screen_type(self, img):
        """Deteksi jenis layar - loading atau lobby dengan akurasi tinggi"""
        if img is None:
            return "unknown", {}
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Deteksi progress bar kuning (loading screen)
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        
        # Deteksi background ungu/biru (loading screen)
        purple_lower = np.array([120, 50, 50])
        purple_upper = np.array([150, 255, 255])
        purple_mask = cv2.inRange(hsv, purple_lower, purple_upper)
        purple_pixels = cv2.countNonZero(purple_mask)
        
        # Deteksi UI coklat/orange (lobby screen)
        brown_lower = np.array([10, 100, 50])
        brown_upper = np.array([20, 255, 200])
        brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
        brown_pixels = cv2.countNonZero(brown_mask)
        
        # Deteksi platform karakter (lobby)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=20, maxRadius=100)
        circle_count = len(circles[0]) if circles is not None else 0
        
        # Deteksi MAIN STAGE button (lobby indicator yang kuat)
        height, width = img.shape[:2]
        center_region = img[height//3:2*height//3, width//3:2*width//3]
        center_hsv = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
        center_brown_mask = cv2.inRange(center_hsv, np.array([10, 100, 50]), np.array([20, 255, 200]))
        center_brown_pixels = cv2.countNonZero(center_brown_mask)
        
        # Logic deteksi yang diperbaiki
        if center_brown_pixels > 5000 and brown_pixels > 15000:
            screen_type = "lobby"
            confidence = "high"
        elif yellow_pixels > 5000 and purple_pixels > 50000:
            screen_type = "loading"
            confidence = "high"
        elif brown_pixels > 20000 and circle_count >= 3:
            screen_type = "lobby" 
            confidence = "high"
        elif brown_pixels > 10000:
            screen_type = "lobby"
            confidence = "medium"
        elif purple_pixels > 30000:
            screen_type = "loading"
            confidence = "medium"
        else:
            screen_type = "unknown"
            confidence = "low"
        
        detection_info = {
            "screen_type": screen_type,
            "confidence": confidence,
            "yellow_pixels": int(yellow_pixels),
            "purple_pixels": int(purple_pixels), 
            "brown_pixels": int(brown_pixels),
            "center_brown_pixels": int(center_brown_pixels),
            "circles_detected": circle_count
        }
        
        log_action("SCREEN_DETECTED", f"{screen_type} ({confidence})")
        print_step("DETECT", f"Layar: {screen_type} ({confidence}) - Kuning:{yellow_pixels}, Ungu:{purple_pixels}, Coklat:{brown_pixels}")
        
        return screen_type, detection_info
    
    def analyze_gameplay_screen(self, img):
        """Analyze screen untuk gameplay elements"""
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
    
    def create_puter_ai_interface(self, analysis, screen_type):
        """Create Puter AI interface untuk gameplay decisions"""
        with open(self.screenshot_path, "rb") as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()
        
        # Create context berdasarkan screen type
        if screen_type == "lobby":
            context = f"""
Line Ranger Mobile Game - Expert Gameplay Guide:

GAME KNOWLEDGE:
Line Ranger is a tower defense game where you place ranger characters to defend against enemies.

LOBBY SCREEN FLOW:
1. MAIN STAGE (red/brown button in center) - Click this to enter stages
2. Avoid QUEST button (usually on right side)
3. Look for stage numbers (yellow circular buttons with numbers like 1, 2, 3)
4. After selecting stage, click START button
5. Then place available rangers on battlefield

CURRENT SCREEN ANALYSIS:
- Time: {analysis['timestamp']}
- Screen Type: LOBBY
- Buttons found: {len(analysis['buttons'])}
- Colors detected: {[c['color'] for c in analysis['colors']]}
- Top 3 button positions: {[btn['pos'] for btn in analysis['buttons'][:3]]}

PRIORITY ACTIONS:
1. If you see "MAIN STAGE" button (large, central, red/brown) - CLICK IT
2. If you see yellow circular stage numbers (1, 2, 3, etc) - CLICK the lowest available number
3. If you see "START" button (green/blue) - CLICK IT
4. AVOID clicking "QUEST" or "GACHA" buttons

Current Task: Navigate through Line Ranger gameplay flow.
Suggest ONE specific action with coordinates (x, y) and explain why.

Available buttons: {analysis['buttons'][:3]}
            """.strip()
        else:
            context = f"""
Line Ranger Game Screen - Advanced Gameplay Guide:

GAME FLOW KNOWLEDGE:
1. STAGE SELECTION: Look for yellow circular buttons with numbers (1, 2, 3, etc)
2. BATTLE PREPARATION: After selecting stage, click START button
3. RANGER PLACEMENT: Drag/click rangers onto battlefield slots
4. BATTLE: Use skills, auto-battle, or manual control
5. RESULTS: Click NEXT or CONTINUE after victory

CURRENT SCREEN ANALYSIS:
- Time: {analysis['timestamp']}
- Screen Type: {screen_type.upper()}
- Buttons found: {len(analysis['buttons'])}
- Colors detected: {[c['color'] for c in analysis['colors']]}
- Top 3 button positions: {[btn['pos'] for btn in analysis['buttons'][:3]]}

SMART ACTIONS:
1. If you see yellow circular stage numbers - CLICK the lowest unlocked number
2. If you see "START" or "시작" button (green/blue) - CLICK IT
3. If you see ranger characters at bottom - CLICK and drag to battlefield
4. If you see "NEXT" or "다음" button - CLICK IT to continue
5. If you see skill buttons during battle - USE THEM strategically
6. If you see "AUTO" button - CLICK IT for automatic battle

AVOID:
- Don't click "BACK" or "뒤로" unless stuck
- Don't click "QUEST" or "퀘스트" buttons
- Don't click "SHOP" or "상점" during gameplay

Current Task: Progress through Line Ranger stages efficiently.
Suggest ONE specific action with coordinates (x, y) and explain the reasoning.

Available buttons: {analysis['buttons'][:3]}
            """.strip()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Ultimate Line Ranger AI</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f0f8ff; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .screenshot {{ max-width: 100%; border: 3px solid #333; border-radius: 10px; }}
        .analysis {{ background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 15px 0; }}
        .ai-response {{ background: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 5px solid #4caf50; }}
        .button-target {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 5px solid #ffc107; }}
        .screen-type {{ background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎮 Ultimate Line Ranger AI</h2>
        
        <div class="screen-type">
            📱 Screen Type: {screen_type.upper()}
        </div>
        
        <div>
            <h3>📸 Current Game Screen:</h3>
            <img src="data:image/png;base64,{screenshot_base64}" class="screenshot">
        </div>
        
        <div class="analysis">
            <h3>🔍 Screen Analysis:</h3>
            <strong>Time:</strong> {analysis['timestamp']}<br>
            <strong>Resolution:</strong> {analysis['resolution']}<br>
            <strong>Buttons Found:</strong> {len(analysis['buttons'])}<br>
            <strong>Colors Detected:</strong> {', '.join([c['color'] for c in analysis['colors']])}<br>
            <strong>Top Button Positions:</strong> {[btn['pos'] for btn in analysis['buttons'][:3]]}
        </div>
        
        <div id="ai-decision">
            <h3>🤖 Puter AI Decision:</h3>
            <div id="ai-output">🧠 Analyzing with Puter AI...</div>
        </div>
    </div>
    
    <script>
        const context = `{context}`;
        
        puter.ai.chat(context, {{
            model: "gpt-5-nano",
            max_tokens: 100,
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
                    '<strong>🎯 AI Target: (' + x + ', ' + y + ')</strong><br>' +
                    '<em>Click coordinates determined by Puter AI</em>' +
                    '</div>';
                window.aiTarget = {{x: x, y: y}};
            }}
        }}).catch(error => {{
            document.getElementById('ai-output').innerHTML = 
                '<div style="color: red;">❌ Puter AI Error: ' + error + '</div>';
        }});
    </script>
</body>
</html>
        """
        
        with open("ultimate_ai.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print_step("AI", "✅ Puter AI interface created: ultimate_ai.html")
        log_action("AI_INTERFACE_CREATED", f"Screen type: {screen_type}")
    
    def safe_click(self, x, y):
        """Safe click dengan logging"""
        try:
            subprocess.run([
                self.adb_path, "-s", self.device,
                "shell", "input", "tap", str(x), str(y)
            ], capture_output=True, timeout=5)
            log_action("CLICK", f"Klik di ({x}, {y})")
            print_step("CLICK", f"👆 Klik di ({x}, {y})")
            return True
        except:
            print_step("ERROR", "Klik gagal")
            return False
    
    def find_yellow_stage_numbers(self, img):
        """Cari tombol stage numbers kuning (1, 2, 3, etc)"""
        if img is None:
            return []
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Look for yellow/gold stage buttons
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        # Find contours of yellow areas
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        stage_buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 15000:  # Stage button size
                x, y, w, h = cv2.boundingRect(contour)
                # Check if it's roughly circular (stage numbers are usually circular)
                aspect_ratio = w / h
                if 0.7 < aspect_ratio < 1.3:  # Roughly square/circular
                    center_x, center_y = x + w//2, y + h//2
                    stage_buttons.append((center_x, center_y))
        
        # Sort by position (left to right, top to bottom)
        stage_buttons.sort(key=lambda pos: (pos[1], pos[0]))
        
        if stage_buttons:
            print_step("DETECT", f"Found {len(stage_buttons)} yellow stage buttons")
            log_action("STAGE_BUTTONS_FOUND", f"Count: {len(stage_buttons)}")
        
        return stage_buttons
    
    def find_start_button(self, img):
        """Cari tombol START/GO"""
        if img is None:
            return None
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Look for green START buttons
        green_lower = np.array([40, 50, 50])
        green_upper = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 3000 < area < 50000:  # Button size
                x, y, w, h = cv2.boundingRect(contour)
                if 0.3 < w/h < 3:  # Button-like aspect ratio
                    center_x, center_y = x + w//2, y + h//2
                    print_step("DETECT", f"Found START button at ({center_x}, {center_y})")
                    return (center_x, center_y)
        
        return None
    
    def find_main_stage_button(self, img):
        """Cari tombol MAIN STAGE secara spesifik"""
        if img is None:
            return None
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        height, width = img.shape[:2]
        
        # Look for red/brown MAIN STAGE button
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([20, 255, 255])
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 8000 < area < 50000:  # MAIN STAGE button size
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w//2, y + h//2
                
                # MAIN STAGE should be in center area, avoid shop/feather area
                if (width * 0.3 < center_x < width * 0.7 and  # Center horizontally
                    height * 0.25 < center_y < height * 0.6):  # Upper-center vertically
                    
                    print_step("DETECT", f"Found MAIN STAGE button at ({center_x}, {center_y})")
                    log_action("MAIN_STAGE_FOUND", f"Position: ({center_x}, {center_y})")
                    return (center_x, center_y)
        
        return None
    
    def wait_for_lobby(self, max_wait=120):
        """Tunggu loading selesai sampai lobby"""
        print_step("WAIT", "Menunggu loading selesai...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            img = self.safe_screenshot()
            if img is not None:
                screen_type, info = self.detect_screen_type(img)
                
                if screen_type == "lobby":
                    elapsed = int(time.time() - start_time)
                    log_action("LOBBY_REACHED", f"Loading selesai dalam {elapsed}s")
                    print_step("SUCCESS", f"🎉 Sampai di lobby! ({elapsed}s)")
                    return True
                elif screen_type == "loading":
                    elapsed = int(time.time() - start_time)
                    print_step("WAIT", f"Masih loading... ({elapsed}s)")
                else:
                    elapsed = int(time.time() - start_time)
                    print_step("WAIT", f"Layar tidak dikenal, lanjut... ({elapsed}s)")
            
            time.sleep(5)
        
        print_step("TIMEOUT", "❌ Timeout menunggu lobby!")
        return False
    
    def run_ultimate_automation(self, cycles=10):
        """Run ultimate automation dengan Puter AI"""
        print_step("AUTO", "Memulai Ultimate Automation dengan Puter AI...")
        
        for cycle in range(cycles):
            print_step("CYCLE", f"🔄 Automation Cycle {cycle + 1}/{cycles}")
            
            # Take screenshot
            img = self.safe_screenshot()
            if img is None:
                print_step("ERROR", "Screenshot gagal, skip cycle")
                time.sleep(5)
                continue
            
            # Detect screen type
            screen_type, detection_info = self.detect_screen_type(img)
            
            # Analyze screen for gameplay
            analysis = self.analyze_gameplay_screen(img)
            print_step("ANALYSIS", f"Found {len(analysis['buttons'])} buttons, colors: {[c['color'] for c in analysis['colors']]}")
            
            # Create Puter AI interface
            self.create_puter_ai_interface(analysis, screen_type)
            
            # Execute action based on screen type and analysis
            if screen_type == "lobby":
                # Smart lobby actions
                # 1. Look for MAIN STAGE button first (avoid shop/feather area)
                main_stage_found = False
                height, width = img.shape[:2]
                
                # Define safe MAIN STAGE area (center, avoid top-right shop area)
                safe_center_x = width // 2
                safe_center_y = height // 2 - 50  # Slightly above center
                
                for button in analysis["buttons"]:
                    x, y = button["pos"]
                    # MAIN STAGE should be in center area, NOT in top-right (shop/feather area)
                    if (abs(x - safe_center_x) < 150 and 
                        abs(y - safe_center_y) < 100 and 
                        x < width * 0.8 and  # Avoid right side (shop area)
                        y > height * 0.2):   # Avoid top area (UI elements)
                        
                        print_step("ACTION", f"Klik MAIN STAGE button di ({x}, {y}) - area aman")
                        self.safe_click(x, y)
                        main_stage_found = True
                        break
                
                # 2. Use specific MAIN STAGE detection if general detection failed
                if not main_stage_found:
                    main_stage_pos = self.find_main_stage_button(img)
                    if main_stage_pos:
                        x, y = main_stage_pos
                        print_step("ACTION", f"Klik MAIN STAGE (deteksi spesifik) di ({x}, {y})")
                        self.safe_click(x, y)
                        main_stage_found = True
                
                # 3. Look for yellow stage numbers if MAIN STAGE still not found
                if not main_stage_found:
                    yellow_stages = self.find_yellow_stage_numbers(img)
                    if yellow_stages:
                        # Click first available stage
                        x, y = yellow_stages[0]
                        print_step("ACTION", f"Klik stage number kuning di ({x}, {y})")
                        self.safe_click(x, y)
                    else:
                        # Safe fallback - click known MAIN STAGE area, avoid shop
                        height, width = img.shape[:2]
                        safe_x = width // 2
                        safe_y = height // 2 - 80  # Above center, where MAIN STAGE usually is
                        print_step("ACTION", f"Klik area MAIN STAGE aman di ({safe_x}, {safe_y})")
                        self.safe_click(safe_x, safe_y)
                    
            elif screen_type == "loading":
                print_step("WAIT", "Loading screen detected, menunggu...")
                time.sleep(3)
                continue
                
            else:
                # Smart actions for other screens (stage selection, battle, etc)
                action_taken = False
                
                # 1. Look for yellow stage numbers first
                yellow_stages = self.find_yellow_stage_numbers(img)
                if yellow_stages and not action_taken:
                    x, y = yellow_stages[0]  # Click first stage
                    print_step("ACTION", f"Klik stage number kuning di ({x}, {y})")
                    self.safe_click(x, y)
                    action_taken = True
                
                # 2. Look for START button
                if not action_taken:
                    start_button = self.find_start_button(img)
                    if start_button:
                        x, y = start_button
                        print_step("ACTION", f"Klik START button di ({x}, {y})")
                        self.safe_click(x, y)
                        action_taken = True
                
                # 3. Look for green buttons (START/GO/NEXT)
                if not action_taken:
                    for color_info in analysis["colors"]:
                        if color_info["color"] == "green" and color_info["pixels"] > 10000:
                            # Find green button position
                            for button in analysis["buttons"][:3]:
                                x, y = button["pos"]
                                print_step("ACTION", f"Klik tombol hijau (START/NEXT) di ({x}, {y})")
                                self.safe_click(x, y)
                                action_taken = True
                                break
                            break
                
                # 4. Fallback to largest button (avoid small UI elements)
                if not action_taken and analysis["buttons"]:
                    # Filter out small buttons (likely UI elements)
                    large_buttons = [btn for btn in analysis["buttons"] if btn["area"] > 5000]
                    if large_buttons:
                        largest_button = large_buttons[0]
                        x, y = largest_button["pos"]
                        print_step("ACTION", f"Klik tombol besar di ({x}, {y})")
                        self.safe_click(x, y)
                        action_taken = True
                
                # 5. Last resort - click center
                if not action_taken:
                    height, width = img.shape[:2]
                    center_x, center_y = width // 2, height // 2
                    print_step("ACTION", f"Klik tengah layar di ({center_x}, {center_y})")
                    self.safe_click(center_x, center_y)
            
            # Wait before next cycle
            time.sleep(8)
        
        log_action("AUTOMATION_COMPLETE", f"Ultimate automation selesai ({cycles} cycles)")
        print_step("COMPLETE", "✅ Ultimate automation selesai!")

def main():
    """Main automation workflow yang ultimate"""
    print("🚀 ULTIMATE LINE RANGER AI AUTOMATION")
    print("=" * 70)
    
    # Step 1: Smart system checks
    if not check_ldplayer_status():
        if not start_ldplayer():
            print_step("ERROR", "❌ Gagal memulai LDPlayer")
            return
    
    if not check_adb_connection():
        print_step("ERROR", "❌ Gagal koneksi ADB")
        return
    
    if not check_android_ready():
        print_step("ERROR", "❌ Android tidak siap")
        return
    
    if not check_line_ranger_running():
        if not launch_line_ranger():
            print_step("ERROR", "❌ Gagal meluncurkan Line Ranger")
            return
    
    # Step 2: Ultimate AI automation
    print_step("AI", "Memulai Ultimate AI automation...")
    ultimate_ai = UltimateGameplayAI()
    
    # Step 3: Wait for lobby
    if not ultimate_ai.wait_for_lobby():
        print_step("ERROR", "❌ Gagal mencapai lobby")
        return
    
    # Step 4: Run ultimate automation with Puter AI
    ultimate_ai.run_ultimate_automation(cycles=15)
    
    print_step("COMPLETE", "🎉 ULTIMATE AUTOMATION SELESAI!")
    print_step("INFO", "📁 Cek 'ultimate_automation_log.json' untuk log detail")
    print_step("INFO", "📁 Cek 'ultimate_ai.html' untuk Puter AI decisions")

if __name__ == "__main__":
    main()