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

## Maintaining the Formula

When a new version of zpace is released, a `repository_dispatch` event triggers the [Update Formula](../../actions/workflows/update-formula.yml) workflow automatically. It can also be triggered manually from the Actions tab with an optional version number.

The workflow:
1. Updates the zpace `url` and `sha256` in the formula
2. Installs zpace into a clean virtualenv with `uv` and resolves all dependencies
3. Fetches each dependency's sdist URL and sha256 from the PyPI JSON API
4. Rewrites the resource blocks in the formula
5. Smoke-tests the PyPI package with `uvx "zpace==<version>" --help`
6. Commits and pushes the result (or prints the current formula if already up to date)

### Locally

Requires [`uv`](https://github.com/astral-sh/uv), `curl`, and `jq`.

```bash
# Update to the latest version on PyPI
./scripts/update-formula.sh

# Update to a specific version
./scripts/update-formula.sh 0.6.0
```

The script updates the formula in place and prints the diff for review. Commit the result when satisfied.
