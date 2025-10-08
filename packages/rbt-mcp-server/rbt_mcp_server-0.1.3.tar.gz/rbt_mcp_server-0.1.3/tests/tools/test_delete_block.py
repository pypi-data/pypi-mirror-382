"""
Test cases for delete_block tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-011-DeleteBlockTool
"""

import os
import tempfile
import pytest
from pathlib import Path

from rbt_mcp_server.document_service import DocumentService
from rbt_mcp_server.errors import ToolError
from rbt_mcp_server.models import PathInfo


class TestDeleteBlock:
    """Test suite for delete_block functionality following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def service(self, temp_root):
        """Create a DocumentService instance with temp root."""
        return DocumentService(temp_root)

    @pytest.fixture
    def setup_test_files(self, temp_root):
        """Setup test file structure with sample document containing multiple blocks."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a sample document with multiple blocks of different types
        sample_md = """---
id: REQ-test
group_id: test-project
type: Requirement
feature: test-feature
---

<!-- info-section -->
> status: Draft
> priority: High

<!-- id: sec-root -->
# Requirement: Test Requirement

<!-- id: sec-content -->
### 1. Content Section

<!-- id: blk-para-1, type: paragraph -->
This is the first paragraph block.

<!-- id: blk-list-1, type: list -->
**Key Points**
  - Point 1
  - Point 2
  - Point 3

<!-- id: blk-para-2, type: paragraph -->
This is the second paragraph block that should remain after deletion.

<!-- id: blk-table-1, type: table -->
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

<!-- id: sec-nested -->
#### 1.1 Nested Section

<!-- id: blk-nested-para, type: paragraph -->
This is a paragraph in a nested section.
"""
        req_file = feature_dir / "REQ-test-feature.md"
        req_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "req_file": str(req_file)
        }

    # Test Case 1: Delete paragraph block successfully
    def test_delete_paragraph_block_success(self, service, setup_test_files):
        """Test deleting a paragraph block from a section."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Load document and verify block exists
        json_data = service.load_document(path_info)
        section = service.read_section(path_info, "sec-content")
        initial_block_count = len(section["blocks"])

        # Verify the block to be deleted exists
        block_ids = [block["id"] for block in section["blocks"]]
        assert "blk-para-1" in block_ids

        # Delete the block
        service.delete_block(path_info, "blk-para-1")

        # Verify block is deleted
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        assert os.path.exists(new_file)

        # Read from the new file
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )
        section_after = service.read_section(new_path_info, "sec-content")

        # Verify block count decreased
        assert len(section_after["blocks"]) == initial_block_count - 1

        # Verify the deleted block is gone
        block_ids_after = [block["id"] for block in section_after["blocks"]]
        assert "blk-para-1" not in block_ids_after

        # Verify other blocks remain
        assert "blk-list-1" in block_ids_after
        assert "blk-para-2" in block_ids_after
        assert "blk-table-1" in block_ids_after

    # Test Case 2: Delete list block successfully
    def test_delete_list_block_success(self, service, setup_test_files):
        """Test deleting a list block from a section."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Delete the list block
        service.delete_block(path_info, "blk-list-1")

        # Verify deletion
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )
        section_after = service.read_section(new_path_info, "sec-content")

        block_ids_after = [block["id"] for block in section_after["blocks"]]
        assert "blk-list-1" not in block_ids_after

    # Test Case 3: Delete table block successfully
    def test_delete_table_block_success(self, service, setup_test_files):
        """Test deleting a table block from a section."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Delete the table block
        service.delete_block(path_info, "blk-table-1")

        # Verify deletion
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )
        section_after = service.read_section(new_path_info, "sec-content")

        block_ids_after = [block["id"] for block in section_after["blocks"]]
        assert "blk-table-1" not in block_ids_after

    # Test Case 4: Delete block from nested section
    def test_delete_block_from_nested_section(self, service, setup_test_files):
        """Test deleting a block from a nested section."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Delete block from nested section
        service.delete_block(path_info, "blk-nested-para")

        # Verify deletion
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )
        section_after = service.read_section(new_path_info, "sec-nested")

        # Nested section should now have no blocks or empty blocks list
        if "blocks" in section_after:
            block_ids_after = [block["id"] for block in section_after["blocks"]]
            assert "blk-nested-para" not in block_ids_after

    # Test Case 5: Delete non-existent block raises error
    def test_delete_nonexistent_block_error(self, service, setup_test_files):
        """Test deleting a non-existent block raises ToolError."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Attempt to delete non-existent block
        with pytest.raises(ToolError) as exc_info:
            service.delete_block(path_info, "blk-nonexistent")

        assert exc_info.value.code == "BLOCK_NOT_FOUND"
        assert "blk-nonexistent" in exc_info.value.message

    # Test Case 6: Delete last block in section
    def test_delete_last_block_in_section(self, service, setup_test_files):
        """Test deleting the only block in a section leaves empty blocks list."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Delete the only block in nested section
        service.delete_block(path_info, "blk-nested-para")

        # Verify section still exists but has no blocks
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )
        section_after = service.read_section(new_path_info, "sec-nested")

        # Section should exist but blocks should be empty
        assert section_after is not None
        assert section_after["id"] == "sec-nested"
        if "blocks" in section_after:
            assert len(section_after["blocks"]) == 0

    # Test Case 7: Multiple deletions in sequence
    def test_multiple_deletions_sequence(self, service, setup_test_files):
        """Test deleting multiple blocks in sequence."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Get initial block count
        section_initial = service.read_section(path_info, "sec-content")
        initial_count = len(section_initial["blocks"])

        # Delete first block
        service.delete_block(path_info, "blk-para-1")

        # Update path_info to point to .new.md for subsequent operations
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )

        # Delete second block
        service.delete_block(new_path_info, "blk-list-1")

        # Verify both blocks are deleted
        section_after = service.read_section(new_path_info, "sec-content")
        block_ids_after = [block["id"] for block in section_after["blocks"]]

        assert len(section_after["blocks"]) == initial_count - 2
        assert "blk-para-1" not in block_ids_after
        assert "blk-list-1" not in block_ids_after
        assert "blk-para-2" in block_ids_after
        assert "blk-table-1" in block_ids_after
