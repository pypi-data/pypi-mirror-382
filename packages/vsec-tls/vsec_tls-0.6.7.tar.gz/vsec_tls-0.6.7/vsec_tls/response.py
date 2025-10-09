import json
from typing import Dict, Any, Optional, Union


class Response:
    """Response object similar to requests.Response."""

    def __init__(
            self,
            status_code: int,
            headers: Dict[str, str],
            content: Union[str, bytes],
            url: str,
            request_headers: Dict[str, str],
            tls_version: str = "",
            cipher_suite: str = "",
            ja3_hash: str = ""
    ):
        self.status_code = status_code
        self.headers = headers
        self._raw_content = content
        self.url = url
        self.request = type('Request', (), {
            'headers': request_headers,
            'url': url
        })()

        # TLS info
        self.tls_version = tls_version
        self.cipher_suite = cipher_suite
        self.ja3_hash = ja3_hash

        # Store both string and bytes versions intelligently
        if isinstance(content, bytes):
            self._content_bytes = content
            self._content_text = self._decode_bytes_to_text(content)
        else:
            self._content_text = content
            self._content_bytes = self._encode_text_to_bytes(content)

        # Parse cookies
        self.cookies = self._parse_cookies()

    def _decode_bytes_to_text(self, content_bytes: bytes) -> str:
        """Safely decode bytes to text."""
        # Try to detect encoding from headers
        content_type = self.headers.get('content-type', '').lower()
        encoding = 'utf-8'  # default

        if 'charset=' in content_type:
            try:
                encoding = content_type.split('charset=')[-1].split(';')[0].strip()
            except:
                encoding = 'utf-8'

        # For binary content types, don't try to decode as text
        binary_types = ['application/pdf', 'image/', 'video/', 'audio/', 'application/octet-stream']
        if any(bt in content_type for bt in binary_types):
            return f"[BINARY CONTENT - {len(content_bytes)} bytes]"

        try:
            return content_bytes.decode(encoding)
        except UnicodeDecodeError:
            try:
                return content_bytes.decode('utf-8', errors='replace')
            except:
                try:
                    return content_bytes.decode('latin1')
                except:
                    return f"[BINARY CONTENT - {len(content_bytes)} bytes]"

    def _encode_text_to_bytes(self, content_text: str) -> bytes:
        """Encode text to bytes."""
        if content_text.startswith('[BINARY CONTENT'):
            return b''  # Can't reconstruct binary from placeholder
        return content_text.encode('utf-8')

    @property
    def content(self) -> bytes:
        """Response content as bytes."""
        return self._content_bytes

    @property
    def text(self) -> str:
        """Response content as text."""
        # If this is binary content, don't try to decode
        content_type = self.headers.get('content-type', '').lower()
        binary_types = ['application/pdf', 'image/', 'video/', 'audio/', 'application/octet-stream']

        if any(bt in content_type for bt in binary_types):
            return f"[BINARY CONTENT - {len(self._content_bytes)} bytes - Use .content for raw bytes]"

        return self._content_text

    def json(self) -> Any:
        """Parse response as JSON."""
        return json.loads(self.text)

    @property
    def ok(self) -> bool:
        """Returns True if status_code is less than 400."""
        return self.status_code < 400

    @property
    def is_redirect(self) -> bool:
        """Returns True if this response is a redirect."""
        return self.status_code in (301, 302, 303, 307, 308)

    @property
    def is_permanent_redirect(self) -> bool:
        """Returns True if this response is a permanent redirect."""
        return self.status_code in (301, 308)

    def raise_for_status(self):
        """Raises an HTTPError if status code indicates an error."""
        if not self.ok:
            from .exceptions import TlsClientError
            raise TlsClientError(f"HTTP {self.status_code} Error for URL: {self.url}")

    def _parse_cookies(self) -> Dict[str, str]:
        """Parse cookies from response headers."""
        cookies = {}

        set_cookie = self.headers.get('set-cookie', '')
        if not set_cookie:
            return cookies

        # Split by comma, but only if followed by a space and word character
        import re
        cookie_parts = re.split(r',\s*(?=[a-zA-Z])', set_cookie)

        for cookie in cookie_parts:
            # Get only the name=value part (before first semicolon)
            main_part = cookie.split(';')[0].strip()
            if '=' in main_part:
                name, value = main_part.split('=', 1)
                cookies[name.strip()] = value.strip()

        return cookies

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

    def __bool__(self) -> bool:
        """Returns True if status_code is less than 400."""
        return self.ok