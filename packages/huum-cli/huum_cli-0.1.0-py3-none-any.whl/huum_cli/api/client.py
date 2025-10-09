"""Huum API client with session-based authentication."""

from datetime import datetime
from typing import Any, Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from huum_cli.api.models import AuthCredentials, SaunaDevice


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
            # Determine heating state
            heating_state = "idle"
            session_active = False

            # Check if there's an active session (has endDate in the future)
            if status.get("endDate"):
                from datetime import datetime
                end_time = datetime.fromtimestamp(status["endDate"])
                if end_time > datetime.now():
                    heating_state = "heating"
                    session_active = True

            devices.append(
                SaunaDevice(
                    device_id=device_id,
                    name=status.get("saunaName") or f"Sauna {device_id}",
                    online=status.get("door", False),  # door=true means online
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
    # Try both known API endpoints
    # Based on user testing, sauna.huum.eu works
    base_urls = ["https://sauna.huum.eu", "https://api.huum.eu"]

    last_error = None
    for base_url in base_urls:
        client = httpx.Client(base_url=base_url, timeout=10.0)

        try:
            response = client.post(
                "/action/login",
                json={
                    "username": username,
                    "password": password,
                },
            )

            # Check for 404 before trying to parse JSON
            if response.status_code == 404:
                # Try next base URL
                client.close()
                continue

            # Try to parse JSON response
            try:
                # Huum API returns JSONP format: ({"key":"value"});
                # Strip the parentheses to get valid JSON
                text = response.text.strip()
                if text.startswith("(") and text.endswith(");"):
                    text = text[1:-2]  # Remove leading ( and trailing );
                elif text.startswith("(") and text.endswith(")"):
                    text = text[1:-1]  # Remove leading ( and trailing )

                # Parse the cleaned JSON
                import json
                data = json.loads(text)
            except Exception as e:
                # Not JSON, likely HTML error page
                raise APIError(
                    f"API returned non-JSON response (status {response.status_code}). "
                    f"Response preview: {response.text[:200]}"
                )

            if response.status_code == 200:
                # Huum API returns session_hash, user_id, email
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
                raise APIError(f"Authentication failed: {response.status_code}")
        except (AuthenticationError, APIError):
            # Re-raise auth/API errors immediately
            client.close()
            raise
        except httpx.HTTPError as e:
            # Try next base URL on connection errors
            client.close()
            if base_url == base_urls[-1]:
                # Last URL failed
                raise APIError(f"Cannot connect to Huum API: {e}")
            continue
        finally:
            if not client.is_closed:
                client.close()

    raise APIError("All API endpoints failed")
