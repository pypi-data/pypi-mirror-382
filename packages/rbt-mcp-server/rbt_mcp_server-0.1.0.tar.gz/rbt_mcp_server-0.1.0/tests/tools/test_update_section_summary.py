"""
Test cases for update_section_summary tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-007-UpdateSectionSummaryTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the update_section_summary tool function and error types
from rbt_mcp_server.errors import ToolError


class TestUpdateSectionSummaryTool:
    """Test suite for update_section_summary tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document for update testing."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a sample RBT document
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
This is the original goal description that will be updated.

<!-- id: sec-scope -->
### 2. Scope Section

<!-- id: blk-scope-para, type: paragraph -->
This section defines the scope.

<!-- id: sec-nested -->
#### 2.1 Nested Section

<!-- id: blk-nested-para, type: paragraph -->
This is a nested section.
"""
        req_file = feature_dir / "REQ-test-feature.md"
        req_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "doc_type": "REQ",
            "req_file": str(req_file),
            "feature_dir": str(feature_dir)
        }

    @pytest.fixture
    def mock_root_dir(self, temp_root):
        """Mock the RBT_ROOT_DIR environment variable and document_service."""
        # Set environment variable
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import update_section_summary
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service to use our test service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, update_section_summary)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    # ========== Test Case 1: Successfully update summary and generate .new.md ==========
    def test_update_section_summary_success(self, setup_test_document, mock_root_dir):
        """
        Test Case 1: Successfully update summary and generate .new.md file.

        Given: A valid RBT document with multiple sections
        When: update_section_summary is called with valid section_id and new_summary
        Then:
            - Section summary is updated
            - File is saved as .new.md
            - Other sections remain unchanged
            - Success message is returned

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-007-UpdateSectionSummaryTool
        """
        # Unpack fixture
        _, update_section_summary = mock_root_dir

        # Define test data
        section_id = "sec-goal"
        new_summary = "This is the UPDATED goal description with new content."

        # Call update_section_summary
        result = update_section_summary(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"],
            section_id=section_id,
            new_summary=new_summary
        )

        # Verify success message
        assert result is not None
        assert isinstance(result, str)
        assert "success" in result.lower()
        assert section_id in result

        # Verify .new.md file exists
        feature_dir = Path(setup_test_document["feature_dir"])
        new_file = feature_dir / "REQ-test-feature.new.md"
        assert new_file.exists(), ".new.md file should be created"

        # Read and verify the new file content
        new_content = new_file.read_text()

        # Verify the updated summary is in the file
        # Summary should be written as [SUMMARY: ...] in Markdown
        assert f"[SUMMARY: {new_summary}]" in new_content, "New summary should be in [SUMMARY: ...] format"

        # Verify the original block content remains unchanged (summary is separate from blocks)
        assert "This is the original goal description that will be updated." in new_content

        # Verify other sections remain unchanged
        assert "### 2. Scope Section" in new_content
        assert "This section defines the scope." in new_content

        # Verify metadata is preserved
        assert "id: REQ-test" in new_content
        assert "type: Requirement" in new_content

        # Additional verification: Load the document and check JSON structure
        from rbt_mcp_server.document_service import DocumentService
        service = DocumentService(setup_test_document["temp_root"])
        from rbt_mcp_server.path_resolver import PathResolver

        path_resolver = PathResolver(setup_test_document["temp_root"])
        path_info = path_resolver.resolve(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        json_data = service.load_document(path_info)

        # Find the updated section in JSON
        def find_section(sections, target_id):
            for section in sections:
                if section.get("id") == target_id:
                    return section
                if "sections" in section:
                    result = find_section(section["sections"], target_id)
                    if result:
                        return result
            return None

        updated_section = find_section(json_data["sections"], section_id)
        assert updated_section is not None

        # Verify the summary field in the section is updated
        # Summary is a separate field from blocks
        assert "summary" in updated_section
        assert updated_section["summary"] == new_summary

        # Verify blocks remain unchanged
        assert "blocks" in updated_section
        assert len(updated_section["blocks"]) > 0
        first_block = updated_section["blocks"][0]
        assert "This is the original goal description that will be updated." in first_block.get("content", "")

    # ========== Test Case 2: Section not found error ==========
    def test_update_section_summary_not_found(self, setup_test_document, mock_root_dir):
        """
        Test Case 2: Section ID does not exist -> ToolError.

        Given: A valid RBT document
        When: update_section_summary is called with non-existent section_id
        Then: ToolError is raised with appropriate message

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-007-UpdateSectionSummaryTool
        """
        # Unpack fixture
        _, update_section_summary = mock_root_dir

        # Define test data with non-existent section ID
        section_id = "sec-non-existent"
        new_summary = "This should not be saved."

        # Attempt to update non-existent section
        with pytest.raises(ToolError) as exc_info:
            update_section_summary(
                project_id=setup_test_document["project_id"],
                feature_id=setup_test_document["feature_id"],
                doc_type=setup_test_document["doc_type"],
                section_id=section_id,
                new_summary=new_summary
            )

        # Verify error details
        error = exc_info.value
        assert error.code == "SECTION_NOT_FOUND" or "UPDATE_SUMMARY_ERROR" in error.code
        assert section_id in str(error)
        assert "not found" in str(error).lower()

        # Verify .new.md file was NOT created (since operation failed)
        feature_dir = Path(setup_test_document["feature_dir"])
        new_file = feature_dir / "REQ-test-feature.new.md"
        assert not new_file.exists(), ".new.md file should NOT be created on error"
