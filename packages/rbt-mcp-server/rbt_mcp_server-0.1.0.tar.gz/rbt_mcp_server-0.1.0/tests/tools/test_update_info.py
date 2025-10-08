"""
Test cases for update_info tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-016-UpdateInfoTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestUpdateInfoTool:
    """Test suite for update_info tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document with info section."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a RBT document with info section
        sample_md = """---
id: BP-test
group_id: test-project
type: Blueprint
feature: test-feature
---

<!-- info-section -->
> status: Draft
> update_date: 2025-10-01
> dependencies: []

<!-- id: sec-root -->
# Blueprint: Test Blueprint

<!-- id: sec-intro -->
### Introduction

<!-- id: blk-desc, type: paragraph -->
This is a test document.
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
    def test_tc1_update_status_success(self, setup_test_document):
        """
        TC1: Update status successfully.

        Given: A document with info section (status: Draft)
        When: Update status to "In Progress"
        Then: Status is updated, other fields unchanged
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

        # Update status
        doc_service.update_info(path_info, status="In Progress")

        # Verify: Load document and check status updated
        json_data = doc_service.load_document(path_info)
        assert json_data["info"]["status"] == "In Progress"
        assert json_data["info"]["update_date"] == "2025-10-01"  # Unchanged
        assert json_data["info"]["dependencies"] == []  # Unchanged

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc2_update_update_date_success(self, setup_test_document):
        """
        TC2: Update update_date successfully.

        Given: A document with info section (update_date: 2025-10-01)
        When: Update update_date to "2025-10-08"
        Then: update_date is updated, other fields unchanged
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

        # Update update_date
        doc_service.update_info(path_info, update_date="2025-10-08")

        # Verify: Load document and check update_date updated
        json_data = doc_service.load_document(path_info)
        assert json_data["info"]["status"] == "Draft"  # Unchanged
        assert json_data["info"]["update_date"] == "2025-10-08"
        assert json_data["info"]["dependencies"] == []  # Unchanged

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc3_update_dependencies_success(self, setup_test_document):
        """
        TC3: Update dependencies successfully.

        Given: A document with info section (dependencies: [])
        When: Update dependencies to ["TASK-001", "TASK-002"]
        Then: dependencies is updated, other fields unchanged
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

        # Update dependencies
        doc_service.update_info(path_info, dependencies=["TASK-001", "TASK-002"])

        # Verify: Load document and check dependencies updated
        json_data = doc_service.load_document(path_info)
        assert json_data["info"]["status"] == "Draft"  # Unchanged
        assert json_data["info"]["update_date"] == "2025-10-01"  # Unchanged
        assert json_data["info"]["dependencies"] == ["TASK-001", "TASK-002"]

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc4_partial_update_multiple_fields(self, setup_test_document):
        """
        TC4: Partial update (update multiple fields).

        Given: A document with info section
        When: Update both status and update_date
        Then: Both fields are updated, dependencies unchanged
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

        # Update multiple fields
        doc_service.update_info(
            path_info,
            status="Done",
            update_date="2025-10-09"
        )

        # Verify: Load document and check both fields updated
        json_data = doc_service.load_document(path_info)
        assert json_data["info"]["status"] == "Done"
        assert json_data["info"]["update_date"] == "2025-10-09"
        assert json_data["info"]["dependencies"] == []  # Unchanged

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc5_no_fields_provided_error(self, setup_test_document):
        """
        TC5: Error handling when no fields provided.

        Given: A document with info section
        When: Call update_info without any fields
        Then: Raise NO_FIELDS_PROVIDED error
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

        # Attempt to update without any fields
        with pytest.raises(ToolError) as exc_info:
            doc_service.update_info(path_info)

        assert exc_info.value.code == "NO_FIELDS_PROVIDED"
        assert "At least one field" in str(exc_info.value)

    @pytest.fixture
    def setup_document_without_info(self, temp_root):
        """Setup a document without info section."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create a general document without info section
        sample_md = """---
id: general-doc
group_id: test-project
type: General
---

<!-- id: sec-root -->
# Document Without Info

<!-- id: sec-content -->
### Content

<!-- id: blk-text, type: paragraph -->
This document has no info section.
"""
        doc_file = docs_dir / "test-doc.md"
        doc_file.write_text(sample_md)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "file_path": "test-doc.md",
            "doc_file": str(doc_file)
        }

    @patch.dict(os.environ, {"RBT_ROOT_DIR": ""})
    def test_tc6_info_section_not_found_error(self, setup_document_without_info):
        """
        TC6: Error handling when document has no info section.

        Given: A document without info section
        When: Attempt to update info
        Then: Raise INFO_SECTION_NOT_FOUND error
        """
        from rbt_mcp_server.document_service import DocumentService
        from rbt_mcp_server.path_resolver import PathResolver

        # Setup
        os.environ["RBT_ROOT_DIR"] = setup_document_without_info["temp_root"]
        path_resolver = PathResolver(setup_document_without_info["temp_root"])
        doc_service = DocumentService(path_resolver)

        # Resolve path
        path_info = path_resolver.resolve(
            project_id=setup_document_without_info["project_id"],
            file_path=setup_document_without_info["file_path"]
        )

        # Attempt to update info on document without info section
        with pytest.raises(ToolError) as exc_info:
            doc_service.update_info(path_info, status="Done")

        assert exc_info.value.code == "INFO_SECTION_NOT_FOUND"
        assert "info section" in str(exc_info.value)
