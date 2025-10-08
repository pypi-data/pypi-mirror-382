"""
Test cases for update_table_row tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-013-UpdateTableRowTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestUpdateTableRowTool:
    """Test suite for update_table_row tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document with table blocks."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a comprehensive RBT document with table blocks
        sample_md = """---
id: BP-test
group_id: test-project
type: Blueprint
feature: test-feature
---

<!-- info-section -->
> status: Draft
> update_date: 2025-10-08

<!-- id: sec-root -->
# Blueprint: Test Blueprint

<!-- id: sec-components -->
### 1. Component Specifications

<!-- id: blk-component-table, type: table -->
| Component | Description | Status | Priority |
|-----------|-------------|--------|----------|
| Component A | Description A | Active | High |
| Component B | Description B | Pending | Medium |
| Component C | Description C | Active | Low |

<!-- id: sec-tasks -->
### 2. Task Tracking

<!-- id: blk-task-table, type: table -->
| Task ID | Title | Assignee | Status |
|---------|-------|----------|--------|
| TASK-001 | First task | Alice | Done |
| TASK-002 | Second task | Bob | In Progress |
| TASK-003 | Third task | Charlie | Pending |
| TASK-004 | Fourth task | Diana | Done |

<!-- id: blk-desc, type: paragraph -->
This is a test blueprint document for testing update_table_row tool.
"""
        bp_file = feature_dir / "BP-test-feature.md"
        bp_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "doc_type": "BP",
            "bp_file": str(bp_file)
        }

    @pytest.fixture
    def setup_general_document(self, temp_root):
        """Setup a general document with table blocks."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create a general document with table blocks
        sample_md = """---
id: general-doc
group_id: test-project
type: General
---

<!-- info-section -->
> status: Active

<!-- id: sec-root -->
# General Document

<!-- id: sec-data -->
### Data Table

<!-- id: blk-simple-table, type: table -->
| Name | Age | Role |
|------|-----|------|
| Alice | 30 | Engineer |
| Bob | 25 | Designer |
"""
        doc_file = docs_dir / "test-doc.md"
        doc_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "file_path": "test-doc.md",
            "doc_file": str(doc_file)
        }

    # TDD Red - Test Case 1: Normal operation - update table row successfully
    def test_update_table_row_success(self, setup_test_document):
        """Test successful table row update."""
        # Import here after RBT_ROOT_DIR is set
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            # Update the first row of component table
            result = update_table_row(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-component-table",
                row_index=0,
                row_data=["Component A", "Updated description", "Inactive", "Critical"]
            )

            # Should return success message
            assert "success" in result.lower()
            assert "blk-component-table" in result

            # Verify the file was updated (.new.md should exist)
            new_file = setup_test_document["bp_file"].replace(".md", ".new.md")
            assert os.path.exists(new_file)

            # Verify the content was updated
            with open(new_file, 'r') as f:
                content = f.read()
                assert "Updated description" in content
                assert "Inactive" in content
                assert "Critical" in content
                # Original values should not exist in that row
                assert "Description A" not in content or content.count("Description A") == 0

    # TDD Red - Test Case 2: Update middle row of a table
    def test_update_table_row_middle(self, setup_test_document):
        """Test updating a middle row of a table."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            # Update the second row (index 1) of task table
            result = update_table_row(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-task-table",
                row_index=1,
                row_data=["TASK-002", "Updated task title", "Eve", "Completed"]
            )

            assert "success" in result.lower()

            # Verify the update
            new_file = setup_test_document["bp_file"].replace(".md", ".new.md")
            with open(new_file, 'r') as f:
                content = f.read()
                assert "Updated task title" in content
                assert "Eve" in content
                assert "Completed" in content

    # TDD Red - Test Case 3: Update last row of a table
    def test_update_table_row_last(self, setup_test_document):
        """Test updating the last row of a table."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            # Update the last row (index 2) of component table
            result = update_table_row(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-component-table",
                row_index=2,
                row_data=["Component C", "New description", "Completed", "High"]
            )

            assert "success" in result.lower()

            # Verify the update
            new_file = setup_test_document["bp_file"].replace(".md", ".new.md")
            with open(new_file, 'r') as f:
                content = f.read()
                assert "New description" in content
                assert "Completed" in content

    # TDD Red - Test Case 4: Update row in general document
    def test_update_table_row_general_document(self, setup_general_document):
        """Test updating table row in a general document."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_general_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            result = update_table_row(
                project_id=setup_general_document["project_id"],
                file_path=setup_general_document["file_path"],
                block_id="blk-simple-table",
                row_index=0,
                row_data=["Alice", "31", "Senior Engineer"]
            )

            assert "success" in result.lower()

            # Verify the update
            new_file = setup_general_document["doc_file"].replace(".md", ".new.md")
            with open(new_file, 'r') as f:
                content = f.read()
                assert "31" in content
                assert "Senior Engineer" in content

    # TDD Red - Error Test Case 5: Block not found
    def test_update_table_row_block_not_found(self, setup_test_document):
        """Test error handling when block ID doesn't exist."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            with pytest.raises(Exception) as exc_info:
                update_table_row(
                    project_id=setup_test_document["project_id"],
                    feature_id=setup_test_document["feature_id"],
                    doc_type=setup_test_document["doc_type"],
                    block_id="blk-nonexistent",
                    row_index=0,
                    row_data=["Data 1", "Data 2"]
                )

            # Should raise ToolError with appropriate message
            assert "not found" in str(exc_info.value).lower() or "BLOCK_NOT_FOUND" in str(exc_info.value)

    # TDD Red - Error Test Case 6: Block is not a table type
    def test_update_table_row_wrong_block_type(self, setup_test_document):
        """Test error handling when block is not a table type."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            with pytest.raises(Exception) as exc_info:
                update_table_row(
                    project_id=setup_test_document["project_id"],
                    feature_id=setup_test_document["feature_id"],
                    doc_type=setup_test_document["doc_type"],
                    block_id="blk-desc",  # This is a paragraph block
                    row_index=0,
                    row_data=["Data 1", "Data 2"]
                )

            # Should raise ToolError indicating wrong block type
            assert "table" in str(exc_info.value).lower() or "INVALID_BLOCK_TYPE" in str(exc_info.value)

    # TDD Red - Error Test Case 7: Row index out of range
    def test_update_table_row_index_out_of_range(self, setup_test_document):
        """Test error handling when row index is out of range."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            with pytest.raises(Exception) as exc_info:
                update_table_row(
                    project_id=setup_test_document["project_id"],
                    feature_id=setup_test_document["feature_id"],
                    doc_type=setup_test_document["doc_type"],
                    block_id="blk-component-table",
                    row_index=10,  # Only 3 rows in the table
                    row_data=["Data 1", "Data 2", "Data 3", "Data 4"]
                )

            # Should raise error about index out of range
            assert "index" in str(exc_info.value).lower() or "out of range" in str(exc_info.value).lower()

    # TDD Red - Error Test Case 8: Column count mismatch
    def test_update_table_row_column_mismatch(self, setup_test_document):
        """Test error handling when row data has wrong number of columns."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            with pytest.raises(Exception) as exc_info:
                update_table_row(
                    project_id=setup_test_document["project_id"],
                    feature_id=setup_test_document["feature_id"],
                    doc_type=setup_test_document["doc_type"],
                    block_id="blk-component-table",
                    row_index=0,
                    row_data=["Only", "Two"]  # Table has 4 columns
                )

            # Should raise error about column count mismatch
            assert "column" in str(exc_info.value).lower() or "mismatch" in str(exc_info.value).lower()

    # TDD Red - Error Test Case 9: Negative row index
    def test_update_table_row_negative_index(self, setup_test_document):
        """Test error handling when row index is negative."""
        with patch.dict(os.environ, {"RBT_ROOT_DIR": setup_test_document["temp_root"]}):
            from rbt_mcp_server.server import update_table_row

            with pytest.raises(Exception) as exc_info:
                update_table_row(
                    project_id=setup_test_document["project_id"],
                    feature_id=setup_test_document["feature_id"],
                    doc_type=setup_test_document["doc_type"],
                    block_id="blk-component-table",
                    row_index=-1,
                    row_data=["Data 1", "Data 2", "Data 3", "Data 4"]
                )

            # Should raise error about invalid index
            assert "index" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
