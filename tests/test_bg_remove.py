import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock dependencies
mock_st = MagicMock()
# Mock cache_data
def mock_cache_data(func):
    return func
mock_st.cache_data = mock_cache_data

# Mock columns to return 2 items
mock_st.columns.return_value = [MagicMock(), MagicMock()]

# Mock file_uploader to return None by default so script doesn't run fix_image automatically
mock_st.sidebar.file_uploader.return_value = None

sys.modules["streamlit"] = mock_st
mock_rembg = MagicMock()
sys.modules["rembg"] = mock_rembg

class TestBgRemoveSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Import the module
        if "bg_remove" in sys.modules:
            del sys.modules["bg_remove"]
        import bg_remove
        cls.module = bg_remove

    def setUp(self):
        mock_st.reset_mock()
        # Restore return values that reset_mock might clear if not configured on the instance properly
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.sidebar.file_uploader.return_value = None

    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.path.exists")
    def test_fix_image_path_traversal_blocked(self, mock_exists, mock_open):
        """Test that passing an unauthorized path does NOT open the file."""
        # Arrange
        bad_path = "/etc/passwd"
        mock_exists.return_value = True

        # Act
        self.module.fix_image(bad_path)

        # Assert
        # The secure implementation should NOT open the file
        mock_open.assert_not_called()

    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.path.exists")
    def test_fix_image_valid_default(self, mock_exists, mock_open):
        """Test that a valid default image IS processed."""
        # Arrange
        valid_path = "./zebra.jpg"
        mock_exists.return_value = True

        with patch("bg_remove.process_image") as mock_process:
            mock_process.return_value = (MagicMock(), MagicMock())

            # Act
            self.module.fix_image(valid_path)

            # Assert
            mock_open.assert_called_with(valid_path, "rb")

if __name__ == "__main__":
    unittest.main()
