"""Stop sauna session command."""

from typing import Optional

import httpx
import typer

from huum_cli.api.client import APIError, DeviceOfflineError, HuumAPIClient
from huum_cli.utils.formatters import console, format_error
from huum_cli.utils.storage import get_credentials


def stop_command(
    device_id: Optional[str] = typer.Argument(None, help="Device ID to control"),
) -> None:
    """
    Stop sauna heating session.

    If device_id not specified and single device exists, auto-selects that device.
    """
    # Check authentication
    credentials = get_credentials()
    if not credentials:
        format_error("Not authenticated. Run 'huum auth login' first.")
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
                    "Please specify device_id."
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

        # Check if session is active
        if not target_device.session_active:
            console.print(
                f"\n[yellow]Warning:[/yellow] No active session for device '{target_device.name}'\n"
            )
            return  # Exit 0 - not an error

        # Stop session
        console.print(f"\n[bold]Stopping sauna: {target_device.name}[/bold]\n")

        response = client.stop_session(device_id)

        # Display session summary if available
        session_duration = response.get("session_duration_minutes")
        max_temp = response.get("max_temperature")

        if session_duration or max_temp:
            console.print("[bold]Session Summary:[/bold]")
            if session_duration:
                hours = session_duration // 60
                mins = session_duration % 60
                if hours > 0:
                    console.print(f"  Duration: {hours} hour(s) {mins} minute(s)")
                else:
                    console.print(f"  Duration: {mins} minute(s)")
            if max_temp:
                console.print(f"  Max temperature reached: {max_temp}°C")
            console.print()

        console.print("[green]✓[/green] Session stopped successfully\n")

    except (httpx.HTTPError, APIError) as e:
        format_error(f"Failed to stop session: {e}")
        raise typer.Exit(2)
    except DeviceOfflineError:
        format_error(f"Device is offline")
        raise typer.Exit(2)
    except Exception as e:
        format_error(f"Unexpected error: {e}")
        raise typer.Exit(2)
