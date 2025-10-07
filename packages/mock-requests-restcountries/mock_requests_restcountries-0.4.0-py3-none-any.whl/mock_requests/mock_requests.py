
"""
REST Countries mock (per-URL caching)
----------------------------------------------
- Prefer packaged per-URL JSONs under mock_requests/data.
- Else check user cache (~/.cache/mock_requests_rc).
- Else perform a live GET (unless MOCK_REQUESTS_OFFLINE=1), cache that JSON, and return.
"""

import os
import re
import json
import hashlib
import urllib.parse
import requests
from typing import Optional

# Find packaged data directory (installed files)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Compute user-cache directory (can be overridden by env)
_DEFAULT_USER_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "mock_requests_rc")
USER_CACHE_DIR = os.getenv("MOCK_REQUESTS_USER_CACHE_DIR", _DEFAULT_USER_CACHE)

# Ensure the user-cache directory exists
if not os.path.isdir(USER_CACHE_DIR):
    os.makedirs(USER_CACHE_DIR, exist_ok=True)

# Allowed REST Countries prefixes
_ALLOWED_PREFIXES = ("https://restcountries.com/v3.1/", "http://restcountries.com/v3.1/")

# Environment controls
_OFFLINE = os.getenv("MOCK_REQUESTS_OFFLINE", "0") == "1"
_TIMEOUT = int(os.getenv("MOCK_REQUESTS_TIMEOUT", "30"))

def _hash_filename_for(url: str) -> str:
    """
    Turn a URL into a short, safe filename using SHA-256.
    We keep the first 24 hex chars to balance uniqueness and brevity.
    """
    sha = hashlib.sha256(url.encode("utf-8")).hexdigest()
    name = "rc_" + sha[:24] + ".json"
    return name

def _path_in_package(filename: str) -> str:
    """
    Build the absolute path to a packaged data file.
    """
    return os.path.join(DATA_DIR, filename)

def _path_in_user_cache(filename: str) -> str:
    """
    Build the absolute path to a user-cache data file.
    """
    return os.path.join(USER_CACHE_DIR, filename)

class MockResponse:
    """
    Minimal response wrapper with .json(), .text, .ok, .status_code
    backed by a JSON file path.
    """
    def __init__(self, filepath: str, status_code: int) -> None:
        self.filepath = filepath
        self.status_code = status_code
        self._text_cache: Optional[str] = None

    def json(self):
        if not self.filepath:
            return None
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def text(self) -> str:
        if self._text_cache is None:
            payload = self.json()
            self._text_cache = json.dumps(payload)
        return self._text_cache

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def __str__(self) -> str:
        return f"<Response [{self.status_code}]>"

def _is_supported(url: str) -> bool:
    """
    Confirm the URL matches REST Countries v3.1.
    """
    for prefix in _ALLOWED_PREFIXES:
        if url.startswith(prefix):
            return True
    return False

def _load_packaged_or_cached(url: str) -> Optional[MockResponse]:
    """
    Try to satisfy the URL from packaged data, then from user cache.
    Return a MockResponse if found; otherwise None.
    """
    filename = _hash_filename_for(url)

    # 1) Packaged data
    pkg_path = _path_in_package(filename)
    if os.path.exists(pkg_path) and os.path.getsize(pkg_path) > 0:
        return MockResponse(pkg_path, 200)

    # 2) User cache
    user_path = _path_in_user_cache(filename)
    if os.path.exists(user_path) and os.path.getsize(user_path) > 0:
        return MockResponse(user_path, 200)

    return None

def _live_fetch_and_cache(url: str) -> Optional[MockResponse]:
    """
    Perform a live GET request, save JSON to user cache (short hashed name), return response.
    Return None if offline or fetch fails.
    """
    if _OFFLINE:
        return None

    filename = _hash_filename_for(url)
    user_path = _path_in_user_cache(filename)

    try:
        r = requests.get(url, timeout=_TIMEOUT)
    except requests.RequestException:
        return None

    try:
        data = r.json()
    except ValueError:
        return None

    try:
        with open(user_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        return None

    return MockResponse(user_path, r.status_code)

def get(url: str) -> MockResponse:
    """
    Public entry point emulating requests.get(url).
    """
    if not _is_supported(url):
        return MockResponse("", 404)

    # Try packaged or cached
    found = _load_packaged_or_cached(url)
    if found is not None:
        return found

    # Otherwise live fetch (unless offline), then cache
    fetched = _live_fetch_and_cache(url)
    if fetched is not None:
        return fetched

    # Give a conservative 404-like response if nothing worked
    return MockResponse("", 404)
