from __future__ import annotations

from typing import Dict, Any

# Import new modular metadata client
from spotiflac.metadata.spotify import (
    SpotifyAPIClient,
    SpotifyInvalidUrlException,
)


class SpotifyMetadataService:
    """Service facade for Spotify metadata operations.
    
    Provides a clean interface to Spotify metadata fetching.
    
    Example:
        >>> service = SpotifyMetadataService()
        >>> metadata = service.fetch_metadata("https://open.spotify.com/track/...")
        >>> url_info = service.parse_url("https://open.spotify.com/album/...")
    """
    
    def __init__(self, *, api_client: Any = None):
        """Initialize service.
        
        Args:
            api_client: Optional SpotifyAPIClient instance
        """
        self.api_client = api_client or SpotifyAPIClient()

    def fetch_metadata(self, url: str, **kwargs) -> Dict[str, Any]:
        """Fetch complete metadata for a Spotify URL.
        
        Args:
            url: Spotify URL (track, album, playlist, artist)
            **kwargs: Additional arguments passed to API client
            
        Returns:
            Metadata dictionary with track/album/playlist information (legacy format)
            
        Raises:
            SpotifyInvalidUrlException: If URL format is invalid
        """
        # Get data from new API client
        raw_data = self.api_client.fetch_metadata(url, **kwargs)
        
        # Convert to legacy format for backward compatibility
        return self._convert_to_legacy_format(raw_data, url)

    def _convert_to_legacy_format(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        # TO DO: implement conversion logic here
        # For now, just return the raw data
        return raw_data

    def parse_url(self, url: str) -> Dict[str, Any]:
        """Parse Spotify URL and extract type and ID information.
        
        Args:
            url: Spotify URL to parse
            
        Returns:
            Dictionary with 'type' (track/album/playlist/artist) and 'id'
            
        Raises:
            SpotifyInvalidUrlException: If URL format is invalid
        """
        return self.api_client.parser.parse(url)


__all__ = ["SpotifyMetadataService", "SpotifyInvalidUrlException"]
