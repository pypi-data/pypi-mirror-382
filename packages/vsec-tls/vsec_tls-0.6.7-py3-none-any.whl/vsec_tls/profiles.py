import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Profile definitions
PROFILES = {
    "chrome_139_windows": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0",
        "alpn": ["h2", "http/1.1"],
        "http_headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.66 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Chromium";v="139", "Google Chrome";v="139", "Not=A?Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-wow64": "?0",
            "sec-ch-ua-platform-version": '"15.0.0"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "dnt": "1"
        },
        "http2_settings": {
            "header_table_size": 65536,
            "enable_push": False,
            "max_concurrent_streams": 1000,
            "initial_window_size": 6291456,
            "max_frame_size": 16384,
            "max_header_list_size": 262144
        },
        "pseudo_header_order": [":method", ":authority", ":scheme", ":path"],
        "connection_flow": 15663105,
        "tls_padding": 512,
        "force_http1": False,
        "enable_grease": True,
        "randomize_extension_order": False,
        "tcp_stealth": False,
        "http_version": "2",
        "platform": {
            "name": "Windows",
            "version": "15.0.0",
            "mobile": False
        }
    },
    "chrome_112_macos": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0",
        "alpn": ["h2", "http/1.1"],
        "http_headers": {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        },
        "http2_settings": {
            "header_table_size": 65536,
            "enable_push": False,
            "max_concurrent_streams": 1000,
            "initial_window_size": 6291456,
            "max_frame_size": 16384,
            "max_header_list_size": 262144
        },
        "pseudo_header_order": [":method", ":authority", ":scheme", ":path"],
        "connection_flow": 15663105,
        "tls_padding": 512,
        "force_http1": False,
        "enable_grease": True,
        "randomize_extension_order": False,
        "tcp_stealth": False,
        "http_version": "2",
        "platform": {
            "name": "macOS",
            "version": "10.15.7",
            "mobile": False
        }
    },
    "chrome_android_13": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0",
        "alpn": ["h2", "http/1.1"],
        "http_headers": {
            "user-agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.6099.99 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Chromium";v="139", "Google Chrome";v="139", "Not=A?Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "x-requested-with": "com.android.chrome"
        },
        "http2_settings": {
            "header_table_size": 65536,
            "enable_push": False,
            "max_concurrent_streams": 100,
            "initial_window_size": 6291456,
            "max_frame_size": 16384,
            "max_header_list_size": 262144
        },
        "pseudo_header_order": [":method", ":authority", ":scheme", ":path"],
        "connection_flow": 15663105,
        "tls_padding": 256,
        "force_http1": False,
        "enable_grease": True,
        "randomize_extension_order": False,
        "tcp_stealth": True,
        "http_version": "2",
        "platform": {
            "name": "Android",
            "version": "chrome-mobile-13",
            "mobile": True
        }
    },
    "okhttp_android_12": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-13-51-45-43,29-23-24,0",
        "alpn": ["h2", "http/1.1"],
        "http_headers": {
            "user-agent": "okhttp/4.12.0",
            "accept": "*/*",
            "accept-encoding": "gzip",
            "connection": "keep-alive"
        },
        "http2_settings": {
            "header_table_size": 4096,
            "enable_push": False,
            "max_concurrent_streams": 100,
            "initial_window_size": 65535,
            "max_frame_size": 16384,
            "max_header_list_size": 8192
        },
        "pseudo_header_order": [":method", ":path", ":authority", ":scheme"],
        "connection_flow": 12517377,
        "tls_padding": 0,
        "force_http1": False,
        "enable_grease": False,
        "randomize_extension_order": False,
        "tcp_stealth": True,
        "http_version": "2",
        "platform": {
            "name": "Android",
            "version": "okhttp-4.12",
            "mobile": True
        }
    },
    "webview_android_11": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0",
        "alpn": ["h2", "http/1.1"],
        "http_headers": {
            "user-agent": "Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/118.0.0.0 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "x-requested-with": "com.example.app"
        },
        "http2_settings": {
            "header_table_size": 65536,
            "enable_push": False,
            "max_concurrent_streams": 100,
            "initial_window_size": 6291456,
            "max_frame_size": 16384,
            "max_header_list_size": 262144
        },
        "pseudo_header_order": [":method", ":authority", ":scheme", ":path"],
        "connection_flow": 15663105,
        "tls_padding": 256,
        "force_http1": False,
        "enable_grease": True,
        "randomize_extension_order": False,
        "tcp_stealth": True,
        "http_version": "2",
        "platform": {
            "name": "Android",
            "version": "webview-11",
            "mobile": True
        }
    }
}


def get_profile(name: str) -> Dict[str, Any]:
    """Get a profile by name.

    Args:
        name: Profile name

    Returns:
        Profile dictionary

    Raises:
        ValueError: If profile not found
    """
    if name not in PROFILES:
        available = ", ".join(PROFILES.keys())
        raise ValueError(f"Profile '{name}' not found. Available profiles: {available}")

    return PROFILES[name].copy()


def list_profiles() -> List[str]:
    """Get list of available profile names."""
    return list(PROFILES.keys())


def create_custom_profile(
        name: str,
        ja3: str,
        alpn: List[str],
        headers: Dict[str, str],
        http2_settings: Optional[Dict[str, Any]] = None,
        save: bool = False,
        output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Create a custom profile.

    Args:
        name: Profile name for internal storage
        ja3: JA3 fingerprint
        alpn: ALPN protocols
        headers: HTTP headers
        http2_settings: HTTP/2 settings
        save: Save to PROFILES dict
        output_path: Save to JSON file

    Returns:
        Profile dictionary
    """
    profile = {
        "ja3": ja3,
        "alpn": alpn,
        "http_headers": headers
    }

    if http2_settings:
        profile["http2_settings"] = http2_settings

    if save:
        PROFILES[name] = profile

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)

    return profile