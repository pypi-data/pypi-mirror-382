"""Tests for CLI commands."""

import json

from typer.testing import CliRunner

from ideporter.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Check for key text that appears in help
    assert "import" in result.stdout.lower() or "export" in result.stdout.lower()


def test_detect_command(temp_project):
    """Test detect command."""
    # Create some IDE artifacts
    (temp_project / ".cursorrules").write_text("# Rules")

    result = runner.invoke(app, ["detect", str(temp_project)])
    assert result.exit_code == 0
    assert "cursor" in result.stdout.lower()


def test_detect_command_json(temp_project):
    """Test detect command with JSON output."""
    result = runner.invoke(
        app, ["detect", str(temp_project), "--json"], env={"NO_COLOR": "1", "TERM": "dumb"}
    )
    assert result.exit_code == 0

    # The output should be valid JSON - parse it directly
    # Rich console shouldn't interfere with JSON output
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        # If direct parsing fails, try cleaning the output
        import re

        # Remove ANSI escape codes
        clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
        # Remove box drawing and other unicode control chars
        clean_output = re.sub(r"[\u2500-\u257F]", "", clean_output)
        # Remove other control characters except newlines and tabs
        clean_output = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", clean_output)
        # Try to extract just the JSON object
        json_match = re.search(r"\{.*\}", clean_output, re.DOTALL)
        if json_match:
            clean_output = json_match.group(0)
        output = json.loads(clean_output)

    assert "detections" in output
    assert "project_path" in output


def test_init_command(temp_project):
    """Test init command."""
    result = runner.invoke(app, ["init", str(temp_project)])
    assert result.exit_code == 0

    # Check canonical structure was created
    canonical_dir = temp_project / "ai" / "context"
    assert canonical_dir.exists()
    assert (canonical_dir / "rules.md").exists()
    assert (canonical_dir / "manifest.yaml").exists()


def test_init_command_dry_run(temp_project):
    """Test init command with dry-run."""
    result = runner.invoke(app, ["init", str(temp_project), "--dry-run"])
    assert result.exit_code == 0

    # Nothing should be created
    canonical_dir = temp_project / "ai" / "context"
    assert not canonical_dir.exists()


def test_import_command(temp_project):
    """Test import command."""
    # Create Cursor files
    (temp_project / ".cursorrules").write_text("# Test Rules")

    result = runner.invoke(app, ["import", "--from", "cursor", "--path", str(temp_project)])
    assert result.exit_code == 0

    # Check canonical was created
    canonical_dir = temp_project / "ai" / "context"
    assert (canonical_dir / "rules.md").exists()


def test_import_command_invalid_ide(temp_project):
    """Test import command with invalid IDE."""
    result = runner.invoke(app, ["import", "--from", "invalid", "--path", str(temp_project)])
    assert result.exit_code == 1
    assert "Unknown adapter" in result.stdout


def test_export_command(temp_project):
    """Test export command."""
    # Initialize canonical context
    canonical_dir = temp_project / "ai" / "context"
    canonical_dir.mkdir(parents=True)
    (canonical_dir / "rules.md").write_text("# Test Rules")
    (canonical_dir / "manifest.yaml").write_text("version: '1.0'")

    result = runner.invoke(app, ["export", "--to", "cursor", "--path", str(temp_project)])
    assert result.exit_code == 0

    # Check Cursor files were created
    assert (temp_project / ".cursorrules").exists()


def test_export_command_no_canonical(temp_project):
    """Test export command without canonical context."""
    result = runner.invoke(app, ["export", "--to", "cursor", "--path", str(temp_project)])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_convert_command(temp_project):
    """Test convert command."""
    # Create Cursor files
    (temp_project / ".cursorrules").write_text("# Test Rules")

    result = runner.invoke(
        app, ["convert", "--from", "cursor", "--to", "vscode", "--path", str(temp_project)]
    )
    assert result.exit_code == 0

    # Check VS Code files were created
    vscode_dir = temp_project / ".vscode"
    assert (vscode_dir / "AI_RULES.md").exists()


def test_convert_command_dry_run(temp_project):
    """Test convert command with dry-run."""
    (temp_project / ".cursorrules").write_text("# Test Rules")

    result = runner.invoke(
        app,
        [
            "convert",
            "--from",
            "cursor",
            "--to",
            "vscode",
            "--path",
            str(temp_project),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0

    # VS Code files should not be created
    vscode_dir = temp_project / ".vscode"
    assert not vscode_dir.exists()


def test_validate_command(temp_project):
    """Test validate command."""
    # Create valid canonical context
    canonical_dir = temp_project / "ai" / "context"
    canonical_dir.mkdir(parents=True)
    (canonical_dir / "rules.md").write_text("# Test Rules")
    (canonical_dir / "manifest.yaml").write_text("version: '1.0'")

    result = runner.invoke(app, ["validate", str(temp_project)])
    assert result.exit_code == 0
    assert "passed" in result.stdout.lower()


def test_validate_command_json(temp_project):
    """Test validate command with JSON output."""
    # Create valid canonical context
    canonical_dir = temp_project / "ai" / "context"
    canonical_dir.mkdir(parents=True)
    (canonical_dir / "rules.md").write_text("# Test Rules")
    (canonical_dir / "manifest.yaml").write_text("version: '1.0'")

    result = runner.invoke(
        app, ["validate", str(temp_project), "--json"], env={"NO_COLOR": "1", "TERM": "dumb"}
    )
    assert result.exit_code == 0

    # Strip any ANSI codes and control characters, then parse JSON
    import re

    # Remove ANSI escape codes
    clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    # Remove other control characters except newlines and tabs
    clean_output = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", clean_output)
    # Strip whitespace
    clean_output = clean_output.strip()

    output = json.loads(clean_output)
    assert "valid" in output
    assert output["valid"] is True


def test_validate_command_invalid(temp_project):
    """Test validate command with invalid context."""
    # Create incomplete canonical context
    canonical_dir = temp_project / "ai" / "context"
    canonical_dir.mkdir(parents=True)
    # Missing rules.md

    result = runner.invoke(app, ["validate", str(temp_project)])
    assert result.exit_code == 1
    assert "failed" in result.stdout.lower()


def test_force_flag(temp_project):
    """Test --force flag prevents backups."""
    # Initialize canonical
    canonical_dir = temp_project / "ai" / "context"
    canonical_dir.mkdir(parents=True)
    (canonical_dir / "rules.md").write_text("# Original Rules")
    (canonical_dir / "manifest.yaml").write_text("version: '1.0'")

    # Export to cursor
    runner.invoke(app, ["export", "--to", "cursor", "--path", str(temp_project)])

    # Modify and re-export with force
    (canonical_dir / "rules.md").write_text("# Modified Rules")
    result = runner.invoke(
        app, ["export", "--to", "cursor", "--path", str(temp_project), "--force"]
    )

    assert result.exit_code == 0

    # Check no .bak files were created (force skips backups)
    bak_files = list(temp_project.glob("*.bak"))
    assert len(bak_files) == 0
