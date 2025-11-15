from __future__ import annotations

from typing import List, Optional, Sequence

from PyQt6.QtCore import QObject, pyqtSignal

from spotiflac.models import Track
from spotiflac.services import SpotifyMetadataService
from spotiflac.workers import DownloadWorker, MetadataFetchWorker, SecretScrapeWorker


class DownloadController(QObject):
    """Controller managing download workflow and worker thread lifecycle.
    
    Orchestrates metadata fetching, downloads, and secret scraping operations
    by managing worker threads and exposing Qt signals for GUI integration.
    
    Signals:
        metadata_finished(dict): Emitted when metadata fetch completes successfully
        metadata_error(str): Emitted when metadata fetch fails
        download_progress(str, int): Emitted during download (message, percentage)
        download_finished(bool, str, list, list, list): Download complete
            (success, message, failed_tracks, successful_tracks, skipped_tracks)
        secret_progress(str): Progress messages during secret scraping
        secret_finished(bool, str): Secret scraping complete (success, message)
    
    Example:
        >>> controller = DownloadController(spotify_service)
        >>> controller.metadata_finished.connect(on_metadata_ready)
        >>> controller.fetch_metadata("https://open.spotify.com/track/...")
    """
    
    metadata_finished = pyqtSignal(dict)
    metadata_error = pyqtSignal(str)

    download_progress = pyqtSignal(str, int)
    download_finished = pyqtSignal(bool, str, list, list, list)

    secret_progress = pyqtSignal(str)
    secret_finished = pyqtSignal(bool, str)

    def __init__(self, spotify_service: SpotifyMetadataService) -> None:
        """Initialize controller with Spotify metadata service.
        
        Args:
            spotify_service: Service for fetching Spotify metadata
        """
        super().__init__()
        self.spotify_service = spotify_service
        self._metadata_worker: Optional[MetadataFetchWorker] = None
        self._download_worker: Optional[DownloadWorker] = None
        self._secret_worker: Optional[SecretScrapeWorker] = None

    def fetch_metadata(self, url: str) -> None:
        """Start asynchronous metadata fetch for a Spotify URL.
        
        Stops any running metadata worker before starting a new one.
        Results are emitted via metadata_finished or metadata_error signals.
        
        Args:
            url: Spotify URL to fetch metadata for
        """
        self._stop_metadata_worker()
        self._metadata_worker = MetadataFetchWorker(url, self.spotify_service)
        self._metadata_worker.finished.connect(self.metadata_finished.emit)
        self._metadata_worker.error.connect(self.metadata_error.emit)
        self._metadata_worker.start()

    def start_download(
        self,
        tracks: Sequence[Track],
        outpath: str,
        *,
        is_single_track: bool,
        is_album: bool,
        is_playlist: bool,
        album_or_playlist_name: str,
        filename_format: str,
        use_track_numbers: bool,
        use_artist_subfolders: bool,
        use_album_subfolders: bool,
        service: str,
        tidal_api_url: Optional[str],
        deezer_fallback_enabled: bool,
    ) -> None:
        """Start asynchronous download of tracks.
        
        Stops any running download before starting a new one.
        Progress is emitted via download_progress signal.
        Completion is emitted via download_finished signal.
        
        Args:
            tracks: Sequence of Track objects to download
            outpath: Base output directory path
            is_single_track: True if downloading a single track
            is_album: True if downloading an album
            is_playlist: True if downloading a playlist
            album_or_playlist_name: Name for folder organization
            filename_format: Format string for output filenames
            use_track_numbers: Prefix filenames with track numbers
            use_artist_subfolders: Organize by artist folders
            use_album_subfolders: Organize by album folders
            service: Download service ('tidal' or 'deezer')
            tidal_api_url: Optional Tidal API URL (if service is 'tidal')
            deezer_fallback_enabled: Try Deezer if Tidal fails
        """
        self.stop_download()
        
        # Don't resolve 'auto' here - let the worker handle it with smart fallback
        # This allows the worker to try multiple APIs if one fails
        self._download_worker = DownloadWorker(
            tracks,
            outpath,
            is_single_track,
            is_album,
            is_playlist,
            album_or_playlist_name,
            filename_format,
            use_track_numbers,
            use_artist_subfolders,
            use_album_subfolders,
            service,
            tidal_api_url,  # Pass 'auto' directly to worker
            deezer_fallback_enabled,
        )
        self._download_worker.progress.connect(self.download_progress.emit)
        self._download_worker.finished.connect(self._handle_download_finished)
        self._download_worker.start()

    def _handle_download_finished(self, success: bool, message: str, failed: list, success_list: list, skipped: list) -> None:
        self.download_finished.emit(success, message, failed, success_list, skipped)
        self._download_worker = None

    def pause_download(self) -> None:
        """Pause the currently running download."""
        if self._download_worker:
            self._download_worker.pause()

    def resume_download(self) -> None:
        """Resume a paused download."""
        if self._download_worker:
            self._download_worker.resume()

    def stop_download(self) -> None:
        """Stop and cleanup the currently running download."""
        if self._download_worker:
            self._download_worker.stop()
            self._download_worker = None

    def start_secret_fix(self) -> None:
        """Start asynchronous Spotify secret scraping/fixing.
        
        Used to refresh authentication tokens when metadata fetch fails.
        Progress is emitted via secret_progress signal.
        Completion is emitted via secret_finished signal.
        """
        self._stop_secret_worker()
        self._secret_worker = SecretScrapeWorker()
        self._secret_worker.progress.connect(self.secret_progress.emit)
        self._secret_worker.finished.connect(self._handle_secret_finished)
        self._secret_worker.start()

    def _handle_secret_finished(self, success: bool, message: str) -> None:
        self.secret_finished.emit(success, message)
        self._secret_worker = None

    def _stop_metadata_worker(self) -> None:
        if self._metadata_worker and self._metadata_worker.isRunning():
            self._metadata_worker.quit()
            self._metadata_worker.wait()
        self._metadata_worker = None

    def _stop_secret_worker(self) -> None:
        if self._secret_worker and self._secret_worker.isRunning():
            self._secret_worker.quit()
            self._secret_worker.wait()
        self._secret_worker = None

    def cleanup(self) -> None:
        """Stop and cleanup all running workers.
        
        Should be called before application shutdown to ensure
        all threads are properly terminated.
        """
        self.stop_download()
        self._stop_metadata_worker()
        self._stop_secret_worker()
