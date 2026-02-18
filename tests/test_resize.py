"""Tests for image resize logic."""

import pytest
from unittest.mock import MagicMock


class TestResizeImage:
    """Tests for the resize_image function."""

    def test_does_not_resize_small_image(self, mock_env):
        bg_remove = mock_env["module"]

        mock_img = MagicMock()
        mock_img.size = (500, 500)

        result = bg_remove.resize_image(mock_img, 2000)

        assert result is mock_img
        mock_img.resize.assert_not_called()

    def test_resizes_wide_image(self, mock_env):
        bg_remove = mock_env["module"]

        mock_img = MagicMock()
        mock_img.size = (4000, 2000)
        mock_img.resize.return_value = MagicMock()

        result = bg_remove.resize_image(mock_img, 2000)

        mock_img.resize.assert_called_once()
        args, _ = mock_img.resize.call_args
        new_size = args[0]
        assert new_size[0] == 2000  # Width capped at max_size
        assert new_size[1] == 1000  # Height proportionally scaled

    def test_resizes_tall_image(self, mock_env):
        bg_remove = mock_env["module"]

        mock_img = MagicMock()
        mock_img.size = (1000, 5000)
        mock_img.resize.return_value = MagicMock()

        result = bg_remove.resize_image(mock_img, 2000)

        mock_img.resize.assert_called_once()
        args, _ = mock_img.resize.call_args
        new_size = args[0]
        assert new_size[0] == 400  # Width proportionally scaled
        assert new_size[1] == 2000  # Height capped at max_size

    def test_uses_bicubic_filter(self, mock_env):
        bg_remove = mock_env["module"]

        mock_img = MagicMock()
        mock_img.size = (5000, 5000)
        mock_img.resize.return_value = MagicMock()

        bg_remove.resize_image(mock_img, 2000)

        args, _ = mock_img.resize.call_args
        assert args[1] == bg_remove.Image.BICUBIC

    def test_image_exactly_at_max_not_resized(self, mock_env):
        bg_remove = mock_env["module"]

        mock_img = MagicMock()
        mock_img.size = (2000, 2000)

        result = bg_remove.resize_image(mock_img, 2000)

        assert result is mock_img
        mock_img.resize.assert_not_called()
