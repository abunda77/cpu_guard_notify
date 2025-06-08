#!/usr/bin/env python3

import psutil
import time
import os
import requests
import shutil
import sys
from datetime import datetime

# ==== Konfigurasi ====
THRESHOLD = 100
DURATION = 60
INTERVAL = 5
LOG_FILE = "/var/log/cpu_guard.log"

# WhatsApp API
API_URL = "http://193.219.97.148:3001/api/v1/messages"
API_KEY = "u408c106ff9e2481.39fa1c08bbd44c9a8277f707a84b5f1c"
RECIPIENT_NUMBER = "6281310307754"

MALWARE_DIR = "/root/.x"
high_cpu_processes = {}

# ==== Mode Debug ====
DEBUG = "--debug" in sys.argv

def log(msg):
    """
    Mencatat pesan log dengan timestamp ke file dan console (jika mode debug aktif).

    Args:
        msg (str): Pesan yang akan dicatat dalam log

    Returns:
        None

    Fungsi ini akan:
    - Menambahkan timestamp pada pesan
    - Menampilkan ke console jika mode DEBUG aktif
    - Menyimpan pesan ke file log yang ditentukan dalam LOG_FILE
    """
    timestamp = f"{datetime.now()}: "
    full_msg = timestamp + msg
    if DEBUG:
        print(full_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(full_msg + "\n")

def send_whatsapp_message(message):
    """
    Mengirim notifikasi WhatsApp melalui API WhatsApp.

    Args:
        message (str): Pesan yang akan dikirim melalui WhatsApp

    Returns:
        None

    Fungsi ini akan:
    - Membuat payload JSON dengan format yang sesuai untuk API WhatsApp
    - Mengirim request POST ke API WhatsApp dengan authorization header
    - Mencatat hasil pengiriman ke log (berhasil atau gagal)
    - Menangani exception jika terjadi error dalam pengiriman
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
    Memeriksa dan menghapus direktori malware yang mencurigakan jika ditemukan.

    Args:
        None

    Returns:
        None

    Fungsi ini akan:
    - Memeriksa apakah direktori MALWARE_DIR (/root/.x) ada
    - Jika ada, menghapus seluruh direktori beserta isinya menggunakan shutil.rmtree()
    - Mencatat aktivitas penghapusan ke log
    - Mengirim notifikasi WhatsApp tentang penghapusan folder mencurigakan
    - Menangani exception jika terjadi error saat penghapusan
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
