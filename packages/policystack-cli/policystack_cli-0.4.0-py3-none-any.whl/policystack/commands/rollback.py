"""Rollback command for PolicyStack CLI."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..core.backup_manager import BackupManager
from ..models.backup import BackupStatus


@click.command()
@click.argument("element_name")
@click.option(
    "--backup-id",
    "-b",
    help="Specific backup ID to restore (defaults to latest)",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    help="PolicyStack project path",
)
@click.option(
    "--list",
    "-l",
    "list_backups",
    is_flag=True,
    help="List available backups",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.pass_obj
def rollback(
    ctx,
    element_name: str,
    backup_id: Optional[str],
    path: Optional[Path],
    list_backups: bool,
    yes: bool,
) -> None:
    """
    Roll back an element to a previous state.

    Restore an element from a backup created during installation or upgrade.
    This is useful when an upgrade fails or introduces conflicts that are
    difficult to resolve.

    Examples:

    \b
        # List available backups
        policystack rollback openshift-logging --list

    \b
        # Roll back to latest backup
        policystack rollback openshift-logging

    \b
        # Roll back to specific backup
        policystack rollback openshift-logging --backup-id 20250108_143022_1.0.0

    \b
        # Roll back with automatic confirmation
        policystack rollback openshift-logging --yes
    """
    console: Console = ctx.console

    # Determine stack path
    if path:
        stack_path = path / "stack"
    else:
        stack_path = Path.cwd() / "stack"

    element_path = stack_path / element_name

    if not element_path.exists():
        console.print(f"[red]Element '{element_name}' not found at {element_path}[/red]")
        return

    # Initialize backup manager
    backup_manager = BackupManager(element_path)

    # List backups if requested
    if list_backups:
        _list_backups(console, backup_manager, element_name)
        return

    # Get backup to restore
    if backup_id:
        backup = backup_manager.get_backup(backup_id)
        if not backup:
            console.print(f"[red]Backup '{backup_id}' not found[/red]")
            console.print("\nUse --list to see available backups")
            return
    else:
        backup = backup_manager.get_latest_backup()
        if not backup:
            console.print(f"[yellow]No backups found for {element_name}[/yellow]")
            return

    # Display rollback plan
    console.print(
        Panel.fit(
            f"[bold]Rollback Plan[/bold]\n"
            f"Element: {element_name}\n"
            f"Backup ID: {backup.backup_id}\n"
            f"Created: {_format_timestamp(backup.timestamp)}\n"
            f"Version: {backup.display_version}\n"
            f"Reason: {backup.display_reason}\n"
            f"Has conflicts: {'Yes' if backup.has_conflicts else 'No'}",
            border_style="yellow",
        )
    )

    # Warn if backup has conflicts
    if backup.has_conflicts:
        console.print(
            "\n[yellow]⚠  Warning: This backup was created when conflicts were present.[/yellow]"
        )
        console.print("[yellow]   Rolling back will restore the conflicted state.[/yellow]")

    # Confirm rollback
    if not yes:
        console.print("\n[dim]This will replace the current element state with the backup.[/dim]")
        proceed = Confirm.ask("[bold]Proceed with rollback?[/bold]", default=True)
        if not proceed:
            console.print("[yellow]Rollback cancelled[/yellow]")
            return

    # Perform rollback
    try:
        console.print("\n[cyan]Performing rollback...[/cyan]")

        success = backup_manager.restore_backup(backup.backup_id)

        if success:
            console.print(
                f"\n[green]✓ Successfully rolled back {element_name} to backup {backup.backup_id}[/green]"
            )

            # Show what was restored
            console.print(f"\n[bold]Restored state:[/bold]")
            console.print(f"  Version: {backup.from_version}")
            console.print(f"  Backup created: {_format_timestamp(backup.timestamp)}")

            if backup.has_conflicts:
                console.print(
                    f"\n[yellow]Note: The restored state may have conflict markers.[/yellow]"
                )
                console.print(
                    f"[yellow]Review the files and resolve any remaining conflicts.[/yellow]"
                )

            # Suggest next steps
            console.print(f"\n[bold]Next steps:[/bold]")
            console.print(f"  1. Review the restored files at {element_path}")
            console.print(f"  2. Test your configuration")
            console.print(
                f"  3. If needed, try upgrading again: policystack upgrade {element_name}"
            )

    except Exception as e:
        console.print(f"[red]Rollback failed: {e}[/red]")
        if ctx.debug:
            console.print_exception()


def _list_backups(console: Console, backup_manager: BackupManager, element_name: str) -> None:
    """Display list of available backups."""
    backups = backup_manager.list_backups()

    if not backups:
        console.print(f"[yellow]No backups found for {element_name}[/yellow]")
        return

    console.print(f"\n[bold]Available Backups for {element_name}[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Backup ID", style="green")
    table.add_column("Created", style="white")
    table.add_column("Type", style="blue")
    table.add_column("Version", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Conflicts", style="red")

    for backup in backups:
        status_display = backup.status.value
        if backup.status == BackupStatus.RESTORED:
            status_display = f"✓ {status_display}"

        conflicts_display = "Yes" if backup.has_conflicts else "No"

        table.add_row(
            backup.backup_id,
            _format_timestamp(backup.timestamp),
            backup.backup_type.value,
            backup.display_version,
            status_display,
            conflicts_display,
        )

    console.print(table)

    console.print(
        f"\n[dim]To restore a backup:[/dim] policystack rollback {element_name} --backup-id <id>"
    )


def _format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp_str
