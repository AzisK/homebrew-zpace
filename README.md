# homebrew-zpace

A [Homebrew](https://brew.sh) tap for [Zpace](https://github.com/AzisK/Zpace) - a CLI tool to discover what's consuming your disk space.

## Installation

First, add this tap to Homebrew:

```bash
brew tap AzisK/zpace
```

Then install Zpace:

```bash
brew install zpace
```

Or install in one command:

```bash
brew install AzisK/zpace/zpace
```

## Usage

```bash
# Scan your home directory (default)
zpace

# Scan a specific directory
zpace /path/to/directory

# Show top 20 items per category
zpace -n 20

# Set minimum file size to 1MB
zpace -m 1024
```

## Update

```bash
brew upgrade zpace
```

## Uninstall

```bash
brew uninstall zpace
```

## Alternative Installation

Using [uv](https://github.com/astral-sh/uv) (faster):

```bash
uv tool install zpace
```

Or with pip:

```bash
pip install zpace
```

## About Zpace

Zpace is a CLI tool that helps you identify:
- 📊 Large files grouped by type (Documents, Videos, Code, Pictures, etc.)
- 📦 Space-hungry directories like node_modules, Python virtual environments, and build artifacts
- 🎯 Actionable insights to help you quickly free up space

For more information, visit the [Zpace repository](https://github.com/AzisK/Zpace).
