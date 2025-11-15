"""Spotify data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class SpotifyTrack:
    """Spotify track metadata."""
    artists: str
    name: str
    album_name: str
    duration_ms: int
    images: str
    release_date: str
    track_number: int
    external_urls: str
    isrc: str = ""
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> SpotifyTrack:
        """Parse track from API response."""
        artists = ", ".join([a['name'] for a in data.get('artists', [])])
        album = data.get('album', {})
        images = album.get('images', [{}])[0].get('url', '') if album.get('images') else ''
        isrc = data.get('external_ids', {}).get('isrc', '')
        
        return cls(
            artists=artists,
            name=data.get('name', ''),
            album_name=album.get('name', ''),
            duration_ms=data.get('duration_ms', 0),
            images=images,
            release_date=album.get('release_date', ''),
            track_number=data.get('track_number', 0),
            external_urls=data.get('external_urls', {}).get('spotify', ''),
            isrc=isrc
        )


@dataclass
class SpotifyAlbumInfo:
    """Spotify album information."""
    total_tracks: int
    name: str
    release_date: str
    artists: str
    images: str
    batch: str = ""


@dataclass
class SpotifyAlbum:
    """Spotify album with tracks."""
    album_info: SpotifyAlbumInfo
    track_list: List[SpotifyTrack]


@dataclass
class SpotifyPlaylistInfo:
    """Spotify playlist information."""
    tracks_total: int
    followers_total: int
    owner_display_name: str
    name: str
    images: str
    batch: str = ""


@dataclass
class SpotifyPlaylist:
    """Spotify playlist with tracks."""
    playlist_info: SpotifyPlaylistInfo
    track_list: List[SpotifyTrack]


@dataclass
class SpotifyArtist:
    """Spotify artist information."""
    name: str
    followers: int
    genres: List[str]
    images: str
    external_urls: str
    popularity: int = 0


@dataclass
class SpotifyAlbumListItem:
    """Album item in discography."""
    id: str
    name: str
    album_type: str
    release_date: str
    total_tracks: int
    artists: str
    images: str
    external_urls: str


@dataclass
class SpotifyArtistDiscography:
    """Spotify artist discography."""
    artist_info: Dict[str, Any]
    album_list: List[SpotifyAlbumListItem]
    track_list: List[SpotifyTrack]


__all__ = [
    "SpotifyTrack",
    "SpotifyAlbum",
    "SpotifyAlbumInfo",
    "SpotifyPlaylist",
    "SpotifyPlaylistInfo",
    "SpotifyArtist",
    "SpotifyAlbumListItem",
    "SpotifyArtistDiscography",
]
