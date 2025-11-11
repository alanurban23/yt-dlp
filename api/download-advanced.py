from http.server import BaseHTTPRequestHandler
import json
import yt_dlp
import os
import tempfile

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', 'demo-token')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            video_url = data.get('url')
            if not video_url:
                self.send_error_response(400, 'Missing video URL')
                return

            # Try all 5 methods in sequence until one works
            methods = [
                self.method_1_android_ssl_bypass,
                self.method_2_ios_custom_headers,
                self.method_3_multi_client_fallback,
                self.method_4_tv_embedded,
                self.method_5_combined_ultimate,
            ]

            last_error = None
            for i, method in enumerate(methods, 1):
                try:
                    result = method(video_url)
                    result['method_used'] = f'Method {i}'
                    result['method_name'] = method.__name__.replace('_', ' ').title()

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    return
                except Exception as e:
                    last_error = str(e)
                    continue

            # All methods failed
            self.send_error_response(500, f'All 5 methods failed. Last error: {last_error}')

        except Exception as e:
            self.send_error_response(500, f'Request error: {str(e)}')

    def method_1_android_ssl_bypass(self, video_url):
        """
        METHOD 1: Android Client with SSL Bypass
        - Uses Android mobile API
        - Bypasses SSL certificate verification
        - Skips webpage extraction for speed
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720]',
            'socket_timeout': 30,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'no_check_certificate': True,
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            return {
                'status': 'success',
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'formats_count': len(info.get('formats', [])),
                'description': 'Android client with SSL bypass',
            }

    def method_2_ios_custom_headers(self, video_url):
        """
        METHOD 2: iOS Client with Custom Headers
        - Emulates iOS YouTube app
        - Custom user agent and headers
        - Multiple client fallback
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720]',
            'socket_timeout': 30,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                    'player_skip': ['webpage'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
                'X-YouTube-Client-Name': '5',
                'X-YouTube-Client-Version': '19.09.3',
            },
            'no_check_certificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            return {
                'status': 'success',
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'formats_count': len(info.get('formats', [])),
                'description': 'iOS client with custom headers',
            }

    def method_3_multi_client_fallback(self, video_url):
        """
        METHOD 3: Multi-Client Fallback Chain
        - Tries multiple YouTube clients
        - Android mobile user agent
        - Accept language headers
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720]',
            'socket_timeout': 30,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'tv_embedded', 'web'],
                    'player_skip': ['configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            },
            'no_check_certificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            return {
                'status': 'success',
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'formats_count': len(info.get('formats', [])),
                'description': 'Multi-client fallback chain',
            }

    def method_4_tv_embedded(self, video_url):
        """
        METHOD 4: TV Embedded Client
        - Uses YouTube TV client
        - Embedded player bypass
        - Age restriction override
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720]',
            'socket_timeout': 30,
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv_embedded', 'android'],
                    'player_skip': [],
                }
            },
            'age_limit': 99,
            'no_check_certificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            return {
                'status': 'success',
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'formats_count': len(info.get('formats', [])),
                'description': 'TV embedded client',
            }

    def method_5_combined_ultimate(self, video_url):
        """
        METHOD 5: Combined Ultimate Method
        - All techniques combined
        - Maximum compatibility
        - Nuclear option - tries everything
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720]',
            'socket_timeout': 45,
            'retries': 3,
            'fragment_retries': 3,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'tv_embedded', 'web', 'mweb', 'android_creator'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/19.09.36 (Linux; U; Android 13) gzip',
                'X-YouTube-Client-Name': '3',
                'X-YouTube-Client-Version': '19.09.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
            },
            'age_limit': 99,
            'no_check_certificate': True,
            'nocheckcertificate': True,
            'prefer_insecure': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            return {
                'status': 'success',
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'formats_count': len(info.get('formats', [])),
                'view_count': info.get('view_count', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'description': 'Combined ultimate method - all techniques',
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
