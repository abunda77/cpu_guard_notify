#!/usr/bin/env python3

import psutil
import time
import os
import requests
import shutil
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==== Konfigurasi ====
THRESHOLD = int(os.getenv('THRESHOLD', 100))
DURATION = int(os.getenv('DURATION', 30))
INTERVAL = int(os.getenv('INTERVAL', 5))
LOG_FILE = os.getenv('LOG_FILE', "/var/log/cpu_guard.log")

# WhatsApp API
API_URL = os.getenv('API_URL')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
RECIPIENT_NUMBER = os.getenv('RECIPIENT_NUMBER')

MALWARE_DIR = os.getenv('MALWARE_DIR', "/root/.x")
high_cpu_processes = {}

# ==== Mode Debug ====
DEBUG = "--debug" in sys.argv

def log(msg):
    timestamp = f"{datetime.now()}: "
    full_msg = timestamp + msg
    if DEBUG:
        print(full_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(full_msg + "\n")

def send_whatsapp_message(message):
    log(f"DEBUG: Sending WhatsApp message: {message}")
    log(f"DEBUG: API URL: {API_URL}")
    log(f"DEBUG: Recipient: {RECIPIENT_NUMBER}")
    
    payload = {
        "phone": f"{RECIPIENT_NUMBER}@s.whatsapp.net",
        "message": message,
        "reply_message_id": "",
        "is_forwarded": False,
        "duration": 3600
    }
    
    log(f"DEBUG: Payload: {payload}")
    
    try:
        # Test koneksi dengan timeout
        response = requests.post(API_URL, json=payload, auth=(USERNAME, PASSWORD), timeout=10)
        log(f"DEBUG: Response status: {response.status_code}")
        log(f"DEBUG: Response headers: {dict(response.headers)}")
        log(f"DEBUG: Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            log(f"DEBUG: Response JSON: {result}")
            log("✅ WhatsApp notification sent.")
            return True
        else:
            log(f"❌ WhatsApp error: {response.status_code} | {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log("❌ WhatsApp timeout error: Request took too long")
        return False
    except requests.exceptions.ConnectionError:
        log("❌ WhatsApp connection error: Could not connect to API")
        return False
    except Exception as e:
        log(f"❌ WhatsApp send error: {type(e).__name__}: {e}")
        return False

def remove_malware_dir_if_exists():
    log(f"DEBUG: Checking for malware directory: {MALWARE_DIR}")
    if os.path.exists(MALWARE_DIR):
        log(f"DEBUG: Malware directory found: {MALWARE_DIR}")
        try:
            # Cek permission
            if os.access(MALWARE_DIR, os.W_OK):
                shutil.rmtree(MALWARE_DIR)
                log(f"✅ Folder {MALWARE_DIR} detected & deleted automatically.")
                send_whatsapp_message(f"[CPU GUARD]\nFolder mencurigakan {MALWARE_DIR} telah dihapus otomatis.")
            else:
                log(f"❌ No write permission for {MALWARE_DIR}")
        except Exception as e:
            log(f"❌ Failed to delete {MALWARE_DIR}: {type(e).__name__}: {e}")
    else:
        log(f"DEBUG: Malware directory not found: {MALWARE_DIR}")

# ===== Main Loop =====
log("🚀 CPU Guard started with debug mode")
log(f"DEBUG: Configuration - THRESHOLD: {THRESHOLD}, DURATION: {DURATION}, INTERVAL: {INTERVAL}")
log(f"DEBUG: Log file: {LOG_FILE}")

# Test WhatsApp API saat startup
log("DEBUG: Testing WhatsApp API connection...")
test_message = "[CPU GUARD] System started successfully"
send_whatsapp_message(test_message)

while True:
    log(f"DEBUG: Starting monitoring cycle...")
    
    # 1. Cek dan hapus folder malware
    remove_malware_dir_if_exists()

    # 2. Pantau proses CPU tinggi
    log("DEBUG: Scanning processes...")
    active_processes = 0
    
    for proc in psutil.process_iter(['pid', 'cpu_percent', 'name']):
        try:
            cpu = proc.info['cpu_percent']
            pid = proc.info['pid']
            name = proc.info['name']
            
            if cpu > 0:  # Hanya proses aktif
                active_processes += 1
                log(f"DEBUG: Process {name}(PID:{pid}) CPU:{cpu:.2f}%")

            if cpu >= THRESHOLD:
                log(f"DEBUG: High CPU detected: {name}(PID:{pid}) CPU:{cpu:.2f}%")
                
                if pid in high_cpu_processes:
                    high_cpu_processes[pid]['duration'] += INTERVAL
                    log(f"DEBUG: Process {pid} duration increased to {high_cpu_processes[pid]['duration']}s")
                else:
                    high_cpu_processes[pid] = {'duration': INTERVAL, 'name': name}
                    log(f"DEBUG: New high CPU process tracked: {name}(PID:{pid})")

                if high_cpu_processes[pid]['duration'] >= DURATION:
                    log(f"⚠️  Killing PID {pid} ({name}) CPU {cpu:.2f}% after {DURATION}s")
                    try:
                        os.kill(pid, 9)
                        log(f"✅ Killed PID {pid} ({name})")
                        remove_malware_dir_if_exists()
                        success = send_whatsapp_message(
                            f"[CPU GUARD]\nProses {name} (PID {pid}) dihentikan karena CPU {cpu:.2f}% selama {DURATION} detik. Folder {MALWARE_DIR} juga telah dihapus."
                        )
                        if not success:
                            log("❌ Failed to send WhatsApp notification")
                    except Exception as e:
                        log(f"❌ Failed to kill PID {pid}: {type(e).__name__}: {e}")
                    del high_cpu_processes[pid]
            else:
                if pid in high_cpu_processes:
                    log(f"DEBUG: Removing process {pid} from tracking (CPU below threshold)")
                    del high_cpu_processes[pid]

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    log(f"DEBUG: Cycle complete. Active processes: {active_processes}, Tracked processes: {len(high_cpu_processes)}")
    time.sleep(INTERVAL)
