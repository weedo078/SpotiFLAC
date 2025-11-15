# SpotiFLAC v5.4 - Refactored Edition

## 🎉 Major Refactoring & Improvements

This release represents a complete architectural overhaul of SpotiFLAC with significant improvements in stability, reliability, and code quality.

## ✨ New Features

### Smart API Fallback System
- **Automatic Tidal API Testing**: Tests all 14 available Tidal API instances automatically
- **API Caching**: Remembers working APIs for faster subsequent downloads
- **Intelligent Fallback**: Automatically switches to Deezer when all Tidal APIs fail
- **Session Persistence**: Working API is cached for the entire download session

### Improved Download Reliability
- **Robust Error Handling**: Better error messages and recovery mechanisms
- **Multi-Source Support**: Seamlessly switches between Tidal and Deezer
- **Progress Tracking**: Real-time download progress with detailed status updates

## 🔧 Technical Improvements

### Modular Architecture
- Complete restructuring into `spotiflac/` package
- Separated concerns: downloaders, metadata, GUI, services, workers
- Comprehensive test suite with 20+ unit tests
- Better code organization and maintainability

### Fixed Tidal Integration
- **OAuth Authentication**: Uses official `auth.tidal.com` server
- **Search API**: Uses official `api.tidal.com` for track search
- **Download API**: Uses proxy servers for download URLs (like legacy version)
- **ISRC Filtering**: Searches by track name, then filters by ISRC for better results
- **HIRES Support**: Prefers HIRES_LOSSLESS quality when available

### Enhanced Logging
- DEBUG level logging for troubleshooting
- Detailed error messages with context
- Better visibility into download process

## 🐛 Bug Fixes

### Fixed Issues
- **#59**: "API returned status code: 404" - Fixed with smart fallback system
- **#75**: "Error: Deezer download failed" - Improved error handling and logging
- **#78**: "Regarding the use of unsafe Api endpoint" - Now uses official Tidal APIs for auth/search

### Other Fixes
- Fixed `format_duration` AttributeError
- Fixed `log_output` initialization issues
- Fixed Deezer `download_by_isrc` method name
- Improved metadata handling for both legacy and new API formats

## 📦 What's Included

- **SpotiFLAC.exe**: Standalone executable (no Python required)
- **Modular codebase**: Clean, maintainable code structure
- **Test suite**: Comprehensive unit tests
- **Documentation**: Updated README and RUNNING.md

## 🚀 How to Use

1. Download `SpotiFLAC.exe`
2. Run the executable
3. Enter a Spotify URL
4. Choose Tidal (with auto-fallback) or Deezer
5. Click Download!

## ⚙️ Recommended Settings

- **Service**: Tidal with "Auto Fallback (recommended)"
- **Deezer Fallback**: Enable "Try Deezer automatically if Tidal fails"
- This combination provides maximum reliability

## 📊 Statistics

- **89 files changed**
- **7,353 insertions**
- **1,274 deletions**
- **20+ unit tests**
- **5 modular packages**

## 🙏 Credits

- Original project by afkarxyz
- Refactoring and improvements by weedo078
- Community feedback and bug reports

## 📝 Migration Notes

For developers:
- Legacy files moved to `legacy_backup/`
- New entry point: `python -m spotiflac.app`
- Modular imports: `from spotiflac.downloaders import TidalDownloader`

---

**Full Changelog**: https://github.com/weedo078/SpotiFLAC/compare/main...refactored
