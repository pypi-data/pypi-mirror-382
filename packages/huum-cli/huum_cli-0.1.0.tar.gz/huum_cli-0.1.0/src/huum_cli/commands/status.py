"""Status command for Huum CLI."""

import typer
from rich.table import Table

from huum_cli.api.client import HuumAPIClient
from huum_cli.utils.formatters import console, format_error
from huum_cli.utils.storage import get_credentials


def status_command() -> None:
    """
    Show status of all sauna devices.

    Displays current temperature, target temperature, and heating state.
    """
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        format_error("Not authenticated. Run 'huum auth login' first.")
        raise typer.Exit(1)

    try:
        # Get device status
        client = HuumAPIClient(credentials.session)
        devices = client.get_status()

        if not devices:
            console.print("No sauna devices found.")
            return

        # Create table
        table = Table(title="Sauna Status")
        table.add_column("Device ID", style="cyan")
        table.add_column("Name", style="blue")
        table.add_column("Online", style="green")
        table.add_column("Current", justify="right")
        table.add_column("Target", justify="right")
        table.add_column("State", style="yellow")

        for device in devices:
            online_icon = "✓" if device.online else "✗"
            online_style = "green" if device.online else "red"

            state_style = "green" if device.session_active else "dim"

            table.add_row(
                device.device_id,
                device.name,
                f"[{online_style}]{online_icon}[/{online_style}]",
                f"{device.current_temperature}°C",
                f"{device.target_temperature}°C" if device.target_temperature else "-",
                f"[{state_style}]{device.heating_state}[/{state_style}]",
            )

        console.print(table)

    except Exception as e:
        format_error(f"Failed to get status: {e}")
        raise typer.Exit(2)
