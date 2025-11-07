from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import urllib.request
import os
import tempfile
import subprocess
import base64

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', 'demo-token')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            video_url = data.get('url')
            if not video_url:
                self.send_error_response(400, 'Missing video URL')
                return

            # Use Browserless to bypass YouTube restrictions
            cookies = self.get_youtube_cookies_via_browser()

            # Download video using yt-dlp with cookies
            result = self.download_video(video_url, cookies)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_error_response(500, f'Download failed: {str(e)}')

    def get_youtube_cookies_via_browser(self):
        """Use Browserless to get authenticated YouTube cookies"""
        try:
            function_url = f'https://chrome.browserless.io/function?token={BROWSERLESS_TOKEN}'

            # JavaScript to login and get cookies
            js_code = """
            module.exports = async ({ page }) => {
                // Navigate to YouTube
                await page.goto('https://www.youtube.com', {
                    waitUntil: 'networkidle2',
                    timeout: 30000
                });

                // Accept cookies consent if present
                try {
                    await page.waitForSelector('button[aria-label*="Accept"]', { timeout: 5000 });
                    await page.click('button[aria-label*="Accept"]');
                    await page.waitForTimeout(1000);
                } catch (e) {
                    // No consent dialog
                }

                // Get all cookies
                const cookies = await page.cookies();

                // Convert to Netscape format for yt-dlp
                let netscapeCookies = '# Netscape HTTP Cookie File\\n';
                for (const cookie of cookies) {
                    const domain = cookie.domain.startsWith('.') ? cookie.domain : '.' + cookie.domain;
                    const flag = domain.startsWith('.') ? 'TRUE' : 'FALSE';
                    const path = cookie.path || '/';
                    const secure = cookie.secure ? 'TRUE' : 'FALSE';
                    const expiration = cookie.expires ? Math.floor(cookie.expires) : '0';

                    netscapeCookies += `${domain}\\t${flag}\\t${path}\\t${secure}\\t${expiration}\\t${cookie.name}\\t${cookie.value}\\n`;
                }

                return {
                    cookies: netscapeCookies,
                    count: cookies.length
                };
            };
            """

            req_data = {'code': js_code}
            req = urllib.request.Request(
                function_url,
                data=json.dumps(req_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('cookies', '')

        except Exception as e:
            print(f'Cookie fetch error: {e}')
            return ''

    def download_video(self, video_url, cookies_content):
        """Download video using yt-dlp with cookies"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save cookies to temp file
            cookies_file = os.path.join(tmpdir, 'cookies.txt')
            if cookies_content:
                with open(cookies_file, 'w') as f:
                    f.write(cookies_content)

            output_template = os.path.join(tmpdir, 'video.%(ext)s')

            # yt-dlp command with cookies
            cmd = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '-f', 'best[height<=720]',  # Limit to 720p for faster download
                '--max-filesize', '100M',    # Limit file size
                '--socket-timeout', '30',
                '-o', output_template,
            ]

            if cookies_content:
                cmd.extend(['--cookies', cookies_file])

            # Add YouTube-specific options
            cmd.extend([
                '--extractor-args', 'youtube:player_client=android',
                video_url
            ])

            # Execute download
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise Exception(f'yt-dlp error: {result.stderr}')

            # Find downloaded file
            files = [f for f in os.listdir(tmpdir) if f.startswith('video.')]
            if not files:
                raise Exception('No video file was downloaded')

            video_file = os.path.join(tmpdir, files[0])

            # Get file info
            file_size = os.path.getsize(video_file)

            # For demo purposes, return info instead of actual file
            # In production, you'd upload to storage and return URL
            return {
                'status': 'success',
                'message': 'Video downloaded successfully',
                'filename': files[0],
                'size': file_size,
                'size_mb': round(file_size / 1024 / 1024, 2),
                'note': 'Video downloaded server-side. In production, this would be uploaded to cloud storage.'
            }

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
