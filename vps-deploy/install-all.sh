#!/bin/bash
#
# 🚀 ONE-CLICK INSTALL - Wszystko w jednym skrypcie!
# Użycie: sudo bash install-all.sh
#
# Co robi:
# 1. Instaluje wszystko (Python, Chrome, Nginx, etc)
# 2. Tworzy app.py
# 3. Konfiguruje services
# 4. Uruchamia serwer
#
# Jedyne co musisz zrobić potem: Zalogować się do Chrome przez VNC!
#

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🚀 yt-dlp VPS - ONE-CLICK INSTALL                     ║"
echo "║  Google Cloud + Automatic YouTube Cookies              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo bash install-all.sh"
    exit 1
fi

# ============= STEP 1: INSTALL PACKAGES =============
echo "📦 [1/5] Installing system packages..."
apt update -qq
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    x11vnc \
    xvfb \
    wget \
    curl \
    > /dev/null 2>&1

# Install Chrome
if ! command -v google-chrome &> /dev/null; then
    echo "🌐 [1/5] Installing Google Chrome..."
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - > /dev/null 2>&1
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
    apt update -qq
    apt install -y google-chrome-stable > /dev/null 2>&1
fi

echo "✅ [1/5] Packages installed"

# ============= STEP 2: CREATE APP =============
echo "🐍 [2/5] Creating Python app..."

mkdir -p /opt/yt-dlp-app
cd /opt/yt-dlp-app

# Create virtualenv
python3 -m venv venv > /dev/null 2>&1
source venv/bin/activate

# Create requirements.txt
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

# Install Python packages
pip install -q -r requirements.txt

# Create app.py
cat > app.py << 'PYEOF'
#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

def get_video_info(video_url):
    methods = [
        {'name': 'Android SSL', 'opts': {'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage', 'configs']}}, 'no_check_certificate': True}},
        {'name': 'iOS Headers', 'opts': {'extractor_args': {'youtube': {'player_client': ['ios', 'android']}}, 'http_headers': {'User-Agent': 'com.google.ios.youtube/19.09.3'}, 'no_check_certificate': True}},
        {'name': 'Multi-Client', 'opts': {'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'tv_embedded', 'web']}}, 'no_check_certificate': True}},
        {'name': 'TV Embedded', 'opts': {'extractor_args': {'youtube': {'player_client': ['tv_embedded', 'android']}}, 'age_limit': 99, 'no_check_certificate': True}},
        {'name': 'Combined', 'opts': {'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'tv_embedded', 'web', 'mweb'], 'player_skip': ['webpage']}}, 'age_limit': 99, 'no_check_certificate': True}},
    ]

    for i, method in enumerate(methods, 1):
        try:
            opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'socket_timeout': 30, 'cookiesfrombrowser': ('chrome',)}
            opts.update(method['opts'])
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {'status': 'success', 'method': i, 'name': method['name'], 'title': info.get('title'), 'duration': info.get('duration'), 'formats': len(info.get('formats', [])), 'views': info.get('view_count'), 'uploader': info.get('uploader'), 'cookies': True}
        except Exception as e:
            continue
    raise Exception("All methods failed")

@app.route('/')
def index():
    return jsonify({'status': 'running', 'message': 'yt-dlp VPS with Chrome cookies', 'methods': 5})

@app.route('/api/info', methods=['GET', 'POST', 'OPTIONS'])
def api_info():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True}), 200
    url = request.args.get('url') if request.method == 'GET' else request.get_json().get('url')
    if not url:
        return jsonify({'error': 'No URL'}), 400
    try:
        return jsonify(get_video_info(url)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
PYEOF

chmod +x app.py
echo "✅ [2/5] App created"

# ============= STEP 3: CREATE SYSTEMD SERVICE =============
echo "⚙️  [3/5] Creating systemd service..."

cat > /etc/systemd/system/yt-dlp.service << 'EOF'
[Unit]
Description=yt-dlp VPS Server
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/opt/yt-dlp-app
Environment="PATH=/opt/yt-dlp-app/venv/bin"
ExecStart=/opt/yt-dlp-app/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable yt-dlp > /dev/null 2>&1
echo "✅ [3/5] Service created"

# ============= STEP 4: CONFIGURE NGINX =============
echo "🌐 [4/5] Configuring Nginx..."

cat > /etc/nginx/sites-available/yt-dlp << 'EOF'
server {
    listen 80;
    server_name _;

    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/yt-dlp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t > /dev/null 2>&1
systemctl restart nginx
echo "✅ [4/5] Nginx configured"

# ============= STEP 5: START SERVICES =============
echo "🚀 [5/5] Starting services..."

systemctl start yt-dlp
sleep 2

echo "✅ [5/5] Services started"

# ============= GET EXTERNAL IP =============
EXTERNAL_IP=$(curl -s ifconfig.me)

# ============= SUMMARY =============
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ INSTALLATION COMPLETE!                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Server URL: http://$EXTERNAL_IP"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  Start VNC server (to login to Chrome):"
echo "   sudo x11vnc -create -forever -bg"
echo ""
echo "2️⃣  Connect with VNC Viewer:"
echo "   Download: https://www.realvnc.com/en/connect/download/viewer/"
echo "   Connect to: $EXTERNAL_IP:5900"
echo ""
echo "3️⃣  In VNC window:"
echo "   - Open terminal"
echo "   - Run: google-chrome"
echo "   - Go to youtube.com"
echo "   - LOGIN to your YouTube account"
echo "   - Close Chrome"
echo ""
echo "4️⃣  Test the API:"
echo "   curl 'http://$EXTERNAL_IP/api/info?url=https://youtube.com/watch?v=dQw4w9WgXcQ'"
echo ""
echo "💡 Once you login to Chrome, ALL videos work automatically!"
echo ""
echo "📊 Useful commands:"
echo "   Status:  sudo systemctl status yt-dlp"
echo "   Logs:    sudo journalctl -u yt-dlp -f"
echo "   Restart: sudo systemctl restart yt-dlp"
echo ""
echo "🎉 Happy downloading!"
echo ""
