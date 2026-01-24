import sys
import unittest
from unittest.mock import MagicMock, patch

# Create a mock for streamlit
st_mock = MagicMock()
sys.modules["streamlit"] = st_mock

# Mock columns to return a list of mocks, as they are unpacked
col1 = MagicMock()
col2 = MagicMock()
st_mock.columns.return_value = [col1, col2]

# Mock cache_data decorator
def cache_mock(func):
    return func
st_mock.cache_data = cache_mock

# Ensure file_uploader returns None so the script doesn't try to process immediately
st_mock.sidebar.file_uploader.return_value = None

# Mock dependencies used in process_image
sys.modules["rembg"] = MagicMock()
sys.modules["PIL"] = MagicMock()

# Now import the app module
# We need to suppress output because the app prints things
with patch('builtins.print'):
    import bg_remove

class TestBgRemove(unittest.TestCase):
    def setUp(self):
        # Reset mocks before each test
        st_mock.reset_mock()
        bg_remove.col1.reset_mock()
        bg_remove.col2.reset_mock()
        # Ensure process_image returns valid mocks
        self.mock_image = MagicMock()
        self.mock_fixed = MagicMock()

        # Patch process_image to avoid actual heavy lifting
        self.process_patcher = patch('bg_remove.process_image')
        self.mock_process = self.process_patcher.start()
        self.mock_process.return_value = (self.mock_image, self.mock_fixed)

    def tearDown(self):
        self.process_patcher.stop()

    def test_fix_image_ux_improvements(self):
        # Setup upload mock
        mock_upload = MagicMock()
        mock_upload.getvalue.return_value = b"data"

        # Call the function
        bg_remove.fix_image(mock_upload)

        # CHECK 1: Verify Subheaders
        bg_remove.col1.subheader.assert_called_with("Original Image :camera:")
        bg_remove.col2.subheader.assert_called_with("Fixed Image :wrench:")

        # CHECK 2: Verify Toast
        st_mock.toast.assert_called_with("Background removed successfully!", icon="🎉")

        print("Test ran successfully (all verifications passed)")

if __name__ == '__main__':
    unittest.main()
