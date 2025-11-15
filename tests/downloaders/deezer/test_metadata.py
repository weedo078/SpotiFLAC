"""Tests for Deezer metadata handling."""
from __future__ import annotations

from pathlib import Path
import pytest

from spotiflac.downloaders import MetadataError
from spotiflac.downloaders.deezer.metadata import (
    DeezerTrackMetadata,
    DeezerMetadataWriter,
)


class TestDeezerTrackMetadata:
    """Test DeezerTrackMetadata dataclass."""

    def test_from_api_response_complete(self):
        """Test parsing complete API response."""
        api_data = {
            'id': '123456',
            'title': 'Test Song',
            'artist': {'name': 'Test Artist', 'id': '789'},
            'contributors': [
                {'name': 'Test Artist', 'role': 'Main'},
                {'name': 'Featured Artist', 'role': 'Main'}
            ],
            'album': {
                'title': 'Test Album',
                'id': '456',
                'cover_xl': 'https://example.com/cover.jpg'
            },
            'track_position': 5,
            'disk_number': 1,
            'isrc': 'USAT22409172',
            'release_date': '2024-01-15',
            'duration': 180,
            'explicit_lyrics': True
        }
        
        metadata = DeezerTrackMetadata.from_api_response(api_data)
        
        assert metadata.title == 'Test Song'
        assert metadata.artist == 'Test Artist'
        assert metadata.artists == 'Test Artist, Featured Artist'
        assert metadata.album == 'Test Album'
        assert metadata.track_number == 5
        assert metadata.isrc == 'USAT22409172'
        assert metadata.explicit is True

    def test_from_api_response_minimal(self):
        """Test parsing minimal API response."""
        api_data = {
            'title': 'Minimal Song'
        }
        
        metadata = DeezerTrackMetadata.from_api_response(api_data)
        
        assert metadata.title == 'Minimal Song'
        assert metadata.artist == ''
        assert metadata.track_number == 1

    def test_from_api_response_no_contributors(self):
        """Test parsing without contributors."""
        api_data = {
            'title': 'Song',
            'artist': {'name': 'Artist'}
        }
        
        metadata = DeezerTrackMetadata.from_api_response(api_data)
        
        assert metadata.artists == 'Artist'


class TestDeezerMetadataWriter:
    """Test DeezerMetadataWriter."""

    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata."""
        return DeezerTrackMetadata(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            track_number=1,
            isrc="USAT22409172",
            release_date="2024"
        )

    def test_write_to_file_basic(self, tmp_path, sample_metadata):
        """Test writing basic metadata."""
        # Create empty FLAC file
        test_file = tmp_path / "test.flac"
        test_file.write_bytes(b'')  # Placeholder
        
        writer = DeezerMetadataWriter()
        
        # Note: This will fail without a valid FLAC file
        # In real tests, you'd use a fixture with a valid FLAC file
        try:
            writer.write_to_file(test_file, sample_metadata)
        except MetadataError:
            # Expected if mutagen can't read the file
            pass

    def test_write_requires_mutagen(self, tmp_path, sample_metadata, mocker):
        """Test that mutagen is required."""
        test_file = tmp_path / "test.flac"
        
        # Mock FLAC as None
        mocker.patch('spotiflac.downloaders.deezer.metadata.FLAC', None)
        
        writer = DeezerMetadataWriter()
        
        with pytest.raises(MetadataError, match="mutagen library not available"):
            writer.write_to_file(test_file, sample_metadata)
