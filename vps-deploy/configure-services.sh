#!/bin/bash
#
# 🔧 CONFIGURE SERVICES - Systemd + Nginx
# Uruchom po skopiowaniu app.py: sudo bash configure-services.sh
#

set -e

echo "🔧 Configuring services..."

# Create systemd service
echo "📝 Creating systemd service..."
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

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/yt-dlp << 'EOF'
server {
    listen 80;
    server_name _;

    # Increase timeouts for long-running requests
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/yt-dlp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

# Start and enable services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable yt-dlp
systemctl start yt-dlp
systemctl restart nginx

echo ""
echo "✅ Services configured and started!"
echo ""
echo "📊 Status check:"
systemctl status yt-dlp --no-pager | head -10
echo ""
echo "🌐 Server is running!"
echo "   Local: http://localhost"
echo "   External: http://<your-vm-ip>"
echo ""
echo "📝 Useful commands:"
echo "   Status: sudo systemctl status yt-dlp"
echo "   Logs: sudo journalctl -u yt-dlp -f"
echo "   Restart: sudo systemctl restart yt-dlp"
echo ""
