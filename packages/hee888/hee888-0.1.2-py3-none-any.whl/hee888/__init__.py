"""hee888 package initializer.

This module avoids importing the full `app` module at import time because
`app` pulls optional heavy third-party dependencies (like `yt_dlp`). We
expose small lazy wrappers so importing `hee888` (e.g., when console
entry points are created) doesn't fail unless the caller actually calls
the heavy functions.
"""
from __future__ import annotations

import importlib
from typing import Optional


def _get_app_module():
    return importlib.import_module("hee888.app")


def main(argv: Optional[list[str]] = None) -> None:
    """Call through to hee888.app.main lazily."""
    mod = _get_app_module()
    return mod.main(argv)


def make_session(default_headers: Optional[dict] = None):
    """Lazy wrapper for app.make_session."""
    mod = _get_app_module()
    return mod.make_session(default_headers)


def create_prepared_request(url: str, method: str = "GET", headers: Optional[dict] = None, params: Optional[dict] = None, data: Optional[object] = None):
    """Lazy wrapper for app.create_prepared_request."""
    mod = _get_app_module()
    return mod.create_prepared_request(url, method=method, headers=headers, params=params, data=data)


__all__ = ["main", "make_session", "create_prepared_request"]
