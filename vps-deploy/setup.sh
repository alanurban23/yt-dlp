#!/bin/bash
#
# 🚀 AUTOMATYCZNY SETUP SKRYPT - Google Cloud VM dla yt-dlp
# Uruchom jako root: sudo bash setup.sh
#

set -e  # Exit on error

echo "🚀 Starting yt-dlp VPS setup on Google Cloud..."
echo "================================================"

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and pip..."
apt install -y python3 python3-pip python3-venv

# Install Chrome (Google's own browser on Google Cloud = best combo!)
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt update
apt install -y google-chrome-stable

# Install VNC for GUI (to login to YouTube once)
echo "🖥️  Installing VNC server for GUI..."
apt install -y x11vnc xvfb

# Install Nginx
echo "🌐 Installing Nginx..."
apt install -y nginx

# Create app directory
echo "📁 Creating app directory..."
mkdir -p /opt/yt-dlp-app
cd /opt/yt-dlp-app

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
cat > requirements.txt << 'EOF'
flask==3.0.0
flask-cors==4.0.0
yt-dlp
gunicorn==21.2.0
brotli>=1.0.9
certifi
mutagen
pycryptodomex
requests>=2.32.2
urllib3>=1.26.17
websockets>=13.0
EOF

pip install -r requirements.txt

echo ""
echo "✅ Setup complete! Next steps:"
echo ""
echo "1. Run VNC server to login to Chrome:"
echo "   sudo x11vnc -create -forever -bg"
echo ""
echo "2. Connect via VNC Viewer to: <your-vm-ip>:5900"
echo ""
echo "3. Open Chrome and login to YouTube"
echo ""
echo "4. Copy app files to /opt/yt-dlp-app/"
echo ""
echo "5. Run: sudo bash configure-services.sh"
echo ""
