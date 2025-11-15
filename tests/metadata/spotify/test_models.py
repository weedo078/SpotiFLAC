"""Tests for Spotify data models."""
from __future__ import annotations

from spotiflac.metadata.spotify import SpotifyTrack


class TestSpotifyTrack:
    """Test SpotifyTrack dataclass."""

    def test_from_api_response(self):
        """Test parsing track from API response."""
        data = {
            'name': 'Test Song',
            'artists': [{'name': 'Artist 1'}, {'name': 'Artist 2'}],
            'album': {
                'name': 'Test Album',
                'release_date': '2024-01-01',
                'images': [{'url': 'https://example.com/image.jpg'}]
            },
            'duration_ms': 180000,
            'track_number': 5,
            'external_urls': {'spotify': 'https://open.spotify.com/track/123'},
            'external_ids': {'isrc': 'USAT22409172'}
        }
        
        track = SpotifyTrack.from_api_response(data)
        
        assert track.name == 'Test Song'
        assert track.artists == 'Artist 1, Artist 2'
        assert track.album_name == 'Test Album'
        assert track.duration_ms == 180000
        assert track.track_number == 5
        assert track.isrc == 'USAT22409172'

    def test_from_api_response_minimal(self):
        """Test parsing minimal response."""
        data = {'name': 'Minimal'}
        
        track = SpotifyTrack.from_api_response(data)
        
        assert track.name == 'Minimal'
        assert track.artists == ''
        assert track.isrc == ''
