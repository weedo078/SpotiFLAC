"""Tests for Tidal API client."""
from __future__ import annotations

from unittest.mock import Mock
import pytest
import requests

from spotiflac.downloaders import TrackNotFoundError
from spotiflac.downloaders.tidal.client import TidalAPIClient, TidalAPIError


class TestTidalAPIClient:
    """Test TidalAPIClient."""

    def test_search_track_by_isrc_success(self, mocker):
        """Test successful track search."""
        # Mock authenticator
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test_token'
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'items': [{'id': '123', 'title': 'Test Song'}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        
        client = TidalAPIClient(
            api_url="https://test.com",
            authenticator=mock_auth
        )
        client.session = mock_session
        
        result = client.search_track_by_isrc("USAT22409172")
        
        assert result['id'] == '123'
        assert result['title'] == 'Test Song'

    def test_search_track_by_isrc_not_found(self, mocker):
        """Test track not found."""
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test_token'
        
        mock_response = Mock()
        mock_response.json.return_value = {'items': []}
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        
        client = TidalAPIClient(
            api_url="https://test.com",
            authenticator=mock_auth
        )
        client.session = mock_session
        
        with pytest.raises(TrackNotFoundError):
            client.search_track_by_isrc("INVALID")

    def test_get_stream_url_success(self, mocker):
        """Test successful stream URL retrieval."""
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test_token'
        
        mock_response = Mock()
        mock_response.json.return_value = {'url': 'https://stream.com/track.flac'}
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        
        client = TidalAPIClient(
            api_url="https://test.com",
            authenticator=mock_auth
        )
        client.session = mock_session
        
        url = client.get_stream_url("123")
        
        assert url == 'https://stream.com/track.flac'

    def test_download_cover_art_success(self, mocker):
        """Test cover art download."""
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test_token'
        
        mock_response = Mock()
        mock_response.content = b'fake_image'
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        
        client = TidalAPIClient(
            api_url="https://test.com",
            authenticator=mock_auth
        )
        client.session = mock_session
        
        cover = client.download_cover_art("abc-123")
        
        assert cover == b'fake_image'
