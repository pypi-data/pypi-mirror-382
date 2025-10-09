# Research: Huum Sauna CLI Manager

**Date**: 2025-10-08
**Feature**: 001-a-simple-cli
**Purpose**: Resolve technical unknowns and establish technology choices for Python CLI implementation

## Overview

This document consolidates research findings for building a Python-based CLI application using uv as the package manager. Three key areas required clarification: CLI framework selection, HTTP client library, and secure credential storage approach.

## 1. CLI Framework Selection

### Decision: Typer

Use Typer for building the Huum Sauna CLI application with 6 primary commands (auth, start, stop, status, list, config).

### Rationale

1. **Type Safety**: Typer leverages Python type hints (Python 3.6+) to provide automatic parameter validation, better IDE support, and catches errors at development time rather than runtime
2. **Minimal Boilerplate**: Requires less code than alternatives - define commands as regular Python functions with type annotations, and Typer handles argument parsing and validation automatically
3. **Easiest Learning Curve**: Most beginner-friendly option, significantly easier than Click and much easier than argparse
4. **Built on Click**: Built on top of Click, providing all of Click's battle-tested functionality with a more modern interface
5. **Rich Output Support**: Comes with Rich library integration for beautiful terminal output with colors, tables, and progress bars - perfect for displaying sauna status information
6. **Perfect uv Integration**: Seamlessly integrates with uv package manager via `uv add typer` and pyproject.toml entry points
7. **Excellent Documentation**: Comprehensive documentation at typer.tiangolo.com with active community support

### Alternatives Considered

- **argparse (Standard Library)**: Most verbose syntax, steepest learning curve, no type safety. Rejected due to excessive boilerplate for a 6-command CLI
- **Click**: Widely adopted, decorator-based, but requires more boilerplate than Typer and lacks native type hint support. Since Typer is built on Click, using Typer provides the same underlying functionality with better developer experience

### Implementation Notes

```toml
# pyproject.toml
[project.scripts]
huum = "huum_cli.cli:app"
```

```python
# Basic Typer pattern
import typer
app = typer.Typer()

@app.command()
def start(device_id: str, temperature: int = 80):
    """Start sauna heating session"""
    # Implementation
```

## 2. HTTP Client Library

### Decision: httpx (synchronous mode)

Use httpx in synchronous mode for making REST API calls to the Huum API.

### Rationale

1. **Dual Sync/Async Support**: Supports both synchronous and asynchronous patterns - start with synchronous mode for simplicity with option to add async later without changing libraries
2. **Modern & Type-Safe**: Fully type-annotated, providing better IDE support and type checking with mypy, complementing the type-safe CLI built with Typer
3. **HTTP/2 Support**: Unlike requests, httpx supports HTTP/2, improving performance when making multiple requests to the same API endpoint
4. **Better Defaults**: Has strict timeouts everywhere (no default timeouts in requests), crucial for CLI responsiveness and meeting spec's <10 second response requirement
5. **Connection Pooling**: httpx.Client() provides connection pooling for better performance with multiple API calls
6. **Requests-Compatible API**: Provides a broadly requests-compatible API, familiar for Python developers while offering modern improvements
7. **Built-in Retry Support**: Has built-in connection retry for ConnectError and ConnectTimeout; integrates well with tenacity library for other retry scenarios

### Alternatives Considered

- **requests**: Most battle-tested (established 2011), extensive community support, but synchronous only, no HTTP/2 support, no timeouts by default, not type-annotated, no async migration path. While more mature, httpx offers better future-proofing
- **aiohttp**: Best for high-concurrency async operations, but async-only with no sync support. Rejected as overkill for CLI where commands run sequentially - async complexity adds no value when user runs commands and waits for responses

### Implementation Recommendations

1. Create a dedicated API client class wrapping httpx.Client for connection reuse
2. Use tenacity library for retry logic on network errors and API rate limits
3. Implement proper timeout handling (connect timeout + read timeout) for all requests
4. Handle common HTTP errors explicitly: 401 (auth), 429 (rate limit), 503 (service unavailable)

```python
# Basic httpx pattern with retry
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_sauna_status(client: httpx.Client, device_id: str):
    response = client.get(f"/devices/{device_id}/status", timeout=5.0)
    response.raise_for_status()
    return response.json()
```

## 3. Credential Storage

### Decision: keyring library for OS-native credential storage

Use the keyring library for storing authentication tokens with OS-native credential stores.

### Rationale

1. **Cross-Platform Security**: Provides consistent API across platforms while using native secure storage:
   - **macOS**: Keychain (requires Python 3.8.7+ for macOS 11+)
   - **Windows**: Windows Credential Manager (encrypted with user's logon credentials)
   - **Linux**: GNOME Keyring/KWallet (via SecretStorage/dbus)
2. **No Custom Encryption Required**: Abstracts away encryption complexity - OS handles secure storage, key management, and access control
3. **Simple API**: Minimal code to store and retrieve credentials
4. **CLI Support**: Includes command-line interface for manual credential management
5. **Minimal Dependencies**: Has minimal dependencies and integrates well with uv projects
6. **Active Maintenance**: Actively maintained (version 25.6.1+ as of 2025)

### Platform-Specific Considerations

1. **Linux Headless Servers**: On headless Linux without GNOME Keyring, keyring falls back to encrypted file storage. For production Linux servers:
   - Consider installing SecretStorage backend explicitly
   - Use keyrings.cryptfile (encrypted file backend) as fallback
   - Document this limitation for users

2. **Linux Desktop**: For KDE/GNOME environments, install dbus-python as system package:
   ```bash
   sudo apt-get install python3-dbus  # Debian/Ubuntu
   ```

3. **macOS/Windows**: Work out-of-box with no additional configuration

### Token Refresh and Expiration Handling

keyring doesn't track token expiration - implement at application level:

1. **Store Token Metadata**: Store expiration time alongside the token
2. **Check Expiration Before API Calls**: Implement decorator/wrapper to check token validity
3. **Handle 401 Responses**: Catch HTTP 401 errors and trigger automatic token refresh
4. **Proactive Refresh**: Refresh tokens before expiration (e.g., at 50 minutes for 1-hour tokens)
5. **Secure Token Rotation**: Immediately invalidate old tokens when refreshing if API supports it

### Best Practices

1. Use unique service name ("huum-cli") to avoid conflicts
2. Store only authentication tokens in keyring, not other configuration
3. Handle missing credentials gracefully with helpful error messages
4. Provide logout/clear command to remove stored credentials
5. Document Linux backend requirements in README

### Alternatives Considered

- **Encrypted Config Files (keyrings.cryptfile)**: Requires user to provide encryption password, less secure than OS keychains. Only suitable as fallback for headless Linux servers
- **Environment Variables (.env files)**: Tokens stored in plaintext, easily exposed. Acceptable for non-sensitive config but not credentials
- **Plain Config Files (JSON/TOML)**: Fundamentally insecure - never store authentication tokens in plaintext
- **Custom Encryption (cryptography library)**: Requires implementing secure key management, prone to errors. "Don't roll your own crypto"

```python
# Basic keyring pattern
import keyring
import json
from datetime import datetime, timedelta

# Store token with metadata
token_data = {
    "access_token": "...",
    "refresh_token": "...",
    "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
}
keyring.set_password("huum-cli", "auth_data", json.dumps(token_data))

# Retrieve token
token_json = keyring.get_password("huum-cli", "auth_data")
if token_json is None:
    print("Error: Not authenticated. Run 'huum auth' first.")
    sys.exit(1)
token_data = json.loads(token_json)
```

## Summary of Technology Choices

| Decision Area | Recommendation | Key Reason |
|--------------|----------------|------------|
| CLI Framework | Typer | Type-safe, minimal boilerplate, easiest learning curve |
| HTTP Client | httpx (sync) | Modern features, type-safe, requests-compatible |
| Credential Storage | keyring | OS-native security, cross-platform, simple API |

## Installation Commands

```bash
# Add dependencies
uv add typer httpx keyring tenacity

# Add development dependencies
uv add --dev pytest pytest-mock
```

## Dependencies Added to Technical Context

- **CLI Framework**: Typer (type-safe, built on Click)
- **HTTP Client**: httpx in synchronous mode
- **Credential Storage**: keyring library
- **Retry Logic**: tenacity library
- **Terminal Output**: Rich (included with Typer)

## Huum API Authentication (Updated)

**API Documentation**: https://app.swaggerhub.com/apis-docs/info716/HUUM/1.2
**Base URL**: `https://sauna.huum.eu`
**Authentication Method**: Session-based (not OAuth2 or Bearer tokens)

The Huum API uses session-based authentication:
1. POST credentials to `/action/login` → receive session token
2. Include session token in request body for all authenticated endpoints
3. Session tokens don't expire explicitly - validate via `/action/loginwithsession`

**Storage Impact**: Store session token (not JWT) with user_id and email in keyring. Track creation time for age-based revalidation.

See [contracts/huum-api.md](./contracts/huum-api.md) for complete API integration details.

## Next Steps for Implementation

1. ✅ Review Huum API Documentation (completed - session-based auth confirmed)
2. Create API Client Wrapper: Build HuumAPIClient class wrapping httpx with retry logic
3. Implement Auth Command First to establish credential storage patterns
4. Add Status Command Next to test full flow (retrieve credentials → API call → display)
5. Build Remaining Commands (start, stop, list, config) using established patterns

## References

- Typer Documentation: https://typer.tiangolo.com
- httpx Documentation: https://www.python-httpx.org
- keyring Documentation: https://github.com/jaraco/keyring
- tenacity Documentation: https://tenacity.readthedocs.io
