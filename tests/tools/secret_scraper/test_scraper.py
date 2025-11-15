"""Tests for secret scraper."""
from __future__ import annotations

from unittest.mock import Mock
import pytest

from spotiflac.tools.secret_scraper import (
    SpotifySecretScraper,
    SecretScraperError,
)


class TestSpotifySecretScraper:
    """Test SpotifySecretScraper."""

    def test_initialization(self):
        """Test initialization."""
        scraper = SpotifySecretScraper(headless=True)
        assert scraper.browser is not None
        assert scraper.storage is not None

    def test_scrape_secrets_success(self, mocker):
        """Test successful secret scraping."""
        mock_browser = Mock()
        mock_browser.start = Mock()
        mock_browser.navigate_to_spotify = Mock()
        mock_browser.enable_network_monitoring = Mock()
        mock_browser.capture_secrets = Mock(return_value=[
            {"version": 1, "secret": [1, 2, 3]}
        ])
        mock_browser.close = Mock()
        
        mock_storage = Mock()
        mock_storage.process_captured_secrets = Mock(return_value=[
            {"version": 1, "secret": [1, 2, 3]}
        ])
        
        scraper = SpotifySecretScraper(
            browser=mock_browser,
            storage=mock_storage
        )
        
        secrets = scraper.scrape_secrets()
        
        assert len(secrets) == 1
        mock_browser.start.assert_called_once()
        mock_browser.close.assert_called_once()

    def test_save_secrets(self, mocker, tmp_path):
        """Test saving secrets."""
        output_path = tmp_path / "secrets.json"
        
        scraper = SpotifySecretScraper()
        secrets = [{"version": 1, "secret": [1, 2, 3]}]
        
        scraper.save_secrets(secrets, output_path=output_path)
        
        assert output_path.exists()
