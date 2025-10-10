from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
import webbrowser

from fastmcp import FastMCP
from fastmcp.client.auth import BearerAuth
from fastmcp.server.proxy import ProxyClient
from fastmcp.tools import Tool

from urllib.parse import urlencode

from .tools import (
    configure_dispatcher,
    capture,
    rotate_viewer,
    set_bridge_url,
    show_structures,
    validate_simulation,
)


def _proxy_name_for_host(host: str | None) -> str:
    if not host:
        return 'Tidy3D'
    formatted = host.replace('_', ' ').replace('-', ' ').strip()
    return f'Tidy3D ({formatted.title()})'


def _select_free_port() -> int:
    """Return a host-local TCP port that is currently unused."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(('127.0.0.1', 0))
        _, port = candidate.getsockname()
    return int(port)


def _viewer_bridge_uri(port: int, host: str | None) -> str:
    """Build the deeplink URI used to request a viewer bridge."""
    params: dict[str, str] = {'port': str(port)}
    if host:
        params['host'] = host
    normalized = (host or '').lower()
    scheme: str | None
    if 'cursor' in normalized:
        scheme = 'cursor'
    elif 'vscode' in normalized:
        scheme = 'vscode'
    else:
        scheme = None
    query = urlencode(params)
    extension_id = 'Flexcompute.tidy3d'
    if scheme:
        return f'{scheme}://{extension_id}/bridge?{query}'
    return f'tidy3d://bridge?{query}'


def _open_deeplink(uri: str) -> None:
    """Launch the viewer deeplink or fail if unavailable."""
    launched = webbrowser.open(uri, new=0, autoraise=True)
    if not launched:
        raise RuntimeError('deeplink launch was rejected by the host OS')


def _await_bridge(port: int, timeout: float = 15.0) -> str:
    """Wait for the viewer bridge to bind and return its base URL."""
    deadline = time.monotonic() + timeout
    endpoint = f'http://127.0.0.1:{port}'
    while True:
        payload = json.dumps({}).encode('utf-8')
        request = urllib.request.Request(
            f'{endpoint}/viewer/ping',
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=1.0):
                return endpoint
        except urllib.error.URLError:
            if time.monotonic() >= deadline:
                break
            time.sleep(0.25)
    raise RuntimeError('viewer bridge did not start within the expected window')


def _bootstrap_viewer_bridge(host: str | None) -> None:
    """Activate the viewer bridge via deeplink and persist its location."""
    port = _select_free_port()
    deeplink = _viewer_bridge_uri(port, host)
    _open_deeplink(deeplink)
    bridge_url = _await_bridge(port)
    set_bridge_url(bridge_url)


def main(argv: list[str] | None = None):
    """Launch the FastMCP proxy with host-aware bookkeeping."""
    parser = argparse.ArgumentParser(prog='tidy3d-mcp')
    parser.add_argument('--host', choices=('vscode', 'cursor'), default='vscode')
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--viewer-bridge', default=None)
    parser.add_argument('--enable-viewer', action='store_true')
    args = parser.parse_args(argv)

    configure_dispatcher(args.host, args.viewer_bridge)
    viewer_enabled = bool(args.enable_viewer)
    if viewer_enabled:
        if args.viewer_bridge:
            set_bridge_url(args.viewer_bridge)
        else:
            try:
                _bootstrap_viewer_bridge(args.host)
            except Exception as exc:
                print(f'Viewer bridge initialization failed: {exc}', file=sys.stderr)
                set_bridge_url(None)
                viewer_enabled = False
    mcp_url = os.getenv('REMOTE_MCP_URL', 'https://flexagent.dev-simulation.cloud/')
    auth = BearerAuth(token=args.api_key)
    proxy_name = _proxy_name_for_host(args.host)
    proxy = FastMCP.as_proxy(ProxyClient(mcp_url, auth=auth), name=proxy_name)

    if viewer_enabled:
        proxy.add_tool(Tool.from_function(validate_simulation))
        proxy.add_tool(Tool.from_function(capture))
        proxy.add_tool(Tool.from_function(rotate_viewer))
        proxy.add_tool(Tool.from_function(show_structures))

    proxy.run()


if __name__ == '__main__':
    main()
