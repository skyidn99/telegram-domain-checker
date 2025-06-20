#!/bin/bash

# Quick deployment script for VPS
echo "🚀 Starting Telegram Bot Deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root or with sudo"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git nginx supervisor curl wget

# Create user for bot (if not exists)
if ! id "botuser" &>/dev/null; then
    echo "👤 Creating bot user..."
    useradd -m -s /bin/bash botuser
fi

# Setup project directory
PROJECT_DIR="/home/botuser/telegram-domain-checker"
echo "📁 Setting up project directory: $PROJECT_DIR"

# Copy project files (assuming current directory contains the project)
if [ -d "telegram-domain-checker" ]; then
    cp -r telegram-domain-checker $PROJECT_DIR
else
    echo "❌ Project directory not found. Please ensure telegram-domain-checker folder exists."
    exit 1
fi

# Set ownership
chown -R botuser:botuser $PROJECT_DIR

# Setup virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u botuser bash -c "cd $PROJECT_DIR && python3.11 -m venv venv"
sudo -u botuser bash -c "cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Create log directory
echo "📝 Creating log directory..."
mkdir -p /var/log/telegram-bot
chown botuser:botuser /var/log/telegram-bot

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/telegram-bot.service << EOF
[Unit]
Description=Telegram Domain Checker Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python src/main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable telegram-bot

# Setup nginx (optional)
echo "🌐 Setting up nginx..."
cat > /etc/nginx/sites-available/telegram-bot << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
systemctl enable nginx

# Setup firewall
echo "🔒 Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Set your bot token:"
echo "   echo 'TELEGRAM_BOT_TOKEN=your_token_here' | sudo tee $PROJECT_DIR/.env"
echo ""
echo "2. Start the bot:"
echo "   sudo systemctl start telegram-bot"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status telegram-bot"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u telegram-bot -f"
echo ""
echo "🌐 Web interface will be available at: http://your-server-ip"

