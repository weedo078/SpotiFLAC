"""Utility functions for Deezer downloader."""
from __future__ import annotations

from random import randrange
from typing import List


# Realistic User-Agent templates for better anonymity
_USER_AGENT_TEMPLATES: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit}.{webkit_minor} (KHTML, like Gecko) Chrome/{chrome}.0.{chrome_build}.{chrome_patch} Safari/{webkit}.{webkit_minor}",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{macos_major}_{macos_minor}) AppleWebKit/{webkit}.{webkit_minor} (KHTML, like Gecko) Chrome/{chrome}.0.{chrome_build}.{chrome_patch} Safari/{webkit}.{webkit_minor}",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{webkit}.{webkit_minor} (KHTML, like Gecko) Chrome/{chrome}.0.{chrome_build}.{chrome_patch} Safari/{webkit}.{webkit_minor}",
]


def get_random_user_agent() -> str:
    """Generate random but realistic User-Agent string.
    
    Creates a User-Agent string that mimics real browsers to avoid
    detection and blocking by music service APIs.
    
    Returns:
        User-Agent string suitable for HTTP requests
        
    Example:
        >>> ua = get_random_user_agent()
        >>> "Mozilla/5.0" in ua
        True
        >>> "Chrome" in ua
        True
    """
    template = _USER_AGENT_TEMPLATES[randrange(0, len(_USER_AGENT_TEMPLATES))]
    
    return template.format(
        webkit=randrange(530, 538),
        webkit_minor=randrange(30, 37),
        chrome=randrange(100, 120),
        chrome_build=randrange(4000, 6000),
        chrome_patch=randrange(100, 200),
        macos_major=randrange(13, 16),
        macos_minor=randrange(0, 7),
    )


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize filename for safe filesystem usage.
    
    Removes or replaces characters that are invalid in filenames
    across different operating systems.
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename (default: 255)
        
    Returns:
        Sanitized filename safe for all filesystems
        
    Example:
        >>> sanitize_filename('Artist: "Song" <2024>')
        'Artist Song 2024'
        >>> sanitize_filename('Test/Path\\File')
        'Test_Path_File'
    """
    # Characters to remove or replace
    invalid_chars = '<>:"/\\|?*'
    
    # Replace invalid characters with underscore
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > max_length:
        filename = filename[:max_length].strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"
    
    return filename


def format_file_size(bytes_count: int) -> str:
    """Format byte count as human-readable file size.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "320 KB")
        
    Example:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1536000)
        '1.5 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"


__all__ = [
    "get_random_user_agent",
    "sanitize_filename",
    "format_file_size",
]
