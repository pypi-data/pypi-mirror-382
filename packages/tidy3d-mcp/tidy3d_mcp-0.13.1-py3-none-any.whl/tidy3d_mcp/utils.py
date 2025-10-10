from __future__ import annotations

from pathlib import Path


def ensure_file_uri(path: str | None) -> str:
    """Normalize `path` into a file URI."""
    if not path:
        raise ValueError('path is required')
    if path.startswith('file://'):
        return path
    return Path(path).expanduser().resolve().as_uri()
