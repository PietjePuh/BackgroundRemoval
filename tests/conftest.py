"""Shared test fixtures and mock setup for bg_remove tests.

This module provides a clean way to mock Streamlit and other heavy dependencies
before importing bg_remove, avoiding import-time side effects.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock


def _clean_modules():
    """Remove any cached bg_remove-related modules from sys.modules."""
    keys_to_remove = [
        k
        for k in sys.modules
        if "bg_remove" in k or "PIL" in k or "streamlit" in k or "rembg" in k
    ]
    for k in keys_to_remove:
        del sys.modules[k]


def _create_mock_streamlit():
    """Create a fully configured Streamlit mock."""
    mock_st = MagicMock()
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_st.columns.return_value = [mock_col1, mock_col2]
    mock_st.sidebar.file_uploader.return_value = None

    # Make cache decorators pass-through
    def mock_cache_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda func: func

    mock_st.cache_data = mock_cache_decorator
    mock_st.cache_resource = mock_cache_decorator
    mock_st.session_state = {}

    return mock_st, mock_col1, mock_col2


def _create_mock_pil():
    """Create a fully configured PIL mock with proper exception classes."""
    mock_image_module = MagicMock()

    class MockDecompressionBombError(Exception):
        pass

    mock_image_module.DecompressionBombError = MockDecompressionBombError
    mock_image_module.LANCZOS = 1
    mock_image_module.BICUBIC = 2

    mock_pil = MagicMock()
    mock_pil.Image = mock_image_module
    mock_pil.ImageFilter = MagicMock()

    return mock_pil, mock_image_module


@pytest.fixture
def mock_env():
    """Set up mocked environment and import bg_remove cleanly.

    Returns a dict with all mock objects and the imported bg_remove module.
    """
    _clean_modules()

    mock_st, mock_col1, mock_col2 = _create_mock_streamlit()
    mock_pil, mock_image_module = _create_mock_pil()

    sys.modules["streamlit"] = mock_st
    sys.modules["rembg"] = MagicMock()
    sys.modules["numpy"] = MagicMock()
    sys.modules["PIL"] = mock_pil
    sys.modules["PIL.Image"] = mock_image_module
    sys.modules["PIL.ImageFilter"] = mock_pil.ImageFilter

    # Ensure bg_remove can be found
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    import bg_remove

    yield {
        "module": bg_remove,
        "st": mock_st,
        "col1": mock_col1,
        "col2": mock_col2,
        "pil": mock_pil,
        "image_module": mock_image_module,
    }

    # Cleanup
    _clean_modules()
