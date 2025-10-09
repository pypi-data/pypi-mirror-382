import sys
import platform
import json
import base64
from pathlib import Path
from typing import Dict, Any, Union, Optional

from vsec_tls.exceptions import PlatformNotSupportedError


def detect_platform_lib() -> str:
    """Detect the correct library path based on the platform."""
    system = platform.system().lower()
    lib_name = {
        'darwin': 'libtls_client.dylib',
        'linux': 'libtls_client.so',
        'windows': 'tls_client.dll'
    }.get(system)

    if not lib_name:
        raise PlatformNotSupportedError(f"Unsupported platform: {system}")

    lib_path = Path(__file__).parent / 'lib' / system / lib_name
    if not lib_path.exists():
        raise FileNotFoundError(f"Library not found at: {lib_path}")

    return str(lib_path)


def prepare_body(body: Union[str, bytes, dict]) -> str:
    """Convert different body types to raw string."""
    if isinstance(body, str):
        return body  # Direkt zurück
    elif isinstance(body, bytes):
        return body.decode('utf-8')  # Als UTF-8 String
    elif isinstance(body, dict):
        return json.dumps(body)  # Als JSON-String
    raise ValueError(f"Unsupported body type: {type(body)}")


def guess_content_type(body: Union[str, bytes, dict]) -> str:
    """Guess content type based on body."""
    if isinstance(body, dict):
        return "application/json"
    elif isinstance(body, bytes):
        return "application/octet-stream"
    elif isinstance(body, str):
        try:
            json.loads(body)
            return "application/json"
        except:
            return "text/plain"
    return "application/octet-stream"