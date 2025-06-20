# Panduan Deployment Bot Telegram Nawala Checker di VPS/Server

## Daftar Isi

1. [Persiapan VPS/Server](#persiapan-vpsserver)
2. [Instalasi Dependencies](#instalasi-dependencies)
3. [Upload dan Setup Project](#upload-dan-setup-project)
4. [Konfigurasi Environment](#konfigurasi-environment)
5. [Setup Systemd Service](#setup-systemd-service)
6. [Konfigurasi Nginx (Opsional)](#konfigurasi-nginx-opsional)
7. [Monitoring dan Logging](#monitoring-dan-logging)
8. [Backup dan Maintenance](#backup-dan-maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Persiapan VPS/Server

### Spesifikasi Minimum

Untuk menjalankan bot Telegram Nawala Checker, Anda memerlukan VPS dengan spesifikasi minimal:

- **RAM**: 512 MB (disarankan 1 GB)
- **Storage**: 5 GB (disarankan 10 GB)
- **CPU**: 1 vCPU
- **OS**: Ubuntu 20.04 LTS atau lebih baru
- **Bandwidth**: Unlimited atau minimal 1 TB/bulan
- **Koneksi Internet**: Stabil dengan uptime tinggi

### Provider VPS yang Direkomendasikan

1. **DigitalOcean** - Droplet $5/bulan
2. **Vultr** - Cloud Compute $3.50/bulan
3. **Linode** - Nanode $5/bulan
4. **AWS EC2** - t2.micro (free tier)
5. **Google Cloud Platform** - e2-micro (free tier)

### Akses SSH

Pastikan Anda memiliki akses SSH ke VPS dengan:
- Username: root atau user dengan sudo privileges
- SSH key atau password
- IP address VPS

```bash
# Contoh koneksi SSH
ssh root@your-vps-ip
# atau
ssh username@your-vps-ip
```

---

## Instalasi Dependencies

### Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git unzip software-properties-common
```

### Install Python 3.11

```bash
# Add deadsnakes PPA for Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify installation
python3.11 --version
```

### Install Additional Tools

```bash
# Install process manager
sudo apt install -y supervisor

# Install nginx (optional, for reverse proxy)
sudo apt install -y nginx

# Install htop for monitoring
sudo apt install -y htop

# Install fail2ban for security
sudo apt install -y fail2ban
```

---

## Upload dan Setup Project

### Method 1: Git Clone (Recommended)

```bash
# Navigate to home directory
cd /home/ubuntu

# Clone project (if you have it in a git repository)
# git clone https://github.com/yourusername/telegram-domain-checker.git

# Or create directory manually
mkdir telegram-domain-checker
cd telegram-domain-checker
```

### Method 2: Upload via SCP

Dari komputer lokal, upload project ke VPS:

```bash
# Upload project folder
scp -r telegram-domain-checker/ root@your-vps-ip:/home/ubuntu/

# Or upload as zip
scp telegram-domain-checker.zip root@your-vps-ip:/home/ubuntu/
ssh root@your-vps-ip
cd /home/ubuntu
unzip telegram-domain-checker.zip
```

### Setup Virtual Environment

```bash
cd /home/ubuntu/telegram-domain-checker

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

---

## Konfigurasi Environment

### Create Environment File

```bash
# Create .env file
nano /home/ubuntu/telegram-domain-checker/.env
```

Isi file `.env`:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7927097878:AAGPBxnF1ezBdqXtnvSsS6ld0wKKiSxrQ7k

# Database Configuration (optional, uses SQLite by default)
DATABASE_URL=sqlite:///src/database/app.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/telegram-bot/bot.log

# API Configuration
SKIDDLE_API_URL=https://check.skiddle.id/

# Schedule Configuration
CHECK_INTERVAL_MINUTES=30
```

### Update Main Script untuk Environment File

Buat file `src/config.py`:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///src/database/app.db')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/telegram-bot/bot.log')
    SKIDDLE_API_URL = os.getenv('SKIDDLE_API_URL', 'https://check.skiddle.id/')
    CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', 30))
```

### Install python-dotenv

```bash
source venv/bin/activate
pip install python-dotenv
pip freeze > requirements.txt
```

### Create Log Directory

```bash
sudo mkdir -p /var/log/telegram-bot
sudo chown ubuntu:ubuntu /var/log/telegram-bot
sudo chmod 755 /var/log/telegram-bot
```

---

## Setup Systemd Service

### Create Service File

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Isi file service:

```ini
[Unit]
Description=Telegram Domain Checker Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/telegram-domain-checker
Environment=PATH=/home/ubuntu/telegram-domain-checker/venv/bin
ExecStart=/home/ubuntu/telegram-domain-checker/venv/bin/python src/main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/ubuntu/telegram-domain-checker
ReadWritePaths=/var/log/telegram-bot

[Install]
WantedBy=multi-user.target
```

### Enable dan Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-bot

# Start the service
sudo systemctl start telegram-bot

# Check service status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

### Service Management Commands

```bash
# Start service
sudo systemctl start telegram-bot

# Stop service
sudo systemctl stop telegram-bot

# Restart service
sudo systemctl restart telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs (last 50 lines)
sudo journalctl -u telegram-bot -n 50

# Follow logs in real-time
sudo journalctl -u telegram-bot -f

# View logs for specific date
sudo journalctl -u telegram-bot --since "2024-01-01" --until "2024-01-02"
```

---

## Konfigurasi Nginx (Opsional)

Jika Anda ingin mengakses status bot melalui web interface:

### Install dan Konfigurasi Nginx

```bash
# Install nginx
sudo apt install -y nginx

# Create nginx configuration
sudo nano /etc/nginx/sites-available/telegram-bot
```

Isi konfigurasi nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Ganti dengan domain Anda

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

### Enable Site dan Restart Nginx

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable nginx to start on boot
sudo systemctl enable nginx
```

### Setup SSL dengan Let's Encrypt (Opsional)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## Monitoring dan Logging

### Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/telegram-bot
```

Isi konfigurasi logrotate:

```
/var/log/telegram-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload telegram-bot
    endscript
}
```

### Monitoring Script

Buat script monitoring:

```bash
nano /home/ubuntu/monitor-bot.sh
```

Isi script:

```bash
#!/bin/bash

# Bot monitoring script
BOT_SERVICE="telegram-bot"
LOG_FILE="/var/log/telegram-bot/monitor.log"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"  # Ganti dengan chat ID Anda
TELEGRAM_BOT_TOKEN="7927097878:AAGPBxnF1ezBdqXtnvSsS6ld0wKKiSxrQ7k"

# Function to send telegram message
send_telegram_message() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d text="${message}"
}

# Check if service is running
if ! systemctl is-active --quiet $BOT_SERVICE; then
    echo "$(date): Bot service is not running. Attempting to restart..." >> $LOG_FILE
    
    # Try to restart service
    systemctl restart $BOT_SERVICE
    sleep 10
    
    # Check if restart was successful
    if systemctl is-active --quiet $BOT_SERVICE; then
        message="✅ Bot service restarted successfully at $(date)"
        echo "$(date): Bot service restarted successfully" >> $LOG_FILE
    else
        message="❌ Failed to restart bot service at $(date)"
        echo "$(date): Failed to restart bot service" >> $LOG_FILE
    fi
    
    send_telegram_message "$message"
else
    echo "$(date): Bot service is running normally" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    message="⚠️ Disk usage is ${DISK_USAGE}% on $(hostname)"
    send_telegram_message "$message"
    echo "$(date): High disk usage: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 80 ]; then
    message="⚠️ Memory usage is ${MEMORY_USAGE}% on $(hostname)"
    send_telegram_message "$message"
    echo "$(date): High memory usage: ${MEMORY_USAGE}%" >> $LOG_FILE
fi
```

### Setup Cron untuk Monitoring

```bash
# Make script executable
chmod +x /home/ubuntu/monitor-bot.sh

# Add to crontab
crontab -e
```

Tambahkan baris berikut:

```bash
# Monitor bot every 5 minutes
*/5 * * * * /home/ubuntu/monitor-bot.sh

# Restart bot daily at 3 AM (optional)
0 3 * * * systemctl restart telegram-bot
```

---

## Backup dan Maintenance

### Database Backup Script

```bash
nano /home/ubuntu/backup-bot.sh
```

Isi script backup:

```bash
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
PROJECT_DIR="/home/ubuntu/telegram-domain-checker"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $PROJECT_DIR/src/database/app.db $BACKUP_DIR/app_db_$DATE.db

# Backup configuration
cp $PROJECT_DIR/.env $BACKUP_DIR/env_$DATE.backup

# Compress old backups (keep last 7 days)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.backup" -mtime +7 -delete

echo "$(date): Backup completed - app_db_$DATE.db" >> /var/log/telegram-bot/backup.log
```

### Setup Backup Cron

```bash
chmod +x /home/ubuntu/backup-bot.sh

# Add to crontab
crontab -e
```

Tambahkan:

```bash
# Backup database daily at 2 AM
0 2 * * * /home/ubuntu/backup-bot.sh
```

### Update Script

```bash
nano /home/ubuntu/update-bot.sh
```

Isi script update:

```bash
#!/bin/bash

PROJECT_DIR="/home/ubuntu/telegram-domain-checker"
cd $PROJECT_DIR

# Stop service
sudo systemctl stop telegram-bot

# Backup current version
cp -r $PROJECT_DIR $PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)

# Pull updates (if using git)
# git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Start service
sudo systemctl start telegram-bot

# Check status
sleep 5
sudo systemctl status telegram-bot

echo "$(date): Bot updated successfully" >> /var/log/telegram-bot/update.log
```

---

## Troubleshooting

### Common Issues dan Solutions

#### 1. Bot tidak merespons

**Diagnosis:**
```bash
# Check service status
sudo systemctl status telegram-bot

# Check logs
sudo journalctl -u telegram-bot -n 50

# Check if port is listening
sudo netstat -tlnp | grep :5000
```

**Solutions:**
- Pastikan token bot benar
- Cek koneksi internet VPS
- Restart service: `sudo systemctl restart telegram-bot`

#### 2. Database Error

**Diagnosis:**
```bash
# Check database file permissions
ls -la /home/ubuntu/telegram-domain-checker/src/database/

# Check disk space
df -h
```

**Solutions:**
```bash
# Fix permissions
sudo chown ubuntu:ubuntu /home/ubuntu/telegram-domain-checker/src/database/app.db
sudo chmod 664 /home/ubuntu/telegram-domain-checker/src/database/app.db

# Recreate database if corrupted
cd /home/ubuntu/telegram-domain-checker
source venv/bin/activate
python -c "from src.models.domain import db; db.create_all()"
```

#### 3. High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
free -h
htop

# Check bot process
ps aux | grep python
```

**Solutions:**
```bash
# Restart service
sudo systemctl restart telegram-bot

# Add swap if needed
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 4. API Rate Limiting

**Diagnosis:**
```bash
# Check logs for rate limit errors
sudo journalctl -u telegram-bot | grep -i "rate\|limit\|429"
```

**Solutions:**
- Kurangi frekuensi pengecekan domain
- Implementasi retry dengan backoff
- Gunakan multiple API endpoints jika tersedia

### Log Analysis Commands

```bash
# View real-time logs
sudo journalctl -u telegram-bot -f

# Search for errors
sudo journalctl -u telegram-bot | grep -i error

# View logs for specific time period
sudo journalctl -u telegram-bot --since "1 hour ago"

# Export logs to file
sudo journalctl -u telegram-bot > bot-logs.txt

# Check service restart history
sudo journalctl -u telegram-bot | grep -i "started\|stopped"
```

### Performance Monitoring

```bash
# Check CPU usage
top -p $(pgrep -f "python src/main.py")

# Check memory usage
ps -o pid,ppid,cmd,%mem,%cpu -p $(pgrep -f "python src/main.py")

# Check network connections
sudo netstat -tulpn | grep python

# Check disk I/O
sudo iotop -p $(pgrep -f "python src/main.py")
```

---

## Security Best Practices

### Firewall Configuration

```bash
# Install ufw
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS (if using nginx)
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Fail2Ban Configuration

```bash
# Create jail for SSH
sudo nano /etc/fail2ban/jail.local
```

Isi konfigurasi:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban

# Check status
sudo fail2ban-client status
```

### Regular Security Updates

```bash
# Create update script
nano /home/ubuntu/security-update.sh
```

```bash
#!/bin/bash

# Update package list
apt update

# Install security updates
apt upgrade -y

# Clean package cache
apt autoremove -y
apt autoclean

echo "$(date): Security updates completed" >> /var/log/security-updates.log
```

```bash
# Make executable
chmod +x /home/ubuntu/security-update.sh

# Add to crontab (weekly updates)
sudo crontab -e
```

Tambahkan:

```bash
# Security updates every Sunday at 4 AM
0 4 * * 0 /home/ubuntu/security-update.sh
```

---

Dengan mengikuti panduan ini, bot Telegram Nawala Checker Anda akan berjalan dengan stabil di VPS/Server dengan monitoring, backup, dan security yang baik. Pastikan untuk melakukan testing setelah deployment dan monitor logs secara berkala untuk memastikan bot berfungsi dengan optimal.

