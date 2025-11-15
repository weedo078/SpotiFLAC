"""Tests for Deezer API client."""
from __future__ import annotations

from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from spotiflac.downloaders import TrackNotFoundError
from spotiflac.downloaders.deezer.client import DeezerAPIClient, DeezerAPIError


@pytest.fixture
def api_client():
    """Create API client with mocked session."""
    return DeezerAPIClient()


@pytest.fixture
def mock_session():
    """Create mock session."""
    session = Mock(spec=requests.Session)
    session.headers = {}
    return session


class TestDeezerAPIClient:
    """Test DeezerAPIClient initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        client = DeezerAPIClient()
        assert client.session is not None
        assert client.timeout == 30
        assert 'User-Agent' in client.session.headers

    def test_initialization_custom_session(self, mock_session):
        """Test initialization with custom session."""
        client = DeezerAPIClient(session=mock_session)
        assert client.session is mock_session

    def test_initialization_custom_timeout(self):
        """Test initialization with custom timeout."""
        client = DeezerAPIClient(timeout=60)
        assert client.timeout == 60


class TestGetTrackByISRC:
    """Test get_track_by_isrc method."""

    def test_successful_track_fetch(self, api_client, mocker):
        """Test successful track fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': '123456',
            'title': 'Test Song',
            'artist': {'name': 'Test Artist'}
        }
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        result = api_client.get_track_by_isrc("USAT22409172")
        
        assert result['id'] == '123456'
        assert result['title'] == 'Test Song'
        api_client.session.get.assert_called_once()

    def test_track_not_found(self, api_client, mocker):
        """Test track not found error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'error': {
                'type': 'DataException',
                'message': 'Track not found'
            }
        }
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        with pytest.raises(TrackNotFoundError, match="Track not found"):
            api_client.get_track_by_isrc("INVALID")

    def test_api_error(self, api_client, mocker):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'error': {
                'type': 'OtherError',
                'message': 'API error'
            }
        }
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        with pytest.raises(DeezerAPIError, match="Deezer API error"):
            api_client.get_track_by_isrc("USAT22409172")

    def test_network_error(self, api_client, mocker):
        """Test network error handling."""
        mocker.patch.object(
            api_client.session,
            'get',
            side_effect=requests.exceptions.ConnectionError("Network error")
        )
        
        with pytest.raises(DeezerAPIError, match="Failed to fetch track"):
            api_client.get_track_by_isrc("USAT22409172")


class TestGetDownloadURL:
    """Test get_download_url method."""

    def test_successful_url_fetch(self, api_client, mocker):
        """Test successful download URL fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'links': {
                'flac': 'https://example.com/track.flac',
                'mp3_320': 'https://example.com/track.mp3'
            }
        }
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        url = api_client.get_download_url("123456")
        
        assert url == 'https://example.com/track.flac'

    def test_custom_quality(self, api_client, mocker):
        """Test download URL with custom quality."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'links': {
                'flac': 'https://example.com/track.flac',
                'mp3_320': 'https://example.com/track.mp3'
            }
        }
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        url = api_client.get_download_url("123456", quality="mp3_320")
        
        assert url == 'https://example.com/track.mp3'

    def test_api_request_failed(self, api_client, mocker):
        """Test API request failure."""
        mock_response = Mock()
        mock_response.json.return_value = {'success': False}
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        with pytest.raises(DeezerAPIError, match="Deezmate API request failed"):
            api_client.get_download_url("123456")

    def test_quality_not_available(self, api_client, mocker):
        """Test quality not available."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'links': {
                'mp3_128': 'https://example.com/track.mp3'
            }
        }
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        with pytest.raises(DeezerAPIError, match="Quality 'flac' not available"):
            api_client.get_download_url("123456", quality="flac")


class TestDownloadFile:
    """Test download_file method."""

    def test_successful_download(self, api_client, mocker, tmp_path):
        """Test successful file download."""
        output_file = tmp_path / "test.flac"
        
        mock_response = Mock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content = Mock(return_value=[b'chunk1', b'chunk2'])
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        bytes_downloaded = api_client.download_file(
            "https://example.com/track.flac",
            str(output_file)
        )
        
        assert bytes_downloaded == 12  # len('chunk1') + len('chunk2')
        assert output_file.exists()

    def test_download_with_progress_callback(self, api_client, mocker, tmp_path):
        """Test download with progress callback."""
        output_file = tmp_path / "test.flac"
        progress_calls = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        mock_response = Mock()
        mock_response.headers = {'content-length': '100'}
        mock_response.iter_content = Mock(return_value=[b'a' * 50, b'b' * 50])
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        api_client.download_file(
            "https://example.com/track.flac",
            str(output_file),
            progress_callback=progress_callback
        )
        
        assert len(progress_calls) == 2
        assert progress_calls[0] == (50, 100)
        assert progress_calls[1] == (100, 100)

    def test_download_network_error(self, api_client, mocker, tmp_path):
        """Test download network error."""
        output_file = tmp_path / "test.flac"
        
        mocker.patch.object(
            api_client.session,
            'get',
            side_effect=requests.exceptions.ConnectionError("Network error")
        )
        
        with pytest.raises(DeezerAPIError, match="Failed to download file"):
            api_client.download_file(
                "https://example.com/track.flac",
                str(output_file)
            )


class TestDownloadCoverArt:
    """Test download_cover_art method."""

    def test_successful_cover_download(self, api_client, mocker):
        """Test successful cover art download."""
        mock_response = Mock()
        mock_response.content = b'fake_image_data'
        mock_response.raise_for_status = Mock()
        
        mocker.patch.object(api_client.session, 'get', return_value=mock_response)
        
        cover_data = api_client.download_cover_art("https://example.com/cover.jpg")
        
        assert cover_data == b'fake_image_data'

    def test_empty_url(self, api_client):
        """Test with empty URL."""
        result = api_client.download_cover_art("")
        assert result is None

    def test_none_url(self, api_client):
        """Test with None URL."""
        result = api_client.download_cover_art(None)
        assert result is None

    def test_download_failure(self, api_client, mocker):
        """Test cover download failure."""
        mocker.patch.object(
            api_client.session,
            'get',
            side_effect=requests.exceptions.ConnectionError("Network error")
        )
        
        result = api_client.download_cover_art("https://example.com/cover.jpg")
        assert result is None
