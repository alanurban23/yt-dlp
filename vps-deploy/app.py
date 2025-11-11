#!/usr/bin/env python3
"""
🚀 yt-dlp VPS Server - Automatyczne cookies z Chrome
Działa z 5 metodami bypass + wspólne konto YouTube
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Automatycznie użyje cookies z Chrome na serwerze!
CHROME_USER = os.environ.get('CHROME_USER', 'root')

def get_video_info_with_methods(video_url):
    """
    Testuje 5 metod z automatycznymi cookies z Chrome
    """

    # 5 METOD HAKOWANIA
    methods = [
        {
            'name': 'Method 1: Android Client + SSL Bypass',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'no_check_certificate': True,
            }
        },
        {
            'name': 'Method 2: iOS Custom Headers',
            'opts': {
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
        },
        {
            'name': 'Method 3: Multi-Client Fallback',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios', 'tv_embedded', 'web'],
                        'player_skip': ['configs'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                'no_check_certificate': True,
            }
        },
        {
            'name': 'Method 4: TV Embedded Client',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv_embedded', 'android'],
                        'player_skip': [],
                    }
                },
                'age_limit': 99,
                'no_check_certificate': True,
            }
        },
        {
            'name': 'Method 5: Combined Ultimate',
            'opts': {
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
                },
                'age_limit': 99,
                'no_check_certificate': True,
                'prefer_insecure': True,
            }
        }
    ]

    # Try each method WITH automatic Chrome cookies!
    for i, method in enumerate(methods, 1):
        try:
            print(f"🔧 Trying {method['name']}...")

            # Base options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'socket_timeout': 30,
            }

            # Merge with method-specific options
            ydl_opts.update(method['opts'])

            # 🔥 MAGIC: Automatycznie użyj cookies z Chrome!
            ydl_opts['cookiesfrombrowser'] = ('chrome',)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                return {
                    'status': 'success',
                    'method_used': f'Method {i}',
                    'method_name': method['name'],
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'formats_count': len(info.get('formats', [])),
                    'view_count': info.get('view_count', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': method['name'] + ' + Chrome cookies (automatic!)',
                    'cookies_used': True,
                    'server': 'Google Cloud Compute Engine'
                }

        except Exception as e:
            print(f"❌ {method['name']} failed: {str(e)[:100]}")
            continue

    # All methods failed
    raise Exception("All 5 methods failed. Video may be unavailable or deleted.")


@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'yt-dlp VPS Server with automatic Chrome cookies',
        'methods': 5,
        'cookies': 'automatic from Chrome',
        'server': 'Google Cloud Compute Engine'
    })


@app.route('/api/info', methods=['GET', 'POST', 'OPTIONS'])
def get_info():
    """
    GET /api/info?url=VIDEO_URL
    POST /api/info with JSON: {"url": "VIDEO_URL"}
    """

    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    # Get URL from query param or JSON body
    if request.method == 'GET':
        video_url = request.args.get('url')
    else:
        data = request.get_json() or {}
        video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'Missing video URL'}), 400

    try:
        result = get_video_info_with_methods(video_url)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True)
