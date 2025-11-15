# SpotiFLAC Tests

## Übersicht

Dieses Verzeichnis enthält die Test-Suite für SpotiFLAC Phase 4 Refactoring.

## Test-Kategorien

### Unit Tests

- **`test_settings_repository.py`**: Tests für `SettingsRepository` und `AppSettings`
  - Laden von Einstellungen mit Defaults
  - Persistierung von Werten
  - Typ-Coercion (bool, str)
  - Mehrfach-Updates

- **`test_theme_manager.py`**: Tests für `ThemeManager`
  - Theme-Farben ändern
  - Icon-Recoloring (SVG)
  - Theme-Anwendung (qdarktheme/pyqtdarktheme)
  - Button-Style-Updates

### GUI Tests

- **`test_gui_smoke.py`**: Smoke Tests für die GUI
  - Fenster-Erstellung
  - Tab-Präsenz
  - Grundlegende Interaktionen
  - Settings/Theme-Integration

### CLI Tests

- **`test_cli_entry.py`**: Tests für CLI Entry Point
  - `python -m spotiflac.__main__` Funktionalität
  - QApplication-Initialisierung
  - Exit-Code-Handling

## Tests ausführen

### Alle Tests

```bash
pytest
```

### Spezifische Test-Datei

```bash
pytest tests/test_settings_repository.py -v
```

### Ohne GUI Tests

```bash
pytest -m "not gui"
```

## Abhängigkeiten

Die Tests benötigen folgende Pakete (siehe `requirements.txt`):

- `pytest`: Test-Framework
- `pytest-qt`: PyQt6 Test-Support
- `pytest-mock`: Mocking-Unterstützung

## Installation

```bash
pip install -r requirements.txt
```

## Hinweise

- GUI-Tests benötigen ein Display (X11/Wayland auf Linux, native auf Windows/macOS)
- Tests verwenden temporäre QSettings-Dateien und beeinflussen keine produktiven Einstellungen
- CLI-Tests mocken QApplication und GUI-Komponenten
