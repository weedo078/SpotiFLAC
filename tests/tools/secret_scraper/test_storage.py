"""Tests for secret storage."""
from __future__ import annotations

from pathlib import Path
import pytest

from spotiflac.tools.secret_scraper import SecretStorage, SecretStorageError


class TestSecretStorage:
    """Test SecretStorage."""

    def test_initialization_default(self):
        """Test default initialization."""
        storage = SecretStorage()
        assert storage.storage_path == SecretStorage.DEFAULT_PATH

    def test_initialization_custom_path(self, tmp_path):
        """Test custom path initialization."""
        custom_path = tmp_path / "secrets.json"
        storage = SecretStorage(storage_path=custom_path)
        assert storage.storage_path == custom_path

    def test_save_secrets(self, tmp_path):
        """Test saving secrets."""
        storage_path = tmp_path / "secrets.json"
        storage = SecretStorage(storage_path=storage_path)
        
        secrets = [
            {"version": 1, "secret": [1, 2, 3]},
            {"version": 2, "secret": [4, 5, 6]}
        ]
        
        storage.save_secrets(secrets)
        
        assert storage_path.exists()

    def test_load_secrets(self, tmp_path):
        """Test loading secrets."""
        storage_path = tmp_path / "secrets.json"
        storage = SecretStorage(storage_path=storage_path)
        
        secrets = [{"version": 1, "secret": [1, 2, 3]}]
        storage.save_secrets(secrets)
        
        loaded = storage.load_secrets()
        assert loaded == secrets

    def test_load_secrets_file_not_found(self, tmp_path):
        """Test loading when file doesn't exist."""
        storage_path = tmp_path / "nonexistent.json"
        storage = SecretStorage(storage_path=storage_path)
        
        with pytest.raises(SecretStorageError, match="not found"):
            storage.load_secrets()

    def test_process_captured_secrets(self):
        """Test processing captured secrets."""
        storage = SecretStorage()
        
        captured = [
            {"version": 1, "secret": [1, 2, 3], "extra": "data"},
            {"version": 2, "secret": [4, 5, 6]}
        ]
        
        processed = storage.process_captured_secrets(captured)
        
        assert len(processed) == 2
        assert processed[0] == {"version": 1, "secret": [1, 2, 3]}
        assert processed[1] == {"version": 2, "secret": [4, 5, 6]}

    def test_process_captured_secrets_filters_invalid(self):
        """Test processing filters invalid entries."""
        storage = SecretStorage()
        
        captured = [
            {"version": 1, "secret": [1, 2, 3]},
            {"version": 2},  # Missing secret
            {"secret": [4, 5, 6]},  # Missing version
        ]
        
        processed = storage.process_captured_secrets(captured)
        
        assert len(processed) == 1
        assert processed[0] == {"version": 1, "secret": [1, 2, 3]}
