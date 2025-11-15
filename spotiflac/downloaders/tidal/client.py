"""Tidal API client for track search and streaming."""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Callable

import requests

logger = logging.getLogger(__name__)

from spotiflac.downloaders import TrackNotFoundError, DownloadError
from .auth import TidalAuthenticator
from .utils import TidalAPIDiscovery


class TidalAPIError(DownloadError):
    """Raised when Tidal API returns an error."""
    pass


class TidalAPIClient:
    """Client for interacting with Tidal API.
    
    Handles track search by ISRC and stream URL retrieval.
    
    Example:
        >>> client = TidalAPIClient()
        >>> track = client.search_track_by_isrc("USAT22409172")
        >>> url = client.get_stream_url(track['id'])
    """
    
    def __init__(
        self,
        *,
        api_url: Optional[str] = None,
        authenticator: Optional[TidalAuthenticator] = None,
        timeout: int = 30,
    ):
        """Initialize Tidal API client.
        
        Args:
            api_url: Base URL of Tidal API proxy for downloads (None for auto-discovery)
            authenticator: Optional TidalAuthenticator instance
            timeout: Request timeout in seconds
        """
        self.authenticator = authenticator or TidalAuthenticator(timeout=timeout)
        self.timeout = timeout
        self.session = requests.Session()
        
        # Use official Tidal API for search
        self.search_api_url = "https://api.tidal.com"
        
        # Use proxy for downloads (like legacy version)
        if api_url:
            self.download_api_url = api_url
        else:
            self.download_api_url = TidalAPIDiscovery.get_api_with_fallback()
        
        # Don't setup session in __init__ - do it lazily on first request
        # This allows us to catch auth errors in download_track
        self._token: Optional[str] = None
    
    def _ensure_authenticated(self) -> None:
        """Ensure session is authenticated (lazy initialization)."""
        if self._token:
            return
        
        self._token = self.authenticator.get_access_token(self.search_api_url)
        self.session.headers.update({
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
        })
    
    def search_track_by_isrc(self, isrc: str, query: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for track by ISRC code.
        
        Args:
            isrc: International Standard Recording Code
            query: Optional search query (track name) for better results
            
        Returns:
            Dictionary containing track data
            
        Raises:
            TrackNotFoundError: If track not found
            TidalAPIError: If API returns an error
        """
        # Ensure we're authenticated before making requests
        self._ensure_authenticated()
        
        logger.debug(f"Searching Tidal track by ISRC: {isrc}")
        search_url = f"{self.search_api_url}/v1/search/tracks"
        
        # Use track name for search if provided, otherwise try ISRC
        search_query = query if query else isrc
        
        try:
            response = self.session.get(
                search_url,
                params={
                    'query': search_query,
                    'limit': 25,  # Get more results to filter by ISRC
                    'offset': 0,
                    'countryCode': 'US'
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                raise TrackNotFoundError(f"Track not found for ISRC {isrc}")
            
            # Filter by ISRC if we have results
            isrc_matches = [item for item in items if item.get('isrc') == isrc]
            
            if isrc_matches:
                # Prefer HIRES_LOSSLESS if available
                hires_items = [
                    item for item in isrc_matches
                    if 'HIRES_LOSSLESS' in item.get('mediaMetadata', {}).get('tags', [])
                ]
                return hires_items[0] if hires_items else isrc_matches[0]
            
            # If no ISRC match, return first result (fallback)
            return items[0]
            
        except requests.exceptions.RequestException as e:
            raise TidalAPIError(f"Failed to search track: {e}")
    
    def get_stream_url(
        self,
        track_id: str,
        quality: str = "LOSSLESS",
    ) -> str:
        """Get streaming URL for a track.
        
        Args:
            track_id: Tidal track ID
            quality: Audio quality (LOSSLESS, HIGH, LOW)
            
        Returns:
            Streaming URL
            
        Raises:
            TidalAPIError: If stream URL cannot be obtained
        """
        # Use proxy API for download URL (like legacy version)
        download_url = f"{self.download_api_url}/track/?id={track_id}&quality={quality}"
        
        logger.debug(f"Fetching download URL from proxy: {self.download_api_url}")
        
        try:
            # Don't use auth headers for proxy requests
            response = requests.get(download_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Legacy format: array with OriginalTrackUrl
            for item in data:
                if "OriginalTrackUrl" in item:
                    logger.debug("Download URL found")
                    return item["OriginalTrackUrl"]
            
            raise TidalAPIError("Download URL not found in response")
            
        except requests.exceptions.RequestException as e:
            raise TidalAPIError(f"Failed to get stream URL: {e}")
    
    def download_file(
        self,
        url: str,
        output_path: str,
        *,
        chunk_size: int = 256 * 1024,
        progress_callback: Optional[callable] = None,
    ) -> int:
        """Download file from URL.
        
        Args:
            url: Download URL
            output_path: Path where file should be saved
            chunk_size: Size of chunks for streaming download
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
            
        Returns:
            Total bytes downloaded
        """
        try:
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(bytes_downloaded, total_size)
            
            return bytes_downloaded
            
        except requests.exceptions.RequestException as e:
            raise TidalAPIError(f"Failed to download file: {e}")
    
    def download_cover_art(self, cover_id: str, size: int = 1280) -> Optional[bytes]:
        """Download cover art image.
        
        Args:
            cover_id: Tidal cover ID
            size: Image size (320, 640, 1280)
            
        Returns:
            Image data as bytes, or None if download fails
        """
        if not cover_id:
            return None
        
        # Tidal cover URL format
        cover_url = f"https://resources.tidal.com/images/{cover_id.replace('-', '/')}/{size}x{size}.jpg"
        
        try:
            response = self.session.get(cover_url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException:
            return None


__all__ = [
    "TidalAPIClient",
    "TidalAPIError",
]
