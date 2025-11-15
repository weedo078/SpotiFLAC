"""Spotify API client for metadata fetching."""
from __future__ import annotations

from time import sleep
from typing import Dict, Any, Optional, Tuple, List
import requests
import time
import logging

logger = logging.getLogger(__name__)

from spotiflac.downloaders.deezer.utils import get_random_user_agent
from .auth import SpotifySecretManager, SpotifyAuthError
from .parser import SpotifyURLParser, SpotifyInvalidUrlException


class SpotifyAPIError(Exception):
    """Raised when Spotify API returns an error."""
    pass


class SpotifyAPIClient:
    """Client for Spotify Web API.
    
    Handles authentication, rate limiting, and metadata fetching.
    
    Example:
        >>> client = SpotifyAPIClient()
        >>> data = client.fetch_metadata("https://open.spotify.com/track/...")
    """
    
    TOKEN_URL = 'https://open.spotify.com/api/token'
    PLAYLIST_BASE_URL = 'https://api.spotify.com/v1/playlists/{}'
    ALBUM_BASE_URL = 'https://api.spotify.com/v1/albums/{}'
    TRACK_BASE_URL = 'https://api.spotify.com/v1/tracks/{}'
    ARTIST_BASE_URL = 'https://api.spotify.com/v1/artists/{}'
    ARTIST_ALBUMS_URL = 'https://api.spotify.com/v1/artists/{}/albums'
    
    def __init__(
        self,
        *,
        secret_manager: Optional[SpotifySecretManager] = None,
        parser: Optional[SpotifyURLParser] = None,
        timeout: int = 10,
    ):
        """Initialize Spotify API client.
        
        Args:
            secret_manager: Optional SpotifySecretManager instance
            parser: Optional SpotifyURLParser instance
            timeout: Request timeout in seconds
        """
        self.secret_manager = secret_manager or SpotifySecretManager()
        self.parser = parser or SpotifyURLParser()
        self.timeout = timeout
        self.session = requests.Session()
        self._setup_headers()
    
    def _setup_headers(self) -> None:
        """Configure default headers."""
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'Referer': 'https://open.spotify.com/',
            'Origin': 'https://open.spotify.com'
        })
    
    def get_access_token(self) -> str:
        """Obtain access token using TOTP.
        
        Returns:
            Access token string
            
        Raises:
            SpotifyAuthError: If token retrieval fails
        """
        try:
            totp, server_time, totp_version = self.secret_manager.generate_totp(self.timeout)
            otp_code = totp.at(int(server_time))
            timestamp_ms = int(time.time() * 1000)
            
            params = {
                'reason': 'init',
                'productType': 'web-player',
                'totp': otp_code,
                'totpServerTime': server_time,
                'totpVer': str(totp_version),
                'sTime': server_time,
                'cTime': timestamp_ms,
                'buildVer': 'web-player_2025-07-02_1720000000000_12345678',
                'buildDate': '2025-07-02'
            }
            
            resp = self.session.get(self.TOKEN_URL, params=params, timeout=self.timeout)
            if resp.status_code != 200:
                raise SpotifyAuthError(f"Failed to get access token. Status code: {resp.status_code}")
            
            data = resp.json()
            token = data.get('accessToken')
            
            if not token:
                raise SpotifyAuthError("No access token in response")
            
            return token
            
        except SpotifyAuthError:
            raise
        except Exception as e:
            raise SpotifyAuthError(f"Failed to get access token: {e}")
    
    def _api_request(self, url: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Make API request with rate limiting.
        
        Args:
            url: API endpoint URL
            access_token: Bearer token
            
        Returns:
            JSON response or None if rate limited
            
        Raises:
            SpotifyAPIError: If request fails
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if resp.status_code == 429:
                seconds = int(resp.headers.get("Retry-After", "5")) + 1
                sleep(seconds)
                return None
            
            if resp.status_code != 200:
                logger.error(f"Spotify API request failed: HTTP {resp.status_code}")
                raise SpotifyAPIError(f"API request failed: {resp.status_code}")
            
            return resp.json()
            
        except SpotifyAPIError:
            raise
        except Exception as e:
            raise SpotifyAPIError(f"API request failed: {e}")
    
    def fetch_metadata(
        self,
        spotify_url: str,
        *,
        batch: bool = False,
        delay: float = 1.0,
    ) -> Dict[str, Any]:
        logger.info(f"Fetching Spotify metadata for URL: {spotify_url}")
        """Fetch metadata for any Spotify URL.
        
        Args:
            spotify_url: Spotify URL (track, album, playlist, artist)
            batch: Enable batch fetching for large collections
            delay: Delay between batch requests
            
        Returns:
            Metadata dictionary
            
        Raises:
            SpotifyInvalidUrlException: If URL is invalid
            SpotifyAPIError: If fetching fails
        """
        url_info = self.parser.parse(spotify_url)
        access_token = self.get_access_token()
        
        url_type = url_info['type']
        
        if url_type == "track":
            return self._fetch_track(url_info['id'], access_token)
        elif url_type == "album":
            return self._fetch_album(url_info['id'], access_token, batch, delay)
        elif url_type == "playlist":
            return self._fetch_playlist(url_info['id'], access_token, batch, delay)
        elif url_type == "artist":
            return self._fetch_artist(url_info['id'], access_token)
        elif url_type == "artist_discography":
            return self._fetch_artist_discography(
                url_info['id'],
                url_info.get('discography_type', 'all'),
                access_token,
                batch,
                delay
            )
        else:
            raise SpotifyAPIError(f"Unsupported URL type: {url_type}")
    
    def _fetch_track(self, track_id: str, access_token: str) -> Dict[str, Any]:
        """Fetch single track metadata."""
        url = self.TRACK_BASE_URL.format(track_id)
        data = self._api_request(url, access_token)
        if not data:
            raise SpotifyAPIError("Failed to fetch track")
        return data
    
    def _fetch_album(
        self,
        album_id: str,
        access_token: str,
        batch: bool,
        delay: float
    ) -> Dict[str, Any]:
        """Fetch album with tracks."""
        url = self.ALBUM_BASE_URL.format(album_id)
        data = self._api_request(url, access_token)
        if not data:
            raise SpotifyAPIError("Failed to fetch album")
        
        data['_token'] = access_token
        
        # Fetch all tracks if needed
        if batch or data.get('total_tracks', 0) > 50:
            tracks_url = f"{url}/tracks?limit=50"
            all_tracks = self._fetch_paginated(tracks_url, access_token, delay)
            data['tracks']['items'] = all_tracks
        
        return data
    
    def _fetch_playlist(
        self,
        playlist_id: str,
        access_token: str,
        batch: bool,
        delay: float
    ) -> Dict[str, Any]:
        """Fetch playlist with tracks."""
        url = self.PLAYLIST_BASE_URL.format(playlist_id)
        data = self._api_request(url, access_token)
        if not data:
            raise SpotifyAPIError("Failed to fetch playlist")
        
        # Fetch all tracks
        tracks_url = f"{url}/tracks?limit=100"
        all_tracks = self._fetch_paginated(tracks_url, access_token, delay)
        data['tracks']['items'] = all_tracks
        
        return data
    
    def _fetch_artist(self, artist_id: str, access_token: str) -> Dict[str, Any]:
        """Fetch artist info."""
        url = self.ARTIST_BASE_URL.format(artist_id)
        data = self._api_request(url, access_token)
        if not data:
            raise SpotifyAPIError("Failed to fetch artist")
        return data
    
    def _fetch_artist_discography(
        self,
        artist_id: str,
        discography_type: str,
        access_token: str,
        batch: bool,
        delay: float
    ) -> Dict[str, Any]:
        """Fetch artist discography."""
        # Get artist info
        artist_data = self._fetch_artist(artist_id, access_token)
        
        # Determine include_groups
        if discography_type == "all":
            include_groups = "album,single,compilation"
        else:
            include_groups = discography_type
        
        # Fetch albums
        albums_url = f"{self.ARTIST_ALBUMS_URL.format(artist_id)}?include_groups={include_groups}&limit=50"
        albums = self._fetch_paginated(albums_url, access_token, delay)
        
        return {
            "artist_info": artist_data,
            "albums": albums,
            "discography_type": discography_type,
            "_token": access_token
        }
    
    def _fetch_paginated(
        self,
        url: str,
        access_token: str,
        delay: float
    ) -> List[Dict[str, Any]]:
        """Fetch all pages of paginated results."""
        all_items = []
        
        while url:
            data = self._api_request(url, access_token)
            if not data:
                break
            
            all_items.extend(data.get('items', []))
            url = data.get('next')
            
            if url and "&locale=" in url:
                url = url.split("&locale=")[0]
            
            if url and delay > 0:
                sleep(delay)
        
        return all_items


__all__ = [
    "SpotifyAPIClient",
    "SpotifyAPIError",
]
