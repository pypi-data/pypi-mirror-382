from __future__ import annotations

import json
import base64
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from fastmcp.exceptions import ToolError

from ._dispatcher import invoke_viewer_command
from ._viewers import forget, is_focus_only, remember


def _normalize_visibility(entry: object) -> bool:
    if isinstance(entry, bool):
        return entry
    if entry is None:
        return False
    if isinstance(entry, (int, float)):
        return entry != 0
    if isinstance(entry, str):
        value = entry.strip().lower()
        if value in {'true', '1', 'yes', 'on'}:
            return True
        if value in {'false', '0', 'no', 'off', ''}:
            return False
    return bool(entry)


def _normalize_warnings(raw: object) -> list[str] | None:
    if not raw:
        return None
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Iterable):
        normalized = [str(item) for item in raw if item]
        return normalized or None
    return [str(raw)]


async def rotate_viewer(
    viewer_id: str,
    direction: str,
) -> dict[str, Any]:
    """Align the viewer camera with a principal axis.

    Args:
        viewer_id: Identifier returned by :func:`validate_simulation`.
        direction: One of ``TOP``, ``BOTTOM``, ``LEFT``, ``RIGHT``, ``FRONT``, ``BACK`` (case-insensitive).

    Returns:
        Mapping containing ``viewer_id``, the normalized ``direction`` and the reported status string.
    """
    if not viewer_id:
        raise ValueError('viewer_id is required')
    if not direction:
        raise ValueError('direction is required')
    normalized = direction.upper()
    allowed = {'TOP', 'BOTTOM', 'LEFT', 'RIGHT', 'FRONT', 'BACK'}
    if normalized not in allowed:
        raise ValueError(f'direction must be one of {sorted(allowed)}')
    params: dict[str, object | None] = {'viewer': viewer_id, 'direction': normalized}
    result = invoke_viewer_command('rotate', 'rotate', params, timeout=10.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        if is_focus_only(viewer_id):
            forget(viewer_id)
        raise ToolError(f'rotation failed: {error_msg}')
    status = result.get('status', 'ok')
    return {'viewer_id': viewer_id, 'direction': normalized, 'status': status}


async def show_structures(
    viewer_id: str,
    visibility: list[bool],
) -> dict[str, Any]:
    """Toggle structure visibility in the viewer panel.

    Args:
        viewer_id: Identifier returned by :func:`validate_simulation`.
        visibility: Boolean flags applied in declaration order of the simulation structures.

    Returns:
        Mapping containing ``viewer_id``, status and the echoed visibility list.
    """
    if not viewer_id:
        raise ValueError('viewer_id is required')
    flags = [_normalize_visibility(entry) for entry in visibility]
    payload = json.dumps(flags)
    params: dict[str, object | None] = {'viewer': viewer_id, 'visibility': payload}
    result = invoke_viewer_command('visibility', 'visibility', params, timeout=10.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        if is_focus_only(viewer_id):
            forget(viewer_id)
        raise ToolError(f'visibility update failed: {error_msg}')
    response: dict[str, Any] = {'viewer_id': viewer_id, 'status': result.get('status', 'ok')}
    returned_flags = result.get('visibility')

    if isinstance(returned_flags, list):
        response['visibility'] = [_normalize_visibility(entry) for entry in returned_flags]
    return response


def _build_inline_payload(file: str) -> dict[str, str]:
    """Read file content and prepare inline viewer payload."""
    candidate = Path(file).expanduser()
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ToolError(f'viewer source not found: {candidate}') from exc
    try:
        data = resolved.read_bytes()
    except FileNotFoundError as exc:
        raise ToolError(f'viewer source not found: {resolved}') from exc
    encoded = base64.b64encode(data).decode('ascii')
    payload: dict[str, str] = {
        'inline_content': encoded,
        'inline_encoding': 'base64',
        'inline_name': resolved.name,
    }
    try:
        stat = resolved.stat()
    except OSError:
        return payload
    payload['inline_mtime'] = str(stat.st_mtime_ns)
    return payload


async def validate_simulation(
    file: str | None = None,
    symbol: str | None = None,
    index: int | None = None,
    viewer_id: str | None = None,
) -> dict[str, Any]:
    """Launch or re-validate a simulation and surface viewer diagnostics.

    Args:
        file: Absolute path or workspace-relative URI pointing to a simulation script or notebook. Required when
            ``viewer_id`` is omitted.
        symbol: Optional variable name selecting a ``tidy3d.Simulation`` object inside the file.
        index: Optional zero-based simulation index when multiple simulations are detected.
        viewer_id: Existing viewer identifier returned by a previous validation run. Provide this to re-check
            warnings after editing the source without reopening the viewer.

    Returns:
        Mapping containing the resolved ``viewer_id``, reported ``status`` or ``error`` strings, any collected
        ``warnings``, the originating ``window_id`` when known, and a ``slice`` object with the evaluated code and
        its import requirements.
    """
    launched = False
    start_result: dict[str, Any] | None = None
    start_warnings: list[str] | None = None
    normalized_viewer = viewer_id.strip() if isinstance(viewer_id, str) else None
    inline_payload: dict[str, str] = {}
    if file:
        inline_payload = _build_inline_payload(file)

    if not normalized_viewer:
        if not file:
            raise ValueError('file is required when viewer_id is not provided')
        params: dict[str, object | None] = dict(inline_payload)
        if symbol:
            params['symbol'] = symbol
        if index is not None:
            params['index'] = index
        start_result = invoke_viewer_command('start', 'ready', params, timeout=10.0)
        error_msg = start_result.get('error') if isinstance(start_result, dict) else None
        if isinstance(error_msg, str) and error_msg:
            raise ToolError(f'viewer reported error: {error_msg}')
        resolved = start_result.get('viewer_id') if isinstance(start_result, dict) else None
        if not isinstance(resolved, str) or not resolved:
            raise ValueError('viewer did not confirm readiness')
        normalized_viewer = resolved
        status = start_result.get('status') if isinstance(start_result, dict) else None
        focusable = isinstance(status, str) and status.lower() == 'focused'
        remember(normalized_viewer, focusable=focusable)
        start_warnings = _normalize_warnings(start_result.get('warnings') or start_result.get('warning')) if isinstance(start_result, dict) else None
        launched = True
    else:
        remember(normalized_viewer)

    if not normalized_viewer:
        raise ValueError('viewer_id is required')

    params: dict[str, object | None] = dict(inline_payload)
    params['viewer'] = normalized_viewer
    check_result = invoke_viewer_command('check', 'check', params, timeout=10.0)
    if not isinstance(check_result, dict):
        raise RuntimeError('viewer returned unsupported payload')

    response: dict[str, Any] = {'viewer_id': normalized_viewer}
    status = check_result.get('status')
    if not isinstance(status, str) or not status:
        status = start_result.get('status') if isinstance(start_result, dict) else None
    if isinstance(status, str) and status:
        response['status'] = status
    error_msg = check_result.get('error')
    if isinstance(error_msg, str) and error_msg:
        response['error'] = error_msg
    window_id = check_result.get('window_id')
    if isinstance(window_id, str) and window_id:
        response['window_id'] = window_id

    warnings = _normalize_warnings(check_result.get('warnings') or check_result.get('warning')) or []
    if start_warnings:
        seen = set(warnings)
        for item in start_warnings:
            if item not in seen:
                warnings.append(item)
                seen.add(item)
    if warnings:
        response['warnings'] = warnings

    slice_data = check_result.get('slice')
    if isinstance(slice_data, dict):
        code = slice_data.get('code')
        requirements = slice_data.get('requirements')
        if isinstance(code, str) and code:
            normalized_requirements = requirements if isinstance(requirements, list) else []
            response['slice'] = {
                'code': code,
                'requirements': [str(entry) for entry in normalized_requirements]
            }
    if launched and 'slice' not in response and isinstance(start_result, dict):
        slice_fallback = start_result.get('slice')
        if isinstance(slice_fallback, dict):
            code = slice_fallback.get('code')
            requirements = slice_fallback.get('requirements')
            if isinstance(code, str) and code:
                normalized_requirements = requirements if isinstance(requirements, list) else []
                response['slice'] = {
                    'code': code,
                    'requirements': [str(entry) for entry in normalized_requirements]
                }

    return response
