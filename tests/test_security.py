import sys
from unittest.mock import MagicMock, patch, mock_open
import pytest
import os
import importlib

@pytest.fixture
def bg_remove_sec_env():
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    mock_st.cache_data = lambda func: func

    mock_rembg = MagicMock()
    mock_pil = MagicMock()
    mock_pil_image = MagicMock()
    mock_numpy = MagicMock()

    modules_to_patch = {
        'streamlit': mock_st,
        'rembg': mock_rembg,
        'PIL': mock_pil,
        'PIL.Image': mock_pil_image,
        'numpy': mock_numpy,
    }

    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

    with patch.dict(sys.modules, modules_to_patch):
        if 'bg_remove' in sys.modules:
            import bg_remove
            importlib.reload(bg_remove)
        else:
            import bg_remove
        yield bg_remove

def test_fix_image_blocks_arbitrary_file(bg_remove_sec_env):
    """
    Test that fix_image BLOCKS reading arbitrary files if passed as string.
    """
    bg_remove = bg_remove_sec_env
    test_file = "requirements.txt"

    m = mock_open(read_data=b"fake data")

    with patch("builtins.open", m), \
         patch("os.path.exists", return_value=True), \
         patch.object(bg_remove, "process_image") as mock_process:

        mock_process.return_value = (MagicMock(), MagicMock())

        bg_remove.fix_image(test_file)

        # ASSERTION: The file WAS NOT opened.
        m.assert_not_called()

def test_fix_image_reads_default_image(bg_remove_sec_env):
    """
    Test that fix_image works for default images.
    """
    bg_remove = bg_remove_sec_env
    test_file = "./zebra.jpg"
    m = mock_open(read_data=b"fake data")

    with patch("builtins.open", m), \
         patch("os.path.exists", return_value=True), \
         patch.object(bg_remove, "process_image") as mock_process:

        mock_process.return_value = (MagicMock(), MagicMock())

        bg_remove.fix_image(test_file)

        # ASSERTION: The file WAS opened.
        m.assert_called_with(test_file, "rb")
