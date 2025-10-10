"""Sync/mirror commands for PolicyStack CLI."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from ..core.sync_manager import SyncManager


@click.group()
def sync() -> None:
    """
    Sync and mirror marketplace repositories.

    Pull marketplace repositories, create archives, push to mirrors,
    or sync directly between repositories.
    """


@sync.command()
@click.argument("repository_name")
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output archive path (default: <repo-name>-marketplace.tar.gz)",
)
@click.option(
    "--branch",
    "-b",
    help="Git branch to pull (overrides configured branch)",
)
@click.pass_obj
def pull(
    ctx,
    repository_name: str,
    output: Optional[Path],
    branch: Optional[str],
) -> None:
    """
    Pull marketplace repository and create archive.

    Downloads a marketplace repository and creates a compressed archive
    containing only the relevant marketplace files (templates, registry, etc.).

    REPOSITORY_NAME must be a configured repository name.

    Examples:

    \b
        # Pull from configured repository
        policystack sync pull official

    \b
        # Pull specific branch
        policystack sync pull official --branch develop

    \b
        # Pull with custom output path
        policystack sync pull official -o my-archive.tar.gz
    """
    console: Console = ctx.console
    marketplace = ctx.marketplace
    sync_manager = SyncManager(ctx.config.config.cache_dir, marketplace)

    # Get repository from config
    repo = marketplace.get_repository(repository_name)
    if not repo:
        console.print(f"[red]Repository '{repository_name}' not found in configuration[/red]")
        console.print("\n[yellow]Available repositories:[/yellow]")
        for r in marketplace.repositories:
            console.print(f"  • {r.name}")
        console.print("\n[dim]Add a repository with: policystack repo add <name> <url>[/dim]")
        return

    source_url = repo.url
    source_branch = branch or repo.branch
    source_auth = repo.auth_token

    # Validate source
    console.print(f"[cyan]Validating repository {repo.name}...[/cyan]")
    success, info, message = sync_manager.get_repository_info(source_url, source_auth)

    if not success:
        console.print(f"[red]Cannot access repository: {message}[/red]")
        return

    # Show repository info
    console.print(
        Panel.fit(
            f"[bold]Source Repository[/bold]\n"
            f"Name: {repo.name}\n"
            f"URL: {source_url}\n"
            f"Branch: {source_branch or info.get('default_branch', 'default')}\n"
            f"Accessible: ✓",
            border_style="green",
        )
    )

    # Confirm pull
    if not Confirm.ask("\n[bold]Pull and create archive?[/bold]", default=True):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Perform pull
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Pulling repository...", total=None)

        success, archive_path, message = sync_manager.pull_repository(
            source_url=source_url,
            branch=source_branch,
            auth_token=source_auth,
            output_path=output,
        )

        if success:
            progress.update(task, description="✓ Archive created")
            console.print(f"\n[green]✓ Successfully created archive[/green]")
            console.print(f"  Location: {archive_path}")
            console.print(f"  Size: {archive_path.stat().st_size / (1024*1024):.2f} MB")
        else:
            progress.update(task, description="✗ Pull failed")
            console.print(f"\n[red]✗ Pull failed: {message}[/red]")


@sync.command()
@click.argument("repository_name")
@click.option(
    "--archive",
    "-a",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to archive file",
)
@click.option(
    "--branch",
    "-b",
    help="Target branch (overrides configured branch)",
)
@click.option(
    "--message",
    "-m",
    help="Commit message",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.pass_obj
def push(
    ctx,
    repository_name: str,
    archive: Path,
    branch: Optional[str],
    message: Optional[str],
    yes: bool,
) -> None:
    """
    Push archive contents to target repository.

    Extracts an archive and pushes the contents to a configured Git repository.

    REPOSITORY_NAME must be a configured repository name.

    Examples:

    \b
        # Push archive to configured repository
        policystack sync push my-mirror -a archive.tar.gz

    \b
        # Push to specific branch
        policystack sync push my-mirror -a archive.tar.gz -b develop

    \b
        # Push with custom commit message
        policystack sync push my-mirror -a archive.tar.gz -m "Update marketplace"
    """
    console: Console = ctx.console
    marketplace = ctx.marketplace
    sync_manager = SyncManager(ctx.config.config.cache_dir, marketplace)

    # Get repository from config
    repo = marketplace.get_repository(repository_name)
    if not repo:
        console.print(f"[red]Repository '{repository_name}' not found in configuration[/red]")
        console.print("\n[yellow]Available repositories:[/yellow]")
        for r in marketplace.repositories:
            console.print(f"  • {r.name}")
        console.print("\n[dim]Add a repository with: policystack repo add <name> <url>[/dim]")
        return

    target_url = repo.url
    target_branch = branch or repo.branch
    target_auth = repo.auth_token

    # Show push plan
    console.print(
        Panel.fit(
            f"[bold]Push Plan[/bold]\n"
            f"Archive: {archive}\n"
            f"Repository: {repo.name}\n"
            f"Target: {target_url}\n"
            f"Branch: {target_branch or 'main'}\n"
            f"Message: {message or 'Sync marketplace from upstream'}",
            border_style="cyan",
        )
    )

    # Confirm push
    if not yes:
        if not Confirm.ask("\n[bold]Push archive to target repository?[/bold]", default=True):
            console.print("[yellow]Cancelled[/yellow]")
            return

    # Perform push
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Pushing to repository...", total=None)

        success, push_message = sync_manager.push_archive(
            archive_path=archive,
            target_url=target_url,
            branch=target_branch,
            auth_token=target_auth,
            commit_message=message,
        )

        if success:
            progress.update(task, description="✓ Push complete")
            console.print(f"\n[green]✓ {push_message}[/green]")
        else:
            progress.update(task, description="✗ Push failed")
            console.print(f"\n[red]✗ {push_message}[/red]")


@sync.command()
@click.argument("source_name")
@click.argument("target_name")
@click.option(
    "--source-branch",
    help="Source branch (overrides configured branch)",
)
@click.option(
    "--target-branch",
    help="Target branch (overrides configured branch)",
)
@click.option(
    "--message",
    "-m",
    help="Commit message",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.pass_obj
def mirror(
    ctx,
    source_name: str,
    target_name: str,
    source_branch: Optional[str],
    target_branch: Optional[str],
    message: Optional[str],
    yes: bool,
) -> None:
    """
    Sync directly between repositories without intermediate file.

    Clones source repository, filters content, and pushes to target
    repository in a single operation without creating an intermediate
    archive file.

    Both SOURCE_NAME and TARGET_NAME must be configured repository names.

    Examples:

    \b
        # Mirror between configured repositories
        policystack sync mirror official my-mirror

    \b
        # Mirror specific branch
        policystack sync mirror official my-mirror \\
            --source-branch develop --target-branch main

    \b
        # Mirror with custom commit message
        policystack sync mirror official my-mirror -m "Sync from upstream"
    """
    console: Console = ctx.console
    marketplace = ctx.marketplace
    sync_manager = SyncManager(ctx.config.config.cache_dir, marketplace)

    # Get source repository from config
    source_repo = marketplace.get_repository(source_name)
    if not source_repo:
        console.print(f"[red]Source repository '{source_name}' not found in configuration[/red]")
        console.print("\n[yellow]Available repositories:[/yellow]")
        for r in marketplace.repositories:
            console.print(f"  • {r.name}")
        console.print("\n[dim]Add a repository with: policystack repo add <name> <url>[/dim]")
        return

    # Get target repository from config
    target_repo = marketplace.get_repository(target_name)
    if not target_repo:
        console.print(f"[red]Target repository '{target_name}' not found in configuration[/red]")
        console.print("\n[yellow]Available repositories:[/yellow]")
        for r in marketplace.repositories:
            console.print(f"  • {r.name}")
        console.print("\n[dim]Add a repository with: policystack repo add <name> <url>[/dim]")
        return

    source_url = source_repo.url
    target_url = target_repo.url
    src_branch = source_branch or source_repo.branch
    tgt_branch = target_branch or target_repo.branch
    src_auth = source_repo.auth_token
    tgt_auth = target_repo.auth_token

    # Validate repositories
    console.print("[cyan]Validating repositories...[/cyan]")

    # Check source
    success, source_info, src_message = sync_manager.get_repository_info(source_url, src_auth)
    if not success:
        console.print(f"[red]Cannot access source: {src_message}[/red]")
        return

    # Show sync plan
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("", style="bold")
    table.add_column("Source", style="green")
    table.add_column("Target", style="blue")

    table.add_row("Repository", source_name, target_name)
    table.add_row("URL", source_url, target_url)
    table.add_row(
        "Branch",
        src_branch or source_info.get("default_branch", "main"),
        tgt_branch or src_branch or "main",
    )
    table.add_row("Auth", "✓" if src_auth else "✗", "✓" if tgt_auth else "✗")

    console.print(table)

    # Confirm sync
    if not yes:
        if not Confirm.ask("\n[bold]Sync repositories?[/bold]", default=True):
            console.print("[yellow]Cancelled[/yellow]")
            return

    # Perform sync
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Syncing repositories...", total=None)

        success, sync_message = sync_manager.sync_repositories(
            source_url=source_url,
            target_url=target_url,
            source_branch=src_branch,
            target_branch=tgt_branch,
            source_auth=src_auth,
            target_auth=tgt_auth,
            commit_message=message,
        )

        if success:
            progress.update(task, description="✓ Sync complete")
            console.print(f"\n[green]✓ {sync_message}[/green]")
        else:
            progress.update(task, description="✗ Sync failed")
            console.print(f"\n[red]✗ {sync_message}[/red]")


@sync.command()
@click.argument("repository_name")
@click.pass_obj
def info(
    ctx,
    repository_name: str,
) -> None:
    """
    Show information about a repository.

    Check repository accessibility and display basic information.

    REPOSITORY_NAME must be a configured repository name.

    Examples:

    \b
        # Check configured repository info
        policystack sync info official
    """
    console: Console = ctx.console
    marketplace = ctx.marketplace
    sync_manager = SyncManager(ctx.config.config.cache_dir, marketplace)

    # Get repository from config
    repo = marketplace.get_repository(repository_name)
    if not repo:
        console.print(f"[red]Repository '{repository_name}' not found in configuration[/red]")
        console.print("\n[yellow]Available repositories:[/yellow]")
        for r in marketplace.repositories:
            console.print(f"  • {r.name}")
        console.print("\n[dim]Add a repository with: policystack repo add <name> <url>[/dim]")
        return

    repo_url = repo.url
    repo_auth = repo.auth_token

    # Get info
    console.print(f"[cyan]Checking repository {repo.name}...[/cyan]\n")

    success, info, message = sync_manager.get_repository_info(repo_url, repo_auth)

    if not success:
        console.print(f"[red]✗ {message}[/red]")
        return

    # Display info
    console.print(
        Panel.fit(
            f"[bold green]✓ Repository Accessible[/bold green]\n\n"
            f"[bold]Name:[/bold] {repo.name}\n"
            f"[bold]URL:[/bold] {repo_url}\n"
            f"[bold]Default Branch:[/bold] {info.get('default_branch', 'unknown')}\n"
            f"[bold]Configured Branch:[/bold] {repo.branch or '(default)'}\n"
            f"[bold]Branches:[/bold] {len([r for r in info.get('refs', {}) if r.startswith('refs/heads/')])}",
            title="Repository Information",
            border_style="green",
        )
    )

    # Show branches
    branches = [
        r.replace("refs/heads/", "") for r in info.get("refs", {}) if r.startswith("refs/heads/")
    ]
    if branches:
        console.print("\n[bold]Available Branches:[/bold]")
        for branch in sorted(branches)[:10]:
            console.print(f"  • {branch}")
        if len(branches) > 10:
            console.print(f"  ... and {len(branches) - 10} more")
