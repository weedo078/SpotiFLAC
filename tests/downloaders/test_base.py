"""Tests for base downloader interface."""
from __future__ import annotations

from pathlib import Path

import pytest

from spotiflac.downloaders import (
    BaseDownloader,
    DownloadResult,
    DownloadError,
    TrackNotFoundError,
    DownloadFailedError,
    MetadataError,
)


class TestDownloadResult:
    """Test DownloadResult dataclass."""

    def test_success_result(self):
        """Test successful download result."""
        result = DownloadResult(
            success=True,
            file_path=Path("/tmp/test.flac"),
            bytes_downloaded=1024000,
            metadata={"artist": "Test Artist"}
        )
        
        assert result.success is True
        assert result.file_path == Path("/tmp/test.flac")
        assert result.error is None
        assert result.bytes_downloaded == 1024000
        assert result.metadata["artist"] == "Test Artist"

    def test_failure_result(self):
        """Test failed download result."""
        result = DownloadResult(
            success=False,
            error="Track not found"
        )
        
        assert result.success is False
        assert result.file_path is None
        assert result.error == "Track not found"
        assert result.bytes_downloaded == 0

    def test_metadata_default_dict(self):
        """Test metadata defaults to empty dict."""
        result = DownloadResult(success=True)
        
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)


class TestBaseDownloader:
    """Test BaseDownloader abstract class."""

    def test_cannot_instantiate_directly(self):
        """BaseDownloader cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseDownloader()

    def test_validate_isrc_valid(self):
        """Test ISRC validation with valid codes."""
        # Create a concrete implementation for testing
        class TestDownloader(BaseDownloader):
            def download_track(self, isrc, output_path, *, filename=None):
                pass
            
            def set_progress_callback(self, callback):
                pass
        
        downloader = TestDownloader()
        
        # Valid ISRC codes
        assert downloader.validate_isrc("USAT22409172") is True
        assert downloader.validate_isrc("US-AT2-24-09172") is True
        assert downloader.validate_isrc("GBAYE1200123") is True
        assert downloader.validate_isrc("GB-AYE-12-00123") is True

    def test_validate_isrc_invalid(self):
        """Test ISRC validation with invalid codes."""
        class TestDownloader(BaseDownloader):
            def download_track(self, isrc, output_path, *, filename=None):
                pass
            
            def set_progress_callback(self, callback):
                pass
        
        downloader = TestDownloader()
        
        # Invalid ISRC codes
        assert downloader.validate_isrc("") is False
        assert downloader.validate_isrc("TOOLONG123456") is False
        assert downloader.validate_isrc("SHORT") is False
        assert downloader.validate_isrc("12AT22409172") is False  # Starts with digits
        assert downloader.validate_isrc("USAT2240917X") is False  # Letter in designation
        assert downloader.validate_isrc(None) is False

    def test_validate_isrc_with_hyphens(self):
        """Test ISRC validation handles hyphens correctly."""
        class TestDownloader(BaseDownloader):
            def download_track(self, isrc, output_path, *, filename=None):
                pass
            
            def set_progress_callback(self, callback):
                pass
        
        downloader = TestDownloader()
        
        # With and without hyphens should both work
        assert downloader.validate_isrc("USAT22409172") is True
        assert downloader.validate_isrc("US-AT2-24-09172") is True
        assert downloader.validate_isrc("US AT2 24 09172") is True  # Spaces


class TestExceptions:
    """Test custom exception classes."""

    def test_download_error(self):
        """Test DownloadError exception."""
        with pytest.raises(DownloadError, match="Test error"):
            raise DownloadError("Test error")

    def test_track_not_found_error(self):
        """Test TrackNotFoundError exception."""
        with pytest.raises(TrackNotFoundError, match="Track not found"):
            raise TrackNotFoundError("Track not found")
        
        # Should also be catchable as DownloadError
        with pytest.raises(DownloadError):
            raise TrackNotFoundError("Track not found")

    def test_download_failed_error(self):
        """Test DownloadFailedError exception."""
        with pytest.raises(DownloadFailedError, match="Download failed"):
            raise DownloadFailedError("Download failed")

    def test_metadata_error(self):
        """Test MetadataError exception."""
        with pytest.raises(MetadataError, match="Metadata error"):
            raise MetadataError("Metadata error")


class TestConcreteImplementation:
    """Test that concrete implementations work correctly."""

    def test_minimal_implementation(self):
        """Test minimal concrete implementation."""
        class MinimalDownloader(BaseDownloader):
            def __init__(self):
                self.callback = None
            
            def download_track(self, isrc, output_path, *, filename=None):
                if not self.validate_isrc(isrc):
                    return DownloadResult(success=False, error="Invalid ISRC")
                
                return DownloadResult(
                    success=True,
                    file_path=output_path / f"{filename or isrc}.flac",
                    bytes_downloaded=1024
                )
            
            def set_progress_callback(self, callback):
                self.callback = callback
        
        downloader = MinimalDownloader()
        
        # Test download
        result = downloader.download_track("USAT22409172", Path("/tmp"))
        assert result.success is True
        assert result.file_path == Path("/tmp/USAT22409172.flac")
        
        # Test with invalid ISRC
        result = downloader.download_track("INVALID", Path("/tmp"))
        assert result.success is False
        assert result.error == "Invalid ISRC"
        
        # Test progress callback
        callback = lambda current, total: None
        downloader.set_progress_callback(callback)
        assert downloader.callback is callback
