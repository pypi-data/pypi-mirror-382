"""Credential storage utilities using OS keyring."""

import json
from datetime import datetime, timedelta
from typing import Optional

import keyring

from huum_cli.api.models import AuthCredentials

SERVICE_NAME = "huum-cli"
CREDENTIAL_KEY = "auth_data"


def store_credentials(credentials: AuthCredentials) -> None:
    """
    Store credentials securely in OS keyring.

    Args:
        credentials: AuthCredentials object to store
    """
    data = credentials.model_dump_json()
    keyring.set_password(SERVICE_NAME, CREDENTIAL_KEY, data)


def get_credentials() -> Optional[AuthCredentials]:
    """
    Retrieve credentials from OS keyring.

    Returns:
        AuthCredentials if found, None otherwise
    """
    data = keyring.get_password(SERVICE_NAME, CREDENTIAL_KEY)
    if not data:
        return None

    return AuthCredentials.model_validate_json(data)


def delete_credentials() -> None:
    """Remove credentials from OS keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, CREDENTIAL_KEY)
    except keyring.errors.PasswordDeleteError:
        # Already deleted or doesn't exist
        pass


def should_validate_session(created_at: datetime) -> bool:
    """
    Check if session should be revalidated based on age.

    Args:
        created_at: When the session was created

    Returns:
        True if session is older than 24 hours
    """
    age = datetime.now() - created_at
    return age > timedelta(hours=24)
