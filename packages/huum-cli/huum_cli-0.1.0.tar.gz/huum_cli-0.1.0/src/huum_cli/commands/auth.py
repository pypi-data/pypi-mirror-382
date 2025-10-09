"""Authentication commands for Huum CLI."""

from typing import Optional

import typer

from huum_cli.api.client import AuthenticationError, HuumAPIClient, authenticate
from huum_cli.utils.formatters import console, format_error
from huum_cli.utils.storage import delete_credentials, get_credentials, store_credentials

auth_app = typer.Typer(help="Authentication commands")


@auth_app.command("login")
def login(
    username: Optional[str] = typer.Option(
        None, "--username", "-u", help="Huum account username/email"
    ),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="Huum account password", hide_input=True
    ),
    interactive: bool = typer.Option(
        True, "--interactive", "-i", help="Force interactive credential prompt"
    ),
) -> None:
    """
    Authenticate with Huum account and store session securely.

    If username or password not provided, will prompt interactively.
    """
    # Get credentials interactively if not provided
    if not username or not password or interactive:
        console.print("\n[bold]Huum CLI Authentication[/bold]\n")
        if not username:
            username = typer.prompt("Username/Email")
        if not password:
            password = typer.prompt("Password", hide_input=True)

    # Authenticate
    try:
        console.print("Authenticating...")
        credentials = authenticate(username, password)

        # Store credentials
        store_credentials(credentials)

        # Verify session works by getting device status
        client = HuumAPIClient(credentials.session)
        devices = client.get_status()

        console.print("\n[green]✓[/green] Authentication successful!")
        console.print("[green]✓[/green] Credentials stored securely")
        console.print(f"[green]✓[/green] Found {len(devices)} sauna device(s)\n")

    except AuthenticationError as e:
        format_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        format_error(f"Authentication failed: {e}")
        raise typer.Exit(2)


@auth_app.command("logout")
def logout(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
) -> None:
    """Remove stored credentials and log out."""
    # Check if authenticated
    creds = get_credentials()
    if not creds:
        console.print("Not currently authenticated.")
        return

    # Confirm logout
    if not force:
        confirm = typer.confirm("Are you sure you want to log out?")
        if not confirm:
            console.print("Logout cancelled.")
            return

    # Delete credentials
    try:
        delete_credentials()
        console.print("\n[green]✓[/green] Logged out successfully")
        console.print("[green]✓[/green] Credentials removed from secure storage\n")
    except Exception as e:
        format_error(f"Could not access keyring: {e}")
        raise typer.Exit(3)
