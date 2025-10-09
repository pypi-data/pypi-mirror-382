"""Start sauna session command."""

from typing import Optional

import httpx
import typer

from huum_cli.api.client import APIError, DeviceOfflineError, HuumAPIClient
from huum_cli.utils.formatters import console, format_error
from huum_cli.utils.storage import get_credentials
from huum_cli.utils.validators import validate_temperature


def start_command(
    device_id: Optional[str] = typer.Argument(None, help="Device ID to control"),
    temperature: int = typer.Option(
        85, "--temperature", "-t", help="Target temperature in Celsius (40-110)"
    ),
) -> None:
    """
    Start sauna heating session.

    If device_id not specified and single device exists, auto-selects that device.
    """
    # Check authentication
    credentials = get_credentials()
    if not credentials:
        format_error("Not authenticated. Run 'huum auth login' first.")
        raise typer.Exit(1)

    # Validate temperature
    if not validate_temperature(temperature):
        format_error(
            f"Temperature {temperature}°C is outside safe range (40-110°C). "
            "Please specify a temperature between 40°C and 110°C."
        )
        raise typer.Exit(1)

    try:
        # Get devices
        client = HuumAPIClient(credentials.session)
        devices = client.get_status()

        if not devices:
            format_error("No sauna devices found for your account")
            raise typer.Exit(1)

        # Auto-select device if only one exists
        if not device_id:
            if len(devices) == 1:
                device_id = devices[0].device_id
                console.print(f"Using device: {devices[0].name}")
            else:
                format_error(
                    f"Multiple devices found ({len(devices)}). "
                    "Please specify device_id. Use 'huum list' to see devices."
                )
                raise typer.Exit(1)

        # Find the target device
        target_device = None
        for device in devices:
            if device.device_id == device_id or device.name == device_id:
                target_device = device
                break

        if not target_device:
            format_error(f"Device '{device_id}' not found")
            raise typer.Exit(1)

        # Check if device is online
        if not target_device.online:
            format_error(f"Device '{target_device.name}' is offline")
            raise typer.Exit(2)

        # Check if session already active
        if target_device.session_active:
            format_error(
                f"Session already active on '{target_device.name}'. "
                "Stop current session first with 'huum stop'."
            )
            raise typer.Exit(1)

        # Start session
        console.print(f"\n[bold]Starting sauna: {target_device.name}[/bold]")
        console.print(f"  Target temperature: {temperature}°C")
        console.print(f"  Current temperature: {target_device.current_temperature}°C")

        response = client.start_session(device_id, temperature)

        # Display success message
        estimated_time = response.get("estimated_time", "unknown")
        console.print(
            f"  Estimated time to ready: ~{estimated_time} minutes\n"
            if estimated_time != "unknown"
            else ""
        )
        console.print("[green]✓[/green] Session started successfully\n")

    except (httpx.HTTPError, APIError) as e:
        format_error(f"Failed to start session: {e}")
        raise typer.Exit(2)
    except DeviceOfflineError:
        format_error(f"Device is offline")
        raise typer.Exit(2)
    except Exception as e:
        format_error(f"Unexpected error: {e}")
        raise typer.Exit(2)
