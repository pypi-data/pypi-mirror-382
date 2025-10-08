"""
Test cases for create_document tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-014-CreateDocumentTool
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the create_document tool function and error types
from rbt_mcp_server.errors import ToolError


class TestCreateDocumentTool:
    """Test suite for create_document tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_root_dir(self, temp_root):
        """Mock the RBT_ROOT_DIR environment variable and document_service."""
        # Set environment variable
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

    # ========== Test Case 1: Create RBT document successfully ==========
    def test_create_rbt_document_success(self, mock_root_dir):
        """
        Test Case 1: Create RBT document successfully.

        Given: Valid parameters for a new RBT document (REQ)
        When: create_document is called
        Then: Document is created with metadata, info section, and root section

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        # Unpack fixture
        temp_root, create_document = mock_root_dir

        # Call create_document for RBT document
        result_path = create_document(
            project_id="test-project",
            feature_id="test-feature",
            doc_type="REQ",
            title="Test Requirement Document",
            metadata={
                "id": "REQ-test-feature",
                "type": "Requirement",
                "group_id": "test-project",
                "feature": "test-feature"
            }
        )

        # Verify return value is file path
        assert result_path is not None
        assert isinstance(result_path, str)
        assert result_path.endswith(".new.md")

        # Verify file exists
        assert os.path.exists(result_path), f"File not created at {result_path}"

        # Read and verify file content
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify YAML frontmatter
        assert "---" in content
        assert "id: REQ-test-feature" in content
        assert "type: Requirement" in content
        assert "group_id: test-project" in content
        assert "feature: test-feature" in content

        # Verify info section
        assert "<!-- info-section -->" in content

        # Verify root section
        assert "<!-- id: sec-root -->" in content
        assert "# Test Requirement Document" in content or \
               "# Requirement: Test Requirement Document" in content

        # Verify it's a valid RBT document by converting it
        from rbt_mcp_server.document_service import DocumentService
        service = DocumentService(temp_root)

        # Should be able to load without error
        from rbt_mcp_server.path_resolver import PathResolver
        resolver = PathResolver(temp_root)
        path_info = resolver.resolve(
            project_id="test-project",
            feature_id="test-feature",
            doc_type="REQ"
        )
        json_data = service.load_document(path_info)

        # Verify JSON structure
        assert "metadata" in json_data
        assert json_data["metadata"]["id"] == "REQ-test-feature"
        assert "info" in json_data
        assert "title" in json_data
        assert "sections" in json_data

    # ========== Test Case 2: Create general document successfully ==========
    def test_create_general_document_success(self, mock_root_dir):
        """
        Test Case 2: Create general document successfully.

        Given: Valid parameters for a new general document (in docs/)
        When: create_document is called with file_path parameter
        Then: Document is created in docs/ directory

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        # Unpack fixture
        temp_root, create_document = mock_root_dir

        # Call create_document for general document
        result_path = create_document(
            project_id="test-project",
            file_path="guides/getting-started.md",
            title="Getting Started Guide",
            metadata={
                "id": "DOC-getting-started",
                "type": "Document",
                "author": "Test Author"
            }
        )

        # Verify return value
        assert result_path is not None
        assert isinstance(result_path, str)
        assert result_path.endswith(".new.md")
        assert "docs" in result_path
        assert "guides" in result_path

        # Verify file exists
        assert os.path.exists(result_path), f"File not created at {result_path}"

        # Read and verify content
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify metadata
        assert "id: DOC-getting-started" in content
        assert "type: Document" in content
        assert "author: Test Author" in content

        # Verify title
        assert "Getting Started Guide" in content

    # ========== Test Case 3: Validate metadata fields ==========
    def test_create_document_metadata_validation(self, mock_root_dir):
        """
        Test Case 3: Validate required metadata fields.

        Given: Metadata missing required fields
        When: create_document is called
        Then: Should raise ToolError with appropriate message

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        # Unpack fixture
        _, create_document = mock_root_dir

        # Missing 'id' field
        with pytest.raises(ToolError) as exc_info:
            create_document(
                project_id="test-project",
                feature_id="test-feature",
                doc_type="REQ",
                title="Test Document",
                metadata={
                    "type": "Requirement",
                    # Missing 'id'
                }
            )
        assert "id" in str(exc_info.value).lower()

        # Missing 'type' field
        with pytest.raises(ToolError) as exc_info:
            create_document(
                project_id="test-project",
                feature_id="test-feature",
                doc_type="REQ",
                title="Test Document",
                metadata={
                    "id": "REQ-test",
                    # Missing 'type'
                }
            )
        assert "type" in str(exc_info.value).lower()

    # ========== Test Case 4: File already exists error ==========
    def test_create_document_file_exists(self, mock_root_dir):
        """
        Test Case 4: Handle file already exists error.

        Given: A document already exists at the target path
        When: create_document is called with same parameters
        Then: Should raise ToolError indicating file exists

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        # Unpack fixture
        temp_root, create_document = mock_root_dir

        # Create document first time
        create_document(
            project_id="test-project",
            feature_id="test-feature",
            doc_type="REQ",
            title="Test Document",
            metadata={
                "id": "REQ-test",
                "type": "Requirement",
                "group_id": "test-project",
                "feature": "test-feature"
            }
        )

        # Try to create again
        with pytest.raises(ToolError) as exc_info:
            create_document(
                project_id="test-project",
                feature_id="test-feature",
                doc_type="REQ",
                title="Test Document",
                metadata={
                    "id": "REQ-test",
                    "type": "Requirement",
                    "group_id": "test-project",
                    "feature": "test-feature"
                }
            )

        error_msg = str(exc_info.value)
        assert "exists" in error_msg.lower() or "already" in error_msg.lower()

    # ========== Test Case 5: Create nested directory structure ==========
    def test_create_document_creates_directories(self, mock_root_dir):
        """
        Test Case 5: Automatically create directory structure.

        Given: Directory structure does not exist
        When: create_document is called
        Then: All necessary directories are created

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        # Unpack fixture
        temp_root, create_document = mock_root_dir

        # Verify directory doesn't exist
        project_dir = Path(temp_root) / "new-project" / "features" / "new-feature"
        assert not project_dir.exists()

        # Create document
        result_path = create_document(
            project_id="new-project",
            feature_id="new-feature",
            doc_type="BP",
            title="New Blueprint",
            metadata={
                "id": "BP-new-feature",
                "type": "Blueprint",
                "group_id": "new-project",
                "feature": "new-feature"
            }
        )

        # Verify directory was created
        assert project_dir.exists()
        assert os.path.exists(result_path)

    # ========== Test Case 6: Invalid path characters ==========
    def test_create_document_invalid_path(self, mock_root_dir):
        """
        Test Case 6: Handle invalid path characters.

        Given: Path contains invalid characters
        When: create_document is called
        Then: Should raise ToolError

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        # Unpack fixture
        _, create_document = mock_root_dir

        # Invalid characters in project_id
        with pytest.raises((ToolError, ValueError)) as exc_info:
            create_document(
                project_id="../invalid",
                feature_id="test",
                doc_type="REQ",
                title="Test",
                metadata={"id": "REQ-test", "type": "Requirement"}
            )

        # Error message should indicate path issue
        error_msg = str(exc_info.value).lower()
        assert "path" in error_msg or "invalid" in error_msg or ".." in error_msg
