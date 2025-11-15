"""Tests for Tidal utilities."""
from __future__ import annotations

from unittest.mock import Mock
import pytest
import requests

from spotiflac.downloaders.tidal.utils import TidalAPIDiscovery, TidalAPIDiscoveryError


class TestTidalAPIDiscovery:
    """Test TidalAPIDiscovery."""

    def test_get_available_apis_success(self, mocker):
        """Test successful API discovery."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"instances": [{"instance_type": "api", "url": "https://api1.com", "last_check": {"success": true}, "avg_response_time": 100}]}',
            b'data: more data'
        ]
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.get', return_value=mock_response)
        
        apis = TidalAPIDiscovery.get_available_apis()
        
        assert len(apis) >= 1
        assert apis[0]['url'] == 'https://api1.com'

    def test_get_available_apis_filters_unsuccessful(self, mocker):
        """Test filtering of unsuccessful APIs."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"instances": [{"instance_type": "api", "url": "https://api1.com", "last_check": {"success": false}}]}',
        ]
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.get', return_value=mock_response)
        
        apis = TidalAPIDiscovery.get_available_apis(only_successful=True)
        
        assert len(apis) == 0

    def test_get_available_apis_network_error(self, mocker):
        """Test network error handling."""
        mocker.patch(
            'requests.get',
            side_effect=requests.exceptions.ConnectionError("Network error")
        )
        
        with pytest.raises(TidalAPIDiscoveryError):
            TidalAPIDiscovery.get_available_apis()

    def test_get_best_api(self, mocker):
        """Test getting best API."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"instances": [{"instance_type": "api", "url": "https://fast.com", "last_check": {"success": true}, "avg_response_time": 50}]}',
        ]
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.get', return_value=mock_response)
        
        best = TidalAPIDiscovery.get_best_api()
        
        assert best == 'https://fast.com'

    def test_get_best_api_none_available(self, mocker):
        """Test when no APIs available."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"instances": []}',
        ]
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.get', return_value=mock_response)
        
        best = TidalAPIDiscovery.get_best_api()
        
        assert best is None

    def test_get_api_with_fallback_auto(self, mocker):
        """Test auto fallback."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"instances": [{"instance_type": "api", "url": "https://auto.com", "last_check": {"success": true}, "avg_response_time": 100}]}',
        ]
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.get', return_value=mock_response)
        
        url = TidalAPIDiscovery.get_api_with_fallback("auto")
        
        assert url == 'https://auto.com'

    def test_get_api_with_fallback_specific(self):
        """Test specific URL."""
        url = TidalAPIDiscovery.get_api_with_fallback("https://specific.com")
        assert url == 'https://specific.com'

    def test_get_api_with_fallback_no_apis(self, mocker):
        """Test error when no APIs available."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'data: {"instances": []}',
        ]
        mock_response.raise_for_status = Mock()
        
        mocker.patch('requests.get', return_value=mock_response)
        
        with pytest.raises(TidalAPIDiscoveryError, match="No Tidal API"):
            TidalAPIDiscovery.get_api_with_fallback("auto")
