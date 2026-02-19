import sys
from unittest.mock import MagicMock
import os
import pytest

def test_custom_bg_ux():
    """
    Test UX improvements for the Custom Background Uploader.
    Verifies:
    1. The label includes size constraint "(max 10MB)".
    2. An info message is displayed when no background image is uploaded.
    """
    # 1. Clean up sys.modules
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'PIL' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # 2. Mock modules
    mock_st = MagicMock()

    # Mock sidebar.radio to return "custom_image" to trigger the relevant block
    # Note: We need to handle the format_func argument if strictly mocking, but MagicMock accepts anything.
    # The return value determines which block is executed.
    mock_st.sidebar.radio.return_value = "custom_image"

    # Mock sidebar.file_uploader
    # We want it to return None for the custom bg upload to trigger the info message
    # And return None for the main upload to avoid executing main logic
    mock_st.sidebar.file_uploader.return_value = None

    # Mock other necessary calls
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    mock_st.session_state = {}

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

    # 3. Import the module (executes script body)
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove  # noqa: F401

    # 4. Assertions

    # A. Verify file_uploader label for custom background
    found_custom_uploader = False
    for call in mock_st.sidebar.file_uploader.call_args_list:
        args, kwargs = call
        label = args[0]
        # Distinguish from the main uploader
        if "background image" in label:
            found_custom_uploader = True
            assert "max 10MB" in label, f"Label '{label}' missing size constraint"
            assert "help" in kwargs, "Missing help tooltip"
            assert "Maximum: 10MB" in kwargs["help"], "Help tooltip missing size info"

    assert found_custom_uploader, "Custom background uploader call not found"

    # B. Verify info message when no file uploaded
    # We expect st.sidebar.info to be called
    mock_st.sidebar.info.assert_called_with("Please upload a background image to see the effect.")
