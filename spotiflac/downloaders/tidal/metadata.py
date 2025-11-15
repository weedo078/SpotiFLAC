"""Tidal metadata extraction and FLAC tagging."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from mutagen.flac import FLAC, Picture
    from mutagen.id3 import PictureType
except ImportError:  # pragma: no cover
    FLAC = None
    Picture = None
    PictureType = None

from spotiflac.downloaders import MetadataError


@dataclass
class TidalTrackMetadata:
    """Metadata for a Tidal track.
    
    Attributes:
        title: Track title
        artist: Primary artist name
        artists: All contributing artists
        album: Album title
        track_number: Track position in album
        disc_number: Disc number
        isrc: International Standard Recording Code
        release_date: Release date
        duration: Duration in seconds
        cover_id: Tidal cover ID
        explicit: Whether track has explicit lyrics
        tidal_id: Tidal track ID
        album_id: Tidal album ID
    """
    
    title: str
    artist: str
    album: str
    track_number: int = 1
    disc_number: int = 1
    isrc: str = ""
    release_date: str = ""
    duration: int = 0
    cover_id: str = ""
    explicit: bool = False
    tidal_id: str = ""
    album_id: str = ""
    artists: str = ""
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> TidalTrackMetadata:
        """Parse metadata from Tidal API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            TidalTrackMetadata instance
        """
        # Extract artist information
        artist_name = ""
        if 'artist' in data:
            artist_name = data['artist'].get('name', '')
        
        # Extract all artists
        artists_list = []
        if 'artists' in data:
            for artist in data['artists']:
                artists_list.append(artist.get('name', ''))
        
        artists = ', '.join(artists_list) if artists_list else artist_name
        
        # Extract album information
        album_title = ""
        album_id = ""
        cover_id = ""
        if 'album' in data:
            album = data['album']
            album_title = album.get('title', '')
            album_id = str(album.get('id', ''))
            cover_id = album.get('cover', '')
        
        return cls(
            title=data.get('title', ''),
            artist=artist_name,
            artists=artists,
            album=album_title,
            track_number=data.get('trackNumber', 1),
            disc_number=data.get('volumeNumber', 1),
            isrc=data.get('isrc', ''),
            release_date=data.get('streamStartDate', ''),
            duration=data.get('duration', 0),
            cover_id=cover_id,
            explicit=data.get('explicit', False),
            tidal_id=str(data.get('id', '')),
            album_id=album_id,
        )


class TidalMetadataWriter:
    """Write metadata to FLAC files.
    
    Example:
        >>> writer = TidalMetadataWriter()
        >>> metadata = TidalTrackMetadata(title="Song", artist="Artist", album="Album")
        >>> writer.write_to_file(Path("track.flac"), metadata)
    """
    
    def write_to_file(
        self,
        file_path: Path,
        metadata: TidalTrackMetadata,
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
                # Extract year from date
                year = metadata.release_date.split('-')[0] if '-' in metadata.release_date else metadata.release_date
                audio['DATE'] = year
            
            if metadata.track_number:
                audio['TRACKNUMBER'] = str(metadata.track_number)
            
            if metadata.disc_number:
                audio['DISCNUMBER'] = str(metadata.disc_number)
            
            if metadata.isrc:
                audio['ISRC'] = metadata.isrc
            
            # Embed cover art if provided
            if cover_data and Picture is not None:
                picture = Picture()
                picture.type = PictureType.COVER_FRONT if PictureType else 3
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                picture.data = cover_data
                audio.add_picture(picture)
            
            audio.save()
            
        except Exception as e:
            raise MetadataError(f"Failed to write metadata: {e}")


__all__ = [
    "TidalTrackMetadata",
    "TidalMetadataWriter",
]
