"""Statistics command for Huum CLI."""

import typer
from rich.table import Table
from typing import Optional
from datetime import datetime, timedelta

from huum_cli.api.client import HuumAPIClient
from huum_cli.utils.formatters import console, format_error
from huum_cli.utils.storage import get_credentials
from huum_cli.utils.plot import plot_temperature_data


def statistics_command(
    device_id: Optional[str] = typer.Argument(None, help="Device ID to get statistics for."),
    all: bool = typer.Option(False, "--all", help="Show all available statistics for the current month."),
    graph: bool = typer.Option(False, "--graph", help="Display a graph of temperatures over time."),
) -> None:
    """
    Show temperature statistics for the last 24 hours.
    """
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        format_error("Not authenticated. Run 'huum auth login' first.")
        raise typer.Exit(1)

    try:
        client = HuumAPIClient(credentials.session)

        # If no device ID is provided, get status and select the first device
        if not device_id:
            devices = client.get_status()
            if not devices:
                console.print("No sauna devices found.")
                return
            device_id = devices[0].device_id
            console.print(f"Showing statistics for device: [cyan]{device_id}[/cyan]")

        stats = client.get_statistics(device_id)

        if not all:
            # Filter stats for the last 24 hours
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            stats = [s for s in stats if s.timestamp >= twenty_four_hours_ago]

        if not stats:
            period = "the current month" if all else "the last 24 hours"
            console.print(f"No statistics found for this device for {period}.")
            return

        title_period = "Monthly" if all else "24-Hour"
        title = f"{title_period} Temperature Statistics for {device_id}"

        if graph:
            plot_temperature_data(stats, title)
        else:
            table = Table(title=title)
            table.add_column("Timestamp", style="cyan")
            table.add_column("Temperature (°C)", justify="right", style="green")

            for reading in stats:
                table.add_row(
                    reading.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    f"{reading.temperature}°C",
                )

            console.print(table)

    except Exception as e:
        format_error(f"Failed to get statistics: {e}")
        raise typer.Exit(2)

