"""
Test for duplicate TASK index check in create_document tool.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-014-CreateDocumentTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestCreateDocumentDuplicateIndex:
    """Test suite for duplicate TASK index validation."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_root_dir(self, temp_root):
        """Mock the RBT_ROOT_DIR environment variable and document_service."""
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import create_document
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service to use our test service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, create_document)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    def test_tc5_duplicate_task_index_error(self, mock_root_dir):
        """
        TC5: Duplicate TASK index should raise error.

        Given: A TASK document with index "001" already exists
        When: Attempt to create another TASK document with index "001"
        Then: Raise ToolError with DUPLICATE_TASK_INDEX code

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        temp_root, create_document = mock_root_dir

        # Setup: Create directory structure and an existing TASK-001 file
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        tasks_dir = feature_dir / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        # Create existing TASK-001-ExistingTask.md
        existing_task = tasks_dir / "TASK-001-ExistingTask.md"
        existing_task.write_text("""---
id: TASK-001-ExistingTask
group_id: test-project
type: Task
---

<!-- id: sec-root -->
# Task: Existing Task

Some content here.
""")

        # Attempt to create another TASK with index "001"
        with pytest.raises(ToolError) as exc_info:
            create_document(
                project_id="test-project",
                doc_type="Task",
                feature_id="test-feature",
                replacements={
                    "task-name": "001-NewTask",
                    "任務標題": "New Task with Duplicate Index"
                }
            )

        # Verify error code and message
        error = exc_info.value
        assert error.code == "DUPLICATE_TASK_INDEX"
        assert "001" in error.message
        assert "ExistingTask" in error.message

    def test_tc6_duplicate_task_index_with_new_md(self, mock_root_dir):
        """
        TC6: Duplicate TASK index check should also detect .new.md files.

        Given: A TASK document with index "002" exists as .new.md
        When: Attempt to create another TASK document with index "002"
        Then: Raise ToolError with DUPLICATE_TASK_INDEX code

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        temp_root, create_document = mock_root_dir

        # Setup: Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        tasks_dir = feature_dir / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        # Create existing TASK-002-ExistingTask.new.md
        existing_task = tasks_dir / "TASK-002-AnotherTask.new.md"
        existing_task.write_text("""---
id: TASK-002-AnotherTask
group_id: test-project
type: Task
---

<!-- id: sec-root -->
# Task: Another Task

Some content here.
""")

        # Attempt to create another TASK with index "002"
        with pytest.raises(ToolError) as exc_info:
            create_document(
                project_id="test-project",
                doc_type="Task",
                feature_id="test-feature",
                replacements={
                    "task-name": "002-NewTask",
                    "任務標題": "New Task with Duplicate Index"
                }
            )

        # Verify error code and message
        error = exc_info.value
        assert error.code == "DUPLICATE_TASK_INDEX"
        assert "002" in error.message

    def test_tc7_no_duplicate_different_index(self, mock_root_dir):
        """
        TC7: Creating TASK with different index should succeed.

        Given: A TASK document with index "001" exists
        When: Create a TASK document with index "003"
        Then: Document is created successfully

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        temp_root, create_document = mock_root_dir

        # Setup: Create directory structure and an existing TASK-001 file
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        tasks_dir = feature_dir / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        # Create existing TASK-001-ExistingTask.md
        existing_task = tasks_dir / "TASK-001-ExistingTask.md"
        existing_task.write_text("""---
id: TASK-001-ExistingTask
group_id: test-project
type: Task
---

<!-- id: sec-root -->
# Task: Existing Task

Some content here.
""")

        # Create TASK with different index "003" - should succeed
        result = create_document(
            project_id="test-project",
            doc_type="Task",
            feature_id="test-feature",
            replacements={
                "task-name": "003-NewTask",
                "任務標題": "New Task with Different Index"
            }
        )

        # Verify success
        assert "created successfully" in result.lower()

        # Verify file was created
        expected_file = tasks_dir / "TASK-003-NewTask.new.md"
        assert expected_file.exists(), f"Expected file not created: {expected_file}"
