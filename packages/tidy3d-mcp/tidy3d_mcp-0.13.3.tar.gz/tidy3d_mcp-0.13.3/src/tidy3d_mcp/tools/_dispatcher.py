from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse, urlunparse
from urllib.request import Request, urlopen

_HOST: str | None = None
_BRIDGE_URL: str | None = os.environ.get('TIDY3D_VIEWER_BRIDGE', '').strip() or None


def _normalize_bridge_url(candidate: str | None) -> str | None:
    if not candidate:
        return None
    text = candidate.strip()
    if not text:
        return None
    source = text
    if '://' not in source:
        if source.startswith(':'):
            source = f'http://127.0.0.1{source}'
        else:
            source = f'http://{source}'
    parsed = urlparse(source)
    scheme = parsed.scheme or 'http'
    if scheme not in {'http', 'https'}:
        params = parse_qs(parsed.query)
        port_values = params.get('port') or ()
        for entry in port_values:
            if entry and entry.isdigit():
                return f'http://127.0.0.1:{entry}'
        return None
    hostname = parsed.hostname or ''
    try:
        port = parsed.port
    except ValueError:
        return None
    if not hostname:
        hostname = '127.0.0.1'
    if hostname == 'viewer-bridge':
        hostname = '127.0.0.1'
    netloc = f'{hostname}:{port}' if port else hostname
    path = parsed.path.rstrip('/')
    query = parsed.query
    rebuilt = urlunparse((scheme, netloc, path, '', query, ''))
    return rebuilt.rstrip('/')


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
        normalized = _normalize_bridge_url(bridge_url)
        if normalized:
            _BRIDGE_URL = normalized


def current_host() -> str | None:
    """Return the configured host identifier."""
    return _HOST


def set_bridge_url(url: str | None) -> None:
    """Persist the active viewer bridge endpoint."""
    global _BRIDGE_URL
    if url is None:
        _BRIDGE_URL = None
        return
    normalized = _normalize_bridge_url(url)
    _BRIDGE_URL = normalized


def _bridge_endpoint() -> str | None:
    global _BRIDGE_URL
    if _BRIDGE_URL:
        return _BRIDGE_URL
    candidate = os.environ.get('TIDY3D_VIEWER_BRIDGE', '')
    normalized = _normalize_bridge_url(candidate)
    _BRIDGE_URL = normalized
    return normalized


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
