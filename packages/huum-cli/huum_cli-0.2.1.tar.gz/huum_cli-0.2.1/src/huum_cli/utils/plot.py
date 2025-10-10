"""Plotting utilities for Huum CLI."""

from typing import List
import plotext as plt
from datetime import datetime

from huum_cli.api.models import TemperatureReading


def plot_temperature_data(stats: List[TemperatureReading], title: str):
    """
    Generates and displays a terminal-based plot of temperature over time.

    Args:
        stats: A list of TemperatureReading objects.
        title: The title for the plot.
    """
    if not stats:
        return

    datetimes = [s.timestamp for s in stats]
    temps = [s.temperature for s in stats]

    # Convert datetime objects to strings using plotext's utility
    date_strings = plt.datetimes_to_string(datetimes)
    
    # Set the date format that plotext will use for the axis
    # This format corresponds to the default output of datetimes_to_string
    plt.date_form('d/m/Y H:M:S')

    plt.clf()
    plt.plot(date_strings, temps)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.show()
