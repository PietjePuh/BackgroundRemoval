
import sys
import os
from unittest.mock import MagicMock, patch, mock_open
import pytest

# Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
# Mock col1, col2
mock_col1 = MagicMock()
mock_col2 = MagicMock()
mock_st.columns.return_value = [mock_col1, mock_col2]
mock_st.sidebar.file_uploader.return_value = None

# Mock session_state
mock_st.session_state = {}

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove

def test_filename_from_string_path():
    """
    Test that fix_image generates the correct filename when input is a string path.
    """
    test_path = "./zebra.jpg"

    # Mock open and os.path.exists
    m = mock_open(read_data=b"fake data")

    with patch("builtins.open", m), \
         patch("os.path.exists", return_value=True), \
         patch.object(bg_remove, "process_image") as mock_process, \
         patch.object(bg_remove, "convert_image", return_value=b"fake_png"):

        # process_image returns (original, fixed)
        mock_process.return_value = (MagicMock(), MagicMock())

        bg_remove.fix_image(test_path)

        # Verify download_button call
        # It should be called on col2 (which is the second item in the mocked columns list)
        # However, bg_remove.col2 is the reference we want to check

        # In bg_remove.py:
        # col2.download_button(..., file_name="fixed.png", ...)

        # We want to assert it's now "zebra_rmbg.png"
        # Since we haven't changed the code yet, this test should FAIL with "fixed.png"

        args, kwargs = bg_remove.col2.download_button.call_args
        # Check either positional or keyword arg for file_name
        # The signature is: label, data, file_name, mime, ...
        # Current code: "fixed.png" is the 3rd positional arg

        print(f"Call args: {args}")
        print(f"Call kwargs: {kwargs}")

        if len(args) > 2:
            assert args[2] == "zebra_rmbg.png"
        else:
            assert kwargs.get("file_name") == "zebra_rmbg.png"

def test_filename_from_uploaded_file():
    """
    Test that fix_image generates the correct filename when input is an UploadedFile.
    """
    mock_upload = MagicMock()
    mock_upload.name = "my_photo.png"
    mock_upload.getvalue.return_value = b"fake data"

    with patch.object(bg_remove, "process_image") as mock_process, \
         patch.object(bg_remove, "convert_image", return_value=b"fake_png"):

        mock_process.return_value = (MagicMock(), MagicMock())

        bg_remove.fix_image(mock_upload)

        args, kwargs = bg_remove.col2.download_button.call_args

        if len(args) > 2:
            assert args[2] == "my_photo_rmbg.png"
        else:
            assert kwargs.get("file_name") == "my_photo_rmbg.png"
