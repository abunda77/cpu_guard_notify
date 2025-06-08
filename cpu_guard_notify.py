#!/usr/bin/env python3

import psutil
import time
import os
import requests
import shutil
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==== Konfigurasi ====
# Load configuration from environment variables with default values
THRESHOLD = int(os.getenv('THRESHOLD', 100))
DURATION = int(os.getenv('DURATION', 60))
INTERVAL = int(os.getenv('INTERVAL', 5))
LOG_FILE = os.getenv('LOG_FILE', '/var/log/cpu_guard.log')

# WhatsApp API - Load from environment variables
API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')
RECIPIENT_NUMBER = os.getenv('RECIPIENT_NUMBER')

# Malware directory path
MALWARE_DIR = os.getenv('MALWARE_DIR', '/root/.x')

# Validate required environment variables
if not API_URL or not API_KEY or not RECIPIENT_NUMBER:
    print("❌ Error: Missing required environment variables (API_URL, API_KEY, RECIPIENT_NUMBER)")
    print("Please check your .env file and ensure all required variables are set.")
    sys.exit(1)
high_cpu_processes = {}

# ==== Mode Debug ====
DEBUG = "--debug" in sys.argv

def log(msg):
    """
    Mencatat pesan log dengan timestamp ke file dan, jika mode debug aktif, ke konsol.

    Setiap pesan log akan diawali dengan timestamp (format: YYYY-MM-DD HH:MM:SS.ffffff)
    dan disimpan ke file log yang ditentukan oleh konstanta `LOG_FILE`.
    Jika konstanta `DEBUG` bernilai True, pesan juga akan dicetak ke konsol.

    Args:
        msg (str): Pesan yang akan dicatat.

    Returns:
        None
    """
    timestamp = f"{datetime.now()}: "
    full_msg = timestamp + msg
    if DEBUG:
        print(full_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(full_msg + "\n")

def send_whatsapp_message(message):
    """
    Mengirim pesan teks notifikasi melalui API WhatsApp.

    Fungsi ini menyusun payload JSON yang berisi pesan dan informasi penerima,
    kemudian mengirimkannya sebagai permintaan POST ke `API_URL` yang dikonfigurasi.
    Autentikasi dilakukan menggunakan `API_KEY`. Hasil dari upaya pengiriman
    (baik berhasil maupun gagal beserta detail error) akan dicatat menggunakan fungsi `log`.
    Potensi `Exception` selama permintaan HTTP juga ditangani dan dicatat.

    Args:
        message (str): Isi pesan teks yang akan dikirimkan.

    Returns:
        None
    """
    payload = {
        "recipient_type": "individual",
        "to": RECIPIENT_NUMBER,
        "type": "text",
        "text": {
            "body": message
        }
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            log("✅ WhatsApp notification sent.")
        else:
            log(f"❌ WhatsApp error: {response.status_code} | {response.text}")
    except Exception as e:
        log(f"❌ WhatsApp send error: {e}")

def remove_malware_dir_if_exists():
    """
    Memeriksa keberadaan direktori yang dicurigai sebagai malware dan menghapusnya.

    Direktori yang ditargetkan didefinisikan oleh konstanta `MALWARE_DIR`.
    Jika direktori ini ada, fungsi akan mencoba menghapusnya secara rekursif
    (termasuk semua file dan subdirektori di dalamnya) menggunakan `shutil.rmtree()`.
    Informasi mengenai deteksi dan penghapusan direktori akan dicatat dalam log.
    Sebuah notifikasi WhatsApp juga akan dikirim untuk memberitahukan tindakan ini.
    Potensi `Exception` selama proses pemeriksaan atau penghapusan direktori
    akan ditangani dan dicatat dalam log.

    Args:
        None

    Returns:
        None
    """
    if os.path.exists(MALWARE_DIR):
        try:
            shutil.rmtree(MALWARE_DIR)
            log(f"Folder {MALWARE_DIR} detected & deleted automatically.")
            send_whatsapp_message(f"[CPU GUARD]\nFolder mencurigakan {MALWARE_DIR} telah dihapus otomatis.")
        except Exception as e:
            log(f"❌ Failed to delete {MALWARE_DIR}: {e}")

# ===== Main Loop =====
while True:
    # 1. Cek dan hapus folder malware
    remove_malware_dir_if_exists()

    # 2. Pantau proses CPU tinggi
    for proc in psutil.process_iter(['pid', 'cpu_percent', 'name']):
        try:
            cpu = proc.info['cpu_percent']
            pid = proc.info['pid']
            name = proc.info['name']

            if cpu >= THRESHOLD:
                if pid in high_cpu_processes:
                    high_cpu_processes[pid]['duration'] += INTERVAL
                else:
                    high_cpu_processes[pid] = {'duration': INTERVAL, 'name': name}

                if high_cpu_processes[pid]['duration'] >= DURATION:
                    log(f"Killing PID {pid} ({name}) CPU {cpu:.2f}%")
                    try:
                        os.kill(pid, 9)
                        log(f"Killed PID {pid} ({name})")
                        remove_malware_dir_if_exists()
                        send_whatsapp_message(
                            f"[CPU GUARD]\nProses {name} (PID {pid}) dihentikan karena CPU {cpu:.2f}% selama {DURATION} detik. Folder {MALWARE_DIR} juga telah dihapus."
                        )
                    except Exception as e:
                        log(f"❌ Failed to kill PID {pid}: {e}")
                    del high_cpu_processes[pid]
            else:
                if pid in high_cpu_processes:
                    del high_cpu_processes[pid]

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(INTERVAL)
