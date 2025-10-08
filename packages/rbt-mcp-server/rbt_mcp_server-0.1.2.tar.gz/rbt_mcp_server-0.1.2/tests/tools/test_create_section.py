"""
Test cases for create_section tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-008-CreateSectionTool

Tests cover:
- TC1: Normal operation success
- TC2: Error conditions (ID not exist, type error, RBT restrictions)
"""

import os
import tempfile
import pytest
from pathlib import Path

from rbt_mcp_server.document_service import DocumentService
from rbt_mcp_server.errors import ToolError
from rbt_mcp_server.models import PathInfo


class TestCreateSection:
    """
    Test suite for create_section functionality.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-008-CreateSectionTool
    """

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
    def setup_rbt_document(self, temp_root):
        """Setup RBT document for testing."""
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

<!-- id: sec-root -->
# Requirement: Test Requirement

<!-- id: sec-parent -->
### 1. Parent Section

<!-- id: blk-parent-desc, type: paragraph -->
This is a parent section.

<!-- id: sec-parent-sub -->
#### 1.1 Existing Subsection

<!-- id: blk-sub-desc, type: paragraph -->
This is an existing subsection.
"""
        req_file = feature_dir / "REQ-test-feature.md"
        req_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "req_file": str(req_file),
            "feature_dir": str(feature_dir)
        }

    @pytest.fixture
    def setup_general_document(self, temp_root):
        """Setup general (non-RBT) document for testing."""
        project_dir = Path(temp_root) / "test-project"
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create a general document (no RBT structure)
        sample_md = """# General Document Title

## Section 1

This is section 1 content.

### Section 1.1

This is subsection content.
"""
        doc_file = docs_dir / "general.md"
        doc_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "doc_file": str(doc_file),
            "docs_dir": str(docs_dir)
        }

    # ==================== TC1: Normal Operation Success ====================

    def test_create_section_under_parent(self, service, setup_rbt_document):
        """
        TC1.1: Create new section under existing parent section.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Create new section
        new_section_id = service.create_section(
            path_info=path_info,
            parent_id="sec-parent",
            title="New Subsection",
            summary="This is a new subsection"
        )

        # Verify section was created
        assert new_section_id is not None
        assert new_section_id.startswith("sec-")

        # Load document and verify structure
        json_data = service.load_document(path_info)

        # Find parent section
        def find_section(sections, section_id):
            for section in sections:
                if section.get("id") == section_id:
                    return section
                if "sections" in section:
                    result = find_section(section["sections"], section_id)
                    if result:
                        return result
            return None

        parent_section = find_section(json_data["sections"], "sec-parent")
        assert parent_section is not None
        assert "sections" in parent_section

        # Find new section
        new_section = find_section(parent_section["sections"], new_section_id)
        assert new_section is not None
        assert new_section["title"] == "New Subsection"
        assert new_section["summary"] == "This is a new subsection"

    def test_create_section_without_summary(self, service, setup_rbt_document):
        """
        TC1.2: Create section without summary (optional parameter).

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Create new section without summary
        new_section_id = service.create_section(
            path_info=path_info,
            parent_id="sec-parent",
            title="Section Without Summary"
        )

        # Verify section was created
        assert new_section_id is not None

        # Load and verify
        json_data = service.load_document(path_info)

        def find_section(sections, section_id):
            for section in sections:
                if section.get("id") == section_id:
                    return section
                if "sections" in section:
                    result = find_section(section["sections"], section_id)
                    if result:
                        return result
            return None

        new_section = find_section(json_data["sections"], new_section_id)
        assert new_section is not None
        assert new_section["title"] == "Section Without Summary"
        assert new_section.get("summary", "") == ""

    def test_create_section_saves_as_new_md(self, service, setup_rbt_document):
        """
        TC1.3: Verify document is saved as .new.md file.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Create section
        service.create_section(
            path_info=path_info,
            parent_id="sec-parent",
            title="Test Section"
        )

        # Verify .new.md file exists
        new_file_path = setup_rbt_document["req_file"].replace(".md", ".new.md")
        assert os.path.exists(new_file_path)

    def test_create_section_generates_unique_id(self, service, setup_rbt_document):
        """
        TC1.4: Verify generated section IDs are unique.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Create multiple sections with same title
        id1 = service.create_section(
            path_info=path_info,
            parent_id="sec-parent",
            title="Same Title"
        )

        id2 = service.create_section(
            path_info=path_info,
            parent_id="sec-parent",
            title="Same Title"
        )

        # IDs should be different
        assert id1 != id2

    # ==================== TC2: Error Conditions ====================

    def test_create_section_parent_not_found(self, service, setup_rbt_document):
        """
        TC2.1: Error when parent section does not exist.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Try to create section under non-existent parent
        with pytest.raises(ToolError) as exc_info:
            service.create_section(
                path_info=path_info,
                parent_id="sec-nonexistent",
                title="New Section"
            )

        assert exc_info.value.code == "SECTION_NOT_FOUND"
        assert "sec-nonexistent" in exc_info.value.message

    def test_create_section_duplicate_id(self, service, setup_rbt_document):
        """
        TC2.2: Error when generated ID already exists (edge case).

        This test verifies the ID generation logic handles conflicts.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        # This is an edge case that should be handled by the ID generation logic
        # The implementation should check for duplicates and increment if needed
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Create multiple sections - IDs should all be unique
        ids = []
        for i in range(5):
            section_id = service.create_section(
                path_info=path_info,
                parent_id="sec-parent",
                title="Test"
            )
            ids.append(section_id)

        # All IDs should be unique
        assert len(ids) == len(set(ids))

    def test_create_root_section_in_general_doc(self, service, setup_general_document):
        """
        TC2.3: Allow creating root section in general (non-RBT) documents.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        # For general documents, we should be able to create top-level sections
        # This test verifies the behavior is different from RBT documents
        # Implementation should allow this for non-RBT docs

        # Note: This test may need adjustment based on final implementation
        # For now, we'll skip detailed testing until we clarify requirements
        pass

    def test_create_section_file_not_found(self, service, temp_root):
        """
        TC2.4: Error when document file does not exist.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id="test-project",
            feature_id="nonexistent",
            doc_type="REQ",
            file_path=os.path.join(temp_root, "nonexistent.md"),
            is_rbt=True,
            is_new_file=False
        )

        with pytest.raises(FileNotFoundError):
            service.create_section(
                path_info=path_info,
                parent_id="sec-parent",
                title="New Section"
            )

    def test_create_section_with_special_chars_in_title(self, service, setup_rbt_document):
        """
        TC2.5: Handle special characters in section title.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        path_info = PathInfo(
            project_id=setup_rbt_document["project_id"],
            feature_id=setup_rbt_document["feature_id"],
            doc_type="REQ",
            file_path=setup_rbt_document["req_file"],
            is_rbt=True,
            is_new_file=False
        )

        # Create section with special characters
        new_section_id = service.create_section(
            path_info=path_info,
            parent_id="sec-parent",
            title="Section with / & Special (Chars)"
        )

        # Should create successfully and sanitize ID
        assert new_section_id is not None
        assert new_section_id.startswith("sec-")

        # Verify in document
        json_data = service.load_document(path_info)

        def find_section(sections, section_id):
            for section in sections:
                if section.get("id") == section_id:
                    return section
                if "sections" in section:
                    result = find_section(section["sections"], section_id)
                    if result:
                        return result
            return None

        new_section = find_section(json_data["sections"], new_section_id)
        assert new_section is not None
        assert new_section["title"] == "Section with / & Special (Chars)"
