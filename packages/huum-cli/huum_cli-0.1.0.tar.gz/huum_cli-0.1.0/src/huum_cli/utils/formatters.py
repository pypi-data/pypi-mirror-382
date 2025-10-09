"""Output formatting utilities for CLI."""

import json
import sys
from typing import Any

from rich.console import Console

console = Console()
error_console = Console(stderr=True)


def format_json(data: Any) -> None:
    """
    Format data as JSON for machine-readable output.

    Args:
        data: Data to format (will be serialized to JSON)
    """
    print(json.dumps(data, indent=2, default=str))


def format_error(message: str) -> None:
    """
    Format error message with Rich styling.

    Args:
        message: Error message to display
    """
    error_console.print(f"[red]Error:[/red] {message}")
