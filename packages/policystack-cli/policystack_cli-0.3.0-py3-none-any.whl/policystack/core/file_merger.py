"""File merging utilities"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from merge3 import Merge3


@dataclass
class MergeResult:
    """Result of a merge operation."""

    content: str
    has_conflicts: bool
    conflict_count: int
    base_label: Optional[str] = None
    local_label: Optional[str] = None
    remote_label: Optional[str] = None


class FileMerger:
    """Python file merger using the merge3 library (diff3 algorithm)."""

    def merge_files(
        self,
        base_content: str,
        local_content: str,
        remote_content: str,
        base_label: str = "base",
        local_label: str = "current",
        remote_label: str = "incoming",
    ) -> MergeResult:
        """
        Perform three-way merge of file contents using merge3.

        Args:
            base_content: Common ancestor content
            local_content: Local (current) content
            remote_content: Remote (incoming) content
            base_label: Label for base version in conflicts
            local_label: Label for local version in conflicts
            remote_label: Label for remote version in conflicts

        Returns:
            MergeResult with merged content and conflict information
        """
        # Split into lines
        base_lines = base_content.splitlines(keepends=True)
        local_lines = local_content.splitlines(keepends=True)
        remote_lines = remote_content.splitlines(keepends=True)

        # Perform three-way merge
        m3 = Merge3(base_lines, local_lines, remote_lines)

        # Generate merged output with conflict markers
        merged_lines = []
        has_conflicts = False
        conflict_count = 0

        for group in m3.merge_groups():
            if group[0] == "conflict":
                has_conflicts = True
                conflict_count += 1

                # Add git-style conflict markers
                merged_lines.append(f"<<<<<<< {local_label}\n")
                merged_lines.extend(group[1])  # local lines
                merged_lines.append("=======\n")
                merged_lines.extend(group[3])  # remote lines
                merged_lines.append(f">>>>>>> {remote_label}\n")
            else:
                # Clean merge - use the merged lines
                merged_lines.extend(group[1])

        merged_content = "".join(merged_lines)

        return MergeResult(
            content=merged_content,
            has_conflicts=has_conflicts,
            conflict_count=conflict_count,
            base_label=base_label,
            local_label=local_label,
            remote_label=remote_label,
        )

    def merge_file_paths(self, base_path: Path, local_path: Path, remote_path: Path) -> MergeResult:
        """
        Merge files from paths.

        Args:
            base_path: Path to base version
            local_path: Path to local version
            remote_path: Path to remote version

        Returns:
            MergeResult with merged content
        """
        base_content = base_path.read_text(encoding="utf-8") if base_path.exists() else ""
        local_content = local_path.read_text(encoding="utf-8") if local_path.exists() else ""
        remote_content = remote_path.read_text(encoding="utf-8") if remote_path.exists() else ""

        return self.merge_files(
            base_content,
            local_content,
            remote_content,
            base_label=base_path.name if base_path.exists() else "base",
            local_label="current",
            remote_label="incoming",
        )
