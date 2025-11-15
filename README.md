[![GitHub All Releases](https://img.shields.io/github/downloads/afkarxyz/SpotiFLAC/total?style=for-the-badge)](https://github.com/afkarxyz/SpotiFLAC/releases)

![SpotiFLAC](https://github.com/user-attachments/assets/b4c4f403-edbd-4a71-b74b-c7d433d47d06)

<div align="center">
<b>SpotiFLAC</b> allows you to download Spotify tracks in true FLAC format through services like Tidal & Deezer.
</div>

### [Download](https://github.com/afkarxyz/SpotiFLAC/releases/latest/download/SpotiFLAC.exe)

## Screenshots

![image](https://github.com/user-attachments/assets/416fca55-b885-45c0-af2a-b8b7ce5d5ef3)

![image](https://github.com/user-attachments/assets/f9b11da4-dbc3-435e-8954-5627ebe2ccdc)

![image](https://github.com/user-attachments/assets/7507e58d-e228-4edf-adf7-675731731019)

![image](https://github.com/user-attachments/assets/169da4f1-7b8a-4d50-b72e-c2fe3c51976e)

## Lossless Audio Check

![image](https://github.com/user-attachments/assets/d63b422d-0ea3-4307-850f-96c99d7eaa9a)

![image](https://github.com/user-attachments/assets/7649e6e1-d5d1-49b3-b83f-965d44651d05)

#### [Download](https://github.com/afkarxyz/SpotiFLAC/releases/download/v0/FLAC-Checker.zip) FLAC Checker

---

## Development

### Project Structure

SpotiFLAC follows a modular architecture for maintainability and testability:

```
spotiflac/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point (python -m spotiflac.__main__)
├── controllers/             # Business logic controllers
│   └── download_controller.py
├── gui/                     # GUI components
│   ├── dashboard.py
│   ├── process.py
│   ├── settings.py
│   ├── theme.py
│   ├── about.py
│   └── theme_manager.py     # Theme management
├── models/                  # Data models
│   └── track.py
├── services/                # Service layer
│   ├── spotify.py           # Spotify metadata
│   ├── tidal.py             # Tidal integration
│   ├── deezer.py            # Deezer integration
│   ├── settings.py          # Settings persistence
│   └── theming.py           # Theme utilities
└── workers/                 # Background workers
    ├── metadata.py
    ├── download.py
    └── secret.py
```

### Key Features

- **Modular Architecture**: Clear separation of GUI, business logic, and services
- **Type Safety**: Full type annotations with mypy compatibility
- **Testability**: Dependency injection for easy mocking
- **Settings Management**: Type-safe settings with `SettingsRepository`
- **Theme System**: Centralized theme management with `ThemeManager`
- **Worker Threads**: Non-blocking downloads and metadata fetching

---

## License

See LICENSE file for details.
