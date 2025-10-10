"""Huum API client with session-based authentication."""

from datetime import datetime
from typing import Any, Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from huum_cli.api.models import AuthCredentials, SaunaDevice, TemperatureReading


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class APIError(Exception):
    """Raised when API returns an error."""

    pass


class DeviceOfflineError(Exception):
    """Raised when attempting to control offline device."""

    pass


class SessionAlreadyActiveError(Exception):
    """Raised when attempting to start session while one is active."""

    pass


class HuumAPIClient:
    """Client for interacting with the Huum API."""

    def __init__(self, session_token: str):
        """
        Initialize API client.

        Args:
            session_token: Session token from authentication
        """
        self.session_token = session_token
        self.base_url = "https://sauna.huum.eu"
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=10.0,
        )

    def _request(self, endpoint: str, **params: Any) -> Dict[str, Any]:
        """
        Make authenticated API request.

        Args:
            endpoint: API endpoint path
            **params: Additional parameters to include in request body

        Returns:
            JSON response as dictionary

        Raises:
            APIError: If API returns an error response
            httpx.HTTPStatusError: If HTTP request fails
        """
        payload = {"session": self.session_token, **params}
        response = self.client.post(endpoint, json=payload)
        response.raise_for_status()

        # Parse JSONP response (Huum API wraps JSON in parentheses)
        text = response.text.strip()
        if text.startswith("(") and text.endswith(");"):
            text = text[1:-2]  # Remove leading ( and trailing );
        elif text.startswith("(") and text.endswith(")"):
            text = text[1:-1]  # Remove leading ( and trailing )

        import json
        data = json.loads(text)

        # Check for API-level errors
        if isinstance(data, dict) and not data.get("success", True):
            error_msg = data.get("error", "Unknown API error")
            raise APIError(error_msg)

        return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def get_status(self) -> List[SaunaDevice]:
        """
        Fetch all devices status.

        Returns:
            List of SaunaDevice entities

        Raises:
            APIError: If API returns an error
        """
        # GET request with session as query parameter
        response = self.client.get("/action/status", params={"session": self.session_token})
        response.raise_for_status()

        # Parse JSONP response
        text = response.text.strip()
        if text.startswith("(") and text.endswith(");"):
            text = text[1:-2]
        elif text.startswith("(") and text.endswith(")"):
            text = text[1:-1]

        import json
        data = json.loads(text)

        devices = []
        # Response format: {"device_id": {"temperature": 56, ...}, ...}
        for device_id, status in data.items():
            status_code = status.get("statusCode")
            heating_state = "idle"
            session_active = False
            online = status.get("door", False)

            if status_code == 230: # Offline
                online = False
                heating_state = "offline"
            elif status_code == 231: # Heating
                heating_state = "heating"
                session_active = True
            elif status_code == 232: # Online but not heating
                heating_state = "idle"
                session_active = False
            elif status_code == 233: # Locked by another user
                heating_state = "locked"
                session_active = False # Or True, but CLI can't control it
            elif status_code == 400: # Emergency Stop
                heating_state = "stopped"
                session_active = False

            devices.append(
                SaunaDevice(
                    device_id=device_id,
                    name=status.get("saunaName") or f"Sauna {device_id}",
                    online=online,
                    current_temperature=status.get("temperature", 0),
                    target_temperature=status.get("targetTemperature"),
                    heating_state=heating_state,
                    session_active=session_active,
                    last_updated=datetime.now(),
                )
            )

        return devices

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def start_session(
        self, device_id: str, target_temperature: int, duration: int = 90
    ) -> Dict[str, Any]:
        """
        Start heating session for device.

        Args:
            device_id: Device to control
            target_temperature: Target temperature in Celsius
            duration: Session duration in minutes (default 90)

        Returns:
            API response dictionary

        Raises:
            APIError: If API returns an error
        """
        from datetime import datetime, timedelta

        # Calculate start and end times
        now = datetime.now()
        start_time = int(now.timestamp())
        end_time = int((now + timedelta(minutes=duration)).timestamp())

        return self._request(
            "/action/start",
            targetTemperature=target_temperature,
            startDate=start_time,
            endDate=end_time,
            humidity=0,  # Default to 0 humidity
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def stop_session(self, device_id: str) -> Dict[str, Any]:
        """
        Stop heating session for device.

        Args:
            device_id: Device to control

        Returns:
            API response dictionary

        Raises:
            APIError: If API returns an error
        """
        # GET request with query parameters
        response = self.client.get(
            "/action/stop_sauna",
            params={
                "session": self.session_token,
                "version": "3",
                "saunaId": device_id,
            },
        )
        response.raise_for_status()

        # Parse JSONP response
        text = response.text.strip()
        if text.startswith("(") and text.endswith(");"):
            text = text[1:-2]
        elif text.startswith("(") and text.endswith(")"):
            text = text[1:-1]

        import json
        return json.loads(text)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def validate_session(self) -> bool:
        """
        Validate if session token is still valid.

        Returns:
            True if session is valid, False otherwise
        """
        try:
            result = self._request("/action/loginwithsession")
            return result.get("valid", False)
        except (httpx.HTTPStatusError, APIError):
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def get_statistics(self, device_id: str) -> List[TemperatureReading]:
        """
        Fetch temperature statistics for a device for the current month.

        Args:
            device_id: Device to get statistics for

        Returns:
            List of TemperatureReading entities

        Raises:
            APIError: If API returns an error
        """
        from datetime import datetime
        from huum_cli.api.models import TemperatureReading

        # Get the current month in YYYY-MM format
        current_month = datetime.now().strftime("%Y-%m")

        params = {
            "session": self.session_token,
            "version": "3",
            "month": current_month,
            "saunaId": int(device_id),
        }

        try:
            response = self.client.get(
                "/action/get_temperatures",
                params=params,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(f"API returned an error: {e.response.status_code} - {e.response.text}") from e

        # Parse JSONP response
        text = response.text.strip()
        if text.startswith("(") and text.endswith(");"):
            text = text[1:-2]
        elif text.startswith("(") and text.endswith(")"):
            text = text[1:-1]

        import json
        data = json.loads(text)

        readings = []
        if isinstance(data, list):
            for item in data:
                try:
                    timestamp = datetime.fromtimestamp(int(item["changeTime"]))
                    temperature = int(item["temperature"])
                    readings.append(TemperatureReading(timestamp=timestamp, temperature=temperature))
                except (ValueError, TypeError, KeyError):
                    # Ignore invalid data points
                    continue
        
        # Sort readings by timestamp
        readings.sort(key=lambda r: r.timestamp)

        return readings

    def __enter__(self) -> "HuumAPIClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.client.close()


def authenticate(username: str, password: str) -> AuthCredentials:
    """
    Authenticate user and return session data.

    Args:
        username: Huum account username/email
        password: Huum account password

    Returns:
        AuthCredentials with session token

    Raises:
        AuthenticationError: If authentication fails
        APIError: If API returns an error
    """
    base_urls = ["https://sauna.huum.eu", "https://api.huum.eu"]
    last_error = None

    for base_url in base_urls:
        client = None
        try:
            client = httpx.Client(base_url=base_url, timeout=10.0)
            response = client.post(
                "/action/login",
                json={"username": username, "password": password},
            )

            if response.status_code == 404:
                last_error = APIError(f"API endpoint not found at {base_url} (404)")
                continue

            text = response.text.strip()
            if text.startswith("(") and text.endswith(");"):
                text = text[1:-2]
            elif text.startswith("(") and text.endswith(")"):
                text = text[1:-1]

            if not text:
                last_error = APIError(f"API returned empty response from {base_url}")
                continue

            import json
            data = json.loads(text)

            if response.status_code == 200:
                session = data.get("session_hash")
                user_id = str(data.get("user_id", ""))
                email = data.get("email", username)

                if not session:
                    raise APIError(f"No session token in response. Keys: {list(data.keys())}")

                return AuthCredentials(
                    session=session,
                    user_id=user_id,
                    email=email,
                    created_at=datetime.now(),
                )
            elif response.status_code == 401:
                raise AuthenticationError("Invalid credentials")
            elif "error" in data:
                raise AuthenticationError(data["error"])
            else:
                last_error = APIError(f"Authentication failed at {base_url}: {response.status_code}")
                continue

        except (AuthenticationError, APIError) as e:
            last_error = e
            continue
        except httpx.HTTPError as e:
            last_error = APIError(f"Cannot connect to {base_url}: {e}")
            continue
        except Exception as e:
            last_error = APIError(f"An unexpected error occurred with {base_url}: {e}")
            continue
        finally:
            if client and not client.is_closed:
                client.close()

    if isinstance(last_error, AuthenticationError):
        raise last_error

    raise APIError(f"All API endpoints failed. Last error: {last_error}")
