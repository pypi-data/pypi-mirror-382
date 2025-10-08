"""
Path resolution and validation for RBT documents.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-001-PathResolver
"""

import os
from pathlib import Path
from typing import Optional
from glob import glob

from .models import PathInfo


class PathResolver:
    """
    Resolves and validates file paths for RBT documents and general files.

    Supports:
    - RBT standard paths: {root}/{project_id}/features/{feature_id}/{doc_type}-{feature_id}.md
    - TASK paths: {root}/{project_id}/features/{feature_id}/tasks/TASK-{index}-{name}.md
    - General file paths: {root}/{project_id}/docs/{file_path}
    - .new.md priority: Prefers .new.md over .md when both exist
    - TASK partial matching: Resolves TASK-001 to full filename

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-001-PathResolver
    """

    def __init__(self, root_dir: str):
        """
        Initialize PathResolver with root directory.

        Args:
            root_dir: Root directory for all documents
        """
        self.root_dir = root_dir

    def resolve(
        self,
        project_id: str,
        feature_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> PathInfo:
        """
        Resolve document path based on provided parameters.

        Args:
            project_id: Project identifier (required)
            feature_id: Feature identifier (optional, required for RBT docs)
            doc_type: Document type ('REQ', 'BP', 'TASK') for RBT docs
            file_path: Relative path for general files or TASK name

        Returns:
            PathInfo with resolved path information

        Raises:
            ValueError: If invalid parameter combination
            FileNotFoundError: If resolved file doesn't exist

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-001-PathResolver
        """
        # Validate parameters
        if doc_type is None and file_path is None:
            raise ValueError("Either doc_type or file_path must be provided")

        # Handle RBT document types
        if doc_type:
            return self._resolve_rbt_document(project_id, feature_id, doc_type, file_path)

        # Handle general files
        return self._resolve_general_file(project_id, file_path)

    def _resolve_rbt_document(
        self,
        project_id: str,
        feature_id: Optional[str],
        doc_type: str,
        file_path: Optional[str]
    ) -> PathInfo:
        """
        Resolve RBT standard document path.

        @TASK: TASK-001-PathResolver
        """
        # TASK type has special handling
        if doc_type == "TASK":
            return self._resolve_task_document(project_id, feature_id, file_path)

        # REQ and BP types require feature_id
        if not feature_id:
            raise ValueError(f"feature_id is required for doc_type={doc_type}")

        # Build standard RBT path
        base_path = Path(self.root_dir) / project_id / "features" / feature_id
        filename = f"{doc_type}-{feature_id}.md"
        full_path = base_path / filename

        # Check for .new.md version
        resolved_path, is_new_file = self._check_new_md_version(full_path)

        # Verify file exists
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"RBT document not found: {resolved_path}")

        return PathInfo(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=str(resolved_path),
            is_rbt=True,
            is_new_file=is_new_file
        )

    def _resolve_task_document(
        self,
        project_id: str,
        feature_id: Optional[str],
        file_path: Optional[str]
    ) -> PathInfo:
        """
        Resolve TASK document within specified feature with partial matching support.

        Requirements:
        - feature_id: Required, specifies the feature folder
        - file_path: Optional, specifies TASK identifier with partial matching support
                    Examples: "014" → TASK-014-*.md, "014-CreateDocumentTool" → TASK-014-CreateDocumentTool.md
                    If not provided, returns error

        Path format: {root}/{project_id}/features/{feature_id}/tasks/TASK-{file_path}.md

        @TASK: TASK-001-PathResolver
        """
        # feature_id is required
        if not feature_id:
            raise ValueError("feature_id is required for TASK doc_type")

        # Check if feature folder exists
        feature_path = Path(self.root_dir) / project_id / "features" / feature_id
        if not os.path.exists(feature_path):
            raise FileNotFoundError(f"Feature folder not found: {feature_path}")

        # file_path is required to identify specific TASK
        if not file_path:
            raise ValueError("file_path is required to specify TASK identifier (e.g., '014' or '014-CreateDocumentTool')")

        # Build TASK path
        base_path = feature_path / "tasks"

        # Try exact match first
        filename = f"TASK-{file_path}.md"
        full_path = base_path / filename
        resolved_path, is_new_file = self._check_new_md_version(full_path)

        if os.path.exists(resolved_path):
            return PathInfo(
                project_id=project_id,
                feature_id=feature_id,
                doc_type="TASK",
                file_path=str(resolved_path),
                is_rbt=True,
                is_new_file=is_new_file
            )

        # Exact match failed, try glob matching for partial IDs (e.g., "006" → TASK-006-*.md)
        search_pattern = str(base_path / f"TASK-{file_path}-*.md")
        matches = glob(search_pattern)

        # Also search for .new.md versions
        search_pattern_new = str(base_path / f"TASK-{file_path}-*.new.md")
        matches_new = glob(search_pattern_new)

        # Combine and deduplicate (prefer .new.md)
        all_matches = set()
        for match in matches_new:
            all_matches.add(match)
        for match in matches:
            # Only add .md if no .new.md version exists
            new_version = match.replace(".md", ".new.md")
            if new_version not in all_matches:
                all_matches.add(match)

        all_matches = list(all_matches)

        if len(all_matches) == 0:
            raise FileNotFoundError(f"TASK document not found matching TASK-{file_path}*.md in {base_path}")

        if len(all_matches) > 1:
            raise ValueError(f"Ambiguous TASK identifier '{file_path}': found {len(all_matches)} matches: {[Path(m).name for m in all_matches]}")

        # Single match found
        resolved_path = all_matches[0]
        is_new_file = resolved_path.endswith(".new.md")

        return PathInfo(
            project_id=project_id,
            feature_id=feature_id,
            doc_type="TASK",
            file_path=str(resolved_path),
            is_rbt=True,
            is_new_file=is_new_file
        )

    def _resolve_general_file(self, project_id: str, file_path: str) -> PathInfo:
        """
        Resolve general file path (non-RBT).

        @TASK: TASK-001-PathResolver
        """
        # Build general file path
        full_path = Path(self.root_dir) / project_id / "docs" / file_path

        # Check for .new.md version
        resolved_path, is_new_file = self._check_new_md_version(full_path)

        # Verify file exists
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"General file not found: {resolved_path}")

        return PathInfo(
            project_id=project_id,
            feature_id=None,
            doc_type=None,
            file_path=str(resolved_path),
            is_rbt=False,
            is_new_file=is_new_file
        )

    def _check_new_md_version(self, original_path: Path) -> tuple[str, bool]:
        """
        Check if .new.md version exists and prefer it.

        Args:
            original_path: Original file path (e.g., file.md)

        Returns:
            Tuple of (resolved_path, is_new_file)

        @TASK: TASK-001-PathResolver
        """
        # Handle both .md and non-.md files
        if original_path.suffix == ".md":
            new_version = original_path.with_suffix(".new.md")
        else:
            new_version = Path(str(original_path) + ".new")

        if os.path.exists(new_version):
            return str(new_version), True

        return str(original_path), False
