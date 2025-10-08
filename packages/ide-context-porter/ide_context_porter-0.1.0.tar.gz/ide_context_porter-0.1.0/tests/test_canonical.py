"""Tests for canonical context management."""

from ideporter.canonical import CanonicalContext


def test_canonical_init(temp_project):
    """Test canonical context initialization."""
    canonical = CanonicalContext(temp_project)
    assert not canonical.exists()

    canonical.initialize(dry_run=False)
    assert canonical.exists()

    # Check files were created
    assert (canonical.context_dir / "rules.md").exists()
    assert (canonical.context_dir / "context.md").exists()
    assert (canonical.context_dir / "ignore.txt").exists()
    assert (canonical.context_dir / "extensions.json").exists()
    assert (canonical.context_dir / "manifest.yaml").exists()


def test_canonical_init_dry_run(temp_project):
    """Test canonical context initialization in dry-run mode."""
    canonical = CanonicalContext(temp_project)
    canonical.initialize(dry_run=True)

    # Nothing should be created
    assert not canonical.exists()


def test_canonical_init_idempotent(temp_project):
    """Test that re-initializing is idempotent."""
    canonical = CanonicalContext(temp_project)
    canonical.initialize(dry_run=False)

    # Write custom content
    rules_file = canonical.context_dir / "rules.md"
    custom_content = "# My Custom Rules"
    rules_file.write_text(custom_content)

    # Re-initialize
    canonical.initialize(dry_run=False)

    # Custom content should be preserved
    assert rules_file.read_text() == custom_content


def test_canonical_validate_success(canonical_context):
    """Test validation of valid canonical context."""
    validation = canonical_context.validate()
    assert validation["valid"] is True
    assert len(validation["issues"]) == 0


def test_canonical_validate_missing_directory(temp_project):
    """Test validation when directory doesn't exist."""
    canonical = CanonicalContext(temp_project)
    validation = canonical.validate()

    assert validation["valid"] is False
    assert "does not exist" in validation["issues"][0]


def test_canonical_validate_missing_rules(canonical_context):
    """Test validation when rules.md is missing."""
    rules_file = canonical_context.context_dir / "rules.md"
    rules_file.unlink()

    validation = canonical_context.validate()
    assert validation["valid"] is False
    assert any("rules.md" in issue for issue in validation["issues"])


def test_canonical_validate_empty_rules(canonical_context):
    """Test validation when rules.md is empty."""
    rules_file = canonical_context.context_dir / "rules.md"
    rules_file.write_text("")

    validation = canonical_context.validate()
    assert validation["valid"] is True  # Empty is valid, but warns
    assert any("empty" in warning for warning in validation["warnings"])


def test_canonical_update_manifest(canonical_context):
    """Test manifest update with adapter usage."""
    canonical_context.update_manifest("cursor", dry_run=False, force=False)

    manifest_file = canonical_context.context_dir / "manifest.yaml"
    assert manifest_file.exists()

    import yaml

    manifest = yaml.safe_load(manifest_file.read_text())
    assert "cursor" in manifest["adapters_used"]
    assert "last_updated" in manifest


def test_canonical_get_rules(canonical_context, sample_rules):
    """Test getting rules content."""
    rules_file = canonical_context.context_dir / "rules.md"
    rules_file.write_text(sample_rules)

    rules = canonical_context.get_rules()
    assert rules == sample_rules


def test_canonical_get_context(canonical_context, sample_context):
    """Test getting context content."""
    context_file = canonical_context.context_dir / "context.md"
    context_file.write_text(sample_context)

    context = canonical_context.get_context()
    assert context == sample_context


def test_canonical_get_ignore_patterns(canonical_context):
    """Test getting ignore patterns."""
    ignore_file = canonical_context.context_dir / "ignore.txt"
    ignore_content = """# Comment
node_modules/
dist/
*.log

# Another comment
.env
"""
    ignore_file.write_text(ignore_content)

    patterns = canonical_context.get_ignore_patterns()
    assert "node_modules/" in patterns
    assert "dist/" in patterns
    assert "*.log" in patterns
    assert ".env" in patterns
    assert "# Comment" not in patterns


def test_canonical_get_extensions(canonical_context):
    """Test getting extension recommendations."""
    import json

    extensions_file = canonical_context.context_dir / "extensions.json"
    extensions_data = {"recommendations": ["ms-python.python", "ms-python.vscode-pylance"]}
    extensions_file.write_text(json.dumps(extensions_data))

    extensions = canonical_context.get_extensions()
    assert "ms-python.python" in extensions
    assert "ms-python.vscode-pylance" in extensions
