# Quickstart Guide: Huum Sauna CLI Manager

**Date**: 2025-10-08
**Feature**: 001-a-simple-cli
**Purpose**: Quick reference for developers implementing this feature

## Overview

This quickstart provides the essential information needed to begin implementing the Huum Sauna CLI Manager. It summarizes key decisions, project structure, and implementation order.

## Prerequisites

- Python 3.11+
- uv package manager installed
- Huum account with connected sauna devices
- Access to Huum API documentation (to be reviewed during implementation)

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | User requirement, modern features |
| **Package Manager** | uv | User requirement |
| **CLI Framework** | Typer | Type-safe, minimal boilerplate, built on Click |
| **HTTP Client** | httpx (sync) | Modern, type-safe, requests-compatible |
| **Credential Storage** | keyring | OS-native secure storage |
| **Retry Logic** | tenacity | Robust retry patterns for API calls |
| **Testing** | pytest | Standard Python testing framework |
| **Type Checking** | mypy | Static type checking |
| **Data Validation** | Pydantic | Type-safe data models |

## Project Setup

### 1. Initialize Project

```bash
# Create project structure
mkdir -p huum-cli
cd huum-cli
uv init

# Add dependencies
uv add typer httpx keyring tenacity pydantic rich

# Add development dependencies
uv add --dev pytest pytest-mock mypy ruff
```

### 2. Configure pyproject.toml

```toml
[project]
name = "huum-cli"
version = "0.1.0"
description = "CLI for managing Huum sauna devices"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "httpx>=0.25.0",
    "keyring>=25.0.0",
    "tenacity>=8.2.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0"
]

[project.scripts]
huum = "huum_cli.cli:app"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.12.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0"
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

### 3. Create Directory Structure

```bash
# Create source directories
mkdir -p src/huum_cli/{api,commands,utils}
touch src/huum_cli/{__init__.py,cli.py}
touch src/huum_cli/api/{__init__.py,client.py,models.py}
touch src/huum_cli/commands/{__init__.py,auth.py,start.py,stop.py,status.py,config.py}
touch src/huum_cli/utils/{__init__.py,storage.py,formatters.py}

# Create test directories
mkdir -p tests/{unit,integration,fixtures}
touch tests/unit/{test_api_client.py,test_commands.py,test_storage.py}
touch tests/integration/test_api_integration.py
touch tests/fixtures/mock_responses.py

# Create configuration
touch pyproject.toml README.md .gitignore
```

## Implementation Order

Follow this sequence for systematic, testable development:

### Phase 1: Foundation (Priority P1)

**Goal**: Establish authentication and basic infrastructure

1. **Data Models** (`src/huum_cli/api/models.py`)
   - Define Pydantic models for AuthCredentials, SaunaDevice, Session
   - Reference: [data-model.md](./data-model.md)

2. **Credential Storage** (`src/huum_cli/utils/storage.py`)
   - Implement keyring-based credential storage
   - Functions: `store_credentials()`, `get_credentials()`, `delete_credentials()`
   - Handle token expiration checking

3. **API Client** (`src/huum_cli/api/client.py`)
   - Create `HuumAPIClient` class wrapping httpx
   - Implement retry logic with tenacity
   - Methods: `authenticate()`, `refresh_token()`, `get_devices()`, `start_session()`, `stop_session()`, `get_status()`
   - Review Huum API documentation first

4. **Auth Command** (`src/huum_cli/commands/auth.py`)
   - Implement authentication flow
   - Interactive credential prompts
   - Store credentials via storage module
   - Verify by fetching device list

5. **CLI Entry Point** (`src/huum_cli/cli.py`)
   - Setup Typer app
   - Register auth command
   - Configure global options (--format, --verbose)

**Validation**: At this point, `huum auth` should work end-to-end

### Phase 2: Core Commands (Priority P1)

**Goal**: Implement start/stop functionality

6. **Status Command** (`src/huum_cli/commands/status.py`)
   - Fetch device status from API
   - Implement output formatters (human & JSON)
   - Handle single device and multiple devices display

7. **Output Formatters** (`src/huum_cli/utils/formatters.py`)
   - Human-readable formatting with Rich
   - JSON formatting
   - Progress bars, tables, status indicators

8. **Start Command** (`src/huum_cli/commands/start.py`)
   - Validate temperature range (40-110°C)
   - Auto-select device if only one exists
   - Send start request to API
   - Display confirmation

9. **Stop Command** (`src/huum_cli/commands/stop.py`)
   - Auto-select device if only one exists
   - Send stop request to API
   - Display session summary

**Validation**: Basic sauna control workflow should work: auth → status → start → status → stop

### Phase 3: Enhanced Features (Priority P2+)

**Goal**: Add convenience features and configuration

10. **List Command** (`src/huum_cli/commands/list.py`)
    - Display all devices
    - Show online/offline status

11. **Config Command** (`src/huum_cli/commands/config.py`)
    - Implement configuration file storage
    - Support get/set/reset operations
    - Store in platform-specific config directory

12. **Logout Command** (add to `commands/auth.py`)
    - Clear credentials from keyring
    - Confirmation prompt

### Phase 4: Polish

**Goal**: Improve user experience and robustness

13. **Error Handling**
    - Implement custom exception classes
    - User-friendly error messages
    - Proper exit codes

14. **Testing**
    - Unit tests for each module
    - Integration tests for API client
    - Mock Huum API responses

15. **Documentation**
    - README with installation and usage
    - Help text for all commands
    - API documentation comments

## Key Implementation Patterns

### 1. Command Structure (Typer)

```python
# src/huum_cli/commands/start.py
import typer
from typing import Optional

def start(
    device_id: Optional[str] = typer.Argument(None, help="Device ID to control"),
    temperature: int = typer.Option(85, "--temperature", "-t", help="Target temperature (40-110°C)")
) -> None:
    """Start sauna heating session"""
    # 1. Validate authentication
    credentials = get_credentials()
    if not credentials:
        typer.echo("Error: Not authenticated. Run 'huum auth' first.", err=True)
        raise typer.Exit(1)

    # 2. Validate temperature
    if not 40 <= temperature <= 110:
        typer.echo(f"Error: Temperature {temperature}°C outside safe range (40-110°C)", err=True)
        raise typer.Exit(1)

    # 3. Create API client
    client = HuumAPIClient(credentials)

    # 4. Auto-select device if needed
    if not device_id:
        devices = client.get_devices()
        if len(devices) == 0:
            typer.echo("Error: No devices found", err=True)
            raise typer.Exit(1)
        elif len(devices) > 1:
            typer.echo("Error: Multiple devices found. Specify device_id.", err=True)
            raise typer.Exit(1)
        device_id = devices[0].device_id

    # 5. Start session
    try:
        session = client.start_session(device_id, temperature)
        typer.echo(f"✓ Session started successfully")
        typer.echo(f"  Target: {temperature}°C")
    except DeviceOfflineError:
        typer.echo(f"Error: Device is offline", err=True)
        raise typer.Exit(2)
    except APIError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(2)
```

### 2. API Client with Retry Logic

```python
# src/huum_cli/api/client.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .models import SaunaDevice, Session, AuthCredentials

class HuumAPIClient:
    def __init__(self, session_token: str):
        self.session_token = session_token
        self.base_url = "https://sauna.huum.eu"
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=10.0
        )

    def _request(self, endpoint: str, **params) -> dict:
        """Make authenticated API request"""
        payload = {"session": self.session_token, **params}
        response = self.client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_status(self) -> list[SaunaDevice]:
        """Fetch all devices status"""
        data = self._request("/action/status")
        devices = []
        for device in data.get("devices", []):
            devices.append(SaunaDevice(
                device_id=device["id"],
                name=device["name"],
                online=device["status"]["online"],
                current_temperature=device["status"]["temperature"],
                target_temperature=device["status"].get("targetTemperature"),
                heating_state="heating" if device["status"]["heating"] else "idle",
                session_active=device["status"]["heating"],
                last_updated=datetime.now()
            ))
        return devices

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def start_session(self, device_id: str, temperature: int) -> dict:
        """Start heating session for device"""
        return self._request(
            "/action/start",
            device_id=device_id,
            target_temperature=temperature,
            duration=90
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()
```

### 3. Credential Storage

```python
# src/huum_cli/utils/storage.py
import keyring
import json
from datetime import datetime
from typing import Optional
from ..api.models import AuthCredentials

SERVICE_NAME = "huum-cli"
CREDENTIAL_KEY = "auth_data"

def store_credentials(credentials: AuthCredentials) -> None:
    """Store credentials securely in OS keyring"""
    data = credentials.model_dump_json()
    keyring.set_password(SERVICE_NAME, CREDENTIAL_KEY, data)

def get_credentials() -> Optional[AuthCredentials]:
    """Retrieve credentials from OS keyring"""
    data = keyring.get_password(SERVICE_NAME, CREDENTIAL_KEY)
    if not data:
        return None

    credentials = AuthCredentials.model_validate_json(data)

    # Check if expired
    if datetime.now() >= credentials.expires_at:
        # TODO: Implement token refresh
        return None

    return credentials

def delete_credentials() -> None:
    """Remove credentials from OS keyring"""
    try:
        keyring.delete_password(SERVICE_NAME, CREDENTIAL_KEY)
    except keyring.errors.PasswordDeleteError:
        pass  # Already deleted
```

### 4. Output Formatting

```python
# src/huum_cli/utils/formatters.py
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import json
from typing import Any
from ..api.models import SaunaDevice

console = Console()

def format_device_status_human(device: SaunaDevice) -> None:
    """Format device status for human-readable output"""
    console.print(f"\n[bold]{device.name}[/bold] ({device.device_id})")
    console.print("━" * 40)

    status_color = "green" if device.online else "red"
    console.print(f"Status:        [{status_color}]{'Online' if device.online else 'Offline'}[/{status_color}]")

    if device.session_active:
        console.print(f"Session:       Active")
        console.print(f"Current:       {device.current_temperature}°C")
        console.print(f"Target:        {device.target_temperature}°C")

        # Progress bar
        if device.target_temperature:
            progress = min(100, int((device.current_temperature / device.target_temperature) * 100))
            bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
            console.print(f"Progress:      [{bar}] {progress}%")
    else:
        console.print(f"Session:       Idle")
        console.print(f"Current:       {device.current_temperature}°C")

def format_json(data: Any) -> None:
    """Format data as JSON for machine-readable output"""
    print(json.dumps(data, indent=2, default=str))
```

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_storage.py
import pytest
from unittest.mock import patch, MagicMock
from huum_cli.utils.storage import store_credentials, get_credentials
from huum_cli.api.models import AuthCredentials
from datetime import datetime, timedelta

def test_store_credentials():
    """Test credential storage"""
    credentials = AuthCredentials(
        access_token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1)
    )

    with patch('keyring.set_password') as mock_set:
        store_credentials(credentials)
        mock_set.assert_called_once()

def test_get_credentials_expired():
    """Test expired credentials return None"""
    expired_creds = AuthCredentials(
        access_token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() - timedelta(hours=1)  # Expired
    )

    with patch('keyring.get_password', return_value=expired_creds.model_dump_json()):
        result = get_credentials()
        assert result is None
```

### Integration Tests

```python
# tests/integration/test_api_integration.py
import pytest
import httpx
from huum_cli.api.client import HuumAPIClient
from huum_cli.api.models import AuthCredentials
from datetime import datetime, timedelta

@pytest.fixture
def mock_credentials():
    return AuthCredentials(
        access_token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1)
    )

def test_get_devices_integration(mock_credentials, httpx_mock):
    """Test fetching devices with mocked API"""
    httpx_mock.add_response(
        url="https://api.huum.eu/devices",
        json={
            "devices": [
                {
                    "device_id": "test-123",
                    "name": "Test Sauna",
                    "online": True,
                    "current_temperature": 25,
                    "heating_state": "idle",
                    "session_active": False,
                    "last_updated": datetime.now().isoformat()
                }
            ]
        }
    )

    client = HuumAPIClient(mock_credentials)
    devices = client.get_devices()

    assert len(devices) == 1
    assert devices[0].name == "Test Sauna"
```

## Common Pitfalls to Avoid

1. **Don't hardcode API endpoints**: Review Huum API documentation first
2. **Handle token refresh**: Implement automatic refresh when tokens expire
3. **Validate before API calls**: Check temperature ranges, device IDs locally before hitting API
4. **Proper error handling**: Distinguish between validation errors (exit 1) and API errors (exit 2)
5. **Platform testing**: Test on Linux, macOS, Windows - keyring behaves differently
6. **Don't log tokens**: Never log access_token or refresh_token values

## Huum API Details

**Base URL**: `https://sauna.huum.eu`
**Authentication**: Session-based (POST with session token in request body)
**API Spec**: https://app.swaggerhub.com/apis-docs/info716/HUUM/1.2

Key endpoints:
- `POST /action/login` - Authenticate and get session token
- `POST /action/status` - Get device status
- `POST /action/start` - Start sauna session
- `POST /action/stop_sauna` - Stop sauna session

See [contracts/huum-api.md](./contracts/huum-api.md) for complete API integration details.

## Next Steps

1. **Review API Integration**: See [contracts/huum-api.md](./contracts/huum-api.md) for authentication flow, endpoints, and response formats
2. **Start with Phase 1**: Implement foundation components in order
3. **Test as you go**: Write tests alongside implementation
4. **Refer to design docs**: See [data-model.md](./data-model.md) for entity details, [cli-commands.md](./contracts/cli-commands.md) for command specifications

## References

- **Specification**: [spec.md](./spec.md) - Feature requirements and user scenarios
- **Research**: [research.md](./research.md) - Technology choices and rationale
- **Data Model**: [data-model.md](./data-model.md) - Entity definitions and validation rules
- **CLI Contracts**: [contracts/cli-commands.md](./contracts/cli-commands.md) - Complete command specifications
- **Implementation Plan**: [plan.md](./plan.md) - Overall project plan and structure

## Quick Commands Reference

```bash
# Setup
uv init && uv add typer httpx keyring tenacity pydantic rich
uv add --dev pytest pytest-mock mypy ruff

# Development
uv run huum auth
uv run huum status
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```
