---
sidebar_position: 2
---

# Installation

Get mem8 installed and running on your system.

## Prerequisites

- **Python 3.12+** - mem8 is built with Python
- **uv** - Fast Python package installer (recommended)
- **Git** - For template cloning and version control

## Install with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is the fastest way to install mem8:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install mem8
uv tool install mem8
```

mem8 is now available in your PATH:

```bash
mem8 --version
mem8 --help
```

## Install from Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/killerapp/mem8.git
cd mem8

# Install in editable mode
uv tool install --editable .
```

## Verify Installation

Check that mem8 is installed correctly:

```bash
# Check version
mem8 --version

# View available commands
mem8 --help

# Run diagnostics
mem8 doctor
```

If your project template includes a `.mem8/toolbelt.json` file, `mem8 doctor` will also confirm that the declared core CLI tools are installed for your operating system and suggest installs for any missing recommendations.

## Optional: GitHub CLI

For GitHub integration features, install the GitHub CLI:

```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux
# See https://github.com/cli/cli#installation
```

Authenticate with GitHub:

```bash
gh auth login
```

## Optional: Docker (for Web Interface)

The web interface requires Docker:

- **Docker Desktop** - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** - Included with Docker Desktop

```bash
# Verify Docker installation
docker --version
docker-compose --version
```

## Update mem8

To update to the latest version:

```bash
# With uv
uv tool install mem8 --upgrade

# From source
cd mem8
git pull
uv tool install --editable . --force
```

## Uninstall

To remove mem8:

```bash
# With uv
uv tool uninstall mem8

# Cleanup config (optional)
rm -rf ~/.config/mem8
rm -rf ~/.local/share/mem8
```

## Next Steps

- **[Concepts](./concepts)** - Understand mem8's architecture
- **[User Guide](./user-guide/getting-started)** - Learn how to use mem8
- **[External Templates](./external-templates)** - Use custom templates

## Troubleshooting

### Command not found

If `mem8` command is not found after installation:

```bash
# Check if uv's bin directory is in PATH
echo $PATH | grep uv

# Add to PATH (bash/zsh)
export PATH="$HOME/.local/bin:$PATH"

# Add to PATH (fish)
fish_add_path ~/.local/bin
```

### Permission errors

On Unix systems, you may need to adjust permissions:

```bash
chmod +x ~/.local/bin/mem8
```

### Python version

Ensure you have Python 3.12 or higher:

```bash
python --version
# or
python3 --version
```

If you need to upgrade Python, use [pyenv](https://github.com/pyenv/pyenv) or your system's package manager.
