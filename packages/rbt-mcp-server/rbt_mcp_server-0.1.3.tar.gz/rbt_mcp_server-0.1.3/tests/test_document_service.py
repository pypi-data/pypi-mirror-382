"""
Test cases for DocumentService - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-003-DocumentService
"""

import os
import tempfile
import pytest
from pathlib import Path

from rbt_mcp_server.document_service import DocumentService
from rbt_mcp_server.errors import ToolError
from rbt_mcp_server.models import PathInfo


class TestDocumentService:
    """Test suite for DocumentService following TDD approach."""

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
        """Setup test file structure with sample RBT documents."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a sample RBT document with proper structure
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
This is a test requirement document for testing DocumentService.

<!-- id: blk-goal-list, type: list -->
**Key Points**
  - Point 1
  - Point 2
  - Point 3

<!-- id: sec-details -->
### 2. Details Section

<!-- id: blk-details-table, type: table -->
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

<!-- id: sec-subsection -->
#### 2.1 Subsection

<!-- id: blk-subsection-para, type: paragraph -->
This is a subsection paragraph.
"""
        req_file = feature_dir / "REQ-test-feature.md"
        req_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "req_file": str(req_file)
        }

    # Test Case 1: Load document (no cache)
    def test_load_document_no_cache(self, service, setup_test_files):
        """Test loading document without cache hit."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # First load should read from file
        json_data = service.load_document(path_info)

        # Verify structure
        assert json_data is not None
        assert "metadata" in json_data
        assert json_data["metadata"]["id"] == "REQ-test"
        assert "info" in json_data
        assert "title" in json_data
        assert "sections" in json_data

    # Test Case 2: Load document (cache hit)
    def test_load_document_cache_hit(self, service, setup_test_files):
        """Test loading document with cache hit."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # First load
        json_data_1 = service.load_document(path_info)

        # Modify returned data to verify cache returns copy
        json_data_1["test_marker"] = "modified"

        # Second load should come from cache
        json_data_2 = service.load_document(path_info)

        # Should not have the marker (deep copy)
        assert "test_marker" not in json_data_2
        assert json_data_2["metadata"]["id"] == "REQ-test"

    # Test Case 3: Prefer .new.md version
    def test_load_document_prefer_new_md(self, service, setup_test_files):
        """Test that .new.md version is preferred over .md."""
        # Create .new.md version with modified content
        new_md = """---
id: REQ-test-new
group_id: test-project
type: Requirement
feature: test-feature
---

<!-- info-section -->
> status: Updated

<!-- id: sec-root -->
# Requirement: Updated Version
"""
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        Path(new_file).write_text(new_md)

        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )

        json_data = service.load_document(path_info)

        # Should load the .new.md version
        assert json_data["metadata"]["id"] == "REQ-test-new"
        assert json_data["title"] == "Requirement: Updated Version"

    # Test Case 4: Save document as .new.md
    def test_save_document_as_new_md(self, service, setup_test_files):
        """Test saving document creates .new.md file."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Load and modify
        json_data = service.load_document(path_info)
        json_data["metadata"]["status"] = "Modified"

        # Save should create .new.md
        service.save_document(path_info, json_data)

        # Check .new.md exists
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        assert os.path.exists(new_file)

        # Original file should be unchanged
        original_content = Path(setup_test_files["req_file"]).read_text()
        assert "status: Draft" in original_content

    # Test Case 5: get_outline removes blocks
    def test_get_outline_removes_blocks(self, service, setup_test_files):
        """Test that get_outline returns structure without blocks."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        outline = service.get_outline(path_info)

        # Should have metadata, info, title, sections
        assert "metadata" in outline
        assert "info" in outline
        assert "title" in outline
        assert "sections" in outline

        # Check that blocks are removed recursively
        def check_no_blocks(sections):
            for section in sections:
                assert "blocks" not in section
                if "sections" in section:
                    check_no_blocks(section["sections"])

        check_no_blocks(outline["sections"])

    # Test Case 6: read_section success
    def test_read_section_success(self, service, setup_test_files):
        """Test reading a specific section by ID."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        section_data = service.read_section(path_info, "sec-goal")

        # Should have section data with blocks
        assert section_data is not None
        assert section_data["id"] == "sec-goal"
        assert "title" in section_data
        assert "blocks" in section_data
        assert len(section_data["blocks"]) > 0

    # Test Case 7: read_section not found
    def test_read_section_not_found(self, service, setup_test_files):
        """Test reading non-existent section raises ToolError."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        with pytest.raises(ToolError) as exc_info:
            service.read_section(path_info, "sec-nonexistent")

        assert exc_info.value.code == "SECTION_NOT_FOUND"
        assert "sec-nonexistent" in exc_info.value.message

    # Test Case 8: update_section_summary success
    def test_update_section_summary_success(self, service, setup_test_files):
        """Test updating section summary."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        new_summary = "This is an updated summary for the goal section."
        service.update_section_summary(path_info, "sec-goal", new_summary)

        # Verify .new.md was created
        new_file = setup_test_files["req_file"].replace(".md", ".new.md")
        assert os.path.exists(new_file)

        # Read from the new file to verify the update
        new_path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=new_file,
            is_rbt=True,
            is_new_file=True
        )
        section_data = service.read_section(new_path_info, "sec-goal")
        assert section_data["summary"] == new_summary

    # Test Case 9: clear_cache
    def test_clear_cache(self, service, setup_test_files):
        """Test clearing cache."""
        path_info = PathInfo(
            project_id=setup_test_files["project_id"],
            feature_id=setup_test_files["feature_id"],
            doc_type="REQ",
            file_path=setup_test_files["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Load document to cache it
        service.load_document(path_info)

        # Clear specific file cache
        service.clear_cache(setup_test_files["req_file"])

        # Clear all cache
        service.clear_cache()

        # No error should occur
        assert True
