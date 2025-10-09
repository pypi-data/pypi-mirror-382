# Huum API Integration Specification

**Date**: 2025-10-08
**Feature**: 001-a-simple-cli
**API Version**: 1.2
**Source**: https://app.swaggerhub.com/apis-docs/info716/HUUM/1.2

## Base URL

**Production**: `https://sauna.huum.eu` (user-specified, preferred)
**Alternative**: `https://api.huum.eu`

## Authentication

### Method: Session-Based Authentication

The Huum API uses session-based authentication with a session token.

### Login Flow

**Endpoint**: `POST /action/login`

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "userpassword"
}
```

**Response** (Success):
```json
{
  "session": "session-token-string",
  "user_id": "user-identifier",
  "email": "user@example.com"
}
```

**Response** (Failure):
```json
{
  "error": "Invalid credentials"
}
```

**HTTP Status Codes**:
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account locked or other auth issue

### Session Validation

**Endpoint**: `POST /action/loginwithsession`

**Request Body**:
```json
{
  "session": "session-token-string"
}
```

**Response**:
```json
{
  "valid": true,
  "user_id": "user-identifier"
}
```

Use this to validate existing session tokens before use.

### Using Session Token

Include session token in request body for all authenticated endpoints:

```json
{
  "session": "session-token-string",
  // ... other parameters
}
```

**Note**: Unlike Bearer token authentication, Huum API requires the session token in the request body, not in headers.

---

## Core Endpoints

### 1. Get Sauna Status

**Endpoint**: `POST /action/status`

**Request Body**:
```json
{
  "session": "session-token-string"
}
```

**Response**:
```json
{
  "devices": [
    {
      "id": "device-id",
      "name": "Home Sauna",
      "status": {
        "online": true,
        "temperature": 75,
        "targetTemperature": 85,
        "heating": true,
        "heatingTime": 45,
        "duration": 90
      }
    }
  ]
}
```

**Response Fields**:
- `devices`: Array of sauna devices
- `id`: Unique device identifier
- `name`: User-defined device name
- `status.online`: Device connectivity status
- `status.temperature`: Current temperature in Celsius
- `status.targetTemperature`: Target temperature (if session active)
- `status.heating`: Whether actively heating
- `status.heatingTime`: Estimated minutes until target reached
- `status.duration`: Planned session duration in minutes

### 2. Start Sauna Session

**Endpoint**: `POST /action/start`

**Request Body**:
```json
{
  "session": "session-token-string",
  "device_id": "device-id",
  "target_temperature": 85,
  "duration": 90
}
```

**Parameters**:
- `device_id` (required): Device to control
- `target_temperature` (required): Target temperature in Celsius (40-110°C)
- `duration` (optional): Session duration in minutes (default: 90)

**Response** (Success):
```json
{
  "success": true,
  "session_id": "session-identifier",
  "estimated_time": 45
}
```

**Response** (Failure):
```json
{
  "success": false,
  "error": "Device offline"
}
```

**HTTP Status Codes**:
- `200 OK`: Command accepted
- `400 Bad Request`: Invalid parameters
- `403 Forbidden`: Not authorized for device
- `404 Not Found`: Device not found

### 3. Stop Sauna Session

**Endpoint**: `POST /action/stop_sauna`

**Request Body**:
```json
{
  "session": "session-token-string",
  "device_id": "device-id"
}
```

**Response** (Success):
```json
{
  "success": true,
  "session_duration_minutes": 75,
  "max_temperature": 87
}
```

**Response** (Failure):
```json
{
  "success": false,
  "error": "No active session"
}
```

### 4. Control Sauna Light

**Endpoint**: `POST /action/light`

**Request Body**:
```json
{
  "session": "session-token-string",
  "device_id": "device-id",
  "light_on": true
}
```

**Response**:
```json
{
  "success": true,
  "light_status": true
}
```

**Note**: Optional feature - may not be relevant for MVP but good to have documented.

---

## User Management Endpoints

### Get User Profile

**Endpoint**: `POST /action/profile`

**Request Body**:
```json
{
  "session": "session-token-string"
}
```

**Response**:
```json
{
  "user_id": "user-identifier",
  "email": "user@example.com",
  "name": "User Name",
  "devices": ["device-id-1", "device-id-2"]
}
```

### Register New User

**Endpoint**: `POST /action/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password",
  "name": "User Name"
}
```

**Note**: Likely not needed for CLI - users register via mobile app.

### Password Reset

**Endpoint**: `POST /action/forgot_password`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Password reset email sent"
}
```

---

## Booking Management (Optional)

### Get Bookings

**Endpoint**: `POST /booking/get_bookings`

**Request Body**:
```json
{
  "session": "session-token-string",
  "device_id": "device-id"
}
```

**Response**:
```json
{
  "bookings": [
    {
      "id": "booking-id",
      "start_time": "2025-10-08T18:00:00Z",
      "temperature": 85,
      "duration": 90
    }
  ]
}
```

### Save Booking

**Endpoint**: `POST /booking/save_booking`

**Request Body**:
```json
{
  "session": "session-token-string",
  "device_id": "device-id",
  "start_time": "2025-10-08T18:00:00Z",
  "temperature": 85,
  "duration": 90
}
```

**Note**: Booking functionality is lower priority - focus on manual control first.

---

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes

| Status Code | Error | Meaning |
|------------|-------|---------|
| 400 | Bad Request | Invalid parameters or malformed request |
| 401 | Unauthorized | Session token invalid or expired |
| 403 | Forbidden | Not authorized for requested device/action |
| 404 | Not Found | Device or resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | API temporarily unavailable |

### Session Expiration

Sessions expire after inactivity. When receiving `401 Unauthorized`:
1. Attempt to re-login with stored credentials (if available)
2. If re-login fails, prompt user to authenticate again
3. Clear stored session token

**Best Practice**: Validate session before commands using `/action/loginwithsession`.

---

## Rate Limiting

**Policy**: Not explicitly documented in API spec

**Recommended Practice**:
- Implement exponential backoff on `429` errors
- Use tenacity library for automatic retry with backoff
- Limit concurrent requests to 1 (CLI executes sequentially anyway)
- Cache status responses for short periods (5-10 seconds) to avoid excessive polling

---

## API Version

**Current Version**: 1.2

**Version Parameter**: Some endpoints may accept `version` parameter for compatibility:

```json
{
  "session": "session-token-string",
  "version": "1.2"
}
```

---

## Implementation Notes

### Session Token Storage

Store session token securely using keyring library:

```python
# Storage format in keyring
{
  "session": "session-token-string",
  "user_id": "user-identifier",
  "email": "user@example.com",
  "created_at": "2025-10-08T10:00:00Z"
}
```

**Note**: Unlike JWT tokens, Huum session tokens don't have embedded expiration. Track creation time and validate periodically.

### API Client Implementation

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class HuumAPIClient:
    def __init__(self, session_token: str):
        self.base_url = "https://sauna.huum.eu"
        self.session_token = session_token
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=10.0
        )

    def _request(self, endpoint: str, **params) -> dict:
        """Make authenticated API request"""
        payload = {
            "session": self.session_token,
            **params
        }
        response = self.client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_status(self) -> dict:
        """Get status of all devices"""
        return self._request("/action/status")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def start_sauna(self, device_id: str, target_temp: int, duration: int = 90) -> dict:
        """Start sauna heating session"""
        return self._request(
            "/action/start",
            device_id=device_id,
            target_temperature=target_temp,
            duration=duration
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def stop_sauna(self, device_id: str) -> dict:
        """Stop sauna heating session"""
        return self._request(
            "/action/stop_sauna",
            device_id=device_id
        )

    def validate_session(self) -> bool:
        """Check if session token is still valid"""
        try:
            result = self._request("/action/loginwithsession")
            return result.get("valid", False)
        except httpx.HTTPStatusError:
            return False
```

### Authentication Flow

```python
def authenticate(username: str, password: str) -> dict:
    """Authenticate user and return session data"""
    client = httpx.Client(base_url="https://sauna.huum.eu", timeout=10.0)

    response = client.post(
        "/action/login",
        json={"username": username, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "session": data["session"],
            "user_id": data["user_id"],
            "email": data["email"],
            "created_at": datetime.now().isoformat()
        }
    elif response.status_code == 401:
        raise AuthenticationError("Invalid credentials")
    else:
        raise APIError(f"Authentication failed: {response.status_code}")
```

---

## API Response Mapping

### Status Response → SaunaDevice Entity

**API Response**:
```json
{
  "devices": [{
    "id": "abc123",
    "name": "Home Sauna",
    "status": {
      "online": true,
      "temperature": 75,
      "targetTemperature": 85,
      "heating": true
    }
  }]
}
```

**Maps to SaunaDevice**:
```python
SaunaDevice(
    device_id=device["id"],
    name=device["name"],
    online=device["status"]["online"],
    current_temperature=device["status"]["temperature"],
    target_temperature=device["status"].get("targetTemperature"),
    heating_state="heating" if device["status"]["heating"] else "idle",
    session_active=device["status"]["heating"],
    last_updated=datetime.now()
)
```

---

## Testing

### Mock API Responses

```python
# tests/fixtures/mock_responses.py
MOCK_LOGIN_SUCCESS = {
    "session": "mock-session-token",
    "user_id": "user-123",
    "email": "test@example.com"
}

MOCK_STATUS_RESPONSE = {
    "devices": [{
        "id": "device-123",
        "name": "Test Sauna",
        "status": {
            "online": True,
            "temperature": 25,
            "targetTemperature": None,
            "heating": False
        }
    }]
}

MOCK_START_SUCCESS = {
    "success": True,
    "session_id": "session-456",
    "estimated_time": 45
}
```

---

## References

- **API Documentation**: https://app.swaggerhub.com/apis-docs/info716/HUUM/1.2
- **Base URL**: https://sauna.huum.eu
- **Data Model**: [data-model.md](../data-model.md)
- **CLI Commands**: [cli-commands.md](./cli-commands.md)
