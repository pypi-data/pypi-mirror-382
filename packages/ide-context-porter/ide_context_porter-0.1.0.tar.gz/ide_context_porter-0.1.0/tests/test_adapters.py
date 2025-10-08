"""Tests for IDE adapters."""

import json

import pytest
import yaml

from ideporter.adapters import get_adapter
from ideporter.adapters.claude import ClaudeAdapter
from ideporter.adapters.continue_adapter import ContinueAdapter
from ideporter.adapters.cursor import CursorAdapter
from ideporter.adapters.vscode import VSCodeAdapter
from ideporter.adapters.windsurf import WindsurfAdapter


def test_get_adapter_cursor():
    """Test getting cursor adapter."""
    adapter_class = get_adapter("cursor")
    assert adapter_class == CursorAdapter


def test_get_adapter_vscode():
    """Test getting vscode adapter."""
    adapter_class = get_adapter("vscode")
    assert adapter_class == VSCodeAdapter


def test_get_adapter_invalid():
    """Test getting invalid adapter."""
    with pytest.raises(ValueError, match="Unknown adapter"):
        get_adapter("invalid")


# Cursor Adapter Tests


def test_cursor_detect_with_cursorrules(temp_project):
    """Test Cursor detection with .cursorrules."""
    (temp_project / ".cursorrules").write_text("# Rules")
    adapter = CursorAdapter(temp_project)
    assert adapter.detect() is True


def test_cursor_detect_without_files(temp_project):
    """Test Cursor detection without files."""
    adapter = CursorAdapter(temp_project)
    assert adapter.detect() is False


def test_cursor_import(temp_project, canonical_context, sample_rules):
    """Test importing from Cursor."""
    # Create Cursor files
    (temp_project / ".cursorrules").write_text(sample_rules)
    (temp_project / ".cursorignore").write_text("node_modules/\n*.log")

    adapter = CursorAdapter(temp_project)
    adapter.import_context(canonical_context.context_dir, force=False, dry_run=False)

    # Check canonical files were created
    rules_file = canonical_context.context_dir / "rules.md"
    ignore_file = canonical_context.context_dir / "ignore.txt"

    assert rules_file.exists()
    assert ignore_file.exists()
    assert sample_rules in rules_file.read_text()


def test_cursor_export(temp_project, canonical_context, sample_rules):
    """Test exporting to Cursor."""
    # Create canonical files
    (canonical_context.context_dir / "rules.md").write_text(sample_rules)
    (canonical_context.context_dir / "ignore.txt").write_text("node_modules/")

    adapter = CursorAdapter(temp_project)
    adapter.export_context(canonical_context.context_dir, force=False, dry_run=False)

    # Check Cursor files were created
    cursorrules = temp_project / ".cursorrules"
    cursorignore = temp_project / ".cursorignore"

    assert cursorrules.exists()
    assert cursorignore.exists()
    assert sample_rules in cursorrules.read_text()


def test_cursor_roundtrip(temp_project, canonical_context, sample_rules):
    """Test Cursor import → export roundtrip."""
    # Start with Cursor files
    original_rules = sample_rules
    (temp_project / ".cursorrules").write_text(original_rules)

    adapter = CursorAdapter(temp_project)

    # Import
    adapter.import_context(canonical_context.context_dir, force=True, dry_run=False)

    # Delete original
    (temp_project / ".cursorrules").unlink()

    # Export
    adapter.export_context(canonical_context.context_dir, force=True, dry_run=False)

    # Check roundtrip
    assert (temp_project / ".cursorrules").exists()
    assert original_rules in (temp_project / ".cursorrules").read_text()


# VS Code Adapter Tests


def test_vscode_detect(temp_project):
    """Test VS Code detection."""
    vscode_dir = temp_project / ".vscode"
    vscode_dir.mkdir()
    (vscode_dir / "AI_RULES.md").write_text("# Rules")

    adapter = VSCodeAdapter(temp_project)
    assert adapter.detect() is True


def test_vscode_import(temp_project, canonical_context, sample_rules, sample_context):
    """Test importing from VS Code."""
    vscode_dir = temp_project / ".vscode"
    vscode_dir.mkdir()
    (vscode_dir / "AI_RULES.md").write_text(sample_rules)
    (vscode_dir / "AI_CONTEXT.md").write_text(sample_context)

    adapter = VSCodeAdapter(temp_project)
    adapter.import_context(canonical_context.context_dir, force=False, dry_run=False)

    assert (canonical_context.context_dir / "rules.md").exists()
    assert (canonical_context.context_dir / "context.md").exists()


def test_vscode_export(temp_project, canonical_context, sample_rules):
    """Test exporting to VS Code."""
    (canonical_context.context_dir / "rules.md").write_text(sample_rules)

    adapter = VSCodeAdapter(temp_project)
    adapter.export_context(canonical_context.context_dir, force=False, dry_run=False)

    vscode_dir = temp_project / ".vscode"
    assert (vscode_dir / "AI_RULES.md").exists()


# Continue Adapter Tests


def test_continue_detect(temp_project):
    """Test Continue detection."""
    continue_dir = temp_project / ".continue"
    continue_dir.mkdir()
    (continue_dir / "config.json").write_text("{}")

    adapter = ContinueAdapter(temp_project)
    assert adapter.detect() is True


def test_continue_import(temp_project, canonical_context):
    """Test importing from Continue."""
    continue_dir = temp_project / ".continue"
    continue_dir.mkdir()

    config = {
        "projectPrompts": [
            {"name": "Test Prompt", "content": "This is a test prompt"},
            "Simple string prompt",
        ]
    }
    (continue_dir / "config.json").write_text(json.dumps(config))

    adapter = ContinueAdapter(temp_project)
    adapter.import_context(canonical_context.context_dir, force=False, dry_run=False)

    rules_file = canonical_context.context_dir / "rules.md"
    assert rules_file.exists()
    content = rules_file.read_text()
    assert "Test Prompt" in content
    assert "Simple string prompt" in content


def test_continue_export(temp_project, canonical_context, sample_rules):
    """Test exporting to Continue."""
    (canonical_context.context_dir / "rules.md").write_text(sample_rules)

    adapter = ContinueAdapter(temp_project)
    adapter.export_context(canonical_context.context_dir, force=False, dry_run=False)

    config_file = temp_project / ".continue" / "config.json"
    assert config_file.exists()

    config = json.loads(config_file.read_text())
    assert "projectPrompts" in config


# Claude Adapter Tests


def test_claude_detect(temp_project):
    """Test Claude detection."""
    claude_dir = temp_project / ".claude"
    claude_dir.mkdir()

    adapter = ClaudeAdapter(temp_project)
    assert adapter.detect() is True


def test_claude_export(temp_project, canonical_context, sample_rules):
    """Test exporting to Claude (generates import instructions)."""
    (canonical_context.context_dir / "rules.md").write_text(sample_rules)

    adapter = ClaudeAdapter(temp_project)
    adapter.export_context(canonical_context.context_dir, force=False, dry_run=False)

    import_file = canonical_context.context_dir / "CLAUDE_IMPORT.md"
    assert import_file.exists()

    content = import_file.read_text()
    assert "Claude Code Import Instructions" in content
    assert sample_rules in content


# Windsurf Adapter Tests


def test_windsurf_detect(temp_project):
    """Test Windsurf detection."""
    windsurf_dir = temp_project / ".windsurf"
    windsurf_dir.mkdir()
    (windsurf_dir / "config.yaml").write_text("ai_rules: test")

    adapter = WindsurfAdapter(temp_project)
    assert adapter.detect() is True


def test_windsurf_import(temp_project, canonical_context):
    """Test importing from Windsurf."""
    windsurf_dir = temp_project / ".windsurf"
    windsurf_dir.mkdir()

    config = {"ai_rules": "Test rules content", "ai_context": "Test context content"}
    (windsurf_dir / "config.yaml").write_text(yaml.dump(config))

    adapter = WindsurfAdapter(temp_project)
    adapter.import_context(canonical_context.context_dir, force=False, dry_run=False)

    assert (canonical_context.context_dir / "rules.md").exists()
    assert (canonical_context.context_dir / "context.md").exists()


def test_windsurf_export(temp_project, canonical_context, sample_rules):
    """Test exporting to Windsurf."""
    (canonical_context.context_dir / "rules.md").write_text(sample_rules)

    adapter = WindsurfAdapter(temp_project)
    adapter.export_context(canonical_context.context_dir, force=False, dry_run=False)

    config_file = temp_project / ".windsurf" / "config.yaml"
    assert config_file.exists()

    config = yaml.safe_load(config_file.read_text())
    assert "ai_rules" in config


# Dry-run Tests


def test_adapter_dry_run_import(temp_project, canonical_context):
    """Test dry-run mode for import."""
    (temp_project / ".cursorrules").write_text("# Rules")

    adapter = CursorAdapter(temp_project)
    adapter.import_context(canonical_context.context_dir, force=False, dry_run=True)

    # Canonical files should not be modified in dry-run
    rules_file = canonical_context.context_dir / "rules.md"
    original_content = rules_file.read_text()

    # Content should be unchanged (still the default template)
    assert "Define your AI assistant" in original_content


def test_adapter_dry_run_export(temp_project, canonical_context, sample_rules):
    """Test dry-run mode for export."""
    (canonical_context.context_dir / "rules.md").write_text(sample_rules)

    adapter = CursorAdapter(temp_project)
    adapter.export_context(canonical_context.context_dir, force=False, dry_run=True)

    # Cursor files should not be created in dry-run
    assert not (temp_project / ".cursorrules").exists()
