"""Main CLI application entry point."""

import typer

from huum_cli.commands.auth import auth_app
from huum_cli.commands.start import start_command
from huum_cli.commands.status import status_command
from huum_cli.commands.stop import stop_command

app = typer.Typer(
    name="huum",
    help="CLI for managing Huum sauna devices",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth_app, name="auth")

# Register standalone commands
app.command(name="start")(start_command)
app.command(name="status")(status_command)
app.command(name="stop")(stop_command)

# Global options will be available via context
# Additional commands will be registered here as they are implemented
