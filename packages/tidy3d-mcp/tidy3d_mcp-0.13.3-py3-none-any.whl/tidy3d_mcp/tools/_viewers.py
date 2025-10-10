from __future__ import annotations

_STATE_BY_VIEWER: dict[str, dict[str, bool]] = {}


def remember(viewer_id: str | None, *, focusable: bool = False) -> None:
    if not viewer_id:
        return
    state = _STATE_BY_VIEWER.setdefault(viewer_id, {})
    if focusable:
        state['focusable'] = focusable


def is_focus_only(viewer_id: str | None) -> bool:
    if not viewer_id:
        return False
    state = _STATE_BY_VIEWER.get(viewer_id)
    return bool(state and state.get('focusable'))


def forget(viewer_id: str | None) -> None:
    if viewer_id and viewer_id in _STATE_BY_VIEWER:
        del _STATE_BY_VIEWER[viewer_id]
