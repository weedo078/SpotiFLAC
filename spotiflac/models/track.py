from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Track:
    """Domain entity representing a single audio track to download."""

    external_urls: str
    title: str
    artists: str
    album: str
    track_number: int
    duration_ms: int
    id: str
    isrc: str = ""
    release_date: str = ""
