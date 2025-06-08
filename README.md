# 🛡️ CPU Guard

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

**CPU Guard** adalah aplikasi monitoring sistem yang secara otomatis memantau penggunaan CPU, menghentikan proses dengan penggunaan CPU tinggi, dan mengirim notifikasi real-time melalui WhatsApp. Aplikasi ini juga dilengkapi dengan fitur deteksi dan penghapusan otomatis direktori malware yang mencurigakan.

## 📋 Daftar Isi

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Logging](#-logging)
- [API WhatsApp](#-api-whatsapp)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔍 **Monitoring CPU Real-time**
- Memantau semua proses yang berjalan setiap 5 detik (dapat dikonfigurasi)
- Mendeteksi proses dengan penggunaan CPU di atas threshold yang ditentukan
- Tracking durasi proses dengan CPU tinggi

### ⚡ **Automatic Process Termination**
- Menghentikan proses yang menggunakan CPU tinggi dalam durasi tertentu
- Menggunakan signal SIGKILL (kill -9) untuk memastikan proses benar-benar terhenti
- Logging lengkap untuk setiap aksi yang dilakukan

### 🦠 **Malware Detection & Removal**
- Deteksi otomatis direktori malware yang mencurigakan (`/root/.x`)
- Penghapusan otomatis direktori malware beserta seluruh isinya
- Notifikasi real-time saat malware terdeteksi dan dihapus

### 📱 **WhatsApp Notifications**
- Notifikasi real-time melalui WhatsApp API
- Pesan detail tentang proses yang dihentikan
- Notifikasi saat malware terdeteksi dan dihapus
- Error handling untuk kegagalan pengiriman notifikasi

### 📊 **Comprehensive Logging**
- Log file dengan timestamp lengkap
- Mode debug untuk troubleshooting
- Pencatatan semua aktivitas sistem

## 📋 Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu, CentOS, Debian, dll.)
- **Python**: 3.6 atau lebih tinggi
- **Memory**: Minimal 512MB RAM
- **Storage**: Minimal 100MB free space

### Python Dependencies
```
psutil>=5.8.0
requests>=2.25.0
python-dotenv>=0.19.0
```

## 🚀 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd cpu_guard
```

### 2. Install Python Dependencies
```bash
# Menggunakan pip
pip install -r requirements.txt

# Atau menggunakan pip3
pip3 install -r requirements.txt

# Untuk virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
# Copy template environment file
cp .env.example .env

# Edit file .env dengan editor favorit Anda
nano .env
# atau
vim .env
```

### 4. Setup Permissions (Linux)
```bash
# Berikan permission execute
chmod +x cpu_guard_notify.py

# Setup log directory (optional)
sudo mkdir -p /var/log
sudo touch /var/log/cpu_guard.log
sudo chmod 666 /var/log/cpu_guard.log
```

## ⚙️ Configuration

Semua konfigurasi aplikasi diatur melalui file `.env`. Berikut adalah penjelasan lengkap setiap variabel:

### 📱 WhatsApp API Configuration (Required)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `API_URL` | URL endpoint WhatsApp API | `http://193.219.97.148:3001/api/v1/messages` | ✅ |
| `API_KEY` | API key untuk autentikasi WhatsApp | `u408c106ff9e2481.39fa1c08bbd44c9a8277f707a84b5f1c` | ✅ |
| `RECIPIENT_NUMBER` | Nomor telepon penerima notifikasi (format internasional) | `6281310307754` | ✅ |

### 🔧 CPU Guard Configuration (Optional)

| Variable | Description | Default | Type |
|----------|-------------|---------|------|
| `THRESHOLD` | Batas CPU usage dalam persen | `100` | Integer |
| `DURATION` | Durasi CPU tinggi sebelum proses dihentikan (detik) | `60` | Integer |
| `INTERVAL` | Interval pemeriksaan sistem (detik) | `5` | Integer |
| `LOG_FILE` | Lokasi file log | `/var/log/cpu_guard.log` | String |
| `MALWARE_DIR` | Direktori malware yang dipantau | `/root/.x` | String |

### 📝 Contoh File .env
```env
# WhatsApp API Configuration
API_URL=http://your-whatsapp-api-url.com/api/v1/messages
API_KEY=your_secret_api_key_here
RECIPIENT_NUMBER=628123456789

# CPU Guard Configuration
THRESHOLD=80
DURATION=120
INTERVAL=10
LOG_FILE=/home/user/cpu_guard.log
MALWARE_DIR=/tmp/suspicious
```

## 🎯 Usage

### Basic Usage
```bash
# Menjalankan aplikasi
python cpu_guard_notify.py

# Menjalankan dengan mode debug
python cpu_guard_notify.py --debug

# Menjalankan di background (Linux)
nohup python cpu_guard_notify.py &

# Menjalankan dengan systemd (recommended untuk production)
sudo systemctl start cpu-guard
```

### 🔄 Running as System Service (Linux)

#### 1. Buat file service systemd
```bash
sudo nano /etc/systemd/system/cpu-guard.service
```

#### 2. Isi file service
```ini
[Unit]
Description=CPU Guard Monitoring Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/cpu_guard
ExecStart=/usr/bin/python3 /path/to/cpu_guard/cpu_guard_notify.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Enable dan start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable cpu-guard
sudo systemctl start cpu-guard
sudo systemctl status cpu-guard
```

## 📊 Logging

### Log Format
```
2024-01-15 10:30:45.123456: Killing PID 1234 (malicious_process) CPU 95.50%
2024-01-15 10:30:45.234567: Killed PID 1234 (malicious_process)
2024-01-15 10:30:45.345678: Folder /root/.x detected & deleted automatically.
2024-01-15 10:30:46.456789: ✅ WhatsApp notification sent.
```

### Log Locations
- **Default**: `/var/log/cpu_guard.log`
- **Custom**: Sesuai dengan variabel `LOG_FILE` di `.env`
- **Debug Mode**: Output juga ditampilkan di console

### Log Rotation (Recommended)
```bash
# Buat file logrotate
sudo nano /etc/logrotate.d/cpu-guard

# Isi file logrotate
/var/log/cpu_guard.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

## 📱 API WhatsApp

### Supported WhatsApp API Providers
- **WhatsApp Business API**
- **Third-party providers** (seperti yang digunakan dalam contoh)
- **Custom WhatsApp API implementations**

### Message Format
```json
{
    "recipient_type": "individual",
    "to": "6281310307754",
    "type": "text",
    "text": {
        "body": "[CPU GUARD]\nProses malicious_process (PID 1234) dihentikan karena CPU 95.50% selama 60 detik. Folder /root/.x juga telah dihapus."
    }
}
```

### Error Handling
- **Connection timeout**: Retry otomatis
- **API rate limiting**: Logging error tanpa crash
- **Invalid credentials**: Error message yang jelas
- **Network issues**: Graceful degradation

## 🔒 Security

### Best Practices
1. **Environment Variables**: Jangan pernah commit file `.env` ke repository
2. **API Keys**: Gunakan API key dengan permission minimal yang diperlukan
3. **File Permissions**: Set permission yang tepat untuk file log dan script
4. **Network**: Gunakan HTTPS untuk API WhatsApp jika memungkinkan

### File Permissions
```bash
# Script file
chmod 755 cpu_guard_notify.py

# Environment file
chmod 600 .env

# Log file
chmod 644 /var/log/cpu_guard.log
```

### Firewall Configuration
```bash
# Jika menggunakan UFW
sudo ufw allow out 443/tcp  # HTTPS untuk WhatsApp API
sudo ufw allow out 80/tcp   # HTTP untuk WhatsApp API (jika diperlukan)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError: No module named 'dotenv'**
```bash
# Solution
pip install python-dotenv
```

#### 2. **Permission denied: '/var/log/cpu_guard.log'**
```bash
# Solution
sudo touch /var/log/cpu_guard.log
sudo chmod 666 /var/log/cpu_guard.log
# atau gunakan path yang dapat diakses user
LOG_FILE=/home/user/cpu_guard.log
```

#### 3. **WhatsApp API Error: 401 Unauthorized**
```bash
# Check API credentials
echo $API_KEY
echo $API_URL
# Pastikan API_KEY valid dan tidak expired
```

#### 4. **Process not being killed**
```bash
# Check if running with sufficient privileges
sudo python cpu_guard_notify.py --debug
# Atau jalankan sebagai root untuk akses penuh ke semua proses
```

#### 5. **High CPU usage by CPU Guard itself**
```bash
# Increase INTERVAL to reduce checking frequency
INTERVAL=10  # Check every 10 seconds instead of 5
```

### Debug Mode
```bash
# Jalankan dengan debug untuk troubleshooting
python cpu_guard_notify.py --debug

# Output akan menampilkan:
# - Semua log ke console
# - Detail proses yang dipantau
# - Status API WhatsApp
# - Error messages yang detail
```

### Log Analysis
```bash
# Monitor log real-time
tail -f /var/log/cpu_guard.log

# Search for errors
grep "❌" /var/log/cpu_guard.log

# Check WhatsApp notifications
grep "WhatsApp" /var/log/cpu_guard.log

# Monitor killed processes
grep "Killed PID" /var/log/cpu_guard.log
```

## 📈 Monitoring & Maintenance

### Health Check Script
```bash
#!/bin/bash
# health_check.sh
if pgrep -f "cpu_guard_notify.py" > /dev/null; then
    echo "CPU Guard is running"
    exit 0
else
    echo "CPU Guard is not running"
    exit 1
fi
```

### Performance Monitoring
```bash
# Check CPU usage of CPU Guard itself
ps aux | grep cpu_guard_notify.py

# Check memory usage
pmap $(pgrep -f cpu_guard_notify.py)

# Monitor log file size
ls -lh /var/log/cpu_guard.log
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd cpu_guard

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black cpu_guard_notify.py

# Lint code
flake8 cpu_guard_notify.py
```

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/cpu-guard/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/cpu-guard/wiki)
- **Email**: support@yourcompany.com

## 🙏 Acknowledgments

- [psutil](https://github.com/giampaolo/psutil) - Cross-platform lib for process and system monitoring
- [requests](https://github.com/psf/requests) - HTTP library for Python
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable loader

---

**⚠️ Disclaimer**: Aplikasi ini akan menghentikan proses secara paksa. Pastikan untuk menguji terlebih dahulu di environment development sebelum menggunakan di production. Selalu backup data penting sebelum menjalankan aplikasi ini.
