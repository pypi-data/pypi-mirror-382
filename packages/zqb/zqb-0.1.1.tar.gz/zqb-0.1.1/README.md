# ZQB - Quick Script Runner

A simple command-line utility for quickly running scripts across your system. ZQB automatically discovers and registers scripts from configured directories, making them accessible from anywhere via a unified CLI interface.

## Features

- 🚀 **Quick Script Execution**: Run any registered script with `zqb <script-name>`
- 📁 **Directory Management**: Add/remove directories containing your scripts
- 🔍 **Auto-Discovery**: Automatically finds Python (.py), PowerShell (.ps1), and Bash (.sh, .bash) scripts
- 🏗️ **Hierarchical Organization**: Maintains folder structure as command groups
- 🐚 **Interactive Shell**: Built-in shell mode for continuous script execution
- 🔐 **Secure Storage**: Uses system keyring for storing configuration

## Installation

Install using pip:

```bash
pip install .
```

Or using uv (recommended):

```bash
uv sync
```

## Quick Start

1. **Add a script directory**:
   ```bash
   zqb zqb_config add /path/to/your/scripts
   ```

2. **List configured directories**:
   ```bash
   zqb zqb_config list
   ```

3. **Run ZQB to see available commands**:
   ```bash
   zqb
   ```

4. **Use the interactive shell**:
   ```bash
   zqb zqb_shell
   ```

## Usage Examples

### Basic Commands

```bash
# Show help and available commands
zqb

# Enable debug mode
zqb --debug

# Enter interactive shell
zqb zqb_shell
```

### Configuration Management

```bash
# Add a directory containing scripts
zqb zqb_config add ~/my-scripts

# Add multiple directories
zqb zqb_config add /opt/company-scripts
zqb zqb_config add ~/personal-automation

# List all configured paths
zqb zqb_config list

# Remove a directory
zqb zqb_config remove ~/old-scripts
```

### Script Organization

ZQB respects your directory structure and creates command groups accordingly:

```
~/scripts/
├── database/
│   ├── backup.py
│   └── restore.sh
├── deployment/
│   ├── deploy.ps1
│   └── rollback.py
└── utils.py
```

This structure becomes:

```bash
zqb database backup    # Runs ~/scripts/database/backup.py
zqb database restore   # Runs ~/scripts/database/restore.sh
zqb deployment deploy  # Runs ~/scripts/deployment/deploy.ps1
zqb deployment rollback # Runs ~/scripts/deployment/rollback.py
zqb utils              # Runs ~/scripts/utils.py
```

### Interactive Shell

The interactive shell allows you to run commands without typing `zqb` each time:

```bash
$ zqb zqb_shell
Starting shell...
zqb> database backup --help
zqb> deployment deploy production
zqb> exit
```

## Supported Script Types

- **Python** (`.py`): Executed with the system Python interpreter
- **PowerShell** (`.ps1`): Executed with PowerShell (Windows)
- **Bash** (`.sh`, `.bash`): Executed with Bash shell (Linux/macOS/WSL)

## Configuration Storage

ZQB uses the system keyring to securely store configuration data. The configured paths are stored under:
- **Service**: `ZQB_PY_CONFIG`
- **Username**: Current system user

## Development

### Project Structure

```
src/zqb/
├── __init__.py          # Main module initialization
├── cli.py               # CLI command definitions and main entry point
├── cli_config.py        # Configuration management commands
└── utils.py             # Utility functions for script discovery and execution
```

### Building from Source

1. Clone the repository
2. Install dependencies: `uv sync`
3. Install in development mode: `uv pip install -e .`

### Dependencies

- **click**: Command-line interface creation
- **click-shell**: Interactive shell functionality  
- **keyring**: Secure credential storage

## Troubleshooting

### Common Issues

**Shell command fails with AssertionError**:
- Make sure you're using the latest version
- This was fixed in recent versions - try reinstalling

**Scripts not found**:
- Check that the directory is properly added with `zqb zqb_config list`
- Ensure script files have proper extensions (.py, .ps1, .sh, .bash)
- Use `zqb --debug` to see discovery process

**Permission denied**:
- Ensure script files are executable (`chmod +x script.sh` on Unix systems)
- Check that you have permission to access the configured directories

