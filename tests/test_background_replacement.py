"""Tests for background replacement logic."""

from unittest.mock import MagicMock


class TestApplyBackgroundReplacement:
    """Tests for the apply_background_replacement function."""

    def test_transparent_mode_returns_original(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"

        result = bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="transparent",
        )

        assert result is fixed_img

    def test_solid_color_creates_colored_background(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"
        fixed_img.size = (100, 100)

        mock_background = MagicMock()
        mock_image_module.new.return_value = mock_background

        result = bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="solid_color",
            bg_color="#FF0000",
        )

        # Should create a new RGBA image with the specified color
        mock_image_module.new.assert_called_with("RGBA", (100, 100), (255, 0, 0, 255))
        # Should paste the foreground onto the background
        mock_background.paste.assert_called_once_with(fixed_img, (0, 0), fixed_img)
        assert result is mock_background

    def test_solid_color_parses_hex_correctly(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"
        fixed_img.size = (50, 50)
        mock_image_module.new.return_value = MagicMock()

        bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="solid_color",
            bg_color="#00FF80",
        )

        mock_image_module.new.assert_called_with("RGBA", (50, 50), (0, 255, 128, 255))

    def test_solid_color_handles_hash_prefix(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"
        fixed_img.size = (10, 10)
        mock_image_module.new.return_value = MagicMock()

        # With # prefix
        bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="solid_color",
            bg_color="#AABBCC",
        )

        mock_image_module.new.assert_called_with("RGBA", (10, 10), (170, 187, 204, 255))

    def test_blur_mode_uses_original_image(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"
        fixed_img.size = (200, 200)

        original_img = MagicMock()
        blurred_copy = MagicMock()
        blurred_copy.mode = "RGB"
        blurred_resized = MagicMock()
        blurred_resized.mode = "RGB"
        blurred_filtered = MagicMock()
        blurred_filtered.mode = "RGB"
        blurred_converted = MagicMock()

        original_img.copy.return_value = blurred_copy
        blurred_copy.resize.return_value = blurred_resized
        blurred_resized.filter.return_value = blurred_filtered
        blurred_filtered.convert.return_value = blurred_converted

        bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="blur",
            bg_blur_radius=20,
            original_img=original_img,
        )

        original_img.copy.assert_called_once()
        blurred_copy.resize.assert_called_once()
        blurred_resized.filter.assert_called_once()
        # Should paste foreground onto blurred background
        blurred_converted.paste.assert_called_once_with(fixed_img, (0, 0), fixed_img)

    def test_custom_image_mode_uses_uploaded_background(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"
        fixed_img.size = (300, 300)

        custom_bg = MagicMock()
        custom_bg_copy = MagicMock()
        custom_bg_resized = MagicMock()
        custom_bg_resized.mode = "RGB"
        custom_bg_converted = MagicMock()

        custom_bg.copy.return_value = custom_bg_copy
        custom_bg_copy.resize.return_value = custom_bg_resized
        custom_bg_resized.convert.return_value = custom_bg_converted

        bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="custom_image",
            bg_custom_image=custom_bg,
        )

        custom_bg.copy.assert_called_once()
        custom_bg_copy.resize.assert_called_once()
        custom_bg_converted.paste.assert_called_once_with(fixed_img, (0, 0), fixed_img)

    def test_converts_non_rgba_fixed_image(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGB"  # Not RGBA
        fixed_img.size = (100, 100)

        converted_img = MagicMock()
        converted_img.mode = "RGBA"
        converted_img.size = (100, 100)
        fixed_img.convert.return_value = converted_img

        mock_image_module.new.return_value = MagicMock()

        bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="solid_color",
            bg_color="#FFFFFF",
        )

        fixed_img.convert.assert_called_with("RGBA")

    def test_fallback_returns_image_for_unknown_mode(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"

        result = bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="nonexistent_mode",
        )

        assert result is fixed_img

    def test_solid_color_with_none_color_returns_as_is(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"

        result = bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="solid_color",
            bg_color=None,
        )

        # Should fall through to default return
        assert result is fixed_img

    def test_blur_without_original_returns_as_is(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"

        result = bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="blur",
            original_img=None,
        )

        assert result is fixed_img

    def test_custom_image_without_bg_returns_as_is(self, mock_env):
        bg_remove = mock_env["module"]

        fixed_img = MagicMock()
        fixed_img.mode = "RGBA"

        result = bg_remove.apply_background_replacement(
            fixed_img=fixed_img,
            bg_mode="custom_image",
            bg_custom_image=None,
        )

        assert result is fixed_img
