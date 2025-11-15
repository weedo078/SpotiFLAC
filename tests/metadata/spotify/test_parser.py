"""Tests for Spotify URL parser."""
from __future__ import annotations

import pytest

from spotiflac.metadata.spotify import SpotifyURLParser, SpotifyInvalidUrlException


class TestSpotifyURLParser:
    """Test SpotifyURLParser."""

    def test_parse_track_url(self):
        """Test parsing track URL."""
        result = SpotifyURLParser.parse("https://open.spotify.com/track/7so0lgd0zP2Sbgs2d7a1SZ")
        assert result['type'] == 'track'
        assert result['id'] == '7so0lgd0zP2Sbgs2d7a1SZ'

    def test_parse_album_url(self):
        """Test parsing album URL."""
        result = SpotifyURLParser.parse("https://open.spotify.com/album/6J84szYCnMfzEcvIcfWMFL")
        assert result['type'] == 'album'
        assert result['id'] == '6J84szYCnMfzEcvIcfWMFL'

    def test_parse_playlist_url(self):
        """Test parsing playlist URL."""
        result = SpotifyURLParser.parse("https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF")
        assert result['type'] == 'playlist'
        assert result['id'] == '37i9dQZEVXbNG2KDcFcKOF'

    def test_parse_artist_url(self):
        """Test parsing artist URL."""
        result = SpotifyURLParser.parse("https://open.spotify.com/artist/0du5cEVh5yTK9QJze8zA0C")
        assert result['type'] == 'artist'
        assert result['id'] == '0du5cEVh5yTK9QJze8zA0C'

    def test_parse_artist_discography_all(self):
        """Test parsing artist discography URL."""
        result = SpotifyURLParser.parse("https://open.spotify.com/artist/0du5cEVh5yTK9QJze8zA0C/discography/all")
        assert result['type'] == 'artist_discography'
        assert result['id'] == '0du5cEVh5yTK9QJze8zA0C'
        assert result['discography_type'] == 'all'

    def test_parse_artist_discography_album(self):
        """Test parsing artist discography album URL."""
        result = SpotifyURLParser.parse("https://open.spotify.com/artist/0du5cEVh5yTK9QJze8zA0C/discography/album")
        assert result['type'] == 'artist_discography'
        assert result['discography_type'] == 'album'

    def test_parse_spotify_uri(self):
        """Test parsing spotify: URI."""
        result = SpotifyURLParser.parse("spotify:track:7so0lgd0zP2Sbgs2d7a1SZ")
        assert result['type'] == 'track'
        assert result['id'] == '7so0lgd0zP2Sbgs2d7a1SZ'

    def test_parse_play_spotify_com(self):
        """Test parsing play.spotify.com URL."""
        result = SpotifyURLParser.parse("https://play.spotify.com/track/7so0lgd0zP2Sbgs2d7a1SZ")
        assert result['type'] == 'track'

    def test_parse_invalid_url(self):
        """Test parsing invalid URL."""
        with pytest.raises(SpotifyInvalidUrlException):
            SpotifyURLParser.parse("https://invalid.com/track/123")

    def test_parse_unsupported_format(self):
        """Test parsing unsupported format."""
        with pytest.raises(SpotifyInvalidUrlException):
            SpotifyURLParser.parse("https://open.spotify.com/invalid")
