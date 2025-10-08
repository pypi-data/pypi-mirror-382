# IDE Context Porter

**Move your project's AI prompts and context between IDEs safely and reproducibly.**

[![CI](https://github.com/djmorgan26/IDE-Context-Converter/workflows/CI/badge.svg)](https://github.com/djmorgan26/IDE-Context-Converter/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

IDE Context Porter is a universal CLI tool that imports, exports, and converts AI project instructions ("context") between different IDEs and AI coding environments. It enables seamless migration of your project prompts and rules between tools like:

- **Cursor** (`.cursorrules`, `.cursorignore`)
- **VS Code** (`.vscode/AI_RULES.md`, `.vscode/AI_CONTEXT.md`)
- **Continue.dev** (`.continue/config.json`)
- **Claude Code** (manual import via generated instructions)
- **Windsurf** (`.windsurf/config.yaml`)
- **Future IDEs** (extensible adapter system)

## 🚀 Quick Start

### Installation

```bash
# Using pipx (recommended)
pipx install ide-context-porter

# Using pip
pip install ide-context-porter

# From source
git clone https://github.com/djmorgan26/IDE-Context-Converter.git
cd IDE-Context-Converter
pip install -e .
```

### Basic Usage

```bash
# Initialize canonical context structure
ide-context-porter init

# Import from Cursor to canonical format
ide-context-porter import --from cursor

# Export to VS Code
ide-context-porter export --to vscode

# Convert directly from Cursor to VS Code
ide-context-porter convert --from cursor --to vscode

# Detect which IDEs are present
ide-context-porter detect

# Validate your canonical context
ide-context-porter validate
```

## 📁 Canonical Folder Structure

IDE Context Porter maintains a single source of truth in your project:

```
ai/context/
├── rules.md              # Main AI project prompts/instructions
├── context.md            # Optional architectural/domain notes
├── ignore.txt            # Glob-like ignore patterns for noisy files
├── extensions.json       # Optional list of recommended IDE extensions
└── manifest.yaml         # Metadata (version, last_updated, adapters used)
```

This canonical structure is the authoritative representation of your project's AI context.

## 🧩 Supported IDEs

| IDE / Tool | File Formats | Import | Export | Notes |
|------------|--------------|--------|--------|-------|
| **Cursor** | `.cursorrules`, `.cursorignore` | ✅ | ✅ | Full bidirectional support |
| **VS Code** | `.vscode/AI_RULES.md`, `.vscode/AI_CONTEXT.md` | ✅ | ✅ | Safe augmentation of settings |
| **Continue** | `.continue/config.json` | ✅ | ✅ | Adds projectPrompts entry |
| **Claude Code** | `.claude/` | ⚠️ | ✅ | Generates `CLAUDE_IMPORT.md` for manual paste |
| **Windsurf** | `.windsurf/config.yaml` | ✅ | ✅ | AI rule mappings |

## 📖 Detailed Usage

### Initialize a New Project

```bash
# Create canonical structure in current directory
ide-context-porter init

# Create in specific directory
ide-context-porter init /path/to/project
```

This creates the `ai/context/` directory with starter templates.

### Import from IDE

```bash
# Import from Cursor
ide-context-porter import --from cursor

# Import with custom path
ide-context-porter import --from vscode --path /path/to/project

# Preview without making changes
ide-context-porter import --from cursor --dry-run

# Force overwrite without backups
ide-context-porter import --from cursor --force
```

### Export to IDE

```bash
# Export to VS Code
ide-context-porter export --to vscode

# Export to multiple IDEs
ide-context-porter export --to cursor
ide-context-porter export --to vscode
ide-context-porter export --to continue

# Preview changes
ide-context-porter export --to cursor --dry-run
```

### Convert Between IDEs

```bash
# One-step conversion
ide-context-porter convert --from cursor --to vscode

# With options
ide-context-porter convert --from cursor --to windsurf --path . --dry-run
```

### Detect IDE Artifacts

```bash
# Detect in current directory
ide-context-porter detect

# JSON output for scripting
ide-context-porter detect --json
```

Output:
```json
{
  "project_path": "/path/to/project",
  "detections": {
    "cursor": true,
    "vscode": true,
    "continue": false,
    "claude": false,
    "windsurf": false
  }
}
```

### Validate Canonical Context

```bash
# Validate current project
ide-context-porter validate

# Validate specific project
ide-context-porter validate /path/to/project

# JSON output
ide-context-porter validate --json
```

## 🛡️ Safety Features

### Non-Destructive by Default

- **Automatic Backups**: Creates timestamped `.bak` files before overwriting
- **Dry-Run Mode**: Preview all operations with `--dry-run`
- **Force Mode**: Skip backups with `--force` (use with caution)

### Security

- **Ignores Sensitive Files**: Never touches `.env`, `.git`, credentials, etc.
- **Offline-First**: No network calls or telemetry
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Idempotent Operations

Re-running commands without changes is a no-op. Safe to run multiple times.

## 🔧 Global Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview operations without making changes |
| `--force` | Overwrite existing files, skip backups |
| `--json` | Output structured JSON (for `detect` and `validate`) |
| `--path PATH` | Specify project path (defaults to current directory) |

## 📝 Examples

### Scenario 1: Migrating from Cursor to VS Code

```bash
# You have .cursorrules in your project
cd my-project

# Convert to VS Code format
ide-context-porter convert --from cursor --to vscode

# Result: .vscode/AI_RULES.md created with your rules
```

### Scenario 2: Centralizing AI Context

```bash
# You have rules scattered across different IDE configs
cd my-project

# Import from current IDE
ide-context-porter import --from cursor

# Now edit the canonical version
vim ai/context/rules.md

# Export to all your IDEs
ide-context-porter export --to cursor
ide-context-porter export --to vscode
ide-context-porter export --to continue
```

### Scenario 3: Team Collaboration

```bash
# Commit ai/context/ to version control
git add ai/context/
git commit -m "Add canonical AI context"

# Team members can export to their preferred IDE
ide-context-porter export --to cursor  # Alice uses Cursor
ide-context-porter export --to vscode  # Bob uses VS Code
```

## 🧪 Development

### Setup

```bash
# Clone repository
git clone https://github.com/djmorgan26/IDE-Context-Converter.git
cd IDE-Context-Converter

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ideporter

# Run specific test file
pytest tests/test_adapters.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Run all checks
make test lint
```

## 🏗️ Architecture

### Adapter System

Each IDE has its own adapter implementing the `BaseAdapter` interface:

```python
class BaseAdapter(ABC):
    @abstractmethod
    def detect(self) -> bool:
        """Detect if IDE artifacts exist"""
        
    @abstractmethod
    def import_context(self, canonical_dir: Path, force: bool, dry_run: bool) -> None:
        """Import from IDE to canonical format"""
        
    @abstractmethod
    def export_context(self, canonical_dir: Path, force: bool, dry_run: bool) -> None:
        """Export from canonical to IDE format"""
```

### Adding New Adapters

1. Create `ideporter/adapters/your_ide.py`
2. Implement `BaseAdapter` interface
3. Register in `ideporter/adapters/__init__.py`
4. Add tests in `tests/test_adapters.py`

## ⚠️ Known Limitations

### Claude Code

Claude uses an opaque internal format. The tool generates `CLAUDE_IMPORT.md` with instructions for manual import. Full automation is not currently possible.

### Windsurf

Support is based on assumed configuration format. May need updates as Windsurf evolves.

## 🗺️ Roadmap

- [ ] Plugin discovery system for community adapters
- [ ] Support for Zed, Aider, Sourcegraph Cody
- [ ] JSON Schema validation for `manifest.yaml`
- [ ] Local caching of adapter metadata
- [ ] Web UI for visual context management
- [ ] Git hooks for automatic sync
- [ ] Template library for common project types

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run `make test lint` to verify
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- Inspired by the need for portable AI context across IDEs
- Thanks to all contributors and early adopters

## 📬 Support

- **Issues**: [GitHub Issues](https://github.com/djmorgan26/IDE-Context-Converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/djmorgan26/IDE-Context-Converter/discussions)

---

**Made with ❤️ for the AI-assisted development community**