"""Deezer metadata extraction and FLAC tagging."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from mutagen.flac import FLAC, Picture
except ImportError:  # pragma: no cover
    FLAC = None
    Picture = None

from spotiflac.downloaders import MetadataError


@dataclass
class DeezerTrackMetadata:
    """Metadata for a Deezer track.
    
    Attributes:
        title: Track title
        artist: Primary artist name
        artists: All contributing artists (comma-separated)
        album: Album title
        track_number: Track position in album
        disc_number: Disc number
        isrc: International Standard Recording Code
        release_date: Release date (YYYY-MM-DD or YYYY)
        duration: Duration in seconds
        cover_url: URL to cover art image
        explicit: Whether track has explicit lyrics
        deezer_id: Deezer track ID
        album_id: Deezer album ID
    """
    
    title: str
    artist: str
    album: str
    track_number: int = 1
    disc_number: int = 1
    isrc: str = ""
    release_date: str = ""
    duration: int = 0
    cover_url: str = ""
    explicit: bool = False
    deezer_id: str = ""
    album_id: str = ""
    artists: str = ""
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> DeezerTrackMetadata:
        """Parse metadata from Deezer API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            DeezerTrackMetadata instance
            
        Example:
            >>> api_data = {'title': 'Song', 'artist': {'name': 'Artist'}}
            >>> metadata = DeezerTrackMetadata.from_api_response(api_data)
        """
        # Extract artist information
        artist_name = ""
        if 'artist' in data:
            artist_name = data['artist'].get('name', '')
        
        # Extract all contributing artists
        artists_list = []
        if 'contributors' in data:
            for contributor in data['contributors']:
                if contributor.get('role') == 'Main':
                    artists_list.append(contributor.get('name', ''))
        
        artists = ', '.join(artists_list) if artists_list else artist_name
        
        # Extract album information
        album_title = ""
        album_id = ""
        cover_url = ""
        if 'album' in data:
            album = data['album']
            album_title = album.get('title', '')
            album_id = str(album.get('id', ''))
            cover_url = album.get('cover_xl') or album.get('cover_big', '')
        
        return cls(
            title=data.get('title', ''),
            artist=artist_name,
            artists=artists,
            album=album_title,
            track_number=data.get('track_position', 1),
            disc_number=data.get('disk_number', 1),
            isrc=data.get('isrc', ''),
            release_date=data.get('release_date', ''),
            duration=data.get('duration', 0),
            cover_url=cover_url,
            explicit=data.get('explicit_lyrics', False),
            deezer_id=str(data.get('id', '')),
            album_id=album_id,
        )


class DeezerMetadataWriter:
    """Write metadata to FLAC files.
    
    Example:
        >>> writer = DeezerMetadataWriter()
        >>> metadata = DeezerTrackMetadata(title="Song", artist="Artist", album="Album")
        >>> writer.write_to_file(Path("track.flac"), metadata)
    """
    
    def write_to_file(
        self,
        file_path: Path,
        metadata: DeezerTrackMetadata,
        *,
        cover_data: Optional[bytes] = None,
    ) -> None:
        """Write metadata tags to FLAC file.
        
        Args:
            file_path: Path to FLAC file
            metadata: Track metadata to write
            cover_data: Optional cover art image data
            
        Raises:
            MetadataError: If writing metadata fails
        """
        if FLAC is None:  # pragma: no cover
            raise MetadataError("mutagen library not available")
        
        try:
            audio = FLAC(str(file_path))
            audio.clear()
            
            # Write basic tags
            if metadata.title:
                audio['TITLE'] = metadata.title
            
            if metadata.artists:
                audio['ARTIST'] = metadata.artists
            elif metadata.artist:
                audio['ARTIST'] = metadata.artist
            
            if metadata.album:
                audio['ALBUM'] = metadata.album
            
            if metadata.release_date:
                audio['DATE'] = metadata.release_date
            
            if metadata.track_number:
                audio['TRACKNUMBER'] = str(metadata.track_number)
            
            if metadata.disc_number:
                audio['DISCNUMBER'] = str(metadata.disc_number)
            
            if metadata.isrc:
                audio['ISRC'] = metadata.isrc
            
            # Embed cover art if provided
            if cover_data and Picture is not None:
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                picture.data = cover_data
                audio.add_picture(picture)
            
            audio.save()
            
        except Exception as e:
            raise MetadataError(f"Failed to write metadata: {e}")


__all__ = [
    "DeezerTrackMetadata",
    "DeezerMetadataWriter",
]
