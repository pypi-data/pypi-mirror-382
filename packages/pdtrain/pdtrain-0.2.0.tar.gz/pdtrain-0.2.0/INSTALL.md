# Installation Guide

## Install from Source (Development)

```bash
git clone https://github.com/pipedream/pdtrain
cd pdtrain


# Install in development mode
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"

# Verify installation
pdtrain --version
```

## Install from PyPI (Future)

```bash
pip install pdtrain
```

## First Time Setup

```bash
# Configure API credentials
pdtrain configure

# You'll be prompted for:
# - API URL: http://localhost:8000 (or your production URL)
# - API Key: sdk_xxxxx (from Pipedream dashboard)

# Verify configuration
pdtrain info
```

## Test the CLI

```bash
# List bundles (should work if API is running)
pdtrain bundle list

# Check quota
pdtrain quota
```

## Requirements

- Python 3.8+
- Pipedream Orchestrator API running and accessible
- Valid API key

## Troubleshooting

### "Command not found: pdtrain"

Make sure the installation directory is in your PATH:
```bash
export PATH="$PATH:$HOME/.local/bin"
```

Or reinstall with:
```bash
pip install --user -e .
```

### "CLI not configured"

Run the configuration wizard:
```bash
pdtrain configure
```

### "Connection refused"

Make sure the Orchestrator API is running:
```bash
# Check if API is accessible
curl http://localhost:8000/health
```

## Uninstall

```bash
pip uninstall pdtrain
```
