"""Tests for Tidal authentication."""
from __future__ import annotations

from unittest.mock import Mock
import pytest
import requests

from spotiflac.downloaders.tidal.auth import TidalAuthenticator, TidalAuthError


@pytest.fixture
def authenticator():
    """Create authenticator instance."""
    return TidalAuthenticator()


class TestTidalAuthenticator:
    """Test TidalAuthenticator."""

    def test_initialization_default(self):
        """Test default initialization."""
        auth = TidalAuthenticator()
        assert auth.client_id is not None
        assert auth.client_secret is not None
        assert auth.timeout == 30

    def test_initialization_custom(self):
        """Test custom initialization."""
        auth = TidalAuthenticator(
            client_id="custom_id",
            client_secret="custom_secret",
            timeout=60
        )
        assert auth.client_id == "custom_id"
        assert auth.client_secret == "custom_secret"
        assert auth.timeout == 60

    def test_get_access_token_success(self, authenticator, mocker):
        """Test successful token retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {'access_token': 'test_token_123'}
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.post', return_value=mock_response)
        
        token = authenticator.get_access_token("https://api.example.com")
        
        assert token == 'test_token_123'
        assert authenticator._cached_token == 'test_token_123'

    def test_get_access_token_cached(self, authenticator, mocker):
        """Test cached token is reused."""
        authenticator._cached_token = 'cached_token'
        
        mock_post = mocker.patch('requests.post')
        
        token = authenticator.get_access_token("https://api.example.com")
        
        assert token == 'cached_token'
        mock_post.assert_not_called()

    def test_get_access_token_no_token_in_response(self, authenticator, mocker):
        """Test error when no token in response."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.post', return_value=mock_response)
        
        with pytest.raises(TidalAuthError, match="No access token"):
            authenticator.get_access_token("https://api.example.com")

    def test_get_access_token_network_error(self, authenticator, mocker):
        """Test network error handling."""
        mocker.patch(
            'requests.post',
            side_effect=requests.exceptions.ConnectionError("Network error")
        )
        
        with pytest.raises(TidalAuthError, match="Failed to get access token"):
            authenticator.get_access_token("https://api.example.com")

    def test_clear_cache(self, authenticator):
        """Test cache clearing."""
        authenticator._cached_token = 'test_token'
        authenticator.clear_cache()
        assert authenticator._cached_token is None
