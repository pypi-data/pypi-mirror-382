from __future__ import annotations

import os
from pathlib import Path
def _resolve_path(candidate: Path) -> Path:
    """Resolve candidate without requiring existence."""
    try:
        return candidate.resolve(strict=False)
    except RuntimeError:
        return candidate.absolute()


def ensure_file_uri(path: str | None) -> str:
    """Normalize `path` into a file URI."""
    if not path:
        raise ValueError('path is required')
    if path.startswith('file://'):
        return path
    raw_path = Path(path).expanduser()
    resolved = _resolve_path(raw_path)
    return resolved.as_uri()
