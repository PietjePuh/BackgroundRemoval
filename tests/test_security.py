import sys
from unittest.mock import MagicMock, patch, mock_open
import os

# 1. Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None

sys.modules["streamlit"] = mock_st
sys.modules["rembg"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["numpy"] = MagicMock()

# 2. Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
import bg_remove  # noqa: E402


def test_fix_image_blocks_arbitrary_file():
    """
    Test that fix_image BLOCKS reading arbitrary files if passed as string.
    """
    test_file = "requirements.txt"

    m = mock_open(read_data=b"fake data")

    with (
        patch("builtins.open", m),
        patch("os.path.exists", return_value=True),
        patch.object(bg_remove, "process_image") as mock_process,
    ):
        mock_process.return_value = (MagicMock(), MagicMock())

        bg_remove.fix_image(test_file)

        # ASSERTION: The file WAS NOT opened.
        m.assert_not_called()


def test_fix_image_reads_default_image():
    """
    Test that fix_image works for default images.
    """
    test_file = "./zebra.jpg"
    m = mock_open(read_data=b"fake data")

    with (
        patch("builtins.open", m),
        patch("os.path.exists", return_value=True),
        patch.object(bg_remove, "process_image") as mock_process,
    ):
        mock_process.return_value = (MagicMock(), MagicMock())

        bg_remove.fix_image(test_file)

        # ASSERTION: The file WAS opened.
        m.assert_called_with(test_file, "rb")
