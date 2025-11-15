from __future__ import annotations

import asyncio
import os
import re
from typing import Iterable, List, Optional, Sequence

from mutagen.flac import FLAC
from PyQt6.QtCore import QThread, pyqtSignal

from spotiflac.models import Track
from spotiflac.services import create_deezer_downloader, create_tidal_downloader


class DownloadWorker(QThread):
    finished = pyqtSignal(bool, str, list, list, list)
    progress = pyqtSignal(str, int)

    def __init__(
        self,
        tracks: Sequence[Track],
        outpath: str,
        is_single_track: bool = False,
        is_album: bool = False,
        is_playlist: bool = False,
        album_or_playlist_name: str = "",
        filename_format: str = "title_artist",
        use_track_numbers: bool = True,
        use_artist_subfolders: bool = False,
        use_album_subfolders: bool = False,
        service: str = "tidal",
        tidal_api_url: Optional[str] = None,
        deezer_fallback_enabled: bool = False,
    ) -> None:
        super().__init__()
        self.tracks: List[Track] = list(tracks)
        self.outpath = outpath
        self.is_single_track = is_single_track
        self.is_album = is_album
        self.is_playlist = is_playlist
        self.album_or_playlist_name = album_or_playlist_name
        self.filename_format = filename_format
        self.use_track_numbers = use_track_numbers
        self.use_artist_subfolders = use_artist_subfolders
        self.use_album_subfolders = use_album_subfolders
        self.service = service
        self.tidal_api_url = tidal_api_url
        self.deezer_fallback_enabled = deezer_fallback_enabled
        self.is_paused = False
        self.is_stopped = False
        self.failed_tracks: List[tuple] = []
        self.successful_tracks: List[Track] = []
        self.skipped_tracks: List[Track] = []
        
        # Smart API caching for auto-fallback
        self.working_tidal_api: Optional[str] = None
        self.available_tidal_apis: List[str] = []
        self.tried_tidal_apis: set = set()
        self.switched_to_deezer: bool = False  # Track if we've switched to Deezer

    def get_next_tidal_api(self) -> Optional[str]:
        """Get next Tidal API to try with smart caching.
        
        Returns:
            Next API URL to try, or None if all exhausted
        """
        # If we have a working API, use it
        if self.working_tidal_api:
            return self.working_tidal_api
        
        # If we haven't fetched APIs yet, fetch them now
        if not self.available_tidal_apis:
            from spotiflac.services import get_available_tidal_apis
            apis = get_available_tidal_apis()
            # Filter for working APIs with good uptime
            working_apis = [
                api.get('url') for api in apis 
                if api.get('uptime', 0) > 50 and 
                api.get('last_check', {}).get('success', False) and
                api.get('url')
            ]
            self.available_tidal_apis = working_apis if working_apis else [api.get('url') for api in apis if api.get('url')]
        
        # Try next untried API
        for api_url in self.available_tidal_apis:
            if api_url not in self.tried_tidal_apis:
                self.tried_tidal_apis.add(api_url)
                return api_url
        
        return None
    
    def mark_tidal_api_working(self, api_url: str) -> None:
        """Mark a Tidal API as working and cache it for future tracks."""
        self.working_tidal_api = api_url
        self.progress.emit(f"✅ Found working Tidal API: {api_url}", 0)

    def attempt_tidal_download(
        self,
        track: Track,
        track_outpath: str,
        downloader,
        new_filename: str,
        new_filepath: str,
        auto_fallback: bool,
        is_paused_callback,
        is_stopped_callback,
    ) -> str:
        if not track.isrc:
            raise Exception(f"No ISRC found for track: {track.title}. Skipping.")

        self.progress.emit(
            f"Searching and downloading from Tidal for ISRC: {track.isrc} - {track.title} - {track.artists}",
            0,
        )

        # Use new modular API with track name for better search results
        from pathlib import Path
        search_query = f"{track.title} {track.artists}"
        result = downloader.download_track(
            track.isrc, 
            Path(track_outpath), 
            filename=new_filename,
            query=search_query
        )
        
        if not result.success:
            raise Exception(f"Tidal download failed: {result.error}")
        
        if result.file_path and os.path.exists(result.file_path):
            return str(result.file_path)
        else:
            raise Exception("Downloaded file not found")

    def attempt_deezer_download(self, track: Track, track_outpath: str) -> str:
        if not track.isrc:
            raise Exception(f"No ISRC available for Deezer download: {track.title}")

        self.progress.emit(f"Downloading from Deezer with ISRC: {track.isrc}", 0)

        downloader = create_deezer_downloader()
        downloader.set_progress_callback(lambda current, total: None)

        from pathlib import Path
        result = downloader.download_track(track.isrc, Path(track_outpath))
        
        if not result.success:
            raise Exception(f"Deezer download failed: {result.error}")

        if result.file_path and os.path.exists(result.file_path):
            return str(result.file_path)
        else:
            raise Exception("Downloaded file not found")

    def get_flac_isrc(self, filepath: str) -> Optional[str]:
        try:
            audio = FLAC(filepath)
            if "isrc" in audio:
                return audio["isrc"][0]
        except Exception:
            pass
        return None

    def get_formatted_filename(self, track: Track) -> str:
        if self.filename_format == "artist_title":
            filename = f"{track.artists} - {track.title}.flac"
        elif self.filename_format == "title_only":
            filename = f"{track.title}.flac"
        else:
            filename = f"{track.title} - {track.artists}.flac"
        return re.sub(r'[<>:"/\\|?*]', lambda m: "'" if m.group() == '"' else "_", filename)

    def run(self) -> None:  # noqa: C901 (large but legacy)
        try:
            # Initialize downloader (will be recreated for each API attempt if needed)
            downloader = None
            if self.service == "tidal":
                # For auto-fallback, resolve API on first track
                if self.tidal_api_url == "auto":
                    first_api = self.get_next_tidal_api()
                    if first_api:
                        downloader = create_tidal_downloader(api_url=first_api)
                        self.progress.emit(f"[Auto Fallback 1/{len(self.available_tidal_apis)}] Trying: {first_api}", 0)
                else:
                    downloader = create_tidal_downloader(api_url=self.tidal_api_url)
            else:
                downloader = create_deezer_downloader()

            def progress_update(current, total):
                if current > 0 and total > 0:
                    self.progress.emit(f"Downloading: {current}/{total} bytes", 0)
                else:
                    self.progress.emit("Processing metadata...", 0)

            if downloader:
                downloader.set_progress_callback(progress_update)

            total_tracks = len(self.tracks)

            for i, track in enumerate(self.tracks):
                while self.is_paused:
                    if self.is_stopped:
                        return
                    self.msleep(100)
                if self.is_stopped:
                    return

                self.progress.emit(
                    f"Starting download ({i + 1}/{total_tracks}): {track.title} - {track.artists}",
                    int(i / total_tracks * 100),
                )

                try:
                    if self.is_playlist:
                        track_outpath = self.outpath

                        if self.use_artist_subfolders:
                            artist_name = track.artists.split(", ")[0] if ", " in track.artists else track.artists
                            artist_folder = re.sub(
                                r'[<>:"/\\|?*]', lambda m: "'" if m.group() == '"' else "_", artist_name
                            ).rstrip(". ")
                            track_outpath = os.path.join(track_outpath, artist_folder)

                        if self.use_album_subfolders:
                            album_folder = re.sub(
                                r'[<>:"/\\|?*]', lambda m: "'" if m.group() == '"' else "_", track.album
                            ).rstrip(". ")
                            track_outpath = os.path.join(track_outpath, album_folder)

                        os.makedirs(track_outpath, exist_ok=True)
                    else:
                        track_outpath = self.outpath

                    spotify_isrc = track.isrc
                    if spotify_isrc:
                        is_already_downloaded = False
                        try:
                            for filename in os.listdir(track_outpath):
                                if filename.lower().endswith(".flac"):
                                    filepath = os.path.join(track_outpath, filename)
                                    local_isrc = self.get_flac_isrc(filepath)
                                    if local_isrc and local_isrc == spotify_isrc:
                                        self.progress.emit(
                                            f"Skipped: Track with matching ISRC '{spotify_isrc}' already exists ('{filename}').",
                                            0,
                                        )
                                        self.progress.emit(
                                            f"Skipped: {track.title} - {track.artists}",
                                            int((i + 1) / total_tracks * 100),
                                        )
                                        self.skipped_tracks.append(track)
                                        is_already_downloaded = True
                                        break
                        except FileNotFoundError:
                            pass

                        if is_already_downloaded:
                            continue

                    if (self.is_album or self.is_playlist) and self.use_track_numbers:
                        new_filename = f"{track.track_number:02d} - {self.get_formatted_filename(track)}"
                    else:
                        new_filename = self.get_formatted_filename(track)

                    new_filename = re.sub(r'[<>:"/\\|?*]', lambda m: "'" if m.group() == '"' else "_", new_filename)
                    new_filepath = os.path.join(track_outpath, new_filename)

                    if os.path.exists(new_filepath) and os.path.getsize(new_filepath) > 0:
                        self.progress.emit(f"File already exists by name: {new_filename}. Skipping download.", 0)
                        self.progress.emit(
                            f"Skipped: {track.title} - {track.artists}", int((i + 1) / total_tracks * 100)
                        )
                        self.skipped_tracks.append(track)
                        continue

                    # Check if we've switched to Deezer permanently
                    if self.switched_to_deezer:
                        # Use Deezer for all remaining tracks
                        if not track.isrc:
                            self.progress.emit(f"No ISRC found for track: {track.title}. Skipping.", 0)
                            self.failed_tracks.append((track.title, track.artists, "No ISRC available"))
                            continue

                        self.progress.emit(f"Downloading from Deezer with ISRC: {track.isrc}", 0)
                        
                        from pathlib import Path
                        result = downloader.download_track(track.isrc, Path(track_outpath))
                        
                        if result.success and result.file_path:
                            downloaded_file = str(result.file_path)
                        else:
                            raise Exception(f"Deezer download failed: {result.error}")
                    
                    elif self.service == "tidal":
                        is_paused_callback = lambda: self.is_paused
                        is_stopped_callback = lambda: self.is_stopped
                        auto_fallback = self.tidal_api_url == "auto"
                        
                        downloaded_file = None
                        last_error = None

                        # Try download with smart API fallback
                        while True:
                            try:
                                # If auto-fallback, always get/create downloader with next API
                                if auto_fallback:
                                    if not self.working_tidal_api:
                                        # Try next API
                                        next_api = self.get_next_tidal_api()
                                        if not next_api:
                                            # All APIs exhausted
                                            if last_error:
                                                raise Exception(f"All Tidal APIs failed. Last error: {last_error}")
                                            else:
                                                raise Exception("No Tidal APIs available")
                                        
                                        # Create new downloader with next API
                                        downloader = create_tidal_downloader(api_url=next_api)
                                        downloader.set_progress_callback(progress_update)
                                        attempt_num = len(self.tried_tidal_apis)
                                        total_apis = len(self.available_tidal_apis)
                                        self.progress.emit(f"[Auto Fallback {attempt_num}/{total_apis}] Trying: {next_api}", 0)
                                    # else: use existing working downloader
                                
                                downloaded_file = self.attempt_tidal_download(
                                    track,
                                    track_outpath,
                                    downloader,
                                    new_filename,
                                    new_filepath,
                                    auto_fallback,
                                    is_paused_callback,
                                    is_stopped_callback,
                                )
                                
                                # Success! Mark this API as working
                                if auto_fallback and not self.working_tidal_api:
                                    # Get API URL from the downloader's client
                                    if hasattr(downloader, 'client') and hasattr(downloader.client, 'api_url'):
                                        current_api = downloader.client.api_url
                                    elif hasattr(downloader, 'api_url'):
                                        current_api = downloader.api_url
                                    else:
                                        # Extract from tried_tidal_apis
                                        current_api = list(self.tried_tidal_apis)[-1] if self.tried_tidal_apis else "unknown"
                                    self.mark_tidal_api_working(current_api)
                                
                                break  # Success, exit retry loop
                                
                            except Exception as tidal_error:
                                error_message = str(tidal_error)
                                last_error = error_message
                                
                                # If not auto-fallback or we have a working API, don't retry
                                if not auto_fallback or self.working_tidal_api:
                                    break
                                
                                # Check if we should retry with next API
                                # Retry on any API/auth related error
                                should_retry = any([
                                    "405" in error_message,
                                    "Failed to get access token" in error_message,
                                    "Method Not Allowed" in error_message,
                                    "oauth2" in error_message.lower(),
                                    "authentication" in error_message.lower(),
                                    "unauthorized" in error_message.lower(),
                                    "403" in error_message,
                                    "401" in error_message,
                                ])
                                
                                if should_retry:
                                    self.progress.emit(f"❌ API failed: {error_message[:100]}", 0)
                                    # Continue to try next API
                                    continue
                                else:
                                    # Track-specific error (e.g., no ISRC), don't retry
                                    break
                        
                        if not downloaded_file:
                            error_message = last_error or "Tidal download failed"
                            if error_message == "Download stopped by user":
                                return

                            # If all Tidal APIs failed and Deezer fallback is enabled
                            if auto_fallback and "All Tidal APIs failed" in error_message and self.deezer_fallback_enabled:
                                self.progress.emit(
                                    "❌ Alle Tidal-APIs fehlgeschlagen. Wechsle permanent zu Deezer für restliche Downloads...",
                                    0,
                                )
                                self.switched_to_deezer = True
                                # Create Deezer downloader for all remaining tracks
                                downloader = create_deezer_downloader()
                                downloader.set_progress_callback(progress_update)
                                self.progress.emit("✅ Deezer-Downloader aktiviert für alle weiteren Tracks", 0)
                                
                                # Try downloading current track with Deezer
                                try:
                                    downloaded_file = self.attempt_deezer_download(track, track_outpath)
                                    self.progress.emit("✅ Deezer-Download erfolgreich", 0)
                                except Exception as deezer_error:
                                    raise Exception(f"Deezer-Fallback fehlgeschlagen: {deezer_error}")
                            
                            elif self.deezer_fallback_enabled and not self.is_stopped:
                                # Single track Deezer fallback (not permanent switch)
                                self.progress.emit(
                                    f"Tidal fehlgeschlagen ({error_message}). Versuche Deezer-Fallback...",
                                    0,
                                )
                                try:
                                    downloaded_file = self.attempt_deezer_download(track, track_outpath)
                                    self.progress.emit("✅ Deezer-Fallback erfolgreich", 0)
                                except Exception as deezer_error:
                                    raise Exception(
                                        f"Tidal fehlgeschlagen: {error_message}; Deezer-Fallback fehlgeschlagen: {deezer_error}"
                                    )
                            else:
                                raise Exception(error_message)
                    elif self.service == "deezer":
                        if not track.isrc:
                            self.progress.emit(f"No ISRC found for track: {track.title}. Skipping.", 0)
                            self.failed_tracks.append((track.title, track.artists, "No ISRC available"))
                            continue

                        self.progress.emit(f"Downloading from Deezer with ISRC: {track.isrc}", 0)

                        from pathlib import Path
                        result = downloader.download_track(track.isrc, Path(track_outpath))

                        if result.success and result.file_path:
                            downloaded_file = str(result.file_path)
                        else:
                            raise Exception(f"Deezer download failed: {result.error}")
                    else:
                        track_id = track.id
                        self.progress.emit(f"Getting track info for ID: {track_id} from {self.service}", 0)

                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_closed():
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        metadata = loop.run_until_complete(downloader.get_track_info(track_id, self.service))
                        self.progress.emit("Track info received, starting download process", 0)

                        is_paused_callback = lambda: self.is_paused
                        is_stopped_callback = lambda: self.is_stopped

                        downloaded_file = downloader.download(
                            metadata,
                            track_outpath,
                            is_paused_callback=is_paused_callback,
                            is_stopped_callback=is_stopped_callback,
                        )
                    if self.is_stopped:
                        return

                    if downloaded_file and os.path.exists(downloaded_file):
                        if downloaded_file == new_filepath:
                            self.progress.emit(f"File already exists: {new_filename}", 0)
                            self.progress.emit(
                                f"Skipped: {track.title} - {track.artists}", int((i + 1) / total_tracks * 100)
                            )
                            self.skipped_tracks.append(track)
                            continue

                        if downloaded_file != new_filepath:
                            try:
                                os.rename(downloaded_file, new_filepath)
                                self.progress.emit(f"File renamed to: {new_filename}", 0)
                            except OSError as exc:
                                self.progress.emit(
                                    f"Warning: Could not rename file {downloaded_file} to {new_filepath}: {exc}",
                                    0,
                                )
                    else:
                        raise Exception(f"Download failed or file not found: {downloaded_file}")

                    self.progress.emit(
                        f"Successfully downloaded: {track.title} - {track.artists}",
                        int((i + 1) / total_tracks * 100),
                    )
                    self.successful_tracks.append(track)
                except Exception as exc:
                    self.failed_tracks.append((track.title, track.artists, str(exc)))
                    self.progress.emit(
                        f"Failed to download: {track.title} - {track.artists}\nError: {exc}",
                        int((i + 1) / total_tracks * 100),
                    )
                    continue

            if not self.is_stopped:
                success_message = "Download completed!"
                if self.failed_tracks:
                    success_message += f"\n\nFailed downloads: {len(self.failed_tracks)} tracks"
                if self.successful_tracks:
                    success_message += f"\n\nSuccessful downloads: {len(self.successful_tracks)} tracks"
                if self.skipped_tracks:
                    success_message += f"\n\nSkipped (already exists): {len(self.skipped_tracks)} tracks"
                self.finished.emit(True, success_message, self.failed_tracks, self.successful_tracks, self.skipped_tracks)
        except Exception as exc:  # pragma: no cover - defensive
            self.finished.emit(False, str(exc), self.failed_tracks, self.successful_tracks, self.skipped_tracks)

    def pause(self) -> None:
        self.is_paused = True
        self.progress.emit("Download process paused.", 0)

    def resume(self) -> None:
        self.is_paused = False
        self.progress.emit("Download process resumed.", 0)

    def stop(self) -> None:
        self.is_stopped = True
        self.is_paused = False
