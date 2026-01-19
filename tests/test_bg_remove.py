import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path to find bg_remove.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
# Configure st.columns to return 2 values for unpacking
mock_st.columns.return_value = [MagicMock(), MagicMock()]
# Configure file_uploader to return None to avoid executing processing logic on import
mock_st.sidebar.file_uploader.return_value = None
# Make cache_data a pass-through decorator so process_image is the real function
mock_st.cache_data = lambda func: func
sys.modules["streamlit"] = mock_st

sys.modules["rembg"] = MagicMock()
sys.modules["numpy"] = MagicMock()
# Mock PIL
mock_pil = MagicMock()
sys.modules["PIL"] = mock_pil
# Ensure from PIL import Image works
mock_image_module = MagicMock()
mock_pil.Image = mock_image_module
sys.modules["PIL.Image"] = mock_image_module

# Add constants used in bg_remove
mock_image_module.LANCZOS = 1

# Import the module under test
import bg_remove

def test_process_image_exception_handling():
    print("Testing process_image exception handling...")

    # Mock Image.open on the imported module or the mock
    # bg_remove.Image refers to the mock_image_module

    # We need to ensure that when Image.open is called, it raises exception
    # Since we mocked the module, bg_remove.Image IS mock_image_module

    # Reset side_effect from previous runs/imports if any
    mock_image_module.open.side_effect = Exception("SENSITIVE_PATH_INFO")

    # Call the function
    img, fixed = bg_remove.process_image(b"fake_data")

    # Verify it handled the error gracefully
    assert img is None
    assert fixed is None

    # Verify st.error was called
    assert bg_remove.st.error.called

    # Verify the error message does NOT contain the sensitive info
    # call_args is (args, kwargs)
    error_message = bg_remove.st.error.call_args[0][0]
    print(f"Error message shown: {error_message}")

    assert "SENSITIVE_PATH_INFO" not in error_message
    assert "An error occurred while processing the image" in error_message

def test_fix_image_exception_handling():
    print("\nTesting fix_image exception handling...")

    # Patch process_image to raise exception
    original_process_image = bg_remove.process_image
    bg_remove.process_image = MagicMock(side_effect=Exception("DB_CONNECTION_STRING"))

    # Reset st.error mock
    bg_remove.st.error.reset_mock()

    try:
        # Create a mock upload object
        mock_upload = MagicMock()
        mock_upload.getvalue.return_value = b"data"

        bg_remove.fix_image(mock_upload)

        # Verify st.error was called
        found_generic = False
        found_sensitive = False

        for call in bg_remove.st.error.call_args_list:
            msg = call[0][0]
            print(f"st.error called with: {msg}")
            if "An error occurred while processing the image" in msg:
                found_generic = True
            if "DB_CONNECTION_STRING" in msg:
                found_sensitive = True

        assert found_generic, "Generic error message not found"
        assert not found_sensitive, "Sensitive info leaked in st.error"

    finally:
        bg_remove.process_image = original_process_image

if __name__ == "__main__":
    try:
        test_process_image_exception_handling()
        test_fix_image_exception_handling()
        print("\nAll security tests passed!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTEST ERROR: {e}")
        # print traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)
