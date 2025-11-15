"""Main Tidal downloader implementation."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Callable

from spotiflac.downloaders.base import BaseDownloader, DownloadResult
from spotiflac.downloaders.deezer.utils import sanitize_filename, format_file_size
from .client import TidalAPIClient
from .metadata import TidalTrackMetadata, TidalMetadataWriter

logger = logging.getLogger(__name__)

class TidalDownloader(BaseDownloader):
    """Main Tidal downloader implementation.
    
    Downloads tracks from Tidal by ISRC code, including metadata and cover art.
    
    Example:
        >>> downloader = TidalDownloader()
        >>> result = downloader.download_track("USAT22409172", Path("/output"))
        >>> if result.success:
        ...     print(f"Downloaded: {result.file_path}")
    """
    
    def __init__(
        self,
        *,
        api_client: Optional[TidalAPIClient] = None,
        metadata_writer: Optional[TidalMetadataWriter] = None,
        api_url: Optional[str] = None,
    ):
        """Initialize Tidal downloader.
        
        Args:
            api_client: Optional TidalAPIClient instance
            metadata_writer: Optional TidalMetadataWriter instance
            api_url: Optional API URL (None for auto-discovery)
        """
        self.api_client = api_client or TidalAPIClient(api_url=api_url)
        self.metadata_writer = metadata_writer or TidalMetadataWriter()
        self.progress_callback: Optional[Callable[[int, int], None]] = None
    
    def set_progress_callback(self, callback: Optional[Callable[[int, int], None]]) -> None:
        """Set callback for download progress updates.
        
        Args:
            callback: Function called with (bytes_downloaded, total_bytes)
        """
        self.progress_callback = callback
    
    def download_track(
        self,
        isrc: str,
        output_path: Path,
        *,
        filename: Optional[str] = None,
        query: Optional[str] = None,
    ) -> DownloadResult:
        """Download track by ISRC code.
        
        Args:
            isrc: International Standard Recording Code
            output_path: Directory where file should be saved
            filename: Optional custom filename (without extension)
            
        Returns:
            DownloadResult with success status and details
        """
        logger.info(f"Starting Tidal download for ISRC: {isrc}")
        
        # Validate ISRC
        if not self.validate_isrc(isrc):
            return DownloadResult(
                success=False,
                error=f"Invalid ISRC format: {isrc}"
            )
        
        try:
            # Step 1: Search track by ISRC (with optional track name for better results)
            track_data = self.api_client.search_track_by_isrc(isrc, query=query)
            metadata = TidalTrackMetadata.from_api_response(track_data)
            
            # Step 2: Get stream URL
            stream_url = self.api_client.get_stream_url(
                metadata.tidal_id,
                quality="LOSSLESS"
            )
            
            # Step 3: Prepare output path
            if filename:
                safe_filename = sanitize_filename(filename)
            else:
                safe_artist = sanitize_filename(metadata.artists or metadata.artist)
                safe_title = sanitize_filename(metadata.title)
                safe_filename = f"{safe_artist} - {safe_title}"
            
            output_file = output_path / f"{safe_filename}.flac"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Step 4: Download file
            bytes_downloaded = self.api_client.download_file(
                stream_url,
                str(output_file),
                progress_callback=self.progress_callback
            )
            
            # Step 5: Download cover art
            cover_data = None
            if metadata.cover_id:
                cover_data = self.api_client.download_cover_art(metadata.cover_id)
            
            # Step 6: Write metadata
            self.metadata_writer.write_to_file(
                output_file,
                metadata,
                cover_data=cover_data
            )
            
            return DownloadResult(
                success=True,
                file_path=output_file,
                bytes_downloaded=bytes_downloaded,
                metadata={
                    'title': metadata.title,
                    'artist': metadata.artists or metadata.artist,
                    'album': metadata.album,
                    'isrc': metadata.isrc,
                    'size': format_file_size(bytes_downloaded)
                }
            )
            
        except Exception as e:
            return DownloadResult(
                success=False,
                error=str(e)
            )


__all__ = ["TidalDownloader"]
