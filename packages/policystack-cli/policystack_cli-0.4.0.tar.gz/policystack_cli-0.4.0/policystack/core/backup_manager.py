"""Backup management system for PolicyStack templates."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..models import BackupMetadata, BackupStatus, BackupType


class BackupManager:
    """Manages backups for template upgrades and installations."""

    def __init__(self, element_path: Path):
        """Initialize backup manager for an element."""
        self.element_path = element_path
        self.backup_dir = element_path / ".policystack" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        backup_type: BackupType,
        from_version: str,
        to_version: Optional[str] = None,
        reason: Optional[str] = None,
        has_conflicts: bool = False,
    ) -> BackupMetadata:
        """
        Create a backup of the current element state.

        Args:
            backup_type: Type of backup (upgrade, install, manual)
            from_version: Current version being backed up
            to_version: Target version (for upgrades)
            reason: Human-readable reason for backup
            has_conflicts: Whether this backup is before/after conflicts

        Returns:
            BackupMetadata for the created backup
        """
        timestamp = datetime.now()
        backup_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{from_version}"

        # Create backup directory
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True)

        # Copy all element files
        self._copy_element_files(self.element_path, backup_path)

        # Copy snapshot if exists
        snapshot_dir = self.element_path / ".policystack" / "snapshots"
        if snapshot_dir.exists():
            backup_snapshot_dir = backup_path / ".snapshots"
            backup_snapshot_dir.mkdir()
            for snapshot_file in snapshot_dir.glob("*.json"):
                shutil.copy2(snapshot_file, backup_snapshot_dir / snapshot_file.name)

        # Create metadata
        metadata = BackupMetadata(
            backup_id=backup_id,
            timestamp=timestamp.isoformat(),
            backup_type=backup_type,
            from_version=from_version,
            to_version=to_version,
            reason=reason,
            has_conflicts=has_conflicts,
            status=BackupStatus.ACTIVE,
            element_name=self.element_path.name,
            backup_path=str(backup_path),
        )

        # Save metadata
        self._save_metadata(backup_id, metadata)

        return metadata

    def list_backups(self) -> List[BackupMetadata]:
        """List all available backups."""
        backups = []

        if not self.backup_dir.exists():
            return backups

        for backup_path in sorted(self.backup_dir.iterdir(), reverse=True):
            if backup_path.is_dir():
                metadata_file = backup_path / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = self._load_metadata(backup_path.name)
                        backups.append(metadata)
                    except Exception:
                        # Skip corrupted backups
                        continue

        return backups

    def get_backup(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get metadata for a specific backup."""
        try:
            return self._load_metadata(backup_id)
        except FileNotFoundError:
            return None

    def get_latest_backup(self) -> Optional[BackupMetadata]:
        """Get the most recent backup."""
        backups = self.list_backups()
        return backups[0] if backups else None

    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore element from a backup.

        Args:
            backup_id: ID of backup to restore

        Returns:
            True if restore successful

        Raises:
            FileNotFoundError: If backup doesn't exist
            Exception: If restore fails
        """
        metadata = self.get_backup(backup_id)
        if not metadata:
            raise FileNotFoundError(f"Backup {backup_id} not found")

        backup_path = Path(metadata.backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup files not found at {backup_path}")

        # Create a safety backup of current state before restore
        current_version = self._get_current_version()
        safety_backup = self.create_backup(
            backup_type=BackupType.MANUAL,
            from_version=current_version or "unknown",
            reason=f"Safety backup before restoring {backup_id}",
        )

        try:
            # Clear current element directory (except .policystack)
            self._clear_element_files()

            # Restore files from backup
            self._restore_element_files(backup_path)

            # Restore snapshots
            backup_snapshot_dir = backup_path / ".snapshots"
            if backup_snapshot_dir.exists():
                snapshot_dir = self.element_path / ".policystack" / "snapshots"
                snapshot_dir.mkdir(parents=True, exist_ok=True)
                for snapshot_file in backup_snapshot_dir.glob("*.json"):
                    shutil.copy2(snapshot_file, snapshot_dir / snapshot_file.name)

            # Update metadata
            metadata.status = BackupStatus.RESTORED
            metadata.restored_at = datetime.now().isoformat()
            self._save_metadata(backup_id, metadata)

            # Mark safety backup as used
            safety_metadata = self.get_backup(safety_backup.backup_id)
            if safety_metadata:
                safety_metadata.status = BackupStatus.SUPERSEDED
                self._save_metadata(safety_backup.backup_id, safety_metadata)

            return True

        except Exception as e:
            # Restore failed - try to restore safety backup
            try:
                self._restore_element_files(Path(safety_backup.backup_path))
            except Exception:
                pass  # Double failure - element may be corrupted

            raise Exception(f"Restore failed: {e}")

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        metadata = self.get_backup(backup_id)
        if not metadata:
            return False

        backup_path = Path(metadata.backup_path)
        if backup_path.exists():
            shutil.rmtree(backup_path)

        return True

    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Clean up old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of backups to keep

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()
        deleted = 0

        # Sort by timestamp (newest first)
        backups.sort(key=lambda b: b.timestamp, reverse=True)

        # Keep only the specified number
        for backup in backups[keep_count:]:
            if backup.status not in [BackupStatus.RESTORED, BackupStatus.ACTIVE]:
                # Don't delete currently active backups or recently restored ones
                continue

            if self.delete_backup(backup.backup_id):
                deleted += 1

        return deleted

    def _copy_element_files(self, src: Path, dst: Path) -> None:
        """Copy element files, excluding .policystack directory."""
        for item in src.iterdir():
            if item.name == ".policystack":
                continue

            if item.is_dir():
                shutil.copytree(item, dst / item.name, symlinks=False)
            else:
                shutil.copy2(item, dst / item.name)

    def _restore_element_files(self, backup_path: Path) -> None:
        """Restore element files from backup."""
        for item in backup_path.iterdir():
            if item.name in [".snapshots", "metadata.json"]:
                continue

            dst = self.element_path / item.name

            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst, symlinks=False)
            else:
                shutil.copy2(item, dst)

    def _clear_element_files(self) -> None:
        """Clear element files, preserving .policystack directory."""
        for item in self.element_path.iterdir():
            if item.name == ".policystack":
                continue

            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def _get_current_version(self) -> Optional[str]:
        """Get current version from snapshot."""
        snapshot_path = self.element_path / ".policystack" / "snapshots" / "baseline.json"
        if snapshot_path.exists():
            try:
                with open(snapshot_path, "r") as f:
                    data = json.load(f)
                    return data.get("version")
            except Exception:
                return None
        return None

    def _save_metadata(self, backup_id: str, metadata: BackupMetadata) -> None:
        """Save backup metadata."""
        backup_path = self.backup_dir / backup_id
        metadata_file = backup_path / "metadata.json"

        with open(metadata_file, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2, default=str)

    def _load_metadata(self, backup_id: str) -> BackupMetadata:
        """Load backup metadata."""
        backup_path = self.backup_dir / backup_id
        metadata_file = backup_path / "metadata.json"

        with open(metadata_file, "r") as f:
            data = json.load(f)
            return BackupMetadata.from_dict(data)
