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
    def do_GET(self):
        try:
            # Parse URL and query parameters
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)

            # Get the video URL from query parameters
            video_url = query_params.get('url', [None])[0]

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
                # Limit processing time
                'socket_timeout': 20,
                # Better user agent to avoid bot detection
                'user_agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
                # YouTube specific options - aggressive bypass strategy
                'extractor_args': {
                    'youtube': {
                        # Try multiple clients in order - android works best for bot detection
                        'player_client': ['android', 'tv_embedded', 'ios'],
                        # Skip webpage and configs to use API directly
                        'player_skip': ['webpage', 'configs'],
                        # Skip formats that might trigger additional checks
                        'skip': ['dash', 'hls', 'translated_subs'],
                    }
                },
                # Additional headers to mimic Android app
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'X-YouTube-Client-Name': '3',
                    'X-YouTube-Client-Version': '19.09.37',
                },
                'no_check_certificate': True,
                # Force IPv4 to avoid some regional blocks
                'source_address': '0.0.0.0',
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
