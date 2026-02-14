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
# Mock caches as pass-through
mock_st.cache_data = lambda *args, **kwargs: lambda func: func
mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
# Mock session state
mock_st.session_state = {}

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['numpy'] = MagicMock()

mock_image_module = MagicMock()
class MockDecompressionBombError(Exception):
    pass
mock_image_module.DecompressionBombError = MockDecompressionBombError

sys.modules['PIL'] = MagicMock()
sys.modules['PIL'].Image = mock_image_module
sys.modules['PIL.Image'] = mock_image_module

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove

def test_fix_image_filename_string():
    """Test that fix_image uses the correct filename for download button (string input)."""
    # Mock process_image to return dummy images
    with patch.object(bg_remove, "process_image") as mock_process:
        mock_img = MagicMock()
        mock_fixed = MagicMock()
        mock_process.return_value = (mock_img, mock_fixed)

        # Mock convert_image
        with patch.object(bg_remove, "convert_image", return_value=b"fake_bytes"):
            # Mock os.path.exists to allow default image check
            with patch("os.path.exists", return_value=True):
                # Mock builtins.open
                with patch("builtins.open", new_callable=MagicMock) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = b"fake_bytes_from_file"

                    # Add test path to allowed default images temporarily or mock check
                    original_defaults = bg_remove.DEFAULT_IMAGES
                    bg_remove.DEFAULT_IMAGES = ["test_image.jpg"]

                    try:
                        bg_remove.fix_image("test_image.jpg")

                        # Check download button call
                        # Arguments: label, data, file_name, mime, ...
                        # We look for file_name
                        assert mock_col2.download_button.called
                        args, kwargs = mock_col2.download_button.call_args

                        # Check file_name argument (positional or keyword)
                        # signature: download_button(label, data, file_name=None, mime=None, ...)
                        # In code: download_button("...", convert_image(fixed), "fixed.png", "image/png", ...)
                        # So file_name is likely the 3rd positional arg

                        actual_filename = kwargs.get('file_name')
                        if actual_filename is None and len(args) > 2:
                            actual_filename = args[2]

                        # NEW BEHAVIOR: expects dynamic filename
                        assert actual_filename == "test_image_rmbg.png"

                    finally:
                        bg_remove.DEFAULT_IMAGES = original_defaults

def test_fix_image_filename_uploaded_file():
    """Test that fix_image uses the correct filename for download button (UploadedFile input)."""
    # Mock process_image
    with patch.object(bg_remove, "process_image") as mock_process:
        mock_img = MagicMock()
        mock_fixed = MagicMock()
        mock_process.return_value = (mock_img, mock_fixed)

        with patch.object(bg_remove, "convert_image", return_value=b"fake_bytes"):
            # Mock UploadedFile
            mock_upload = MagicMock()
            mock_upload.name = "my_upload.jpg"
            mock_upload.getvalue.return_value = b"bytes"
            # It needs to not be a string

            bg_remove.fix_image(mock_upload)

            assert mock_col2.download_button.called
            args, kwargs = mock_col2.download_button.call_args

            actual_filename = kwargs.get('file_name')
            if actual_filename is None and len(args) > 2:
                actual_filename = args[2]

            # NEW BEHAVIOR: expects dynamic filename
            assert actual_filename == "my_upload_rmbg.png"
