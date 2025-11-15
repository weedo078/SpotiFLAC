from __future__ import annotations

from typing import Dict

from PyQt6.QtCore import QThread, pyqtSignal

from spotiflac.services import SpotifyMetadataService, SpotifyInvalidUrlException


class MetadataFetchWorker(QThread):
    """Worker thread for asynchronous Spotify metadata fetching.
    
    Signals:
        finished(dict): Emitted when metadata fetch succeeds
        error(str): Emitted when fetch fails with error message
    """
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url: str, spotify_service: SpotifyMetadataService):
        """Initialize worker with URL and service.
        
        Args:
            url: Spotify URL to fetch metadata for
            spotify_service: Service instance for metadata operations
        """
        super().__init__()
        self.url = url
        self.spotify_service = spotify_service

    def run(self) -> None:
        """Execute metadata fetch in background thread.
        
        Emits finished signal with metadata dict on success,
        or error signal with error message on failure.
        """
        try:
            metadata: Dict[str, object] = self.spotify_service.fetch_metadata(self.url)
            if "error" in metadata:
                self.error.emit(str(metadata["error"]))
            else:
                self.finished.emit(metadata)
        except SpotifyInvalidUrlException as exc:
            self.error.emit(str(exc))
        except Exception as exc:  # pragma: no cover - defensive guard
            self.error.emit(f"Failed to fetch metadata: {exc}")
