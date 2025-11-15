"""Downloader modules for various music services."""
from __future__ import annotations

from .base import (
    BaseDownloader,
    DownloadResult,
    DownloadError,
    TrackNotFoundError,
    DownloadFailedError,
    MetadataError,
)
from .deezer import DeezerDownloader
from .tidal import TidalDownloader

__all__ = [
    "BaseDownloader",
    "DownloadResult",
    "DownloadError",
    "TrackNotFoundError",
    "DownloadFailedError",
    "MetadataError",
    "DeezerDownloader",
    "TidalDownloader",
]
