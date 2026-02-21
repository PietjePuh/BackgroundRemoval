import sys
from unittest.mock import MagicMock, patch
import pytest
import os

# Clean up sys.modules to ensure we load bg_remove with OUR mocks
keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'PIL' in k or 'streamlit' in k or 'rembg' in k]
for k in keys_to_remove:
    del sys.modules[k]

# Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
mock_col1 = MagicMock()
mock_col2 = MagicMock()
mock_st.columns.return_value = [mock_col1, mock_col2]
mock_st.sidebar.file_uploader.return_value = None
# Mock caches
mock_st.cache_data = lambda *args, **kwargs: lambda func: func
mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
mock_st.session_state = {}

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Setup Image mock
mock_image_module = MagicMock()
mock_image_module.LANCZOS = 1
mock_image_module.BICUBIC = 2

class MockDecompressionBombError(Exception):
    pass
mock_image_module.DecompressionBombError = MockDecompressionBombError

sys.modules['PIL'] = MagicMock()
sys.modules['PIL'].Image = mock_image_module
sys.modules['PIL.Image'] = mock_image_module

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove

def test_format_file_size():
    """Test the file size formatting helper."""
    assert bg_remove.format_file_size(500) == "500 B"
    assert bg_remove.format_file_size(1024) == "1.0 KB"
    assert bg_remove.format_file_size(1500) == "1.5 KB"
    assert bg_remove.format_file_size(1024 * 1024) == "1.0 MB"
    assert bg_remove.format_file_size(2.5 * 1024 * 1024) == "2.5 MB"

def test_download_button_ux_label_and_help():
    """
    Test that the download button label includes file size and help tooltip includes details.
    """
    # Reset mocks
    mock_col2.download_button.reset_mock()

    # Create dummy data
    mock_img = MagicMock()
    mock_result = MagicMock()
    mock_result.size = (800, 600)
    mock_result.width = 800
    mock_result.height = 600

    output_filename = "test_rmbg.png"
    result_bytes = b"a" * 1024 # 1.0 KB
    output_format = "PNG"

    # Call display_single_result
    bg_remove.display_single_result(
        mock_img,
        mock_result,
        output_filename,
        result_bytes,
        output_format,
        is_default=False
    )

    assert mock_col2.download_button.called
    args, kwargs = mock_col2.download_button.call_args

    # Check label (first arg)
    label = args[0]
    assert "1.0 KB" in label
    assert "Download PNG image" in label

    # Check help (kwargs)
    help_text = kwargs.get('help')
    assert help_text is not None
    assert "Size: 1.0 KB" in help_text
    assert "Resolution: 800x600" in help_text
