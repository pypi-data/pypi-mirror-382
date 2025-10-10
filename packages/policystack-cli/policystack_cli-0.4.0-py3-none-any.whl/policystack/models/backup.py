"""Backup models for PolicyStack CLI."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BackupType(str, Enum):
    """Type of backup."""

    UPGRADE = "upgrade"
    INSTALL = "install"
    MANUAL = "manual"


class BackupStatus(str, Enum):
    """Status of a backup."""

    ACTIVE = "active"  # Backup is available for restore
    RESTORED = "restored"  # Backup was restored
    SUPERSEDED = "superseded"  # Backup was replaced by newer backup
    ARCHIVED = "archived"  # Backup is old but kept for history


class BackupMetadata(BaseModel):
    """Metadata for a backup."""

    backup_id: str = Field(..., description="Unique backup identifier")
    timestamp: str = Field(..., description="When backup was created")
    backup_type: BackupType = Field(..., description="Type of backup")
    from_version: str = Field(..., description="Version backed up")
    to_version: Optional[str] = Field(None, description="Target version (for upgrades)")
    reason: Optional[str] = Field(None, description="Reason for backup")
    has_conflicts: bool = Field(False, description="Whether backup has unresolved conflicts")
    status: BackupStatus = Field(BackupStatus.ACTIVE, description="Backup status")
    element_name: str = Field(..., description="Element name")
    backup_path: str = Field(..., description="Path to backup files")
    restored_at: Optional[str] = Field(None, description="When backup was restored")
    notes: Optional[str] = Field(None, description="Additional notes")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupMetadata":
        """Create from dictionary."""
        return cls(**data)

    @property
    def display_version(self) -> str:
        """Get display string for version."""
        if self.to_version:
            return f"{self.from_version} → {self.to_version}"
        return self.from_version

    @property
    def display_reason(self) -> str:
        """Get display string for reason."""
        if self.reason:
            return self.reason
        elif self.backup_type == BackupType.UPGRADE:
            return f"Before upgrade to {self.to_version}"
        elif self.backup_type == BackupType.INSTALL:
            return "Before initial installation"
        else:
            return "Manual backup"
