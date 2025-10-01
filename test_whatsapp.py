#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import fungsi yang akan diuji
from cpu_guard_notify import send_whatsapp_message

# Aktifkan mode debug
sys.argv.append("--debug")

def test_whatsapp_message():
    """Test fungsi send_whatsapp_message"""
    print("=== Test WhatsApp Message ===")
    
    # Test dengan pesan sederhana
    test_message = "[TEST] Ini adalah pesan test dari CPU Guard"
    print(f"Mengirim pesan test: {test_message}")
    
    result = send_whatsapp_message(test_message)
    
    if result:
        print("✅ Test berhasil: Pesan WhatsApp terkirim")
        return True
    else:
        print("❌ Test gagal: Pesan WhatsApp tidak terkirim")
        return False

if __name__ == "__main__":
    # Cek konfigurasi
    print("=== Konfigurasi WhatsApp ===")
    print(f"API URL: {os.getenv('API_URL')}")
    print(f"Username: {os.getenv('USERNAME')}")
    print(f"Password: {'*' * len(os.getenv('PASSWORD', '')) if os.getenv('PASSWORD') else 'None'}")
    print(f"Recipient: {os.getenv('RECIPIENT_NUMBER')}")
    print()
    
    # Jalankan test
    success = test_whatsapp_message()
    
    if success:
        print("\n✅ Semua test berhasil!")
        sys.exit(0)
    else:
        print("\n❌ Test gagal!")
        sys.exit(1)