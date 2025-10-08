"""
Test cases for create_block tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-009-CreateBlockTool
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the create_block tool function and error types
from rbt_mcp_server.errors import ToolError


class TestCreateBlockTool:
    """Test suite for create_block tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document for testing create_block."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a simple RBT document with sections
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

<!-- id: sec-goal -->
### 1. Goal Section

<!-- id: blk-goal-desc, type: paragraph -->
This is an existing paragraph block for testing.

<!-- id: sec-features -->
### 2. Features Section

<!-- id: blk-features-list, type: list -->
**Key Features**
  - Feature 1
  - Feature 2
"""

        # Write test document
        doc_path = feature_dir / "REQ-test-feature.md"
        doc_path.write_text(sample_md)

        return {
            "root_dir": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "doc_type": "REQ",
            "doc_path": str(doc_path)
        }

    # ========== TC1: Normal Operations (TDD Red Phase) ==========

    @patch.dict(os.environ, {}, clear=True)
    def test_tc1_create_paragraph_block(self, setup_test_document):
        """TC1.1: Successfully create a paragraph block."""
        # Set environment variable
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        # Import server module after setting env var
        from rbt_mcp_server import server

        # Reload to get fresh instance
        import importlib
        importlib.reload(server)

        # Call create_block for paragraph
        result = server.create_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-goal",
            block_type="paragraph",
            content="This is a new paragraph block added by create_block."
        )

        # Verify result is a block ID
        assert result.startswith("blk-paragraph-")

        # Read section to verify block was added
        section = server.read_section(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-goal"
        )

        # Find the new block
        new_block = None
        for block in section.get("blocks", []):
            if block["id"] == result:
                new_block = block
                break

        assert new_block is not None
        assert new_block["type"] == "paragraph"
        assert new_block["content"] == "This is a new paragraph block added by create_block."

    @patch.dict(os.environ, {}, clear=True)
    def test_tc1_create_code_block(self, setup_test_document):
        """TC1.2: Successfully create a code block."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Call create_block for code
        result = server.create_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-goal",
            block_type="code",
            content="def example():\n    return 'test'",
            language="python"
        )

        # Verify result is a block ID
        assert result.startswith("blk-code-")

        # Read section to verify block was added
        section = server.read_section(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-goal"
        )

        # Find the new block
        new_block = None
        for block in section.get("blocks", []):
            if block["id"] == result:
                new_block = block
                break

        assert new_block is not None
        assert new_block["type"] == "code"
        assert new_block["language"] == "python"
        assert "def example():" in new_block["content"]

    @patch.dict(os.environ, {}, clear=True)
    def test_tc1_create_list_block(self, setup_test_document):
        """TC1.3: Successfully create a list block."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Call create_block for list
        result = server.create_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-features",
            block_type="list",
            items=["New item 1", "New item 2", "New item 3"]
        )

        # Verify result is a block ID
        assert result.startswith("blk-list-")

        # Read section to verify block was added
        section = server.read_section(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-features"
        )

        # Find the new block
        new_block = None
        for block in section.get("blocks", []):
            if block["id"] == result:
                new_block = block
                break

        assert new_block is not None
        assert new_block["type"] == "list"
        assert len(new_block["items"]) == 3
        assert new_block["items"][0] == "New item 1"

    @patch.dict(os.environ, {}, clear=True)
    def test_tc1_create_table_block(self, setup_test_document):
        """TC1.4: Successfully create a table block."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Call create_block for table
        result = server.create_block(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-features",
            block_type="table",
            header=["Column 1", "Column 2", "Column 3"],
            rows=[
                ["Value 1A", "Value 1B", "Value 1C"],
                ["Value 2A", "Value 2B", "Value 2C"]
            ]
        )

        # Verify result is a block ID
        assert result.startswith("blk-table-")

        # Read section to verify block was added
        section = server.read_section(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id="sec-features"
        )

        # Find the new block
        new_block = None
        for block in section.get("blocks", []):
            if block["id"] == result:
                new_block = block
                break

        assert new_block is not None
        assert new_block["type"] == "table"
        assert new_block["header"] == ["Column 1", "Column 2", "Column 3"]
        assert len(new_block["rows"]) == 2
        assert new_block["rows"][0] == ["Value 1A", "Value 1B", "Value 1C"]

    # ========== TC2: Error Handling (TDD Red Phase) ==========

    @patch.dict(os.environ, {}, clear=True)
    def test_tc2_section_not_found(self, setup_test_document):
        """TC2.1: Error when section ID doesn't exist."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Try to create block in non-existent section
        with pytest.raises(ToolError) as exc_info:
            server.create_block(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                section_id="sec-nonexistent",
                block_type="paragraph",
                content="This should fail."
            )

        assert exc_info.value.code == "SECTION_NOT_FOUND"
        assert "sec-nonexistent" in exc_info.value.message

    @patch.dict(os.environ, {}, clear=True)
    def test_tc2_invalid_block_type(self, setup_test_document):
        """TC2.2: Error when block type is invalid."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Try to create block with invalid type
        with pytest.raises(ToolError) as exc_info:
            server.create_block(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                section_id="sec-goal",
                block_type="invalid_type",
                content="This should fail."
            )

        assert exc_info.value.code == "INVALID_BLOCK_TYPE"
        assert "invalid_type" in exc_info.value.message

    @patch.dict(os.environ, {}, clear=True)
    def test_tc2_missing_required_params_paragraph(self, setup_test_document):
        """TC2.3: Error when paragraph block missing content."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Try to create paragraph without content
        with pytest.raises(ToolError) as exc_info:
            server.create_block(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                section_id="sec-goal",
                block_type="paragraph"
            )

        assert exc_info.value.code in ["MISSING_REQUIRED_FIELD", "INVALID_BLOCK_DATA"]

    @patch.dict(os.environ, {}, clear=True)
    def test_tc2_missing_required_params_list(self, setup_test_document):
        """TC2.4: Error when list block missing items."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Try to create list without items
        with pytest.raises(ToolError) as exc_info:
            server.create_block(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                section_id="sec-features",
                block_type="list"
            )

        assert exc_info.value.code in ["MISSING_REQUIRED_FIELD", "INVALID_BLOCK_DATA"]

    @patch.dict(os.environ, {}, clear=True)
    def test_tc2_missing_required_params_table(self, setup_test_document):
        """TC2.5: Error when table block missing header or rows."""
        os.environ["RBT_ROOT_DIR"] = setup_test_document["root_dir"]

        from rbt_mcp_server import server
        import importlib
        importlib.reload(server)

        # Try to create table without header
        with pytest.raises(ToolError) as exc_info:
            server.create_block(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                section_id="sec-features",
                block_type="table",
                rows=[["A", "B"]]
            )

        assert exc_info.value.code in ["MISSING_REQUIRED_FIELD", "INVALID_BLOCK_DATA"]
