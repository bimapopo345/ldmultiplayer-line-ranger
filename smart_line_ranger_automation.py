#!/usr/bin/env python3
"""
Smart Line Ranger Automation
- Cek LDPlayer sudah jalan atau belum
- Cek Line Ranger sudah jalan atau belum  
- Lanjut ke deteksi loading/lobby
- Automate main stage
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
    
    log_file = "smart_automation_log.json"
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
    
    # Wait for LDPlayer to start
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
    
    # Cek proses yang berjalan
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

class SmartGameplayAI:
    """AI pintar untuk gameplay dengan deteksi screen"""
    
    def __init__(self):
        self.adb_path = "C:\\LDPlayer\\LDPlayer9\\adb.exe"
        self.device = "emulator-5554"
        self.screenshot_path = "current_screen.png"
        
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
        """Deteksi jenis layar - loading atau lobby"""
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
        
        # Logic deteksi yang diperbaiki
        # Cek teks "MAIN STAGE" dengan mencari area coklat besar di tengah
        height, width = img.shape[:2]
        center_region = img[height//3:2*height//3, width//3:2*width//3]
        center_hsv = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
        center_brown_mask = cv2.inRange(center_hsv, np.array([10, 100, 50]), np.array([20, 255, 200]))
        center_brown_pixels = cv2.countNonZero(center_brown_mask)
        
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
            "circles_detected": circle_count
        }
        
        log_action("SCREEN_DETECTED", f"{screen_type} ({confidence})")
        print_step("DETECT", f"Layar: {screen_type} ({confidence}) - Kuning:{yellow_pixels}, Ungu:{purple_pixels}, Coklat:{brown_pixels}")
        
        return screen_type, detection_info
    
    def safe_click(self, x, y):
        """Klik dengan aman"""
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
    
    def find_main_stage_button(self, img):
        """Cari tombol MAIN STAGE"""
        if img is None:
            return None
        
        height, width = img.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Berdasarkan gambar lobby, MAIN STAGE ada di tengah-atas
        main_stage_pos = (center_x, center_y - 100)
        return main_stage_pos
    
    def find_yellow_buttons(self, img):
        """Cari tombol kuning (stage selection)"""
        if img is None:
            return []
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Cari area kuning
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        yellow_buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 20000:  # Ukuran tombol
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w//2, y + h//2
                yellow_buttons.append((center_x, center_y))
        
        return yellow_buttons
    
    def automate_main_stage_flow(self):
        """Automate alur main stage"""
        print_step("AUTO", "Memulai automasi main stage...")
        
        # Step 1: Klik tombol MAIN STAGE
        img = self.safe_screenshot()
        if img is not None:
            main_stage_pos = self.find_main_stage_button(img)
            if main_stage_pos:
                print_step("ACTION", "Klik tombol MAIN STAGE")
                self.safe_click(main_stage_pos[0], main_stage_pos[1])
                time.sleep(3)
        
        # Step 2: Cari dan klik tombol kuning (stage selection)
        for attempt in range(3):
            img = self.safe_screenshot()
            if img is not None:
                yellow_buttons = self.find_yellow_buttons(img)
                if yellow_buttons:
                    x, y = yellow_buttons[0]
                    print_step("ACTION", f"Klik tombol kuning di ({x}, {y})")
                    self.safe_click(x, y)
                    time.sleep(3)
                    break
            time.sleep(2)
        
        # Step 3: Klik tombol START/NEXT berulang kali
        for step in range(5):
            img = self.safe_screenshot()
            if img is not None:
                # Cari tombol hijau (START/GO)
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                green_lower = np.array([40, 50, 50])
                green_upper = np.array([80, 255, 255])
                green_mask = cv2.inRange(hsv, green_lower, green_upper)
                
                contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                clicked = False
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 2000 < area < 50000:
                        x, y, w, h = cv2.boundingRect(contour)
                        center_x, center_y = x + w//2, y + h//2
                        print_step("ACTION", f"Klik tombol hijau (START/NEXT) di ({center_x}, {center_y})")
                        self.safe_click(center_x, center_y)
                        clicked = True
                        break
                
                if not clicked:
                    # Jika tidak ada tombol hijau, klik tengah layar
                    height, width = img.shape[:2]
                    center_x, center_y = width // 2, height // 2
                    print_step("ACTION", f"Klik tengah layar di ({center_x}, {center_y})")
                    self.safe_click(center_x, center_y)
                
                time.sleep(4)
            
            time.sleep(2)
        
        log_action("AUTOMATION_COMPLETE", "Automasi main stage selesai")
        print_step("COMPLETE", "✅ Automasi main stage selesai!")

def main():
    """Main automation workflow yang pintar"""
    print("🚀 SMART LINE RANGER AUTOMATION")
    print("=" * 60)
    
    # Step 1: Cek LDPlayer
    if not check_ldplayer_status():
        if not start_ldplayer():
            print_step("ERROR", "❌ Gagal memulai LDPlayer")
            return
    
    # Step 2: Cek ADB connection
    if not check_adb_connection():
        print_step("ERROR", "❌ Gagal koneksi ADB")
        return
    
    # Step 3: Cek Android ready
    if not check_android_ready():
        print_step("ERROR", "❌ Android tidak siap")
        return
    
    # Step 4: Cek Line Ranger
    if not check_line_ranger_running():
        if not launch_line_ranger():
            print_step("ERROR", "❌ Gagal meluncurkan Line Ranger")
            return
    
    # Step 5: Mulai AI automation
    print_step("AI", "Memulai AI automation...")
    gameplay_ai = SmartGameplayAI()
    
    # Step 6: Tunggu lobby
    if not gameplay_ai.wait_for_lobby():
        print_step("ERROR", "❌ Gagal mencapai lobby")
        return
    
    # Step 7: Automate main stage
    gameplay_ai.automate_main_stage_flow()
    
    print_step("COMPLETE", "🎉 AUTOMASI SELESAI!")
    print_step("INFO", "📁 Cek 'smart_automation_log.json' untuk log detail")

if __name__ == "__main__":
    main()