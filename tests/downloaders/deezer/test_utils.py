"""Tests for Deezer downloader utilities."""
from __future__ import annotations

import pytest

from spotiflac.downloaders.deezer.utils import (
    get_random_user_agent,
    sanitize_filename,
    format_file_size,
)


class TestGetRandomUserAgent:
    """Test User-Agent generation."""

    def test_returns_string(self):
        """User-Agent should be a string."""
        ua = get_random_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 0

    def test_contains_mozilla(self):
        """User-Agent should contain Mozilla."""
        ua = get_random_user_agent()
        assert "Mozilla/5.0" in ua

    def test_contains_chrome(self):
        """User-Agent should contain Chrome."""
        ua = get_random_user_agent()
        assert "Chrome" in ua

    def test_contains_safari(self):
        """User-Agent should contain Safari."""
        ua = get_random_user_agent()
        assert "Safari" in ua

    def test_randomness(self):
        """Multiple calls should produce different User-Agents."""
        user_agents = {get_random_user_agent() for _ in range(10)}
        # At least some should be different (very high probability)
        assert len(user_agents) > 1

    def test_realistic_format(self):
        """User-Agent should have realistic version numbers."""
        ua = get_random_user_agent()
        # Should contain version-like patterns
        assert any(char.isdigit() for char in ua)
        assert "AppleWebKit" in ua


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_removes_invalid_characters(self):
        """Invalid characters should be replaced."""
        assert sanitize_filename('test<>:"/\\|?*file') == "test_________file"

    def test_preserves_valid_characters(self):
        """Valid characters should be preserved."""
        assert sanitize_filename("Artist - Song (2024)") == "Artist - Song (2024)"

    def test_removes_leading_trailing_spaces(self):
        """Leading and trailing spaces should be removed."""
        assert sanitize_filename("  test  ") == "test"

    def test_removes_leading_trailing_dots(self):
        """Leading and trailing dots should be removed."""
        assert sanitize_filename("..test..") == "test"

    def test_handles_empty_string(self):
        """Empty string should return default name."""
        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename("   ") == "unnamed"

    def test_handles_only_invalid_chars(self):
        """String with only invalid chars should be replaced."""
        result = sanitize_filename("<>?*")
        # All invalid chars replaced with underscore, then stripped
        assert result == "____" or result == "unnamed"

    def test_max_length(self):
        """Filename should be truncated to max length."""
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=100)
        assert len(result) == 100

    def test_max_length_default(self):
        """Default max length should be 255."""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) == 255

    def test_real_world_examples(self):
        """Test with real-world filename patterns."""
        assert sanitize_filename('Artist: "Song Title"') == 'Artist_ _Song Title_'
        # # is not an invalid character, so it's preserved
        assert sanitize_filename('Track #1') == 'Track #1'
        assert sanitize_filename('Song/Remix') == 'Song_Remix'
        assert sanitize_filename('Test\\Path') == 'Test_Path'


class TestFormatFileSize:
    """Test file size formatting."""

    def test_bytes(self):
        """Format bytes correctly."""
        assert format_file_size(0) == "0.0 B"
        assert format_file_size(500) == "500.0 B"
        assert format_file_size(1023) == "1023.0 B"

    def test_kilobytes(self):
        """Format kilobytes correctly."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(10240) == "10.0 KB"

    def test_megabytes(self):
        """Format megabytes correctly."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536 * 1024) == "1.5 MB"
        assert format_file_size(10 * 1024 * 1024) == "10.0 MB"

    def test_gigabytes(self):
        """Format gigabytes correctly."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(2 * 1024 * 1024 * 1024) == "2.0 GB"

    def test_terabytes(self):
        """Format terabytes correctly."""
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_decimal_precision(self):
        """Decimal precision should be one digit."""
        result = format_file_size(1536000)
        assert result.count('.') == 1
        # Should have one decimal place
        assert len(result.split('.')[1].split()[0]) == 1
