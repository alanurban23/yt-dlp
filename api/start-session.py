from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import os

# Browserless API endpoint (can use free tier)
BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', 'demo-token')
BROWSERLESS_URL = f'https://chrome.browserless.io/session?token={BROWSERLESS_TOKEN}'

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Start a new browser session
            req_data = {
                'launch': {
                    'headless': False,
                    'args': ['--no-sandbox', '--disable-setuid-sandbox'],
                    'defaultViewport': {'width': 1280, 'height': 1024}
                },
                'navigate': {
                    'url': 'https://accounts.google.com/ServiceLogin?service=youtube&continue=https://www.youtube.com/',
                    'waitUntil': 'networkidle2'
                }
            }

            req = urllib.request.Request(
                BROWSERLESS_URL,
                data=json.dumps(req_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                session_data = {
                    'sessionId': result.get('sessionId'),
                    'wsEndpoint': result.get('wsEndpoint'),
                    'viewUrl': f"https://chrome.browserless.io/devtools/inspector.html?wss={result.get('wsEndpoint')}",
                    'message': 'Browser session started. Click the link to login.'
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(session_data).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': f'Failed to start session: {str(e)}',
                'fallback': True
            }).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
