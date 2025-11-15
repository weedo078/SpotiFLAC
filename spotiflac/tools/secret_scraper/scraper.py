"""Main secret scraper implementation."""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .browser import SpotifyBrowser, BrowserError
from .storage import SecretStorage, SecretStorageError

logger = logging.getLogger(__name__)


class SecretScraperError(Exception):
    """Raised when secret scraping fails."""
    pass


class SpotifySecretScraper:
    """Main secret scraper for Spotify.
    
    Coordinates browser automation and secret storage.
    
    Example:
        >>> scraper = SpotifySecretScraper()
        >>> secrets = scraper.scrape_secrets()
        >>> scraper.save_secrets(secrets)
    """
    
    def __init__(
        self,
        *,
        browser: Optional[SpotifyBrowser] = None,
        storage: Optional[SecretStorage] = None,
        headless: bool = False,
    ):
        """Initialize scraper.
        
        Args:
            browser: Optional SpotifyBrowser instance
            storage: Optional SecretStorage instance
            headless: Run browser in headless mode
        """
        self.browser = browser or SpotifyBrowser(headless=headless)
        self.storage = storage or SecretStorage()
    
    def scrape_secrets(
        self,
        *,
        timeout: int = 60,
        auto_close: bool = True,
    ) -> List[Dict[str, Any]]:
        """Scrape secrets from Spotify.
        
        Args:
            timeout: Maximum time to wait for secrets
            auto_close: Automatically close browser after scraping
            
        Returns:
            List of captured secrets
            
        Raises:
            SecretScraperError: If scraping fails
        """
        logger.info("Starting Spotify secret scraping")
        
        try:
            # Start browser
            self.browser.start()
            
            # Navigate to Spotify
            self.browser.navigate_to_spotify()
            
            # Enable network monitoring
            self.browser.enable_network_monitoring()
            
            # Capture secrets
            captured = self.browser.capture_secrets(timeout=timeout)
            
            # Process captured data
            secrets = self.storage.process_captured_secrets(captured)
            logger.info(f"Successfully scraped {len(secrets)} secrets")
            
            if auto_close:
                self.browser.close()
            
            return secrets
            
        except (BrowserError, SecretStorageError) as e:
            raise SecretScraperError(f"Failed to scrape secrets: {e}")
        except Exception as e:
            raise SecretScraperError(f"Unexpected error during scraping: {e}")
    
    def save_secrets(
        self,
        secrets: List[Dict[str, Any]],
        *,
        output_path: Optional[Path] = None,
    ) -> None:
        """Save scraped secrets to file.
        
        Args:
            secrets: List of secrets to save
            output_path: Optional custom output path
            
        Raises:
            SecretScraperError: If saving fails
        """
        try:
            if output_path:
                storage = SecretStorage(storage_path=output_path)
            else:
                storage = self.storage
            
            storage.save_secrets(secrets)
            
        except SecretStorageError as e:
            raise SecretScraperError(f"Failed to save secrets: {e}")
    
    def scrape_and_save(
        self,
        *,
        timeout: int = 60,
        output_path: Optional[Path] = None,
    ) -> int:
        """Scrape secrets and save to file.
        
        Args:
            timeout: Maximum time to wait for secrets
            output_path: Optional custom output path
            
        Returns:
            Number of secrets saved
            
        Raises:
            SecretScraperError: If operation fails
        """
        secrets = self.scrape_secrets(timeout=timeout)
        self.save_secrets(secrets, output_path=output_path)
        return len(secrets)


__all__ = [
    "SpotifySecretScraper",
    "SecretScraperError",
]
