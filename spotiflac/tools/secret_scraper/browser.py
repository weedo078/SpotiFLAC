"""Browser automation for secret scraping."""
from __future__ import annotations

from typing import List, Dict, Any, Optional

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False
    ChromiumPage = None
    ChromiumOptions = None


class BrowserError(Exception):
    """Raised when browser operations fail."""
    pass


class SpotifyBrowser:
    """Automated browser for Spotify secret scraping.
    
    Uses DrissionPage to automate Chromium browser.
    
    Example:
        >>> browser = SpotifyBrowser()
        >>> browser.start()
        >>> secrets = browser.capture_secrets()
        >>> browser.close()
    """
    
    SPOTIFY_URL = "https://open.spotify.com"
    
    def __init__(
        self,
        *,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
    ):
        """Initialize browser.
        
        Args:
            headless: Run browser in headless mode
            user_data_dir: Optional custom user data directory
            
        Raises:
            BrowserError: If DrissionPage not available
        """
        if not DRISSION_AVAILABLE:
            raise BrowserError("DrissionPage library not available")
        
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.page: Optional[ChromiumPage] = None
        self._captured_requests: List[Dict[str, Any]] = []
    
    def start(self) -> None:
        """Start browser session.
        
        Raises:
            BrowserError: If browser fails to start
        """
        try:
            options = ChromiumOptions()
            
            if self.headless:
                options.headless(True)
            
            if self.user_data_dir:
                options.set_user_data_path(self.user_data_dir)
            
            self.page = ChromiumPage(addr_or_opts=options)
            
        except Exception as e:
            raise BrowserError(f"Failed to start browser: {e}")
    
    def navigate_to_spotify(self) -> None:
        """Navigate to Spotify website.
        
        Raises:
            BrowserError: If navigation fails
        """
        if not self.page:
            raise BrowserError("Browser not started")
        
        try:
            self.page.get(self.SPOTIFY_URL)
        except Exception as e:
            raise BrowserError(f"Failed to navigate: {e}")
    
    def enable_network_monitoring(self) -> None:
        """Enable network request monitoring.
        
        Raises:
            BrowserError: If monitoring cannot be enabled
        """
        if not self.page:
            raise BrowserError("Browser not started")
        
        try:
            # Enable network monitoring in DrissionPage
            self.page.listen.start('api/token')
        except Exception as e:
            raise BrowserError(f"Failed to enable monitoring: {e}")
    
    def capture_secrets(self, timeout: int = 60) -> List[Dict[str, Any]]:
        """Capture secrets from network requests.
        
        Args:
            timeout: Maximum time to wait for secrets
            
        Returns:
            List of captured secret data
            
        Raises:
            BrowserError: If capture fails
        """
        if not self.page:
            raise BrowserError("Browser not started")
        
        try:
            # Wait for and capture network requests
            captured = []
            
            # Listen for token requests
            for packet in self.page.listen.steps(timeout=timeout):
                if 'api/token' in packet.url:
                    response_data = packet.response.body
                    if response_data:
                        captured.append({
                            'url': packet.url,
                            'response': response_data
                        })
            
            return captured
            
        except Exception as e:
            raise BrowserError(f"Failed to capture secrets: {e}")
    
    def close(self) -> None:
        """Close browser session."""
        if self.page:
            try:
                self.page.quit()
            except:
                pass
            self.page = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


__all__ = [
    "SpotifyBrowser",
    "BrowserError",
]
