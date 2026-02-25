import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Helper to clean up modules
def clean_modules():
    keys_to_remove = [k for k in sys.modules if "bg_remove" in k]
    for k in keys_to_remove:
        del sys.modules[k]

def setup_mocks(output_format_val, bg_mode_val):
    clean_modules()

    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Mock file uploader to return empty list (no uploads)
    mock_st.sidebar.file_uploader.return_value = []

    mock_st.session_state = {}

    # Setup return values for interactive widgets
    # selectbox for output_format
    mock_st.sidebar.selectbox.return_value = output_format_val
    # radio for bg_mode
    mock_st.sidebar.radio.return_value = bg_mode_val

    sys.modules["streamlit"] = mock_st
    sys.modules["rembg"] = MagicMock()
    sys.modules["PIL"] = MagicMock()
    sys.modules["PIL.Image"] = MagicMock()
    sys.modules["numpy"] = MagicMock()

    # Ensure path is correct to import bg_remove
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    return mock_st

def test_jpeg_transparent_warning_shown():
    mock_st = setup_mocks("JPEG", "transparent")

    # Mock os.path.exists to prevent default image processing
    with patch("os.path.exists", return_value=False):
        import bg_remove

    # Check if the specific info message was called
    expected_msg = "Note: JPEG does not support transparency. Result will have a white background."
    mock_st.sidebar.info.assert_called_with(expected_msg)

def test_jpeg_transparent_warning_not_shown_for_png():
    mock_st = setup_mocks("PNG", "transparent")

    with patch("os.path.exists", return_value=False):
        import bg_remove

    expected_msg = "Note: JPEG does not support transparency. Result will have a white background."
    # Get all calls to sidebar.info
    calls = [args[0] for args, _ in mock_st.sidebar.info.call_args_list]
    assert expected_msg not in calls

def test_jpeg_transparent_warning_not_shown_for_solid_color():
    mock_st = setup_mocks("JPEG", "solid_color")

    with patch("os.path.exists", return_value=False):
        import bg_remove

    expected_msg = "Note: JPEG does not support transparency. Result will have a white background."
    calls = [args[0] for args, _ in mock_st.sidebar.info.call_args_list]
    assert expected_msg not in calls
