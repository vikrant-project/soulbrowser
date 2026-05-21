"""Unit tests for backend resolution (_resolve_backend)."""

import os
from unittest.mock import patch

import pytest

from soulbrowser.browser import _resolve_backend


def test_resolve_backend_default():
    """No param, no env var → 'playwright'."""
    with patch.dict(os.environ, {}, clear=True):
        assert _resolve_backend(None) == "playwright"


def test_resolve_backend_explicit_playwright():
    assert _resolve_backend("playwright") == "playwright"


def test_resolve_backend_explicit_patchright():
    assert _resolve_backend("patchright") == "patchright"


def test_resolve_backend_env_var():
    """SOULBROWSER_BACKEND env var used when no param."""
    with patch.dict(os.environ, {"SOULBROWSER_BACKEND": "patchright"}):
        assert _resolve_backend(None) == "patchright"


def test_resolve_backend_param_beats_env():
    """Explicit param overrides env var."""
    with patch.dict(os.environ, {"SOULBROWSER_BACKEND": "patchright"}):
        assert _resolve_backend("playwright") == "playwright"


def test_resolve_backend_invalid_raises():
    with pytest.raises(ValueError, match="Unknown backend 'bogus'"):
        _resolve_backend("bogus")


def test_resolve_backend_invalid_env_raises():
    with patch.dict(os.environ, {"SOULBROWSER_BACKEND": "bogus"}):
        with pytest.raises(ValueError, match="Unknown backend 'bogus'"):
            _resolve_backend(None)
