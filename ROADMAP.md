# 🗺️ SpotiFLAC Roadmap

## Current Version: v5.4

---

## 🚀 Upcoming Features

### v5.5 - Audio Format & Quality Options
**Priority: High** | **Status: Planned**

#### Issue Reference
- Addresses [#45](https://github.com/afkarxyz/SpotiFLAC/issues/45) - Sample rate/bit depth conversion

#### Features
- **Multiple Output Formats**
  - FLAC (current default)
  - MP3 (320kbps, 256kbps, 192kbps, 128kbps)
  - AAC (256kbps, 192kbps, 128kbps)
  - OGG Vorbis (320kbps, 256kbps, 192kbps)
  - OPUS (256kbps, 192kbps, 128kbps)
  - WAV (lossless, uncompressed)

- **Sample Rate Conversion**
  - Auto-convert high sample rates (>48kHz) to 48kHz
  - Manual selection: 44.1kHz, 48kHz, 96kHz, 192kHz
  - Smart downsampling to reduce file size

- **Bit Depth Options**
  - 16-bit (CD quality, smaller files)
  - 24-bit (high quality, larger files)
  - Auto-convert 24-bit to 16-bit option

- **Quality Presets**
  - **Maximum Quality**: FLAC, original sample rate/bit depth
  - **High Quality**: FLAC 48kHz/16-bit or MP3 320kbps
  - **Balanced**: MP3 256kbps or AAC 256kbps
  - **Space Saving**: MP3 192kbps or AAC 192kbps
  - **Mobile**: MP3 128kbps or OPUS 128kbps

#### Implementation Details
- Use `ffmpeg` for audio conversion
- Preserve metadata in all formats
- Batch conversion support
- Progress tracking per file
- Option to keep original + converted file

#### UI Changes
- New "Output Format" section in Settings
- Format dropdown (FLAC, MP3, AAC, etc.)
- Bitrate/quality slider
- Sample rate dropdown
- "Smart conversion" checkbox
- Preview estimated file size

#### Estimated Timeline
- **Planning**: 1 week
- **Implementation**: 2-3 weeks
- **Testing**: 1 week
- **Release**: End of December 2025

---

### v5.6 - CLI & API for Headless Mode
**Priority: High** | **Status: Planned**

#### Features

##### Command Line Interface (CLI)
```bash
# Download single track
spotiflac download "https://open.spotify.com/track/..." --format mp3 --quality 320

# Download playlist
spotiflac download "https://open.spotify.com/playlist/..." --service tidal --output ./music

# Batch download from file
spotiflac batch urls.txt --format flac --sample-rate 48000

# Convert existing files
spotiflac convert input.flac --format mp3 --bitrate 320 --output output.mp3

# List available services
spotiflac services --check-status

# Configuration
spotiflac config set service tidal
spotiflac config set format mp3
spotiflac config set quality 320
```

##### REST API
```bash
# Start API server
spotiflac serve --host 0.0.0.0 --port 8080

# API Endpoints
POST   /api/download          # Start download
GET    /api/download/:id      # Get download status
DELETE /api/download/:id      # Cancel download
GET    /api/downloads         # List all downloads
POST   /api/convert           # Convert audio format
GET    /api/services          # List available services
GET    /api/config            # Get configuration
PUT    /api/config            # Update configuration
```

##### Python API
```python
from spotiflac import SpotiFLAC

# Initialize
client = SpotiFLAC(service='tidal', format='mp3', quality=320)

# Download track
result = client.download('https://open.spotify.com/track/...')

# Download with options
result = client.download(
    url='https://open.spotify.com/track/...',
    format='flac',
    sample_rate=48000,
    bit_depth=16,
    output_dir='./music'
)

# Batch download
results = client.download_batch([url1, url2, url3])

# Convert format
client.convert('input.flac', format='mp3', bitrate=320)
```

#### Implementation Details
- Use `Click` or `Typer` for CLI framework
- FastAPI for REST API (upgrade from Flask)
- Async/await for concurrent downloads
- Job queue system (Celery or RQ)
- Progress callbacks
- Comprehensive error handling
- API authentication (JWT tokens)
- Rate limiting
- OpenAPI/Swagger documentation

#### Use Cases
- **Automation**: Cron jobs for playlist sync
- **Integration**: Home Assistant, Plex, etc.
- **Scripting**: Batch processing
- **Remote Control**: Control from other devices
- **CI/CD**: Automated music library management

#### Estimated Timeline
- **Planning**: 1 week
- **Implementation**: 3-4 weeks
- **Testing**: 2 weeks
- **Release**: End of January 2026

---

## 🔮 Future Considerations (v6.0+)

### Advanced Features
- **Lyrics Integration**
  - Fetch and embed synced lyrics
  - Support for LRC format
  - Multiple lyrics providers

- **Album Art Enhancement**
  - High-resolution cover art
  - Multiple art sources
  - Custom art selection

- **Playlist Sync**
  - Auto-sync Spotify playlists
  - Incremental updates
  - Change detection

- **Music Library Management**
  - Organize by artist/album/genre
  - Duplicate detection
  - Smart playlists

- **Cloud Storage Integration**
  - Google Drive
  - Dropbox
  - OneDrive
  - S3-compatible storage

### Platform Support
- **Mobile Apps**
  - Android app
  - iOS app (TestFlight)
  - React Native or Flutter

- **Browser Extension**
  - Chrome/Firefox extension
  - One-click download from Spotify web

- **Desktop Improvements**
  - System tray integration
  - Global hotkeys
  - Mini player mode

### Performance & Quality
- **Multi-threaded Downloads**
  - Parallel track downloads
  - Concurrent API requests
  - Progress aggregation

- **Smart Caching**
  - Metadata cache
  - API response cache
  - Resume interrupted downloads

- **Quality Analysis**
  - Audio fingerprinting
  - Quality verification
  - Automatic re-download on failure

---

## 📊 Version History

### v5.4 (Current) - November 2025
- ✅ Modular architecture refactor
- ✅ Smart Tidal API fallback (14 APIs)
- ✅ Automatic Deezer fallback
- ✅ Docker support with Web UI
- ✅ Comprehensive test suite
- ✅ Fixed issues #59, #75, #78

### v5.3 - October 2025
- Legacy monolithic version
- Basic Tidal/Deezer support
- PyQt6 GUI

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Priority Areas
1. **Audio Format Conversion** (v5.5)
2. **CLI/API Implementation** (v5.6)
3. **Documentation improvements**
4. **Bug fixes and testing**

### How to Contribute
1. Check the [Issues](https://github.com/weedo078/SpotiFLAC/issues) page
2. Comment on an issue you'd like to work on
3. Fork the repository
4. Create a feature branch
5. Submit a Pull Request

### Development Setup
```bash
git clone https://github.com/weedo078/SpotiFLAC.git
cd SpotiFLAC
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest
```

---

## 📝 Notes

- **Breaking Changes**: We aim to maintain backward compatibility
- **Deprecation Policy**: Features will be deprecated for at least one major version before removal
- **Release Cycle**: Major versions every 2-3 months, patches as needed
- **Support**: Latest version + previous major version

---

## 📬 Feedback

Have ideas for the roadmap? Open an issue or discussion on GitHub!

- **Feature Requests**: [GitHub Issues](https://github.com/weedo078/SpotiFLAC/issues)
- **Discussions**: [GitHub Discussions](https://github.com/weedo078/SpotiFLAC/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/weedo078/SpotiFLAC/issues)

---

**Last Updated**: November 15, 2025  
**Maintained by**: [@weedo078](https://github.com/weedo078)
