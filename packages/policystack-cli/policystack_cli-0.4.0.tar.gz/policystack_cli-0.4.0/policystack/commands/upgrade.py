"""Upgrade command for PolicyStack CLI."""

import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ..core.backup_manager import BackupManager
from ..core.change_detector import ChangeDetector, TemplateSnapshot
from ..core.git_repository import GitRepositoryHandler
from ..core.installer import TemplateInstaller
from ..core.merger import TemplateMerger, TemplateMergeResult
from ..models.backup import BackupType


class TemplateUpgrader:
    """Handles the complete upgrade process for templates."""

    def __init__(self, marketplace, console: Console):
        self.marketplace = marketplace
        self.console = console
        self.installer = TemplateInstaller(marketplace, console)
        self.merger = TemplateMerger()

    async def download_version(
        self, template_name: str, version: str, repository: str = None
    ) -> Path:
        """Download a specific template version to a temporary directory."""
        template = await self.marketplace.get_template(template_name, repository)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        repo = self.marketplace.get_repository(template.repository)
        if not repo:
            raise ValueError(f"Repository {template.repository} not found")

        # Create temp directory for new version
        temp_dir = Path(tempfile.mkdtemp(prefix=f"policystack_upgrade_{template_name}_"))

        # Download template files using git handler
        if repo.is_git:

            git_handler = GitRepositoryHandler(self.marketplace.cache_dir)

            success, template_dir, message = git_handler.get_template_files(
                url=repo.url,
                template_path=template.path,
                version=version,
                branch=repo.branch,
                auth_token=repo.auth_token,
            )

            if not success or not template_dir:
                shutil.rmtree(temp_dir)
                raise Exception(f"Failed to download template: {message}")

            # Move files to our temp directory
            shutil.copytree(template_dir, temp_dir, dirs_exist_ok=True)
            shutil.rmtree(template_dir)

        return temp_dir

    def merge_template_versions(
        self, base_version_path: Path, local_element_path: Path, remote_version_path: Path
    ) -> TemplateMergeResult:
        """
        Merge template versions using industry-standard algorithms.
        """
        return self.merger.merge_template_directory(
            base_version_path, local_element_path, remote_version_path
        )

    def apply_merge_results(
        self, element_path: Path, merge_result: TemplateMergeResult, remote_version_path: Path
    ):
        """
        Apply merged results to element directory.
        """
        # Create backup first
        backup_path = element_path.parent / f".{element_path.name}.backup"
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(element_path, backup_path)

        try:
            # Save all merged files
            self.merger.save_merge_results(merge_result, element_path)

            # Copy any remote-only files that don't exist locally
            self._copy_new_files(remote_version_path, element_path)

            # Preserve local element name in Chart.yaml
            self._preserve_chart_name(element_path)

            # Remove backup if successful
            if backup_path.exists():
                shutil.rmtree(backup_path)

        except Exception as e:
            # Restore from backup on failure
            self.console.print(f"[red]Error during upgrade, restoring backup...[/red]")
            if element_path.exists():
                shutil.rmtree(element_path)
            if backup_path.exists():
                shutil.move(backup_path, element_path)
            raise e

    def _copy_new_files(self, remote_path: Path, local_path: Path):
        """Copy files that only exist in remote version."""
        # Copy new converter files
        remote_converters = remote_path / "converters"
        local_converters = local_path / "converters"
        if remote_converters.exists():
            local_converters.mkdir(exist_ok=True)
            for remote_file in remote_converters.glob("*.yaml"):
                local_file = local_converters / remote_file.name
                if not local_file.exists():
                    shutil.copy2(remote_file, local_file)

        # Always update templates directory (usually no local changes)
        remote_templates = remote_path / "templates"
        local_templates = local_path / "templates"
        if remote_templates.exists():
            if local_templates.exists():
                shutil.rmtree(local_templates)
            shutil.copytree(remote_templates, local_templates)

        # Update examples
        remote_examples = remote_path / "examples"
        local_examples = local_path / "examples"
        if remote_examples.exists():
            if local_examples.exists():
                shutil.rmtree(local_examples)
            shutil.copytree(remote_examples, local_examples)

    def _preserve_chart_name(self, element_path: Path):
        """Ensure Chart.yaml has the correct element name."""
        chart_path = element_path / "Chart.yaml"
        if chart_path.exists():
            with open(chart_path, "r") as f:
                chart_data = yaml.safe_load(f)

            # Set name to match directory
            chart_data["name"] = element_path.name

            with open(chart_path, "w") as f:
                yaml.dump(chart_data, f, default_flow_style=False, sort_keys=False)


@click.command()
@click.argument("element_name")
@click.option(
    "--to-version",
    "-v",
    help="Target version to upgrade to (defaults to latest)",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    help="PolicyStack project path",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force upgrade even if not on upgrade path",
)
@click.option(
    "--auto-resolve",
    is_flag=True,
    help="Automatically resolve conflicts where possible",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be upgraded without making changes",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.pass_obj
def upgrade(
    ctx,
    element_name: str,
    to_version: Optional[str],
    path: Optional[Path],
    force: bool,
    auto_resolve: bool,
    dry_run: bool,
    yes: bool,
) -> None:
    """
    Upgrade an installed template to a newer version.

    Intelligently merges local changes with new template version,
    detecting conflicts and providing resolution options.

    Examples:

    \b
        # Upgrade to latest version
        policystack upgrade openshift-logging

    \b
        # Upgrade to specific version
        policystack upgrade openshift-logging --to-version 1.2.0

    \b
        # Dry run to preview changes
        policystack upgrade openshift-logging --dry-run

    \b
        # Auto-resolve conflicts where possible
        policystack upgrade openshift-logging --auto-resolve
    """
    console: Console = ctx.console
    marketplace = ctx.marketplace

    # Determine stack path
    if path:
        stack_path = path / "stack"
    else:
        stack_path = Path.cwd() / "stack"

    element_path = stack_path / element_name

    if not element_path.exists():
        console.print(f"[red]Element '{element_name}' not found at {element_path}[/red]")
        return

    # Initialize change detector
    detector = ChangeDetector(element_path)

    # Initialize backup manager
    backup_manager = BackupManager(element_path)

    # Load current version from snapshot
    snapshot_path = element_path / ".policystack" / "snapshots" / "baseline.json"
    if not snapshot_path.exists():
        console.print(
            "[red]Cannot determine current version. Was this template properly installed?[/red]"
        )
        console.print("\n[yellow]Creating baseline snapshot from current state...[/yellow]")

        # Try to determine version from Chart.yaml
        chart_path = element_path / "Chart.yaml"
        if chart_path.exists():
            with open(chart_path, "r") as f:
                chart = yaml.safe_load(f)
                version = chart.get("appVersion", "0.0.0")
        else:
            version = "unknown"

        baseline = detector.capture_baseline(version)
        console.print(f"[green]✓ Created baseline snapshot (version: {version})[/green]")
    else:
        baseline = TemplateSnapshot.load(snapshot_path)

    current_version = baseline.version

    async def get_and_upgrade():
        # Get template metadata
        template = await marketplace.get_template(element_name)
        if not template:
            raise ValueError(f"Template '{element_name}' not found in marketplace")

        # Determine target version
        target_version = to_version or template.latest_version

        # Get version details
        target_version_details = template.metadata.get_version_details(target_version)
        if not target_version_details:
            raise ValueError(f"Version {target_version} not found")

        # Check upgrade path
        if hasattr(target_version_details, "can_upgrade_from"):
            can_upgrade, reason = target_version_details.can_upgrade_from(current_version)
        else:
            can_upgrade, reason = True, "No upgrade constraints defined"

        if not can_upgrade and not force:
            raise ValueError(f"Cannot upgrade: {reason}\nUse --force to override")

        # Detect local changes
        console.print("\n[bold]Analyzing local changes...[/bold]")
        changes = detector.detect_changes()
        values_changes = detector.detect_values_changes()

        # Display upgrade plan
        console.print(
            Panel.fit(
                f"[bold]Upgrade Plan[/bold]\n"
                f"Element: {element_name}\n"
                f"Current: {current_version} → Target: {target_version}\n"
                f"Local modifications: {len(changes['modified'])} files\n"
                f"Local additions: {len(changes['added'])} files\n"
                f"Deletions: {len(changes['deleted'])} files",
                border_style="cyan",
            )
        )

        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No changes will be made[/yellow]")

            if changes["modified"]:
                console.print("\n[bold]Files with local changes to merge:[/bold]")
                for change in changes["modified"]:
                    rel_path = change.path.relative_to(element_path)
                    console.print(f"  • {rel_path}")
                    if "values.yaml" in str(rel_path):
                        console.print(
                            f"    [dim]Values changes: {len(values_changes.get('changed', {}))} fields[/dim]"
                        )

            if changes["added"]:
                console.print("\n[bold]Local files to preserve:[/bold]")
                for change in changes["added"]:
                    console.print(f"  • {change.path.relative_to(element_path)}")

            if changes["deleted"]:
                console.print("\n[bold]Deleted files:[/bold]")
                for change in changes["deleted"]:
                    console.print(f"  • {change.path.relative_to(element_path)}")

            return  # Exit here for dry run

        # Confirm upgrade
        if not yes:
            if not Confirm.ask("\n[bold]Proceed with upgrade?[/bold]", default=True):
                console.print("[yellow]Upgrade cancelled[/yellow]")
                return

        # Perform upgrade
        upgrader = TemplateUpgrader(marketplace, console)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Create backup before upgrade
            console.print("\n[cyan]Creating backup before upgrade...[/cyan]")
            backup_metadata = backup_manager.create_backup(
                backup_type=BackupType.UPGRADE,
                from_version=current_version,
                to_version=target_version,
                reason=f"Automatic backup before upgrade to {target_version}",
                has_conflicts=False,
            )
            console.print(f"[green]✓ Backup created: {backup_metadata.backup_id}[/green]")

            task = progress.add_task("Performing upgrade...", total=5)

            # Step 1: Download new version
            progress.update(task, description=f"Downloading version {target_version}...")
            remote_version_path = await upgrader.download_version(
                element_name, target_version, template.repository
            )
            progress.advance(task)

            # Step 2: Download base version for three-way merge
            progress.update(task, description=f"Downloading base version {current_version}...")

            base_version_path = None
            try:
                base_version_path = await upgrader.download_version(
                    element_name, current_version, template.repository
                )
            except Exception as e:
                console.print(
                    f"[yellow]⚠ Cannot download base version {current_version}: {e}[/yellow]"
                )

                # Try to reconstruct base from snapshot
                if baseline and baseline.metadata:
                    console.print(
                        "[yellow]Attempting to reconstruct base from snapshot...[/yellow]"
                    )
                    base_version_path = Path(
                        tempfile.mkdtemp(prefix=f"policystack_base_{element_name}_")
                    )

                    # Create a minimal base with just values.yaml from snapshot metadata
                    if "values" in baseline.metadata:
                        values_file = base_version_path / "values.yaml"
                        values_file.parent.mkdir(parents=True, exist_ok=True)

                        # Write the original values from snapshot
                        with open(values_file, "w") as f:
                            yaml.dump(
                                baseline.metadata["values"],
                                f,
                                default_flow_style=False,
                                sort_keys=False,
                            )

                    # Copy other files from current for structure
                    if baseline.files:
                        for file_rel_path in baseline.files:
                            file_path = element_path / file_rel_path
                            base_file_path = base_version_path / file_rel_path

                            if file_path.exists() and "values.yaml" not in str(file_path):
                                base_file_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, base_file_path)
                else:
                    # No snapshot - warn user
                    console.print(
                        "[red]⚠ WARNING: Cannot determine base version![/red]\n"
                        "[yellow]This will do a 2-way merge (current vs incoming).[/yellow]\n"
                        "[yellow]Conflict detection may be less accurate.[/yellow]"
                    )
                    # Use empty base
                    base_version_path = Path(tempfile.mkdtemp(prefix=f"policystack_base_empty_"))

            progress.advance(task)

            # Step 3: Perform merge
            progress.update(task, description="Merging changes...")

            merge_result = upgrader.merge_template_versions(
                base_version_path, element_path, remote_version_path
            )

            # Show merge summary
            console.print(f"\n[dim]Merge summary:[/dim]")
            console.print(f"[dim]  Total conflicts: {merge_result.total_conflicts}[/dim]")
            if merge_result.values_result:
                console.print(
                    f"[dim]  values.yaml: {'HAS CONFLICTS' if merge_result.values_result.has_conflicts else 'clean merge'}[/dim]"
                )
            if merge_result.chart_result:
                console.print(
                    f"[dim]  Chart.yaml: {'HAS CONFLICTS' if merge_result.chart_result.has_conflicts else 'clean merge'}[/dim]"
                )
            if merge_result.converter_results:
                for name, result in merge_result.converter_results.items():
                    status = (
                        f"HAS CONFLICTS ({result.conflict_count})"
                        if result.has_conflicts
                        else "clean merge"
                    )
                    console.print(f"[dim]  converters/{name}: {status}[/dim]")

            progress.advance(task)

            # Step 4: Handle conflicts if any
            if merge_result.has_conflicts:
                # Update backup to note conflicts
                backup_metadata.has_conflicts = True
                backup_manager._save_metadata(backup_metadata.backup_id, backup_metadata)

                progress.update(task, description="Detected conflicts...")

                console.print(
                    f"\n[yellow]⚠ Found {merge_result.total_conflicts} conflicts that need resolution[/yellow]"
                )

                if merge_result.values_result and merge_result.values_result.has_conflicts:
                    console.print("\n[bold yellow]values.yaml has conflicts![/bold yellow]")

                if merge_result.converter_results:
                    converter_conflicts = [
                        name
                        for name, result in merge_result.converter_results.items()
                        if result.has_conflicts
                    ]
                    if converter_conflicts:
                        console.print(f"\n[bold yellow]Converters with conflicts:[/bold yellow]")
                        for name in converter_conflicts:
                            console.print(f"  • {name}")

                # Ask user if they want to continue
                if not auto_resolve and not yes:
                    proceed = Confirm.ask(
                        "\n[bold]Files will be saved with conflict markers. Continue?[/bold]",
                        default=True,
                    )
                    if not proceed:
                        console.print("[yellow]Upgrade cancelled[/yellow]")
                        # Cleanup
                        if remote_version_path and remote_version_path != element_path:
                            shutil.rmtree(remote_version_path, ignore_errors=True)
                        if base_version_path and base_version_path != element_path:
                            shutil.rmtree(base_version_path, ignore_errors=True)
                        return

            progress.advance(task)

            # Step 5: Apply upgrade
            progress.update(task, description="Applying upgrade...")

            upgrader.apply_merge_results(element_path, merge_result, remote_version_path)

            # Update baseline snapshot
            new_snapshot = TemplateSnapshot(element_path, target_version)

            # Warn if snapshot contains files with conflicts
            if new_snapshot.metadata.get("values_has_conflicts") or new_snapshot.metadata.get(
                "chart_has_conflicts"
            ):
                console.print(
                    "\n[yellow]Note: Baseline snapshot created but contains files with unresolved conflicts.[/yellow]"
                    "\n[yellow]The snapshot will be updated automatically when conflicts are resolved.[/yellow]"
                )

            new_snapshot.save(snapshot_path)

            # Cleanup temp directories
            if remote_version_path and remote_version_path != element_path:
                shutil.rmtree(remote_version_path, ignore_errors=True)
            if base_version_path and base_version_path != element_path:
                shutil.rmtree(base_version_path, ignore_errors=True)

            progress.advance(task)

        if merge_result.has_conflicts:
            # Upgrade completed but with conflicts
            console.print(f"\n[dim]Backup ID: {backup_metadata.backup_id}[/dim]")
            console.print(f"[dim]To rollback: policystack rollback {element_name}[/dim]")
            console.print(
                f"\n[yellow]⚡ Upgrade to {target_version} completed with conflicts[/yellow]"
            )
            console.print(
                f"[yellow]⚠ {merge_result.total_conflicts} conflicts need manual resolution[/yellow]"
            )
            console.print("\nConflicts are marked in the files with:")
            console.print("  <<<<<<< current    (your current version)")
            console.print("  =======            (separator)")
            console.print("  >>>>>>> incoming   (new template version)")
            console.print("\n[bold]To resolve:[/bold]")
            console.print("  1. Open the conflicted files")
            console.print("  2. Search for '<<<<<<< current'")
            console.print("  3. Choose which version to keep (or combine them)")
            console.print("  4. Remove the conflict markers")
            console.print("  5. Test your configuration")
        else:
            # Clean upgrade
            console.print(f"\n[dim]Backup ID: {backup_metadata.backup_id}[/dim]")
            console.print(f"[dim]To rollback: policystack rollback {element_name}[/dim]")
            console.print(
                f"\n[green]✓ Successfully upgraded {element_name} to {target_version}[/green]"
            )

        # Show post-upgrade instructions
        if hasattr(target_version_details, "upgrade") and target_version_details.upgrade:
            if target_version_details.upgrade.post_upgrade_hook:
                console.print(
                    f"\n[bold]Post-upgrade steps required:[/bold]\n"
                    f"Run: {target_version_details.upgrade.post_upgrade_hook}"
                )

    try:
        asyncio.run(get_and_upgrade())
    except Exception as e:
        console.print(f"[red]Upgrade failed: {e}[/red]")
        if ctx.debug:
            console.print_exception()
