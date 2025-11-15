"""Tidal downloader implementation."""
from __future__ import annotations

from .auth import TidalAuthenticator, TidalAuthError
from .client import TidalAPIClient, TidalAPIError
from .downloader import TidalDownloader
from .metadata import TidalTrackMetadata, TidalMetadataWriter
from .utils import TidalAPIDiscovery, TidalAPIDiscoveryError

__all__ = [
    "TidalDownloader",
    "TidalAPIClient",
    "TidalAPIError",
    "TidalAuthenticator",
    "TidalAuthError",
    "TidalTrackMetadata",
    "TidalMetadataWriter",
    "TidalAPIDiscovery",
    "TidalAPIDiscoveryError",
]
