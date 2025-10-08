"""
Test cases for append_table_row tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-017-AppendTableRowTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestAppendTableRowTool:
    """Test suite for append_table_row tool following TDD approach."""

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

<!-- id: blk-empty-table, type: table -->
| Name | Value | Type |
|------|-------|------|

<!-- id: blk-paragraph, type: paragraph -->
This is a test paragraph block.
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

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc1_append_to_existing_table_success(self, setup_test_document):
        """
        TC1: Append row to existing table successfully.

        Given: A document with a table containing 2 rows
        When: Append a new row with matching column count
        Then: New row is added to the end of the table
        """
        from rbt_mcp_server.document_service import DocumentService
        from rbt_mcp_server.path_resolver import PathResolver

        # Setup
        os.environ["RBT_ROOT_DIR"] = setup_test_document["temp_root"]
        path_resolver = PathResolver(setup_test_document["temp_root"])
        doc_service = DocumentService(path_resolver)

        # Resolve path
        path_info = path_resolver.resolve(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Append new row
        new_row = ["Component C", "Description C", "Active", "Low"]
        doc_service.append_table_row(path_info, "blk-component-table", new_row)

        # Verify: Load document and check table has 3 rows
        json_data = doc_service.load_document(path_info)
        section = json_data["sections"][0]  # sec-components
        block = section["blocks"][0]  # blk-component-table

        lines = block["content"].split("\n")
        # Header + separator + 2 existing rows + 1 new row = 5 lines
        assert len(lines) == 5
        assert "Component C" in lines[4]
        assert "Description C" in lines[4]

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc2_append_to_empty_table_success(self, setup_test_document):
        """
        TC2: Append row to empty table (only header) successfully.

        Given: A document with an empty table (only header, no data rows)
        When: Append a new row with matching column count
        Then: New row is added as the first data row
        """
        from rbt_mcp_server.document_service import DocumentService
        from rbt_mcp_server.path_resolver import PathResolver

        # Setup
        os.environ["RBT_ROOT_DIR"] = setup_test_document["temp_root"]
        path_resolver = PathResolver(setup_test_document["temp_root"])
        doc_service = DocumentService(path_resolver)

        # Resolve path
        path_info = path_resolver.resolve(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Append first row to empty table
        new_row = ["Item1", "Value1", "TypeA"]
        doc_service.append_table_row(path_info, "blk-empty-table", new_row)

        # Verify: Load document and check table has 1 data row
        json_data = doc_service.load_document(path_info)
        section = json_data["sections"][0]  # sec-components
        block = section["blocks"][1]  # blk-empty-table

        lines = block["content"].split("\n")
        # Header + separator + 1 new row = 3 lines
        assert len(lines) == 3
        assert "Item1" in lines[2]
        assert "Value1" in lines[2]
        assert "TypeA" in lines[2]

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc3_column_count_mismatch_error(self, setup_test_document):
        """
        TC3: Verify row data length matches header.

        Given: A document with a table (4 columns)
        When: Attempt to append a row with wrong number of columns
        Then: Raise COLUMN_COUNT_MISMATCH error
        """
        from rbt_mcp_server.document_service import DocumentService
        from rbt_mcp_server.path_resolver import PathResolver

        # Setup
        os.environ["RBT_ROOT_DIR"] = setup_test_document["temp_root"]
        path_resolver = PathResolver(setup_test_document["temp_root"])
        doc_service = DocumentService(path_resolver)

        # Resolve path
        path_info = path_resolver.resolve(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Attempt to append row with wrong column count (table has 4 columns)
        wrong_row = ["Component C", "Description C"]  # Only 2 columns

        with pytest.raises(ToolError) as exc_info:
            doc_service.append_table_row(path_info, "blk-component-table", wrong_row)

        assert exc_info.value.code == "COLUMN_COUNT_MISMATCH"
        assert "2 columns" in str(exc_info.value)
        assert "4 columns" in str(exc_info.value)

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc4_non_table_block_error(self, setup_test_document):
        """
        TC4: Error handling for non-table block.

        Given: A document with a paragraph block
        When: Attempt to append table row to paragraph block
        Then: Raise INVALID_BLOCK_TYPE error
        """
        from rbt_mcp_server.document_service import DocumentService
        from rbt_mcp_server.path_resolver import PathResolver

        # Setup
        os.environ["RBT_ROOT_DIR"] = setup_test_document["temp_root"]
        path_resolver = PathResolver(setup_test_document["temp_root"])
        doc_service = DocumentService(path_resolver)

        # Resolve path
        path_info = path_resolver.resolve(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Attempt to append row to non-table block
        new_row = ["Some", "Data"]

        with pytest.raises(ToolError) as exc_info:
            doc_service.append_table_row(path_info, "blk-paragraph", new_row)

        assert exc_info.value.code == "INVALID_BLOCK_TYPE"
        assert "paragraph" in str(exc_info.value)
        assert "table" in str(exc_info.value)

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc5_block_not_found_error(self, setup_test_document):
        """
        TC5: Error handling when block doesn't exist.

        Given: A document
        When: Attempt to append row to non-existent block
        Then: Raise BLOCK_NOT_FOUND error
        """
        from rbt_mcp_server.document_service import DocumentService
        from rbt_mcp_server.path_resolver import PathResolver

        # Setup
        os.environ["RBT_ROOT_DIR"] = setup_test_document["temp_root"]
        path_resolver = PathResolver(setup_test_document["temp_root"])
        doc_service = DocumentService(path_resolver)

        # Resolve path
        path_info = path_resolver.resolve(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Attempt to append row to non-existent block
        new_row = ["Data1", "Data2"]

        with pytest.raises(ToolError) as exc_info:
            doc_service.append_table_row(path_info, "blk-nonexistent", new_row)

        assert exc_info.value.code == "BLOCK_NOT_FOUND"
        assert "blk-nonexistent" in str(exc_info.value)
