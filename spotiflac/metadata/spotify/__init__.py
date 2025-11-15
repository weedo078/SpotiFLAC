"""Spotify metadata extraction."""
from __future__ import annotations

from .auth import SpotifySecretManager, SpotifyAuthError
from .client import SpotifyAPIClient, SpotifyAPIError
from .parser import SpotifyURLParser, SpotifyURLType, SpotifyInvalidUrlException
from .models import (
    SpotifyTrack,
    SpotifyAlbum,
    SpotifyAlbumInfo,
    SpotifyPlaylist,
    SpotifyPlaylistInfo,
    SpotifyArtist,
    SpotifyAlbumListItem,
    SpotifyArtistDiscography,
)

__all__ = [
    "SpotifyAPIClient",
    "SpotifyAPIError",
    "SpotifySecretManager",
    "SpotifyAuthError",
    "SpotifyURLParser",
    "SpotifyURLType",
    "SpotifyInvalidUrlException",
    "SpotifyTrack",
    "SpotifyAlbum",
    "SpotifyAlbumInfo",
    "SpotifyPlaylist",
    "SpotifyPlaylistInfo",
    "SpotifyArtist",
    "SpotifyAlbumListItem",
    "SpotifyArtistDiscography",
]
