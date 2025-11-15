"""Tests for Tidal metadata."""
from __future__ import annotations

import pytest

from spotiflac.downloaders.tidal.metadata import TidalTrackMetadata


class TestTidalTrackMetadata:
    """Test TidalTrackMetadata."""

    def test_from_api_response_complete(self):
        """Test parsing complete response."""
        data = {
            'id': '123',
            'title': 'Test Song',
            'artist': {'name': 'Artist'},
            'artists': [{'name': 'Artist 1'}, {'name': 'Artist 2'}],
            'album': {
                'title': 'Album',
                'id': '456',
                'cover': 'abc-123'
            },
            'trackNumber': 5,
            'volumeNumber': 1,
            'isrc': 'USAT22409172',
            'streamStartDate': '2024-01-15',
            'duration': 180,
            'explicit': True
        }
        
        metadata = TidalTrackMetadata.from_api_response(data)
        
        assert metadata.title == 'Test Song'
        assert metadata.artists == 'Artist 1, Artist 2'
        assert metadata.track_number == 5
        assert metadata.isrc == 'USAT22409172'

    def test_from_api_response_minimal(self):
        """Test parsing minimal response."""
        data = {'title': 'Minimal'}
        
        metadata = TidalTrackMetadata.from_api_response(data)
        
        assert metadata.title == 'Minimal'
        assert metadata.artist == ''
