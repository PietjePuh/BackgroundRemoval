import sys
import unittest
from unittest.mock import MagicMock, patch

# 1. Mock streamlit modules BEFORE importing bg_remove
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st
# Setup specific return values for st calls used at top level
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None

# 2. Mock other heavy dependencies
sys.modules["rembg"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["numpy"] = MagicMock()

# 3. Now import the app
import bg_remove
import os

class TestSecurityFix(unittest.TestCase):
    def test_path_traversal_prevention(self):
        # We want to call fix_image with a path NOT in the allowed list
        # and verify it gets blocked.

        # Define a path that exists but shouldn't be allowed
        test_path = "requirements.txt"

        # Reset mock to clear previous calls (from import time)
        mock_st.error.reset_mock()

        # Call the function
        bg_remove.fix_image(test_path)

        # Check if st.error was called with the expected message
        calls = [args[0] for args, _ in mock_st.error.call_args_list]
        print(f"st.error calls: {calls}")

        # We expect a security error
        self.assertIn("Security violation: Invalid file path provided.", calls)

        # Verify it did NOT try to open the file (which would call st.error("Default image not found...") if check failed,
        # or proceed to processing).
        # Actually, if we pass a valid path like "requirements.txt", the original code would have proceeded.
        # The new code returns early.

    def test_allowed_path(self):
        # Verify allowed paths still work
        allowed_path = "./zebra.jpg" # This is in DEFAULT_IMAGES

        # Mock os.path.exists to True so it proceeds
        with patch("os.path.exists", return_value=True):
             # Mock builtin open because bg_remove uses `open(...)`
             with patch("builtins.open", unittest.mock.mock_open(read_data=b"fake_image_data")):
                 # Mock process_image to return dummy data so it doesn't fail
                 # Note: process_image is decorated with @st.cache_data, which is a mock.
                 # Depending on how the mock is set up, `bg_remove.process_image` might be the wrapper or the original.
                 # Since we mocked st.cache_data as MagicMock, `@st.cache_data` call returns a MagicMock (the wrapper).
                 # So `bg_remove.process_image` IS a MagicMock.
                 bg_remove.process_image.return_value = (MagicMock(), MagicMock())

                 mock_st.error.reset_mock()
                 bg_remove.fix_image(allowed_path)

                 calls = [args[0] for args, _ in mock_st.error.call_args_list]
                 # Should be empty or at least NOT contain security violation
                 self.assertNotIn("Security violation: Invalid file path provided.", calls)

if __name__ == "__main__":
    unittest.main()
