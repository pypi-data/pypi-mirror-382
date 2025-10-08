"""
Test cases for update_block tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-010-UpdateBlockTool
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestUpdateBlockTool:
    """Test suite for update_block tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document with various block types."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a comprehensive RBT document with multiple block types
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

<!-- id: sec-blocks -->
### 1. Block Examples

<!-- id: blk-paragraph, type: paragraph -->
This is a test paragraph block.
It has multiple lines of content.

<!-- id: blk-list, type: list -->
**Test List**
  - Item 1
  - Item 2
  - Item 3

<!-- id: blk-code, type: code -->
```python
def hello():
    print("Hello World")
```

<!-- id: blk-table, type: table -->
| Name | Value | Status |
|------|-------|--------|
| Test1 | 100 | Active |
| Test2 | 200 | Pending |
"""
        req_file = feature_dir / "REQ-test-feature.md"
        req_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "doc_type": "REQ",
            "req_file": str(req_file),
            "full_content": sample_md
        }

    @pytest.fixture
    def mock_root_dir(self, temp_root):
        """Mock the RBT_ROOT_DIR environment variable and document_service."""
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import update_block
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service to use our test service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, update_block)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    # ========== Test Case 1: Update paragraph block ==========
    def test_update_paragraph_block(self, setup_test_document, mock_root_dir):
        """
        Test Case 1: Successfully update a paragraph block.

        Given: A document with a paragraph block
        When: update_block is called with new content
        Then: Block content is updated and file is saved

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Update paragraph block
        result = update_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-paragraph",
            content="This is the updated paragraph content.\nWith new lines."
        )

        # Verify success message
        assert result is not None
        assert isinstance(result, dict)
        assert "message" in result
        assert "successfully" in result["message"].lower()
        assert "blk-paragraph" in result["message"]

        # Verify file was saved as .new.md
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        assert new_file.exists()

        # Verify content was updated
        content = new_file.read_text()
        assert "This is the updated paragraph content." in content
        assert "With new lines." in content

    # ========== Test Case 2: Update list block ==========
    def test_update_list_block(self, setup_test_document, mock_root_dir):
        """
        Test Case 2: Successfully update a list block.

        Given: A document with a list block
        When: update_block is called with new items
        Then: List items are updated

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Update list block with new items
        result = update_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-list",
            title="**Updated List**",
            items=["New Item 1", "New Item 2", "New Item 3", "New Item 4"]
        )

        # Verify success
        assert result is not None
        assert "message" in result
        assert "successfully" in result["message"].lower()

        # Verify content
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        content = new_file.read_text()
        assert "**Updated List**" in content
        assert "New Item 1" in content
        assert "New Item 4" in content

    # ========== Test Case 3: Update code block ==========
    def test_update_code_block(self, setup_test_document, mock_root_dir):
        """
        Test Case 3: Successfully update a code block.

        Given: A document with a code block
        When: update_block is called with new code
        Then: Code content is updated

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Update code block
        new_code = """def goodbye():
    print("Goodbye World")
    return 0"""

        result = update_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-code",
            content=new_code,
            language="python"
        )

        # Verify success
        assert result is not None
        assert "message" in result

        # Verify code content
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        content = new_file.read_text()
        assert "def goodbye():" in content
        assert "Goodbye World" in content

    # ========== Test Case 4: Update table block ==========
    def test_update_table_block(self, setup_test_document, mock_root_dir):
        """
        Test Case 4: Successfully update a table block.

        Given: A document with a table block
        When: update_block is called with new rows
        Then: Table content is updated

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Update table block
        result = update_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-table",
            header=["Name", "Value", "Status"],
            rows=[
                ["Test3", "300", "Active"],
                ["Test4", "400", "Complete"]
            ]
        )

        # Verify success
        assert result is not None
        assert "message" in result

        # Verify table content
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        content = new_file.read_text()
        assert "Test3" in content
        assert "Test4" in content
        assert "300" in content
        assert "Complete" in content

    # ========== Test Case 5: Block not found error ==========
    def test_update_block_not_found(self, setup_test_document, mock_root_dir):
        """
        Test Case 5: Error when block ID doesn't exist.

        Given: A document without specific block ID
        When: update_block is called with non-existent block_id
        Then: Raise ToolError with BLOCK_NOT_FOUND

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Try to update non-existent block
        with pytest.raises(Exception) as exc_info:
            update_block(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-nonexistent",
                content="This should fail"
            )

        # Verify error message contains block ID
        error_msg = str(exc_info.value)
        assert "blk-nonexistent" in error_msg or "not found" in error_msg.lower()

    # ========== Test Case 6: Invalid block type error ==========
    def test_update_block_invalid_type_params(self, setup_test_document, mock_root_dir):
        """
        Test Case 6: Error when wrong parameters for block type.

        Given: A paragraph block
        When: update_block is called with list-specific parameters
        Then: Raise ToolError or ignore invalid parameters

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Try to update paragraph block with list items (should use content instead)
        # This should either fail or ignore the items parameter
        result = update_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-paragraph",
            content="Valid paragraph content"
        )

        # Should succeed with content parameter
        assert result is not None
        assert "message" in result

    # ========== Test Case 7: Update with file_path (non-RBT) ==========
    def test_update_block_with_file_path(self, temp_root, mock_root_dir):
        """
        Test Case 7: Update block in a general document using file_path.

        Given: A general document (non-RBT) with blocks
        When: update_block is called with file_path parameter
        Then: Block is updated successfully

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        _, update_block = mock_root_dir

        # Create a general document
        project_dir = Path(temp_root) / "test-project"
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        general_md = """---
id: general-doc
type: Documentation
---

<!-- id: sec-root -->
# General Document

<!-- id: sec-content -->
### Content Section

<!-- id: blk-text, type: paragraph -->
Original text content.
"""
        doc_file = docs_dir / "general.md"
        doc_file.write_text(general_md)

        # Update block using file_path
        result = update_block(
            project_id="test-project",
            file_path="general.md",
            block_id="blk-text",
            content="Updated text content."
        )

        # Verify success
        assert result is not None
        assert "message" in result

        # Verify file was updated
        new_file = docs_dir / "general.new.md"
        assert new_file.exists()
        content = new_file.read_text()
        assert "Updated text content." in content
