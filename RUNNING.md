# SpotiFLAC - Anwendung starten

## Methoden zum Starten

### 1. Über Python-Modul (empfohlen) ✅
```bash
python -m spotiflac.app
```

### 2. Über Launcher-Skript ✅
```bash
python run_spotiflac.py
```

### 3. Legacy-Methode (funktioniert noch) ⚠️
```bash
python SpotiFLAC.py
```

---

## Voraussetzungen

- Python 3.10+
- Virtual Environment aktiviert
- Alle Dependencies installiert

```bash
# Virtual Environment aktivieren
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt
```

---

## Entwicklung

### Logging

Logs werden gespeichert in:
- **Windows**: `C:\Users\<USER>\.spotiflac\spotiflac.log`
- **Linux/Mac**: `~/.spotiflac/spotiflac.log`

### Tests ausführen

```bash
# Alle Tests
pytest

# Nur Downloader/Metadata/Tools
pytest tests/downloaders/ tests/metadata/ tests/tools/

# Mit Coverage
pytest --cov=spotiflac --cov-report=html
```

---

## Troubleshooting

### "No module named 'spotiflac'"
→ Stelle sicher, dass du im richtigen Verzeichnis bist und die venv aktiviert ist

### "Kein Dark-Theme-Modul verfügbar"
→ Optional, die App funktioniert auch ohne Theme:
```bash
pip install pyqtdarktheme
```

### "DLL load failed while importing QtCore"
→ PyQt6-Problem, versuche:
```bash
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PyQt6
```

---

**Erstellt**: 15. November 2025  
**Version**: 2.0 (Modular Refactored)
