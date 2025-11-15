"""Base downloader interface for all music service downloaders."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional


@dataclass
class DownloadResult:
    """Result of a download operation.
    
    Attributes:
        success: Whether the download succeeded
        file_path: Path to downloaded file (if successful)
        error: Error message (if failed)
        metadata: Additional metadata about the download
        bytes_downloaded: Number of bytes downloaded
    """
    
    success: bool
    file_path: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    bytes_downloaded: int = 0
    
    def __post_init__(self):
        """Initialize metadata dict if None."""
        if self.metadata is None:
            self.metadata = {}


class BaseDownloader(ABC):
    """Abstract base class for music service downloaders.
    
    All downloader implementations (Deezer, Tidal, etc.) should inherit
    from this class and implement the required methods.
    
    Example:
        >>> class MyDownloader(BaseDownloader):
        ...     def download_track(self, isrc: str, output_path: Path) -> DownloadResult:
        ...         # Implementation
        ...         pass
        ...     
        ...     def set_progress_callback(self, callback: Callable) -> None:
        ...         self.progress_callback = callback
    """
    
    @abstractmethod
    def download_track(
        self,
        isrc: str,
        output_path: Path,
        *,
        filename: Optional[str] = None,
    ) -> DownloadResult:
        """Download a track by ISRC code.
        
        Args:
            isrc: International Standard Recording Code
            output_path: Directory where file should be saved
            filename: Optional custom filename (without extension)
            
        Returns:
            DownloadResult with success status and details
            
        Raises:
            DownloadError: If download fails
        """
        pass
    
    @abstractmethod
    def set_progress_callback(self, callback: Optional[Callable[[int, int], None]]) -> None:
        """Set callback for download progress updates.
        
        Args:
            callback: Function called with (bytes_downloaded, total_bytes).
                     Set to None to disable progress callbacks.
        """
        pass
    
    def validate_isrc(self, isrc: str) -> bool:
        """Validate ISRC format.
        
        ISRC format: CC-XXX-YY-NNNNN
        - CC: Country code (2 letters)
        - XXX: Registrant code (3 alphanumeric)
        - YY: Year (2 digits)
        - NNNNN: Designation code (5 digits)
        
        Args:
            isrc: ISRC code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isrc or len(isrc) < 12:
            return False
        
        # Remove hyphens for validation
        clean_isrc = isrc.replace('-', '').replace(' ', '')
        
        if len(clean_isrc) != 12:
            return False
        
        # Check format: 2 letters, 3 alphanumeric, 2 digits, 5 digits
        if not (clean_isrc[:2].isalpha() and
                clean_isrc[2:5].isalnum() and
                clean_isrc[5:7].isdigit() and
                clean_isrc[7:12].isdigit()):
            return False
        
        return True


class DownloadError(Exception):
    """Base exception for download errors."""
    pass


class TrackNotFoundError(DownloadError):
    """Raised when track cannot be found by ISRC."""
    pass


class DownloadFailedError(DownloadError):
    """Raised when download fails."""
    pass


class MetadataError(DownloadError):
    """Raised when metadata operations fail."""
    pass


__all__ = [
    "BaseDownloader",
    "DownloadResult",
    "DownloadError",
    "TrackNotFoundError",
    "DownloadFailedError",
    "MetadataError",
]
