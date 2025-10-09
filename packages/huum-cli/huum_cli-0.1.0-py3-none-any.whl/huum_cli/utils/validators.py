"""Validation utilities for CLI inputs."""


def validate_temperature(temperature: int) -> bool:
    """
    Validate temperature is within safe operating range.

    Args:
        temperature: Temperature in Celsius

    Returns:
        True if valid, False otherwise
    """
    return 40 <= temperature <= 110
