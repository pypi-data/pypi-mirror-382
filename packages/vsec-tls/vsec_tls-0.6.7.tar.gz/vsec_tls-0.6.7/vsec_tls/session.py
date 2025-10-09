import json as js
import base64
import sys
from typing import Union, List, Optional, Dict, Any
from urllib.parse import urlparse
from .exceptions import TlsClientError
from .response import Response
from .utils import prepare_body, guess_content_type
from .profiles import get_profile
from .c_interface_wrapper import _tls_client


class TlsSession:
    """Session object for persistent connections with cookie handling.

    Parameters
    ----------
    license_key : str
        Your Velum Secure license key (required)
    api_key : str
        Your Velum Secure API key (required)
    ja3 : str, optional
        JA3 fingerprint string (format: "tls_version,ciphers,extensions,curves,point_formats")
        Example: "771,4865-4866-4867-49195,0-23-65281-10-11-35,29-23-24,0"
    alpn : list of str, optional
        Application-Layer Protocol Negotiation protocols
        Example: ["http/1.1"] or ["h2", "http/1.1"]
    proxy : dict, optional
        Proxy configuration with keys:
        - type: "socks5" or "http"
        - host: proxy hostname
        - port: proxy port
        - username: optional proxy username
        - password: optional proxy password
    http2_settings : dict, optional
        HTTP/2 settings with keys:
        - header_table_size: int (default: 65536)
        - enable_push: bool (default: False)
        - max_concurrent_streams: int (default: 1000)
        - initial_window_size: int (default: 6291456)
        - max_frame_size: int (default: 16384)
        - max_header_list_size: int (default: 262144)
    tls_padding : int, optional
        TLS padding size in bytes
    headers : dict, optional
        Default HTTP headers for all requests
    cookies : dict, optional
        Default cookies for all requests
    timeout : float, optional
        Request timeout in seconds (default: 30.0)
    verify : bool, optional
        Legacy parameter for SSL verification (default: True)
    default_profile : str, optional
        Browser profile to use (default: "chrome_139_windows")
    force_tls13 : bool, optional
        Force TLS 1.3 only (default: False)
    min_tls_version : str, optional
        Minimum TLS version: "1.2" or "1.3"
    disable_extension_filtering : bool, optional
        Disable TLS extension filtering (default: False)
    openssl_compat_mode : bool, optional
        Enable OpenSSL compatibility mode - forces TLS 1.2 only (default: False)
    extended_profile : str, optional
        Use extended profile: "chrome_android_111" or "chrome_108"
    connection_flow : int, optional
        HTTP/2 connection flow window size (e.g., 15663105)
    pseudo_header_order : list of str, optional
        Order of HTTP/2 pseudo headers
        Example: [":method", ":authority", ":scheme", ":path"]
    settings_order : list of int, optional
        Order of HTTP/2 SETTINGS frame IDs
        Example: [1, 2, 3, 4, 6] for HEADER_TABLE_SIZE, ENABLE_PUSH, etc.
    random_tls_extension_order : bool, optional
        Randomize TLS extension order (default: False)
    verify_certificates : bool, optional
        Enable SSL certificate verification (default: True)
        Set to False to disable certificate validation (useful for testing/debugging)

    Examples
    --------
    Basic usage with certificate verification:

    >>> session = TlsSession(
    ...     license_key="your_license_key",
    ...     api_key="your_api_key"
    ... )

    Disable certificate verification for testing:

    >>> session = TlsSession(
    ...     license_key="your_license_key",
    ...     api_key="your_api_key",
    ...     verify_certificates=False
    ... )

    Advanced usage with custom JA3 and HTTP/2 settings:

    >>> session = TlsSession(
    ...     license_key="your_license_key",
    ...     api_key="your_api_key",
    ...     ja3="771,4865-4866-4867,0-23-65281-10,29-23-24,0",
    ...     alpn=["h2", "http/1.1"],
    ...     http2_settings={
    ...         "header_table_size": 65536,
    ...         "enable_push": False,
    ...         "max_concurrent_streams": 1000
    ...     },
    ...     connection_flow=15663105,
    ...     pseudo_header_order=[":method", ":authority", ":scheme", ":path"],
    ...     settings_order=[1, 2, 3, 4, 6]
    ... )

    Using with proxy:

    >>> session = TlsSession(
    ...     license_key="your_license_key",
    ...     api_key="your_api_key",
    ...     proxy={
    ...         "type": "socks5",
    ...         "host": "proxy.example.com",
    ...         "port": 1080,
    ...         "username": "user",
    ...         "password": "pass"
    ...     }
    ... )

    Notes
    -----
    - Certificate verification is enabled by default for security
    - HTTP/2 settings must match browser fingerprints for accurate spoofing
    """

    def __init__(
            self,
            license_key: str,
            api_key: str,
            ja3: Optional[str] = None,
            alpn: Optional[List[str]] = None,
            proxy: Optional[Dict[str, Any]] = None,
            http2_settings: Optional[Dict[str, Any]] = None,
            tls_padding: Optional[int] = None,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = 30.0,
            verify: bool = True,
            default_profile: str = "chrome_139_windows",
            force_tls13: bool = False,
            min_tls_version: Optional[str] = None,
            disable_extension_filtering: bool = False,
            openssl_compat_mode: bool = False,
            extended_profile: Optional[str] = None,
            connection_flow: Optional[int] = None,
            pseudo_header_order: Optional[List[str]] = None,
            settings_order: Optional[List[int]] = None,
            random_tls_extension_order: bool = False,
            **kwargs
    ):
        """Initialize a TLS session."""
        if not license_key or not api_key:
            raise TlsClientError("license_key and api_key are required for Velum Secure")

        self.license_key = license_key
        self.api_key = api_key

        try:
            license_result = _tls_client.validate_license_py(license_key, api_key)
            self.license_info = license_result
        except Exception as e:
            raise TlsClientError(f"License validation failed: {e}")

        if extended_profile:
            ext_profile = self.get_extended_profile(extended_profile)
            if ext_profile:
                self.ja3 = ja3 or ext_profile.get("ja3")
                self.alpn = alpn or ext_profile.get("alpn")
                self.http2_settings = http2_settings or ext_profile.get("http2_settings")
                profile_headers = ext_profile.get("http_headers", {})
            else:
                profile = get_profile(default_profile)
                self.ja3 = ja3 or profile["ja3"]
                self.alpn = alpn or profile["alpn"]
                self.http2_settings = http2_settings or profile.get("http2_settings")
                profile_headers = profile["http_headers"]
        else:
            profile = get_profile(default_profile)
            self.ja3 = ja3 or profile["ja3"]
            self.alpn = alpn or profile["alpn"]
            self.http2_settings = http2_settings or profile.get("http2_settings")
            profile_headers = profile["http_headers"]

        self.default_headers = headers.copy() if headers else profile_headers.copy()
        self.proxy = proxy
        self.tls_padding = tls_padding
        self.timeout = timeout
        self.verify = verify
        self.force_tls13 = force_tls13
        self.min_tls_version = min_tls_version
        self.disable_extension_filtering = disable_extension_filtering
        self.openssl_compat_mode = openssl_compat_mode
        self.extended_profile = extended_profile
        self.connection_flow = connection_flow
        self.pseudo_header_order = pseudo_header_order
        self.settings_order = settings_order
        self.random_tls_extension_order = random_tls_extension_order

        self.headers = self.default_headers.copy()
        if headers:
            self.headers.update(headers)

        self.cookies = {}
        if cookies:
            self.cookies.update(cookies)

        self._base_profile = self._build_profile()

    @staticmethod
    def get_extended_profile(profile_name: str) -> dict:
        """Get extended profile configuration."""
        profiles = {
            "chrome_android_111": {
                "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,27-11-17513-5-10-18-23-0-45-51-43-35-65281-16-13-21,29-23-24,0",
                "alpn": ["http/1.1"],
                "http2_settings": {
                    "header_table_size": 65536,
                    "enable_push": False,
                    "max_concurrent_streams": 1000,
                    "initial_window_size": 6291456,
                    "max_frame_size": 16384,
                    "max_header_list_size": 262144,
                },
                "connection_flow": 15663105,
                "pseudo_header_order": [":method", ":authority", ":scheme", ":path"],
                "settings_order": [1, 2, 3, 4, 6],
                "random_tls_extension_order": True,
                "http_headers": {
                    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36"
                }
            },
            "chrome_108": {
                "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-13-51-45-43-27-21,29-23-24,0",
                "alpn": ["http/1.1"],
                "http2_settings": {
                    "header_table_size": 65536,
                    "enable_push": False,
                    "max_concurrent_streams": 1000,
                    "initial_window_size": 6291456,
                    "max_frame_size": 16384,
                    "max_header_list_size": 262144,
                },
                "connection_flow": 15663105,
                "random_tls_extension_order": False,
                "http_headers": {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
                }
            }
        }
        return profiles.get(profile_name, {})

    def _build_profile(self) -> Dict[str, Any]:
        """Build the base profile for requests."""
        profile = {
            "ja3": self.ja3,
            "alpn": self.alpn,
            "http_headers": self.headers.copy(),
            "license_key": self.license_key,
            "api_key": self.api_key,
            "timeout": self.timeout,
            "force_tls13": self.force_tls13,
            "min_tls_version": self.min_tls_version,
            "disable_extension_filtering": self.disable_extension_filtering,
            "openssl_compat_mode": self.openssl_compat_mode,
            "random_tls_extension_order": self.random_tls_extension_order,
            "preserve_binary_data": True,
            "response_mode": "auto"
        }

        if self.connection_flow is not None:
            profile["connection_flow"] = self.connection_flow
        if self.pseudo_header_order is not None:
            profile["pseudo_header_order"] = self.pseudo_header_order
        if self.settings_order is not None:
            profile["settings_order"] = self.settings_order
        if self.proxy:
            profile["proxy"] = self.proxy
        if self.http2_settings:
            profile["http2_settings"] = self.http2_settings
        if self.tls_padding is not None:
            profile["tls_padding"] = self.tls_padding

        return profile

    def _update_cookies(self, response_headers: Dict[str, str]):
        """Update cookies from response headers."""
        cookie_headers = []

        for key, value in response_headers.items():
            key_lower = key.lower()
            if key_lower == "set-cookie" or key_lower.startswith("set-cookie-"):
                cookie_headers.append(value)

        for cookie_header in cookie_headers:
            for cookie in cookie_header.split(","):
                parts = cookie.split(";")[0].split("=", 1)
                if len(parts) == 2:
                    key, value = parts
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        self.cookies[key] = value

    def _process_response_content(self, raw_response: Dict[str, Any]) -> Union[str, bytes]:
        """Process response content based on type and binary status."""
        content_type = raw_response.get('headers', {}).get('content-type', '').lower()
        is_binary = raw_response.get('is_binary', False)
        body_bytes = raw_response.get('body_bytes')
        body_text = raw_response.get('body', '')

        if content_type.startswith('application/pdf') or is_binary:
            if body_bytes and len(body_bytes) > 0:
                return bytes(body_bytes)
            elif isinstance(body_text, str) and body_text:
                try:
                    return base64.b64decode(body_text)
                except:
                    return body_text.encode('latin1')
            else:
                return b''
        else:
            if isinstance(body_text, str):
                return body_text
            elif body_bytes and len(body_bytes) > 0:
                try:
                    return bytes(body_bytes).decode('utf-8')
                except UnicodeDecodeError:
                    return bytes(body_bytes).decode('latin1')
            else:
                return body_text or ''

    def request(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[str, bytes, dict]] = None,
            json: Optional[dict] = None,
            params: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            allow_redirects: bool = True,
            **kwargs
    ) -> Response:
        """Make a request."""
        if params:
            parsed = urlparse(url)
            query_parts = []
            if parsed.query:
                query_parts.append(parsed.query)
            query_parts.extend([f"{k}={v}" for k, v in params.items()])
            url = url.split("?")[0] + "?" + "&".join(query_parts)

        profile = self._base_profile.copy()
        profile["method"] = method.upper()

        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        request_cookies = self.cookies.copy()
        if cookies:
            request_cookies.update(cookies)

        if request_cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in request_cookies.items()])
            request_headers["cookie"] = cookie_header

        body = data if data else json
        if body is not None:
            profile["body"] = prepare_body(body)

        profile["http_headers"] = request_headers

        try:
            raw_response = _tls_client.send_profiled_request_sync(profile, url)
            content = self._process_response_content(raw_response)

            response = Response(
                status_code=raw_response["status"],
                headers=raw_response["headers"],
                content=content,
                url=url,
                request_headers=request_headers,
                tls_version=raw_response.get("tls_version", ""),
                cipher_suite=raw_response.get("cipher_suite", ""),
                ja3_hash=raw_response.get("ja3_hash", "")
            )

            response.license_valid = raw_response.get("license_valid", False)
            if raw_response.get("license_info"):
                response.license_info = js.loads(raw_response["license_info"]) if isinstance(raw_response["license_info"], str) else raw_response["license_info"]
            else:
                response.license_info = None

            self._update_cookies(response.headers)

            if allow_redirects and response.is_redirect:
                location = response.headers.get("location")
                if location:
                    if not location.startswith(("http://", "https://")):
                        parsed = urlparse(url)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    return self.request(method="GET", url=location, allow_redirects=True)

            return response

        except Exception as e:
            raise TlsClientError(f"Request failed: {e}")

    async def request_async(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[str, bytes, dict]] = None,
            json: Optional[dict] = None,
            params: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            allow_redirects: bool = True,
            **kwargs
    ) -> Response:
        """Async version of request."""
        if params:
            parsed = urlparse(url)
            query_parts = []
            if parsed.query:
                query_parts.append(parsed.query)
            query_parts.extend([f"{k}={v}" for k, v in params.items()])
            url = url.split("?")[0] + "?" + "&".join(query_parts)

        profile = self._base_profile.copy()
        profile["method"] = method.upper()

        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        request_cookies = self.cookies.copy()
        if cookies:
            request_cookies.update(cookies)

        if request_cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in request_cookies.items()])
            request_headers["cookie"] = cookie_header

        body = data if data else json
        if body is not None:
            profile["body"] = prepare_body(body)

        profile["http_headers"] = request_headers

        try:
            raw_response = await _tls_client.send_profiled_request_async_py(profile, url)
            content = self._process_response_content(raw_response)

            response = Response(
                status_code=raw_response["status"],
                headers=raw_response["headers"],
                content=content,
                url=url,
                request_headers=request_headers,
                tls_version=raw_response.get("tls_version", ""),
                cipher_suite=raw_response.get("cipher_suite", ""),
                ja3_hash=raw_response.get("ja3_hash", "")
            )

            response.license_valid = raw_response.get("license_valid", False)
            if raw_response.get("license_info"):
                response.license_info = js.loads(raw_response["license_info"]) if isinstance(raw_response["license_info"], str) else raw_response["license_info"]
            else:
                response.license_info = None

            self._update_cookies(response.headers)

            if allow_redirects and response.is_redirect:
                location = response.headers.get("location")
                if location:
                    if not location.startswith(("http://", "https://")):
                        parsed = urlparse(url)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    return await self.request_async(method="GET", url=location, allow_redirects=True)

            return response

        except Exception as e:
            raise TlsClientError(f"Request failed: {e}")

    def post_raw(self, url: str, data: bytes, headers: dict, **kwargs):
        """Post raw bytes without JSON processing."""
        return self.request("POST", url, headers=headers, data=data, **kwargs)

    # Convenience methods
    def get(self, url: str, **kwargs) -> Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs) -> Response:
        return self.request("OPTIONS", url, **kwargs)

    # Async convenience methods
    async def get_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("GET", url, **kwargs)

    async def post_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("POST", url, **kwargs)

    async def put_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("PUT", url, **kwargs)

    async def patch_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("PATCH", url, **kwargs)

    async def delete_async(self, url: str, **kwargs) -> Response:
        return await self.request_async("DELETE", url, **kwargs)