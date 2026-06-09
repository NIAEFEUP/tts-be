from __future__ import annotations
import base64
import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from tts_be.settings import BASE_DIR

class MockResponse:
    def __init__(self, status_code, raw):
        self.status_code = status_code
        self._raw = raw

    @property
    def content(self):
        if not self._raw:
            return b""
        if isinstance(self._raw, str) and self._raw.startswith("data:"):
            try:
                _, encoded = self._raw.split(",", 1)
                return base64.b64decode(encoded)
            except Exception:
                return b""
        if isinstance(self._raw, str):
            return self._raw.encode("utf-8")
        return self._raw or b""

    def json(self):
        if not self._raw:
            raise json.JSONDecodeError("No content to decode", "", 0)
        return json.loads(self._raw)

class MockPostResponse:
    def __init__(self, status_code, cookies):
        self.status_code = status_code
        self.cookies = cookies or {}

def _mock_store_path() -> Path:
    return BASE_DIR / "mock-data.json"


def _load_mock() -> dict:
    path = _mock_store_path()
    if not path.exists():
        return {"get": {}, "post": {}}
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"get": {}, "post": {}}

def _get_mock_entry(store: dict, url: str) -> dict | None:
    entry = store.get(url)
    if entry is None:
        parsed = urlparse(url)
        no_query = urlunparse(parsed._replace(query=""))
        entry = store.get(no_query)
    return entry

def get(url: str):
    """Handles mocked GET requests."""
    store = _load_mock().get("get", {})
    entry = _get_mock_entry(store, url)

    if entry is None:
        return MockResponse(404, None)

    return MockResponse(entry.get("status_code", 200), entry.get("data"))

def post(url: str, data=None):
    """Handles mocked POST requests."""
    store = _load_mock().get("post", {})
    entry = _get_mock_entry(store, url)

    if entry is None:
        return MockPostResponse(404, {})

    return MockPostResponse(entry.get("status_code", 200), entry.get("cookies", {}))

