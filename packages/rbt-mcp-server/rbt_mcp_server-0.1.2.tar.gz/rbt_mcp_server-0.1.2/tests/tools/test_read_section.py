"""
Test cases for read_content tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-006-ReadSectionTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the read_content tool function and error types
from rbt_mcp_server.errors import ToolError


class TestReadContentTool:
    """Test suite for read_content tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document with sections and blocks."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a comprehensive RBT document with sections and blocks
        sample_md = """---
id: REQ-test
group_id: test-project
type: Requirement
feature: test-feature
---

<!-- info-section -->
> status: Draft
> priority: High
> update_date: 2025-10-08

<!-- id: sec-root -->
# Requirement: Test Requirement

<!-- id: sec-goal -->
### 1. Goal Section

<!-- id: blk-goal-desc, type: paragraph -->
This is a test requirement document for testing read_content tool.
It contains multiple sections with various block types.

<!-- id: blk-goal-list, type: list -->
**Key Points**
  - Point 1: First important point
  - Point 2: Second important point
  - Point 3: Third important point

<!-- id: sec-scope -->
### 2. Scope Section

<!-- id: blk-scope-para, type: paragraph -->
This section defines the scope of the requirement.

<!-- id: blk-scope-table, type: table -->
| Feature | Description | Priority |
|---------|-------------|----------|
| Feature 1 | Description 1 | High |
| Feature 2 | Description 2 | Medium |
| Feature 3 | Description 3 | Low |

<!-- id: sec-subsection -->
#### 2.1 Subsection

<!-- id: blk-subsection-code, type: code -->
```python
# This is sample code
def example():
    return "test"
```

<!-- id: sec-details -->
### 3. Details Section

<!-- id: blk-details-list, type: list -->
**Details**
  - Detail A: Description of A
  - Detail B: Description of B
  - Detail C: Description of C
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
        # Set the environment variable
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import read_content
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service to use our test service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, read_content)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    # ========== Test Case 1: Successfully read section with blocks ==========
    def test_tc1_read_section_success(self, setup_test_document, mock_root_dir):
        """
        TC1: Successfully read section (with blocks).

        Given: A complete RBT document with sections and blocks
        When: read_content is called with a valid section ID (sec-*)
        Then: Return section data including all blocks

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Unpack fixture
        _, read_content = mock_root_dir

        # Call read_content for sec-goal
        result = read_content(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            content_id="sec-goal"
        )

        # Verify section structure
        assert result is not None
        assert isinstance(result, dict)

        # Verify section metadata
        assert "id" in result
        assert result["id"] == "sec-goal"
        assert "title" in result
        assert "Goal Section" in result["title"]

        # Verify blocks are present
        assert "blocks" in result, "Section should contain blocks"
        blocks = result["blocks"]
        assert len(blocks) > 0, "Section should have at least one block"

        # Verify block structure
        block_ids = [block.get("id") for block in blocks]
        assert "blk-goal-desc" in block_ids
        assert "blk-goal-list" in block_ids

    # ========== Test Case 2: Successfully read block ==========
    def test_tc2_read_block_success(self, setup_test_document, mock_root_dir):
        """
        TC2: Successfully read block.

        Given: A document with blocks
        When: read_content is called with a valid block ID (blk-*)
        Then: Return block data only

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Unpack fixture
        _, read_content = mock_root_dir

        # Call read_content for a block
        result = read_content(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            content_id="blk-goal-desc"
        )

        # Verify block structure
        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == "blk-goal-desc"
        assert result["type"] == "paragraph"
        assert "content" in result
        assert "read_content tool" in result["content"]

        # Verify no section-specific fields
        assert "sections" not in result
        assert "blocks" not in result

    # ========== Test Case 3: Section not found error ==========
    def test_tc3_section_not_found(self, setup_test_document, mock_root_dir):
        """
        TC3: Section_id not found -> ToolError("CONTENT_NOT_FOUND").

        Given: A document without the requested section
        When: read_content is called with non-existent section_id
        Then: Raise ToolError with CONTENT_NOT_FOUND code

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Unpack fixture
        _, read_content = mock_root_dir

        # Attempt to read non-existent section
        with pytest.raises(ToolError) as exc_info:
            read_content(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                content_id="sec-non-existent"
            )

        # Verify error code and message
        error = exc_info.value
        assert error.code == "CONTENT_NOT_FOUND"
        assert "sec-non-existent" in error.message
        assert "not found" in error.message.lower()

    # ========== Test Case 4: Block not found error ==========
    def test_tc4_block_not_found(self, setup_test_document, mock_root_dir):
        """
        TC4: Block_id not found -> ToolError("CONTENT_NOT_FOUND").

        Given: A document without the requested block
        When: read_content is called with non-existent block_id
        Then: Raise ToolError with CONTENT_NOT_FOUND code

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Unpack fixture
        _, read_content = mock_root_dir

        # Attempt to read non-existent block
        with pytest.raises(ToolError) as exc_info:
            read_content(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                content_id="blk-non-existent"
            )

        # Verify error code and message
        error = exc_info.value
        assert error.code == "CONTENT_NOT_FOUND"
        assert "blk-non-existent" in error.message
        assert "not found" in error.message.lower()

    # ========== Test Case 5: Invalid content_id format error ==========
    def test_tc5_invalid_content_id(self, setup_test_document, mock_root_dir):
        """
        TC5: Invalid content_id format -> ToolError("INVALID_CONTENT_ID").

        Given: A document
        When: read_content is called with invalid content_id (not sec-* or blk-*)
        Then: Raise ToolError with INVALID_CONTENT_ID code

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Unpack fixture
        _, read_content = mock_root_dir

        # Attempt to read with invalid content_id
        with pytest.raises(ToolError) as exc_info:
            read_content(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                content_id="invalid-id"
            )

        # Verify error code and message
        error = exc_info.value
        assert error.code == "INVALID_CONTENT_ID"
        assert "sec-" in error.message or "blk-" in error.message

    # ========== Test Case 6: Read table block ==========
    def test_tc6_read_table_block(self, setup_test_document, mock_root_dir):
        """
        TC6: Read table block directly.

        Given: A section with a table block
        When: read_content is called with table block ID
        Then: Return table block data

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Unpack fixture
        _, read_content = mock_root_dir

        # Call read_content for table block
        result = read_content(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            content_id="blk-scope-table"
        )

        # Verify table block
        assert result is not None
        assert result["id"] == "blk-scope-table"
        assert result["type"] == "table"
        assert "content" in result

        # Verify table content
        content = result["content"]
        assert "Feature" in content
        assert "Description" in content
        assert "Priority" in content
        assert "Feature 1" in content
