from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

_HOST: str | None = None
_BRIDGE_URL: str | None = os.environ.get('TIDY3D_VIEWER_BRIDGE', '').strip() or None


def configure_dispatcher(host: str | None, bridge_url: str | None) -> None:
    """Record host metadata for viewer dispatch."""
    global _HOST
    global _BRIDGE_URL
    if isinstance(host, str):
        stripped = host.strip()
        _HOST = stripped or None
    else:
        _HOST = None
    if bridge_url:
        normalized = bridge_url.strip()
        _BRIDGE_URL = normalized or _BRIDGE_URL


def current_host() -> str | None:
    """Return the configured host identifier."""
    return _HOST


def set_bridge_url(url: str | None) -> None:
    """Persist the active viewer bridge endpoint."""
    global _BRIDGE_URL
    if url is None:
        _BRIDGE_URL = None
        return
    normalized = url.strip()
    _BRIDGE_URL = normalized or None


def _bridge_endpoint() -> str | None:
    global _BRIDGE_URL
    if _BRIDGE_URL:
        return _BRIDGE_URL
    candidate = os.environ.get('TIDY3D_VIEWER_BRIDGE', '').strip() or None
    _BRIDGE_URL = candidate
    return candidate


def _stringify_params(params: Mapping[str, object | None]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        result[key] = str(value)
    return result


def _invoke_via_bridge(action: str, params: Mapping[str, object | None], timeout: float) -> dict[str, Any]:
    endpoint = _bridge_endpoint()
    if not endpoint:
        raise RuntimeError('viewer bridge unavailable; ensure the Tidy3D extension is active')
    payload = _stringify_params(params)
    if timeout and timeout > 0:
        payload['timeout_ms'] = str(int(timeout * 1000))
    data = json.dumps(payload).encode('utf-8')
    parsed = urlparse(endpoint)
    path = parsed.path.rstrip('/') + f'/viewer/{action}'
    url = urlunparse((parsed.scheme, parsed.netloc, path, '', parsed.query, ''))
    request = Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f'viewer bridge request failed: {exc}') from exc
    text = raw.decode('utf-8') if raw else '{}'
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError('bridge returned invalid JSON') from exc
    if not isinstance(decoded, dict):
        raise RuntimeError('bridge returned unsupported payload')
    return decoded


def invoke_viewer_command(
    action: str,
    callback_segment: str,
    params: Mapping[str, object | None],
    *,
    timeout: float,
) -> dict[str, Any]:
    """Dispatch a viewer command through the local bridge."""
    del callback_segment  # handled upstream but no longer required
    return _invoke_via_bridge(action, params, timeout)
