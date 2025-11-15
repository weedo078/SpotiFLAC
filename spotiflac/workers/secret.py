from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from spotiflac.tools.secret_scraper import SpotifySecretScraper, SecretScraperError


class SecretScrapeWorker(QThread):
    """Worker thread for Spotify authentication secret scraping.
    
    Used to refresh Spotify access tokens when metadata fetching fails
    due to expired or invalid credentials.
    
    Signals:
        finished(bool, str): Emitted when scraping completes (success, message)
        progress(str): Emitted with progress updates during scraping
    """
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def run(self) -> None:
        """Execute secret scraping in background thread.
        
        Emits progress signals during operation and finished signal
        with success status and message upon completion.
        """
        try:
            self.progress.emit("Fixing error...")
            self.progress.emit("Please wait, this may take a moment...")
            
            scraper = SpotifySecretScraper(headless=True)
            count = scraper.scrape_and_save(timeout=60)
            
            self.finished.emit(True, f"Fixed successfully! Scraped {count} secrets")
        except SecretScraperError as e:
            self.finished.emit(False, str(e))
        except Exception as e:
            self.finished.emit(False, f"Unexpected error: {str(e)}")
