#!/usr/bin/env python3
"""
5 Hackerskich Sposobów Pobierania Restricted YouTube Videos
Test URL: https://www.youtube.com/watch?v=MgqLAp4F3co
"""

import yt_dlp
import json
import ssl
import certifi

TEST_URL = 'https://www.youtube.com/watch?v=MgqLAp4F3co'

def print_result(method_name, success, info=None, error=None):
    """Print formatted test result"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"\n{'='*60}")
    print(f"{status} - {method_name}")
    print(f"{'='*60}")
    if success and info:
        print(f"Title: {info.get('title', 'Unknown')}")
        print(f"Duration: {info.get('duration', 0)}s")
        print(f"Formats available: {len(info.get('formats', []))}")
        print(f"Age limit: {info.get('age_limit', 0)}")
    if error:
        print(f"Error: {str(error)[:200]}")
    print()


def method_1_android_client():
    """
    METHOD 1: Android Client with SSL bypass
    Emulates Android app to bypass web restrictions
    """
    print("\n🔧 Testing Method 1: Android Client Emulation...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'no_check_certificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(TEST_URL, download=False)
            print_result("Method 1: Android Client", True, info)
            return True, info
    except Exception as e:
        print_result("Method 1: Android Client", False, error=e)
        return False, None


def method_2_ios_client():
    """
    METHOD 2: iOS Client with custom headers
    Emulates iOS Safari/YouTube app
    """
    print("\n🔧 Testing Method 2: iOS Client Emulation...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android'],
                'player_skip': ['webpage'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
        },
        'no_check_certificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(TEST_URL, download=False)
            print_result("Method 2: iOS Client", True, info)
            return True, info
    except Exception as e:
        print_result("Method 2: iOS Client", False, error=e)
        return False, None


def method_3_tv_embed():
    """
    METHOD 3: TV Client + Embedded player
    Uses YouTube TV and embedded player APIs
    """
    print("\n🔧 Testing Method 3: TV/Embedded Client...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv_embedded', 'android', 'web'],
                'player_skip': [],
            }
        },
        'age_limit': 99,  # Allow age-restricted content
        'no_check_certificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(TEST_URL, download=False)
            print_result("Method 3: TV/Embedded", True, info)
            return True, info
    except Exception as e:
        print_result("Method 3: TV/Embedded", False, error=e)
        return False, None


def method_4_all_clients():
    """
    METHOD 4: Multi-client fallback chain
    Tries multiple clients in sequence until one works
    """
    print("\n🔧 Testing Method 4: Multi-Client Fallback...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'tv_embedded', 'web', 'mweb'],
                'player_skip': ['configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'no_check_certificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(TEST_URL, download=False)
            print_result("Method 4: Multi-Client", True, info)
            return True, info
    except Exception as e:
        print_result("Method 4: Multi-Client", False, error=e)
        return False, None


def method_5_po_token():
    """
    METHOD 5: PO Token extraction (Advanced)
    Uses proof of origin token for enhanced authentication
    """
    print("\n🔧 Testing Method 5: PO Token Method...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android_creator', 'android', 'ios'],
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
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(TEST_URL, download=False)
            print_result("Method 5: PO Token", True, info)
            return True, info
    except Exception as e:
        print_result("Method 5: PO Token", False, error=e)
        return False, None


def main():
    """Run all 5 methods and report results"""
    print("\n" + "="*60)
    print("🎯 Testing 5 Hacking Methods for Restricted YouTube Videos")
    print("="*60)
    print(f"Target: {TEST_URL}")
    print("="*60)

    results = []

    # Test each method
    methods = [
        ("Method 1: Android Client", method_1_android_client),
        ("Method 2: iOS Client", method_2_ios_client),
        ("Method 3: TV/Embedded", method_3_tv_embed),
        ("Method 4: Multi-Client", method_4_all_clients),
        ("Method 5: PO Token", method_5_po_token),
    ]

    for name, method_func in methods:
        success, info = method_func()
        results.append({
            'name': name,
            'success': success,
            'info': info
        })

    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)

    working_methods = [r for r in results if r['success']]

    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['name']}")

    print(f"\n✅ Working methods: {len(working_methods)}/5")

    if working_methods:
        print("\n🎉 RECOMMENDED METHOD:")
        best = working_methods[0]
        print(f"   {best['name']}")
        print(f"   Title: {best['info'].get('title', 'Unknown')}")
        return best
    else:
        print("\n⚠️  No methods worked. Video may require cookies or be unavailable.")
        return None


if __name__ == '__main__':
    best_method = main()
    if best_method:
        print(f"\n✅ Use {best_method['name']} in production!")
