import sys
from unittest.mock import MagicMock, patch
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

# Improved cache decorator mock to handle both @decorator and @decorator(...)
def mock_cache_decorator(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return lambda func: func

mock_st.cache_data = mock_cache_decorator
mock_st.cache_resource = mock_cache_decorator
mock_st.session_state = {} # Initialize session state

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Setup Image mock
mock_image_module = MagicMock()
mock_image_module.LANCZOS = 1
mock_image_module.BICUBIC = 2

# Define exception class for DecompressionBombError
class MockDecompressionBombError(Exception):
    pass
mock_image_module.DecompressionBombError = MockDecompressionBombError

# We need a real-ish Image object for process_image to work
mock_img_instance = MagicMock()
mock_img_instance.format = "PNG"
mock_img_instance.size = (100, 100)
mock_img_instance.width = 100
mock_img_instance.height = 100
mock_img_instance.resize.return_value = mock_img_instance
mock_img_instance.save = MagicMock()

mock_image_module.open.return_value = mock_img_instance

sys.modules['PIL'] = MagicMock()
sys.modules['PIL'].Image = mock_image_module
sys.modules['PIL.Image'] = mock_image_module

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove  # noqa: E402

def test_download_filename_for_uploaded_file():
    """
    Test that the download button gets a dynamic filename based on the uploaded file name.
    """
    # Reset mocks
    mock_col2.download_button.reset_mock()

    # Create a mock uploaded file
    mock_upload = MagicMock()
    mock_upload.name = "my_cool_photo.jpg"
    mock_upload.getvalue.return_value = b"fake_bytes"
    mock_upload.size = 1024

    # Call fix_image directly
    result_tuple = bg_remove.fix_image(mock_upload)

    # Assert result is not None
    assert result_tuple is not None, "fix_image returned None"

    # Unpack return values: (original_image, result_image, output_filename, result_bytes)
    _, _, actual_filename, _ = result_tuple

    assert actual_filename == "my_cool_photo_rmbg.png"

def test_download_filename_for_default_image():
    """
    Test that the download button gets a dynamic filename based on the default image path.
    """
    # Reset mocks
    mock_col2.download_button.reset_mock()

    # Mock os.path.exists and open to handle the default image path
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", new_callable=MagicMock) as mock_open:

        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_bytes"
        mock_open.return_value.__enter__.return_value = mock_file

        # Test with a path
        test_path = "./zebra.jpg"
        # We need to make sure this path is in DEFAULT_IMAGES or mock DEFAULT_IMAGES
        if test_path not in bg_remove.DEFAULT_IMAGES:
            bg_remove.DEFAULT_IMAGES.append(test_path)

        result_tuple = bg_remove.fix_image(test_path)

        # Assert result is not None
        assert result_tuple is not None, "fix_image returned None"

        # Unpack return values
        _, _, actual_filename, _ = result_tuple

        assert actual_filename == "zebra_rmbg.png"
