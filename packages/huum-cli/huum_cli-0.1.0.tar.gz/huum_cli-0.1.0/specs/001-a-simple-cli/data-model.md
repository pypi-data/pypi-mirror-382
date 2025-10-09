# Data Model: Huum Sauna CLI Manager

**Date**: 2025-10-08
**Feature**: 001-a-simple-cli
**Purpose**: Define data entities, their attributes, relationships, and validation rules

## Overview

This document defines the core data entities for the Huum Sauna CLI application. These entities represent the domain model derived from the feature specification and will be used to structure API responses, internal state, and data validation.

## Core Entities

### 1. SaunaDevice

Represents a physical Huum sauna unit connected to the user's account.

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `device_id` | string | Yes | Unique identifier for the sauna device | Non-empty string, immutable |
| `name` | string | Yes | User-friendly device name | Non-empty string, max 100 characters |
| `online` | boolean | Yes | Whether device is reachable | true/false |
| `current_temperature` | integer | Yes | Current temperature in Celsius | 0-120°C |
| `target_temperature` | integer | No | Target temperature if session active | 40-110°C (safe operating range) |
| `heating_state` | string | Yes | Current heating status | One of: "idle", "heating", "ready", "stopped" |
| `session_active` | boolean | Yes | Whether heating session is active | true/false |
| `last_updated` | datetime | Yes | Timestamp of last status update | ISO 8601 format |

**Relationships**:
- One user account can have multiple SaunaDevice entities (1:N)
- One SaunaDevice can have zero or one active Session (1:0..1)

**State Transitions**:

```
idle → heating (when start command issued)
heating → ready (when target temperature reached)
ready → stopped (when stop command issued)
stopped → idle (automatic transition after cooldown)
heating → stopped (when stop command issued during heating)
```

**Validation Rules**:
- `current_temperature` must be >= 0 and <= 120°C
- `target_temperature`, if present, must be >= 40°C and <= 110°C (safe operating range per spec FR-008)
- `heating_state` must be one of the defined enum values
- `online` must be true for any control commands (start/stop) to succeed
- `device_id` is immutable after creation

**Example**:

```json
{
  "device_id": "huum-abc123",
  "name": "Home Sauna",
  "online": true,
  "current_temperature": 75,
  "target_temperature": 85,
  "heating_state": "heating",
  "session_active": true,
  "last_updated": "2025-10-08T14:32:10Z"
}
```

---

### 2. Session

Represents an active sauna heating session.

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `session_id` | string | Yes | Unique session identifier | Non-empty string, immutable |
| `device_id` | string | Yes | Associated sauna device | Must reference existing SaunaDevice |
| `start_time` | datetime | Yes | When session was initiated | ISO 8601 format, cannot be future |
| `end_time` | datetime | No | When session ended (if completed) | ISO 8601 format, must be after start_time |
| `target_temperature` | integer | Yes | Desired temperature for session | 40-110°C |
| `state` | string | Yes | Current session state | One of: "active", "completed", "cancelled" |
| `duration_minutes` | integer | No | Total session duration | 0-360 minutes (max 6 hours) |

**Relationships**:
- Each Session is associated with exactly one SaunaDevice (N:1)
- Each SaunaDevice can have at most one active Session at a time

**State Transitions**:

```
active → completed (normal session end via stop command)
active → cancelled (abnormal end, e.g., device offline)
```

**Validation Rules**:
- `target_temperature` must be within safe operating range (40-110°C)
- `end_time`, if present, must be after `start_time`
- `duration_minutes` calculated as `end_time - start_time` in minutes
- Cannot create new session if device already has active session
- `session_id` is immutable after creation

**Example**:

```json
{
  "session_id": "session-xyz789",
  "device_id": "huum-abc123",
  "start_time": "2025-10-08T14:00:00Z",
  "end_time": null,
  "target_temperature": 85,
  "state": "active",
  "duration_minutes": null
}
```

---

### 3. AuthCredentials

Represents authentication information for accessing the Huum API.

**Note**: Huum API uses session-based authentication, not Bearer tokens.

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| `session` | string | Yes | Session token for API authentication | Non-empty string, sensitive |
| `user_id` | string | Yes | Huum account user identifier | Non-empty string |
| `email` | string | Yes | User email address | Non-empty string, valid email format |
| `created_at` | datetime | Yes | When session was created | ISO 8601 format |

**Relationships**:
- One AuthCredentials entity per CLI installation (singleton)
- AuthCredentials enables access to all SaunaDevice entities for the authenticated user

**Validation Rules**:
- `session` is sensitive and must be stored securely (via keyring)
- Session tokens do not have embedded expiration (unlike JWT)
- Sessions should be validated before use via `/action/loginwithsession` endpoint
- `session` must never be logged or displayed to user

**Session Lifecycle**:
1. Initial authentication via username/password → creates AuthCredentials with session token
2. Before each API call, optionally validate session (or handle 401 errors)
3. If session invalid (401 error) → prompt re-authentication
4. On logout → delete entire AuthCredentials entity from storage
5. Track `created_at` to implement age-based re-validation (e.g., validate if >24 hours old)

**Example** (for internal use only - never displayed):

```json
{
  "session": "abc123def456session-token",
  "user_id": "user-12345",
  "email": "user@example.com",
  "created_at": "2025-10-08T10:00:00Z"
}
```

---

## Entity Relationships Diagram

```
AuthCredentials (1) ─── authorizes access to ──→ SaunaDevice (0..N)
                                                       │
                                                       │ has
                                                       ↓
                                                  Session (0..1 active)
```

**Explanation**:
- One set of AuthCredentials provides access to zero or more SaunaDevice entities
- Each SaunaDevice can have zero or one active Session at any time
- Historical sessions (completed/cancelled) may exist but are not tracked by this CLI

---

## Data Storage

### Local Storage (Configuration)

**Location**: Platform-specific configuration directory
- **Linux**: `~/.config/huum-cli/config.json`
- **macOS**: `~/Library/Application Support/huum-cli/config.json`
- **Windows**: `%APPDATA%\huum-cli\config.json`

**Contents**: Non-sensitive configuration
```json
{
  "default_device_id": "huum-abc123",
  "default_temperature": 85,
  "output_format": "human-readable"
}
```

### Secure Storage (Credentials)

**Method**: OS-native keyring via keyring library

**Service Name**: `huum-cli`

**Stored Data**:
- **Username/Key**: `auth_data`
- **Value**: JSON-serialized AuthCredentials entity

**Access Pattern**:
```python
import keyring
import json

# Store
auth_data = {"access_token": "...", "expires_at": "..."}
keyring.set_password("huum-cli", "auth_data", json.dumps(auth_data))

# Retrieve
auth_json = keyring.get_password("huum-cli", "auth_data")
auth_data = json.loads(auth_json) if auth_json else None

# Delete (logout)
keyring.delete_password("huum-cli", "auth_data")
```

---

## Validation Summary

### Temperature Validation

**Safe Operating Range**: 40-110°C (per spec FR-008)

```python
def validate_temperature(temp: int) -> bool:
    """Validate temperature is within safe operating range"""
    return 40 <= temp <= 110

# Usage
if not validate_temperature(target_temp):
    raise ValueError(
        f"Temperature {target_temp}°C is outside safe range (40-110°C)"
    )
```

### Device State Validation

**Valid Heating States**: `["idle", "heating", "ready", "stopped"]`

```python
VALID_HEATING_STATES = {"idle", "heating", "ready", "stopped"}

def validate_heating_state(state: str) -> bool:
    """Validate heating state is recognized"""
    return state in VALID_HEATING_STATES
```

### Session Token Validation

**Age Check** (optional - validate old sessions):

```python
from datetime import datetime, timedelta

def should_validate_session(created_at: str) -> bool:
    """Check if session should be revalidated based on age"""
    created = datetime.fromisoformat(created_at)
    age = datetime.now() - created
    return age > timedelta(hours=24)  # Revalidate sessions older than 24h
```

**API Validation**:

```python
def validate_session(session_token: str) -> bool:
    """Validate session token via Huum API"""
    client = httpx.Client(base_url="https://sauna.huum.eu")
    try:
        response = client.post(
            "/action/loginwithsession",
            json={"session": session_token}
        )
        data = response.json()
        return data.get("valid", False)
    except:
        return False
```

---

## API Response Mapping

### Huum API → SaunaDevice Entity

The CLI will map Huum API responses to SaunaDevice entities. Actual API response structure from `/action/status`:

```json
{
  "devices": [{
    "id": "device-123",
    "name": "Home Sauna",
    "status": {
      "online": true,
      "temperature": 75,
      "targetTemperature": 85,
      "heating": true,
      "heatingTime": 45,
      "duration": 90
    }
  }]
}
```

Maps to SaunaDevice:
- `id` → `device_id`
- `name` → `name`
- `status.online` → `online`
- `status.temperature` → `current_temperature`
- `status.targetTemperature` → `target_temperature` (null if not heating)
- `status.heating` → determines `heating_state` and `session_active`
- `status.heatingTime` → estimated minutes to ready (not stored in entity, displayed to user)
- `status.duration` → session duration in minutes (not stored in entity)

**Mapping Logic**:

```python
def map_api_device_to_entity(api_device: dict) -> SaunaDevice:
    status = api_device["status"]
    return SaunaDevice(
        device_id=api_device["id"],
        name=api_device["name"],
        online=status["online"],
        current_temperature=status["temperature"],
        target_temperature=status.get("targetTemperature"),
        heating_state="heating" if status["heating"] else "idle",
        session_active=status["heating"],
        last_updated=datetime.now()
    )
```

### Huum API → AuthCredentials Entity

Login response from `/action/login`:

```json
{
  "session": "session-token-string",
  "user_id": "user-123",
  "email": "user@example.com"
}
```

Maps to AuthCredentials:
- `session` → `session`
- `user_id` → `user_id`
- `email` → `email`
- (current timestamp) → `created_at`

**Note**: API documentation from https://app.swaggerhub.com/apis-docs/info716/HUUM/1.2. See [contracts/huum-api.md](./contracts/huum-api.md) for complete details.

---

## Implementation Notes

### Type Definitions (Python)

Using Pydantic for validation and type safety:

```python
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

class SaunaDevice(BaseModel):
    device_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    online: bool
    current_temperature: int = Field(..., ge=0, le=120)
    target_temperature: Optional[int] = Field(None, ge=40, le=110)
    heating_state: Literal["idle", "heating", "ready", "stopped"]
    session_active: bool
    last_updated: datetime

class Session(BaseModel):
    session_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    start_time: datetime
    end_time: Optional[datetime] = None
    target_temperature: int = Field(..., ge=40, le=110)
    state: Literal["active", "completed", "cancelled"]
    duration_minutes: Optional[int] = Field(None, ge=0, le=360)

class AuthCredentials(BaseModel):
    session: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    created_at: datetime
```

### Error Cases

**Invalid Temperature**:
```python
class InvalidTemperatureError(ValueError):
    """Raised when temperature is outside safe operating range"""
    pass
```

**Device Offline**:
```python
class DeviceOfflineError(RuntimeError):
    """Raised when attempting to control offline device"""
    pass
```

**Authentication Required**:
```python
class AuthenticationRequiredError(RuntimeError):
    """Raised when API call made without valid authentication"""
    pass
```

**Active Session Exists**:
```python
class SessionAlreadyActiveError(RuntimeError):
    """Raised when attempting to start session while one is active"""
    pass
```

---

## References

- Feature Spec: [spec.md](./spec.md) - See "Key Entities" section
- Research: [research.md](./research.md) - Technology choices for implementation
