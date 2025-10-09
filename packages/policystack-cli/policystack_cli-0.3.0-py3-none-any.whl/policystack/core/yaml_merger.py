"""YAML-aware merging with structure and comment preservation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from .file_merger import FileMerger, MergeResult


@dataclass
class YAMLConflict:
    """Represents a YAML merge conflict."""

    path: str
    base_value: Any
    local_value: Any
    remote_value: Any
    resolved: bool = False
    resolution: Optional[str] = None  # 'local', 'remote', or 'manual'


@dataclass
class YAMLMergeResult:
    """Result of YAML merge operation."""

    data: Union[CommentedMap, str]  # Can be parsed YAML or text with conflict markers
    conflicts: List[YAMLConflict] = field(default_factory=list)
    has_conflicts: bool = False

    @property
    def conflict_count(self) -> int:
        """Get number of conflicts."""
        return len(self.conflicts)


class YAMLMerger:
    """YAML merger that preserves structure, comments, and formatting."""

    def __init__(self):
        """Initialize YAML merger."""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 4096  # Prevent line wrapping
        self.yaml.indent(mapping=2, sequence=2, offset=0)
        self.file_merger = FileMerger()

    def merge_yaml_files(
        self, base_path: Path, local_path: Path, remote_path: Path
    ) -> YAMLMergeResult:
        """
        Merge YAML files using text-based merge then parse result.

        This approach:
        1. Uses standard merge algorithms (git merge-file/diff3)
        2. Preserves YAML formatting and comments
        3. Produces standard conflict markers that users understand

        Args:
            base_path: Path to base version
            local_path: Path to local version
            remote_path: Path to remote version

        Returns:
            YAMLMergeResult with merged data and conflicts
        """
        # Perform text-based merge
        merge_result = self.file_merger.merge_file_paths(base_path, local_path, remote_path)

        if not merge_result.has_conflicts:
            # Clean merge - parse the result
            try:
                merged_data = self.yaml.load(merge_result.content)
                return YAMLMergeResult(data=merged_data or CommentedMap(), has_conflicts=False)
            except Exception:
                # Parse error in merged result - treat as conflict
                # Load local as fallback
                with open(local_path, "r") as f:
                    local_data = self.yaml.load(f)

                return YAMLMergeResult(
                    data=local_data or CommentedMap(),
                    has_conflicts=True,
                    conflicts=[
                        YAMLConflict(
                            path="<root>",
                            base_value=None,
                            local_value=local_data,
                            remote_value=None,
                        )
                    ],
                )
        else:
            # Has conflicts - need to extract and preserve them
            return self._handle_conflicted_yaml(merge_result, base_path, local_path, remote_path)

    def _handle_conflicted_yaml(
        self, merge_result: MergeResult, base_path: Path, local_path: Path, remote_path: Path
    ) -> YAMLMergeResult:
        """
        Handle YAML with conflict markers.

        Strategy:
        1. Save the text merge result with standard conflict markers
        2. Parse each version to provide conflict context
        3. Let users manually resolve using standard git workflow
        """
        # Load each version separately for conflict analysis
        with open(base_path, "r") as f:
            base_data = self.yaml.load(f) if base_path.exists() else CommentedMap()
        with open(local_path, "r") as f:
            local_data = self.yaml.load(f) or CommentedMap()
        with open(remote_path, "r") as f:
            remote_data = self.yaml.load(f) or CommentedMap()

        # Extract conflicts by comparing structures
        conflicts = self._extract_conflicts(base_data, local_data, remote_data)

        # Return the merge result text as-is
        # It will be saved with conflict markers by save_with_conflict_markers
        return YAMLMergeResult(
            data=merge_result.content,  # Keep the text with markers
            has_conflicts=True,
            conflicts=conflicts,
        )

    def _extract_conflicts(
        self, base: Any, local: Any, remote: Any, path: str = ""
    ) -> List[YAMLConflict]:
        """
        Recursively extract conflicts between versions.

        A conflict exists when both local and remote differ from base
        and also differ from each other.
        """
        conflicts = []

        # If values are identical, no conflict
        if local == remote:
            return conflicts

        # Handle dictionaries
        if isinstance(local, (dict, CommentedMap)) and isinstance(remote, (dict, CommentedMap)):
            base_dict = base if isinstance(base, (dict, CommentedMap)) else {}

            all_keys = set(local.keys()) | set(remote.keys())

            for key in all_keys:
                key_path = f"{path}.{key}" if path else str(key)

                local_val = local.get(key)
                remote_val = remote.get(key)
                base_val = base_dict.get(key)

                if key in local and key in remote:
                    # Both have the key - check for conflicts recursively
                    sub_conflicts = self._extract_conflicts(
                        base_val, local_val, remote_val, key_path
                    )
                    conflicts.extend(sub_conflicts)
                elif key in local:
                    # Only in local
                    if base_val is not None:
                        # Was in base but removed in remote
                        conflicts.append(
                            YAMLConflict(
                                path=key_path,
                                base_value=base_val,
                                local_value=local_val,
                                remote_value=None,
                            )
                        )
                else:
                    # Only in remote
                    if base_val is not None:
                        # Was in base but removed in local
                        conflicts.append(
                            YAMLConflict(
                                path=key_path,
                                base_value=base_val,
                                local_value=None,
                                remote_value=remote_val,
                            )
                        )

            return conflicts

        # Handle lists
        if isinstance(local, (list, CommentedSeq)) and isinstance(remote, (list, CommentedSeq)):
            # For lists, if they differ, it's a conflict
            base_list = base if isinstance(base, (list, CommentedSeq)) else []

            if local != base and remote != base and local != remote:
                conflicts.append(
                    YAMLConflict(
                        path=path, base_value=base_list, local_value=local, remote_value=remote
                    )
                )

            return conflicts

        # Scalar values
        if local != remote:
            # Check if both changed from base
            if local != base and remote != base:
                conflicts.append(
                    YAMLConflict(path=path, base_value=base, local_value=local, remote_value=remote)
                )

        return conflicts

    def merge_yaml_content(
        self, base_content: str, local_content: str, remote_content: str
    ) -> YAMLMergeResult:
        """
        Merge YAML content strings.

        Args:
            base_content: Base YAML content
            local_content: Local YAML content
            remote_content: Remote YAML content

        Returns:
            YAMLMergeResult with merged data
        """
        # Perform text merge
        merge_result = self.file_merger.merge_files(
            base_content,
            local_content,
            remote_content,
            base_label="base",
            local_label="local",
            remote_label="remote",
        )

        if not merge_result.has_conflicts:
            # Clean merge
            try:
                merged_data = self.yaml.load(merge_result.content)
                return YAMLMergeResult(data=merged_data or CommentedMap(), has_conflicts=False)
            except Exception:
                # Parse error - return local
                local_data = self.yaml.load(local_content)
                return YAMLMergeResult(data=local_data or CommentedMap(), has_conflicts=True)
        else:
            # Has conflicts
            base_data = self.yaml.load(base_content) or CommentedMap()
            local_data = self.yaml.load(local_content) or CommentedMap()
            remote_data = self.yaml.load(remote_content) or CommentedMap()

            conflicts = self._extract_conflicts(base_data, local_data, remote_data)

            return YAMLMergeResult(data=local_data, has_conflicts=True, conflicts=conflicts)

    def save_yaml(self, data: Any, path: Path) -> None:
        """Save YAML data preserving formatting."""
        with open(path, "w") as f:
            self.yaml.dump(data, f)

    def save_with_conflict_markers(self, merge_result: MergeResult, path: Path) -> None:
        """
        Save merged content with conflict markers.

        This creates a file with standard git-style conflict markers
        that users can resolve manually.
        """
        path.write_text(merge_result.content)
