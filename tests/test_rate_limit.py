import sys
from unittest.mock import MagicMock, patch
import pytest
import os
import time

# Clean up sys.modules to ensure we load bg_remove with OUR mocks
keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'rembg' in k]
for k in keys_to_remove:
    del sys.modules[k]

# Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None
mock_st.cache_data = lambda *args, **kwargs: lambda func: func
# Initialize session_state as a dict
mock_st.session_state = {}

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove

def test_check_rate_limit_logic():
    """
    Test the check_rate_limit function logic.
    """
    # Ensure check_rate_limit exists (it will be added)
    if not hasattr(bg_remove, "check_rate_limit"):
        pytest.fail("check_rate_limit function not found in bg_remove module")

    # Reset session state
    mock_st.session_state.clear()

    # 1. First request -> Allowed
    assert bg_remove.check_rate_limit() is True
    assert "request_times" in mock_st.session_state
    assert len(mock_st.session_state["request_times"]) == 1

    # 2. Add 4 more requests -> Allowed (Total 5)
    for _ in range(4):
        assert bg_remove.check_rate_limit() is True

    assert len(mock_st.session_state["request_times"]) == 5

    # 3. 6th request -> Blocked
    assert bg_remove.check_rate_limit() is False

    # 4. Advance time by 61 seconds -> Allowed again
    future_time = time.time() + 61
    with patch('time.time', return_value=future_time):
        assert bg_remove.check_rate_limit() is True
        # Old requests should be gone, only the new one remains
        assert len(mock_st.session_state["request_times"]) == 1
