"""Deezer API client for track metadata and downloads."""
from __future__ import annotations

import logging
import time
from typing import Dict, Any, Optional, Callable

import requests

logger = logging.getLogger(__name__)

from spotiflac.downloaders import TrackNotFoundError, DownloadError
from .utils import get_random_user_agent


class DeezerAPIError(DownloadError):
    """Raised when Deezer API returns an error."""
    pass


class DeezerAPIClient:
    """Client for interacting with Deezer API.
    
    Handles track lookups by ISRC and download URL retrieval.
    
    Example:
        >>> client = DeezerAPIClient()
        >>> track_data = client.get_track_by_isrc("USAT22409172")
        >>> download_url = client.get_download_url(track_data['id'])
    """
    
    DEEZER_API_BASE = "https://api.deezer.com/2.0"
    DEEZMATE_API_BASE = "https://api.deezmate.com"
    
    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        timeout: int = 30,
    ):
        """Initialize Deezer API client.
        
        Args:
            session: Optional requests.Session for connection pooling
            timeout: Request timeout in seconds (default: 30)
        """
        self.session = session or requests.Session()
        self.timeout = timeout
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Configure session with headers."""
        self.session.headers.update({
            'User-Agent': get_random_user_agent()
        })
    
    def get_track_by_isrc(self, isrc: str) -> Dict[str, Any]:
        """Fetch track data by ISRC code.
        
        Args:
            isrc: International Standard Recording Code
            
        Returns:
            Dictionary containing track metadata
            
        Raises:
            TrackNotFoundError: If track not found
            DeezerAPIError: If API returns an error
            
        Example:
            >>> client = DeezerAPIClient()
            >>> track = client.get_track_by_isrc("USAT22409172")
            >>> print(track['title'])
        """
        logger.debug(f"Fetching track info for ISRC: {isrc}")
        url = f"{self.DEEZER_API_BASE}/track/isrc:{isrc}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                if data['error'].get('type') == 'DataException':
                    raise TrackNotFoundError(f"Track not found for ISRC {isrc}: {error_msg}")
                logger.error(f"Deezer API error for track {isrc}: {data['error']}")
                raise DeezerAPIError(f"Deezer API error: {data['error']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch track {isrc}: {e}")
            raise DeezerAPIError(f"Failed to fetch track: {e}")
    
    def get_download_url(
        self,
        track_id: str,
        quality: str = "flac",
    ) -> str:
        """Get download URL for a track.
        
        Uses Deezmate API to obtain download links.
        
        Args:
            track_id: Deezer track ID
            quality: Audio quality (flac, mp3_320, mp3_128)
            
        Returns:
            Download URL for the track
            
        Raises:
            DeezerAPIError: If download URL cannot be obtained
            
        Example:
            >>> client = DeezerAPIClient()
            >>> url = client.get_download_url("123456789", quality="flac")
        """
        logger.debug(f"Fetching download URL for track {track_id}")
        api_url = f"{self.DEEZMATE_API_BASE}/dl/{track_id}"
        
        try:
            response = self.session.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                raise DeezerAPIError("Deezmate API request failed")
            
            links = data.get('links', {})
            download_url = links.get(quality)
            
            if not download_url:
                available = ', '.join(links.keys())
                raise DeezerAPIError(
                    f"Quality '{quality}' not available. Available: {available}"
                )
            
            return download_url
            
        except requests.exceptions.RequestException as e:
            raise DeezerAPIError(f"Failed to get download URL: {e}")
    
    def download_file(
        self,
        url: str,
        output_path: str,
        *,
        chunk_size: int = 8192,
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
            
        Raises:
            DeezerAPIError: If download fails
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
            raise DeezerAPIError(f"Failed to download file: {e}")
    
    def download_cover_art(self, cover_url: str) -> Optional[bytes]:
        """Download cover art image.
        
        Args:
            cover_url: URL to cover art image
            
        Returns:
            Image data as bytes, or None if download fails
        """
        if not cover_url:
            return None
        
        try:
            response = self.session.get(cover_url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException:
            return None


__all__ = [
    "DeezerAPIClient",
    "DeezerAPIError",
]
