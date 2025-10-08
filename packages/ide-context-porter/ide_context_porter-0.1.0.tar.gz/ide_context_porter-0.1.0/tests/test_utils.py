"""Tests for utility functions."""

import json
from pathlib import Path

import pytest
import yaml

from ideporter.utils import (
    create_backup,
    is_ignored_path,
    load_json,
    load_yaml,
    safe_read,
    safe_write,
    save_json,
    save_yaml,
)


def test_safe_write_new_file(tmp_path):
    """Test writing to a new file."""
    file_path = tmp_path / "test.txt"
    content = "Hello, world!"

    safe_write(file_path, content, force=False, dry_run=False)

    assert file_path.exists()
    assert file_path.read_text() == content


def test_safe_write_dry_run(tmp_path):
    """Test dry-run mode doesn't write."""
    file_path = tmp_path / "test.txt"
    content = "Hello, world!"

    safe_write(file_path, content, force=False, dry_run=True)

    assert not file_path.exists()


def test_safe_write_creates_backup(tmp_path):
    """Test that backup is created when overwriting."""
    file_path = tmp_path / "test.txt"
    original_content = "Original"
    new_content = "New"

    # Create original file
    file_path.write_text(original_content)

    # Overwrite
    safe_write(file_path, new_content, force=False, dry_run=False)

    # Check new content
    assert file_path.read_text() == new_content

    # Check backup exists
    backup_files = list(tmp_path.glob("*.bak"))
    assert len(backup_files) == 1
    assert backup_files[0].read_text() == original_content


def test_safe_write_force_no_backup(tmp_path):
    """Test that force mode skips backup."""
    file_path = tmp_path / "test.txt"
    original_content = "Original"
    new_content = "New"

    # Create original file
    file_path.write_text(original_content)

    # Overwrite with force
    safe_write(file_path, new_content, force=True, dry_run=False)

    # Check new content
    assert file_path.read_text() == new_content

    # Check no backup
    backup_files = list(tmp_path.glob("*.bak"))
    assert len(backup_files) == 0


def test_safe_read(tmp_path):
    """Test reading a file."""
    file_path = tmp_path / "test.txt"
    content = "Hello, world!"
    file_path.write_text(content)

    result = safe_read(file_path)
    assert result == content


def test_safe_read_missing_file(tmp_path):
    """Test reading a missing file raises error."""
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        safe_read(file_path)


def test_create_backup(tmp_path):
    """Test creating a backup."""
    file_path = tmp_path / "test.txt"
    content = "Original content"
    file_path.write_text(content)

    backup_path = create_backup(file_path)

    assert backup_path.exists()
    assert backup_path.read_text() == content
    assert ".bak" in backup_path.name


def test_create_backup_nonexistent(tmp_path):
    """Test creating backup of nonexistent file."""
    file_path = tmp_path / "missing.txt"
    backup_path = create_backup(file_path)

    # Should return the original path without creating anything
    assert backup_path == file_path
    assert not backup_path.exists()


def test_load_yaml(tmp_path):
    """Test loading YAML file."""
    file_path = tmp_path / "test.yaml"
    data = {"key": "value", "number": 42}
    file_path.write_text(yaml.dump(data))

    result = load_yaml(file_path)
    assert result == data


def test_save_yaml(tmp_path):
    """Test saving YAML file."""
    file_path = tmp_path / "test.yaml"
    data = {"key": "value", "number": 42}

    save_yaml(file_path, data, force=False, dry_run=False)

    assert file_path.exists()
    loaded = yaml.safe_load(file_path.read_text())
    assert loaded == data


def test_load_json(tmp_path):
    """Test loading JSON file."""
    file_path = tmp_path / "test.json"
    data = {"key": "value", "number": 42}
    file_path.write_text(json.dumps(data))

    result = load_json(file_path)
    assert result == data


def test_save_json(tmp_path):
    """Test saving JSON file."""
    file_path = tmp_path / "test.json"
    data = {"key": "value", "number": 42}

    save_json(file_path, data, force=False, dry_run=False)

    assert file_path.exists()
    loaded = json.loads(file_path.read_text())
    assert loaded == data


def test_is_ignored_path():
    """Test path ignore checking."""
    # Should be ignored
    assert is_ignored_path(Path("/project/.env"))
    assert is_ignored_path(Path("/project/.git/config"))
    assert is_ignored_path(Path("/project/node_modules/package"))
    assert is_ignored_path(Path("/project/dist/bundle.js"))
    assert is_ignored_path(Path("/project/key.pem"))

    # Should not be ignored
    assert not is_ignored_path(Path("/project/src/main.py"))
    assert not is_ignored_path(Path("/project/README.md"))
    assert not is_ignored_path(Path("/project/.vscode/settings.json"))
