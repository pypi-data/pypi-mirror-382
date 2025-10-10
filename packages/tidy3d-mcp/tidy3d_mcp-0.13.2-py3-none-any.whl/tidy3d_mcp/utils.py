from __future__ import annotations

import os
from pathlib import Path


def _resolve_path(candidate: Path) -> Path:
    """Resolve candidate without requiring existence."""
    try:
        return candidate.resolve(strict=False)
    except RuntimeError:
        return candidate.absolute()


def _translate_workspace_path(resolved: Path) -> Path:
    """Map container workspace paths back to the host mirror when configured."""
    container_root_raw = os.environ.get('TIDY3D_CONTAINER_WORKSPACE_ROOT', '').strip()
    host_root_raw = os.environ.get('TIDY3D_HOST_WORKSPACE_ROOT', '').strip()
    if not container_root_raw or not host_root_raw:
        return resolved
    container_root = _resolve_path(Path(container_root_raw).expanduser())
    host_root = _resolve_path(Path(host_root_raw).expanduser())
    try:
        relative = resolved.relative_to(container_root)
    except ValueError:
        return resolved
    candidate = host_root.joinpath(relative)
    return _resolve_path(candidate)


def ensure_file_uri(path: str | None) -> str:
    """Normalize `path` into a file URI."""
    if not path:
        raise ValueError('path is required')
    if path.startswith('file://'):
        return path
    raw_path = Path(path).expanduser()
    resolved = _resolve_path(raw_path)
    translated = _translate_workspace_path(resolved)
    if not translated.is_absolute():
        translated = _resolve_path(translated)
    return translated.as_uri()
