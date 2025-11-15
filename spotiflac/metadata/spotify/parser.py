"""Spotify URL parsing."""
from __future__ import annotations

from urllib.parse import urlparse, parse_qs
from enum import Enum
from typing import Dict, Any


class SpotifyURLType(Enum):
    """Supported Spotify URL types."""
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST = "artist"
    ARTIST_DISCOGRAPHY = "artist_discography"


class SpotifyInvalidUrlException(Exception):
    """Raised when Spotify URL is invalid."""
    pass


class SpotifyURLParser:
    """Parse and validate Spotify URLs.
    
    Supports various URL formats:
    - https://open.spotify.com/track/...
    - https://play.spotify.com/album/...
    - spotify:playlist:...
    - Embed URLs
    
    Example:
        >>> parser = SpotifyURLParser()
        >>> info = parser.parse("https://open.spotify.com/track/123")
        >>> print(info['type'], info['id'])
        track 123
    """
    
    @staticmethod
    def parse(uri: str) -> Dict[str, Any]:
        """Parse Spotify URL and extract type and ID.
        
        Args:
            uri: Spotify URL or URI
            
        Returns:
            Dict with 'type' and 'id' keys, plus optional 'discography_type'
            
        Raises:
            SpotifyInvalidUrlException: If URL format is invalid
            
        Example:
            >>> info = SpotifyURLParser.parse("https://open.spotify.com/track/7so0lgd0zP2Sbgs2d7a1SZ")
            >>> info['type']
            'track'
        """
        u = urlparse(uri)
        
        # Handle embed URLs
        if u.netloc == "embed.spotify.com":
            if not u.query:
                raise SpotifyInvalidUrlException(f"ERROR: url {uri} is not supported")
            qs = parse_qs(u.query)
            return SpotifyURLParser.parse(qs['uri'][0])
        
        # Handle plain playlist IDs
        if not u.scheme and not u.netloc:
            return {"type": "playlist", "id": u.path}
        
        # Parse spotify: URIs or https URLs
        if u.scheme == "spotify":
            parts = uri.split(":")
        else:
            if u.netloc not in ["open.spotify.com", "play.spotify.com"]:
                raise SpotifyInvalidUrlException(f"ERROR: url {uri} is not supported")
            parts = u.path.split("/")
        
        # Handle embed prefix
        if len(parts) > 1 and parts[1] == "embed":
            parts = parts[1:]
        
        # Handle intl- prefix
        if len(parts) > 1 and parts[1].startswith("intl-"):
            parts = parts[1:]
        
        l = len(parts)
        
        # Standard format: /type/id
        if l == 3 and parts[1] in ["album", "track", "playlist", "artist"]:
            return {"type": parts[1], "id": parts[2]}
        
        # User playlist format: /user/id/playlist/id
        if l == 5 and parts[3] == "playlist":
            return {"type": parts[3], "id": parts[4]}
        
        # Artist discography format
        if l >= 4 and parts[1] == "artist":
            if len(parts) >= 4 and parts[3] == "discography":
                discography_type = "all"
                if len(parts) >= 5 and parts[4] in ["all", "album", "single", "compilation"]:
                    discography_type = parts[4]
                return {
                    "type": "artist_discography",
                    "id": parts[2],
                    "discography_type": discography_type
                }
            else:
                return {"type": "artist", "id": parts[2]}
        
        raise SpotifyInvalidUrlException(
            "ERROR: unable to determine Spotify URL type or type is unsupported."
        )


__all__ = [
    "SpotifyURLParser",
    "SpotifyURLType",
    "SpotifyInvalidUrlException",
]
