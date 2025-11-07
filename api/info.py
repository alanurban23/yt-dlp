from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
import os

# Add the parent directory to the path to import yt_dlp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        try:
            video_url = None

            # Handle GET request
            if self.command == 'GET':
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                video_url = query_params.get('url', [None])[0]

            # Handle POST request
            elif self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode('utf-8'))
                    video_url = data.get('url')
                    # cookies_data = data.get('cookies')  # TODO: Implement cookies

            if not video_url:
                self.send_error_response(400, 'Missing url parameter')
                return

            if yt_dlp is None:
                self.send_error_response(500, 'yt-dlp not available')
                return

            # Configure yt-dlp options with advanced YouTube bypass
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
                # Extended timeout for better success rate
                'socket_timeout': 20,
                # YouTube specific options - use android for best results
                'extractor_args': {
                    'youtube': {
                        # Android client works best for bypassing bot detection
                        'player_client': ['android'],
                        # Skip webpage and configs to use API directly
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'no_check_certificate': True,
            }

            # Extract video information
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                # Check if extraction failed
                if info is None:
                    self.send_error_response(400, 'Failed to extract video information. The video may be restricted or unavailable.')
                    return

                # Prepare response data with essential fields
                response_data = {
                    'title': info.get('title'),
                    'uploader': info.get('uploader'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'upload_date': info.get('upload_date'),
                    'description': info.get('description'),
                    'thumbnail': info.get('thumbnail'),
                    'webpage_url': info.get('webpage_url'),
                    'extractor': info.get('extractor'),
                    'formats': [
                        {
                            'format_id': f.get('format_id'),
                            'ext': f.get('ext'),
                            'quality': f.get('quality'),
                            'filesize': f.get('filesize'),
                        }
                        for f in (info.get('formats') or [])[:10]  # Limit to first 10 formats
                    ] if info.get('formats') else []
                }

                self.send_success_response(response_data)

        except yt_dlp.utils.DownloadError as e:
            self.send_error_response(400, f'Download error: {str(e)}')
        except Exception as e:
            self.send_error_response(500, f'Server error: {str(e)}')

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
