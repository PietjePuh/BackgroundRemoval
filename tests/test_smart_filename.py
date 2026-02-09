import sys
from unittest.mock import MagicMock, patch, ANY
import pytest
import os

# Move setup inside a fixture to avoid import time side effects and ensure clean state
@pytest.fixture(scope="function")
def mock_bg_remove():
    # Clean up sys.modules
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'PIL' in k or 'streamlit' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # Mock modules
    mock_st = MagicMock()
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_st.columns.return_value = [mock_col1, mock_col2]
    mock_st.sidebar = MagicMock()
    mock_st.sidebar.file_uploader.return_value = None
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    mock_st.set_page_config = MagicMock()
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.sidebar.header = MagicMock()
    mock_st.sidebar.progress.return_value = MagicMock()
    mock_st.sidebar.empty.return_value = MagicMock()
    mock_st.session_state = {}
    mock_st.stop = MagicMock()

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()

    mock_image_module = MagicMock()
    class MockDecompressionBombError(Exception):
        pass
    mock_image_module.DecompressionBombError = MockDecompressionBombError
    mock_image_module.LANCZOS = 1
    mock_image_module.BICUBIC = 2
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL'].Image = mock_image_module
    sys.modules['PIL.Image'] = mock_image_module

    # Import bg_remove
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove
    return bg_remove, mock_col2

def test_download_button_uses_smart_filename_path(mock_bg_remove):
    """
    Test that the download button uses a smart filename when processing a file path.
    Input: "./zebra.jpg" -> Output: "zebra_rmbg.png"
    """
    bg_remove, mock_col2 = mock_bg_remove
    mock_img = MagicMock()
    mock_fixed = MagicMock()

    with patch.object(bg_remove, 'process_image', return_value=(mock_img, mock_fixed)):
        with patch.object(bg_remove, 'convert_image', return_value=b'fake_bytes'):
            with patch('os.path.exists', return_value=True):
                 with patch('builtins.open', new_callable=MagicMock):
                    bg_remove.fix_image("./zebra.jpg")

            args, kwargs = mock_col2.download_button.call_args
            assert args[2] == "zebra_rmbg.png"

def test_download_button_uses_smart_filename_upload(mock_bg_remove):
    """
    Test that the download button uses a smart filename when processing an uploaded file.
    Input: UploadedFile(name="myphoto.jpeg") -> Output: "myphoto_rmbg.png"
    """
    bg_remove, mock_col2 = mock_bg_remove
    mock_img = MagicMock()
    mock_fixed = MagicMock()

    # Mock UploadedFile
    mock_upload = MagicMock()
    mock_upload.name = "myphoto.jpeg"
    mock_upload.getvalue.return_value = b'fake_bytes'

    with patch.object(bg_remove, 'process_image', return_value=(mock_img, mock_fixed)):
        with patch.object(bg_remove, 'convert_image', return_value=b'fake_bytes'):
            bg_remove.fix_image(mock_upload)

            args, kwargs = mock_col2.download_button.call_args
            assert args[2] == "myphoto_rmbg.png"
