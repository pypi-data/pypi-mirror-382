# Huum Sauna CLI

A command-line interface for managing Huum sauna devices remotely.

## Features

- 🔐 **Secure Authentication** - Store credentials safely in OS keyring
- 🔥 **Start Sessions** - Remotely start your sauna heating
- ⏹️  **Stop Sessions** - Turn off your sauna from the command line
- 📊 **Status Display** - View current and target temperatures with Rich formatting
- 🌡️  **Custom Temperatures** - Set target temperature (40-110°C)
- 🎯 **Auto-device Selection** - Automatically selects device if you have only one
- ⚡ **Fast & Reliable** - Automatic retries with exponential backoff

## Installation

Requires Python 3.11 or higher.

```bash
pip install huum-cli
```

Or with `uv`:

```bash
uv tool install huum-cli
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/tomdyson/huum-cli
cd huum-cli

# Install dependencies
uv sync

# Install the CLI in editable mode
uv pip install -e .
```

## Quick Start

### 1. Authenticate

```bash
huum auth login
```

You'll be prompted for your Huum account credentials. Your session will be stored securely in your system keyring.

### 2. Start Your Sauna

```bash
# Start with default temperature (85°C)
huum start

# Start with custom temperature
huum start --temperature 75
```

### 3. Stop Your Sauna

```bash
huum stop
```

## Commands

### Authentication

```bash
# Log in
huum auth login

# Log in with credentials
huum auth login --username user@example.com --password mypass

# Log out
huum auth logout
```

### Sauna Control

```bash
# Check status
huum status

# Start sauna
huum start [DEVICE_ID] [--temperature 85]

# Stop sauna
huum stop [DEVICE_ID]
```

### Device Management

If you have multiple devices, specify the device ID:

```bash
huum start my-sauna-id --temperature 80
huum stop my-sauna-id
```

## Configuration

Credentials are stored securely using your operating system's keyring:
- **macOS**: Keychain
- **Windows**: Windows Credential Manager
- **Linux**: GNOME Keyring/KWallet

## API

This CLI uses the Huum API (v1.2) at `https://sauna.huum.eu`.

See the [API documentation](https://app.swaggerhub.com/apis-docs/info716/HUUM/1.2) for more details.

## Development

Built with:
- **Typer** - CLI framework
- **httpx** - HTTP client
- **Pydantic** - Data validation
- **Rich** - Terminal formatting
- **keyring** - Secure credential storage

## License

MIT
