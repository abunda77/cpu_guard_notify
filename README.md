# CPU Guard

Aplikasi monitoring CPU yang secara otomatis menghentikan proses dengan penggunaan CPU tinggi dan mengirim notifikasi WhatsApp.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment variables:**
   - Copy `.env.example` to `.env`
   - Edit `.env` file dan isi dengan konfigurasi yang sesuai:
     ```
     API_URL=your_whatsapp_api_url
     API_KEY=your_whatsapp_api_key
     RECIPIENT_NUMBER=your_phone_number
     ```

3. **Run the application:**
   ```bash
   python cpu_guard_notify.py
   ```

   Untuk mode debug:
   ```bash
   python cpu_guard_notify.py --debug
   ```

## Configuration

Semua konfigurasi dapat diatur melalui file `.env`:

- `API_URL`: URL endpoint WhatsApp API
- `API_KEY`: API key untuk WhatsApp
- `RECIPIENT_NUMBER`: Nomor telepon penerima notifikasi
- `THRESHOLD`: Batas CPU usage (default: 100%)
- `DURATION`: Durasi CPU tinggi sebelum proses dihentikan (default: 60 detik)
- `INTERVAL`: Interval pemeriksaan (default: 5 detik)
- `LOG_FILE`: Lokasi file log (default: /var/log/cpu_guard.log)
- `MALWARE_DIR`: Direktori malware yang akan dipantau (default: /root/.x)

## Features

- Monitoring proses dengan CPU usage tinggi
- Automatic termination proses yang melebihi threshold
- Deteksi dan penghapusan otomatis direktori malware
- Notifikasi WhatsApp untuk semua aktivitas
- Logging lengkap dengan timestamp
