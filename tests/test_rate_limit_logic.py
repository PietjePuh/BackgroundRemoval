"""Tests for rate limiting logic."""

import time
from unittest.mock import patch


class TestCheckRateLimit:
    """Tests for the check_rate_limit function."""

    def test_first_request_allowed(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_st.session_state.clear()

        assert bg_remove.check_rate_limit() is True
        assert "request_times" in mock_st.session_state
        assert len(mock_st.session_state["request_times"]) == 1

    def test_five_requests_within_window_allowed(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_st.session_state.clear()

        for i in range(5):
            assert bg_remove.check_rate_limit() is True

        assert len(mock_st.session_state["request_times"]) == 5

    def test_sixth_request_blocked(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_st.session_state.clear()

        for _ in range(5):
            bg_remove.check_rate_limit()

        assert bg_remove.check_rate_limit() is False

    def test_requests_allowed_after_window_expires(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_st.session_state.clear()

        # Fill up the limit
        for _ in range(5):
            bg_remove.check_rate_limit()

        # Advance time by 61 seconds
        future_time = time.time() + 61
        with patch("time.time", return_value=future_time):
            assert bg_remove.check_rate_limit() is True
            # Old requests should be cleaned up
            assert len(mock_st.session_state["request_times"]) == 1

    def test_initializes_session_state(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_st.session_state.clear()

        assert "request_times" not in mock_st.session_state
        bg_remove.check_rate_limit()
        assert "request_times" in mock_st.session_state
