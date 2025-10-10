"""Template file merging using git related merge methods"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .file_merger import FileMerger, MergeResult
from .yaml_merger import YAMLConflict, YAMLMerger, YAMLMergeResult


@dataclass
class TemplateMergeResult:
    """Complete result of template file merge."""

    # Merged files
    values_result: Optional[YAMLMergeResult] = None
    chart_result: Optional[YAMLMergeResult] = None
    converter_results: Dict[str, MergeResult] = None
    template_results: Dict[str, MergeResult] = None

    # Overall status
    has_conflicts: bool = False
    total_conflicts: int = 0

    def __post_init__(self):
        """Calculate overall status."""
        if self.converter_results is None:
            self.converter_results = {}
        if self.template_results is None:
            self.template_results = {}

        # Count total conflicts
        conflicts = 0
        has_conflict = False

        if self.values_result and self.values_result.has_conflicts:
            conflicts += self.values_result.conflict_count
            has_conflict = True

        if self.chart_result and self.chart_result.has_conflicts:
            conflicts += self.chart_result.conflict_count
            has_conflict = True

        for result in self.converter_results.values():
            if result.has_conflicts:
                conflicts += result.conflict_count
                has_conflict = True

        for result in self.template_results.values():
            if result.has_conflicts:
                conflicts += result.conflict_count
                has_conflict = True

        self.total_conflicts = conflicts
        self.has_conflicts = has_conflict


class TemplateMerger:
    """
    Merges PolicyStack template files using industry-standard algorithms.

    This class handles the complete merge workflow for template upgrades:
    - values.yaml: YAML-aware merge preserving comments
    - Chart.yaml: YAML merge with validation
    - converters/*.yaml: Helm template-aware text merge
    - templates/*.yaml: Helm template-aware text merge
    """

    def __init__(self):
        """Initialize the template merger."""
        self.file_merger = FileMerger()
        self.yaml_merger = YAMLMerger()

    def merge_template_directory(
        self, base_dir: Path, local_dir: Path, remote_dir: Path
    ) -> TemplateMergeResult:
        """
        Merge entire template directory structure.

        Args:
            base_dir: Base version directory
            local_dir: Local (current) version directory
            remote_dir: Remote (incoming) version directory

        Returns:
            TemplateMergeResult with all merge results
        """
        result = TemplateMergeResult()

        # Merge values.yaml
        values_base = base_dir / "values.yaml"
        values_local = local_dir / "values.yaml"
        values_remote = remote_dir / "values.yaml"

        if values_local.exists() and values_remote.exists():
            result.values_result = self.yaml_merger.merge_yaml_files(
                values_base if values_base.exists() else values_local, values_local, values_remote
            )

        # Merge Chart.yaml
        chart_base = base_dir / "Chart.yaml"
        chart_local = local_dir / "Chart.yaml"
        chart_remote = remote_dir / "Chart.yaml"

        if chart_local.exists() and chart_remote.exists():
            result.chart_result = self.yaml_merger.merge_yaml_files(
                chart_base if chart_base.exists() else chart_local, chart_local, chart_remote
            )

        # Merge converters
        converters_local = local_dir / "converters"
        converters_remote = remote_dir / "converters"
        converters_base = base_dir / "converters"

        if converters_local.exists() or converters_remote.exists():
            result.converter_results = self._merge_directory_files(
                converters_base if converters_base.exists() else converters_local,
                converters_local,
                converters_remote,
            )

        # Merge templates
        templates_local = local_dir / "templates"
        templates_remote = remote_dir / "templates"
        templates_base = base_dir / "templates"

        if templates_local.exists() or templates_remote.exists():
            result.template_results = self._merge_directory_files(
                templates_base if templates_base.exists() else templates_local,
                templates_local,
                templates_remote,
            )

        return result

    def _merge_directory_files(
        self, base_dir: Path, local_dir: Path, remote_dir: Path
    ) -> Dict[str, MergeResult]:
        """
        Merge all files in a directory.

        Args:
            base_dir: Base version directory
            local_dir: Local directory
            remote_dir: Remote directory

        Returns:
            Dict mapping filename to MergeResult
        """
        results = {}

        # Get all files
        local_files = set()
        remote_files = set()

        if local_dir.exists():
            local_files = {f.name for f in local_dir.glob("*.yaml")}
        if remote_dir.exists():
            remote_files = {f.name for f in remote_dir.glob("*.yaml")}

        all_files = local_files | remote_files

        for filename in all_files:
            base_file = base_dir / filename if base_dir.exists() else None
            local_file = local_dir / filename if local_dir.exists() else None
            remote_file = remote_dir / filename if remote_dir.exists() else None

            # Read contents
            base_content = ""
            local_content = ""
            remote_content = ""

            if base_file and base_file.exists():
                base_content = base_file.read_text(encoding="utf-8")
            if local_file and local_file.exists():
                local_content = local_file.read_text(encoding="utf-8")
            if remote_file and remote_file.exists():
                remote_content = remote_file.read_text(encoding="utf-8")

            # Merge as text (works for Helm templates with {{}} syntax)
            merge_result = self.file_merger.merge_files(
                base_content,
                local_content,
                remote_content,
                base_label="base",
                local_label=filename,
                remote_label="incoming",
            )

            results[filename] = merge_result

        return results

    def save_merge_results(self, result: TemplateMergeResult, output_dir: Path) -> None:
        """
        Save merge results to output directory.

        Args:
            result: Merge results to save
            output_dir: Directory to write merged files
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save values.yaml
        if result.values_result:
            values_path = output_dir / "values.yaml"
            if result.values_result.has_conflicts:
                # Save with conflict markers (data is the raw text)
                if isinstance(result.values_result.data, str):
                    # Add helpful header
                    conflict_help = [
                        "# ============================================",
                        "# MERGE CONFLICTS - MANUAL RESOLUTION NEEDED",
                        "# ============================================",
                        "#",
                        "# This file contains merge conflicts marked with:",
                        "#   <<<<<<< current    (your current version)",
                        "#   =======            (separator)",
                        "#   >>>>>>> incoming   (new template version)",
                        "#",
                        "# To resolve:",
                        "#   1. Search for '<<<<<<< current'",
                        "#   2. Choose which version to keep (or combine them)",
                        "#   3. Remove the conflict markers",
                        "#   4. Test your configuration",
                        "#",
                        "# ============================================",
                        "",
                    ]
                    content = "\n".join(conflict_help) + result.values_result.data
                    values_path.write_text(content, encoding="utf-8")
                else:
                    # Fallback: save as YAML
                    self.yaml_merger.save_yaml(result.values_result.data, values_path)
            else:
                # Clean merge - save parsed YAML
                self.yaml_merger.save_yaml(result.values_result.data, values_path)

        # Save Chart.yaml
        if result.chart_result:
            chart_path = output_dir / "Chart.yaml"
            if result.chart_result.has_conflicts:
                # Save with conflict markers
                if isinstance(result.chart_result.data, str):
                    # Add helpful header for Chart.yaml too
                    conflict_help = [
                        "# ============================================",
                        "# MERGE CONFLICTS - MANUAL RESOLUTION NEEDED",
                        "# ============================================",
                        "# Resolve conflicts marked with <<<<<<< current and >>>>>>> incoming",
                        "",
                    ]
                    content = "\n".join(conflict_help) + result.chart_result.data
                    chart_path.write_text(content, encoding="utf-8")
                else:
                    self.yaml_merger.save_yaml(result.chart_result.data, chart_path)
            else:
                self.yaml_merger.save_yaml(result.chart_result.data, chart_path)

        # Save converters
        if result.converter_results:
            converters_dir = output_dir / "converters"
            converters_dir.mkdir(exist_ok=True)

            for filename, merge_result in result.converter_results.items():
                file_path = converters_dir / filename
                if merge_result.has_conflicts:
                    # Add conflict help header to converters too
                    conflict_help = [
                        "# ============================================",
                        "# MERGE CONFLICTS - MANUAL RESOLUTION NEEDED",
                        "# ============================================",
                        "# Resolve conflicts between <<<<<<< and >>>>>>>",
                        "",
                    ]
                    content = "\n".join(conflict_help) + merge_result.content
                    file_path.write_text(content, encoding="utf-8")
                else:
                    file_path.write_text(merge_result.content, encoding="utf-8")

        # Save templates
        if result.template_results:
            templates_dir = output_dir / "templates"
            templates_dir.mkdir(exist_ok=True)

            for filename, merge_result in result.template_results.items():
                file_path = templates_dir / filename
                file_path.write_text(merge_result.content, encoding="utf-8")


# Backwards compatibility exports
MergeConflict = YAMLConflict


def merge_values_files(
    base_path: Path, local_path: Path, remote_path: Path
) -> Tuple[YAMLMergeResult, List[YAMLConflict]]:
    """
    Convenience function to merge values.yaml files.

    Args:
        base_path: Path to base values.yaml
        local_path: Path to local values.yaml
        remote_path: Path to remote values.yaml

    Returns:
        Tuple of (YAMLMergeResult, conflicts list)
    """
    merger = YAMLMerger()
    result = merger.merge_yaml_files(base_path, local_path, remote_path)
    return result, result.conflicts
