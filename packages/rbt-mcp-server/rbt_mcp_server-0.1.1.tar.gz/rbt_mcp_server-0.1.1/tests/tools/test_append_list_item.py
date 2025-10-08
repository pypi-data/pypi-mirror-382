"""
Test cases for append_list_item tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-012-AppendListItemTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestAppendListItemTool:
    """Test suite for append_list_item tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test document with list blocks."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a document with list blocks
        sample_md = """---
id: REQ-test
group_id: test-project
type: Requirement
feature: test-feature
---

<!-- info-section -->
> status: Draft
> update_date: 2025-10-08

<!-- id: sec-root -->
# Test Document

<!-- id: sec-features -->
### Features Section

<!-- id: blk-feature-list, type: list -->
**Features**
  - Feature A: First feature
  - Feature B: Second feature
  - Feature C: Third feature

<!-- id: blk-empty-list, type: list -->
**Empty List**

<!-- id: sec-implementation -->
### Implementation Section

<!-- id: blk-impl-para, type: paragraph -->
This is a paragraph block, not a list.

<!-- id: blk-impl-code, type: code -->
```python
# Code block
def example():
    pass
```

<!-- id: blk-tasks-list, type: list -->
**Tasks**
  - Task 1: Initial setup
  - Task 2: Core implementation
"""
        req_file = feature_dir / "REQ-test-feature.md"
        req_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "doc_type": "REQ",
            "req_file": str(req_file)
        }

    @pytest.fixture
    def mock_root_dir(self, temp_root):
        """Mock the RBT_ROOT_DIR environment variable and document_service."""
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import append_list_item
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service to use our test service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, append_list_item)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    # ========== Test Case 1: Successfully append item to list ==========
    def test_append_list_item_success(self, setup_test_document, mock_root_dir):
        """
        Test Case 1: Successfully append item to existing list.

        Given: A document with a list block
        When: append_list_item is called with valid block_id and item
        Then: Item is appended to the list and document is saved

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Unpack fixture
        _, append_list_item = mock_root_dir

        # Call append_list_item
        result = append_list_item(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-feature-list",
            item="Feature D: Fourth feature"
        )

        # Verify success message
        assert result is not None
        assert "success" in result.lower()
        assert "blk-feature-list" in result

        # Verify the document was updated with .new.md
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        assert new_file.exists(), ".new.md file should be created"

        # Read and verify the updated content
        with open(new_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Feature D: Fourth feature" in content
            # Verify all original items are still there
            assert "Feature A: First feature" in content
            assert "Feature B: Second feature" in content
            assert "Feature C: Third feature" in content

    # ========== Test Case 2: Append to empty list ==========
    def test_append_to_empty_list(self, setup_test_document, mock_root_dir):
        """
        Test Case 2: Append item to empty list block.

        Given: A document with an empty list block
        When: append_list_item is called
        Then: Item is added as the first item in the list

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Unpack fixture
        _, append_list_item = mock_root_dir

        # Call append_list_item on empty list
        result = append_list_item(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-empty-list",
            item="First item in empty list"
        )

        # Verify success
        assert "success" in result.lower()

        # Verify content
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        with open(new_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "First item in empty list" in content

    # ========== Test Case 3: Block ID not found ==========
    def test_append_list_item_block_not_found(self, setup_test_document, mock_root_dir):
        """
        Test Case 3: Error when block_id doesn't exist.

        Given: A document
        When: append_list_item is called with non-existent block_id
        Then: Raise ToolError with BLOCK_NOT_FOUND

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Unpack fixture
        _, append_list_item = mock_root_dir

        # Attempt to append to non-existent block
        with pytest.raises(ToolError) as exc_info:
            append_list_item(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-nonexistent",
                item="This should fail"
            )

        # Verify error details
        assert exc_info.value.code == "BLOCK_NOT_FOUND"
        assert "blk-nonexistent" in exc_info.value.message

    # ========== Test Case 4: Block is not a list type ==========
    def test_append_list_item_wrong_block_type(self, setup_test_document, mock_root_dir):
        """
        Test Case 4: Error when block is not a list type.

        Given: A document with non-list blocks (paragraph, code)
        When: append_list_item is called on non-list block
        Then: Raise ToolError with INVALID_BLOCK_TYPE

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Unpack fixture
        _, append_list_item = mock_root_dir

        # Test with paragraph block
        with pytest.raises(ToolError) as exc_info:
            append_list_item(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-impl-para",
                item="This should fail"
            )

        assert exc_info.value.code == "INVALID_BLOCK_TYPE"
        assert "list" in exc_info.value.message.lower()
        assert "paragraph" in exc_info.value.message.lower()

        # Test with code block
        with pytest.raises(ToolError) as exc_info:
            append_list_item(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                block_id="blk-impl-code",
                item="This should also fail"
            )

        assert exc_info.value.code == "INVALID_BLOCK_TYPE"
        assert "list" in exc_info.value.message.lower()

    # ========== Test Case 5: Multiple appends in sequence ==========
    def test_append_multiple_items(self, setup_test_document, mock_root_dir):
        """
        Test Case 5: Append multiple items in sequence.

        Given: A document with a list block
        When: append_list_item is called multiple times
        Then: All items are appended in order

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Unpack fixture
        _, append_list_item = mock_root_dir

        # Append first item
        result1 = append_list_item(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-tasks-list",
            item="Task 3: Testing phase"
        )
        assert "success" in result1.lower()

        # Append second item
        result2 = append_list_item(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            block_id="blk-tasks-list",
            item="Task 4: Documentation"
        )
        assert "success" in result2.lower()

        # Verify both items are present in order
        new_file = Path(setup_test_document["req_file"]).parent / "REQ-test-feature.new.md"
        with open(new_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check all items are present
            assert "Task 1: Initial setup" in content
            assert "Task 2: Core implementation" in content
            assert "Task 3: Testing phase" in content
            assert "Task 4: Documentation" in content

            # Verify order (simple check - Task 3 should appear before Task 4)
            task3_pos = content.find("Task 3: Testing phase")
            task4_pos = content.find("Task 4: Documentation")
            assert task3_pos < task4_pos, "Items should be in append order"

    # ========== Test Case 6: General document support ==========
    def test_append_list_item_general_document(self, mock_root_dir):
        """
        Test Case 6: append_list_item works with general documents.

        Given: A general markdown document in docs/
        When: append_list_item is called with file_path parameter
        Then: Item is appended successfully

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Unpack fixture
        temp_root, append_list_item = mock_root_dir

        # Create general document
        project_dir = Path(temp_root) / "test-project"
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        general_doc = """---
id: DOC-checklist
type: Document
---

<!-- info-section -->
> author: Test Author

<!-- id: sec-root -->
# Checklist Document

<!-- id: sec-items -->
## Items

<!-- id: blk-checklist, type: list -->
**Checklist**
  - Item 1: First task
  - Item 2: Second task
"""
        doc_file = docs_dir / "checklist.md"
        doc_file.write_text(general_doc)

        # Append item using file_path parameter
        result = append_list_item(
            project_id="test-project",
            file_path="checklist.md",
            block_id="blk-checklist",
            item="Item 3: Third task"
        )

        # Verify success
        assert "success" in result.lower()

        # Verify content
        new_file = docs_dir / "checklist.new.md"
        assert new_file.exists()
        with open(new_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Item 3: Third task" in content
