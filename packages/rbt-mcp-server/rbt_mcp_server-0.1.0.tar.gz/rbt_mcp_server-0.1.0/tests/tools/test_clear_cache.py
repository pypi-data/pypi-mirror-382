"""
Test cases for clear_cache tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-015-ClearCacheTool
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from rbt_mcp_server.errors import ToolError


class TestClearCacheTool:
    """Test suite for clear_cache tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_documents(self, temp_root):
        """Setup multiple test documents for cache testing."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create test documents
        doc1_content = """---
id: REQ-test1
group_id: test-project
type: Requirement
feature: test-feature
---

<!-- info-section -->
> status: Draft

<!-- id: sec-root -->
# Test Document 1

<!-- id: sec-content -->
### Content

<!-- id: blk-para, type: paragraph -->
This is test document 1.
"""

        doc2_content = """---
id: REQ-test2
group_id: test-project
type: Requirement
feature: test-feature
---

<!-- info-section -->
> status: Draft

<!-- id: sec-root -->
# Test Document 2

<!-- id: sec-content -->
### Content

<!-- id: blk-para, type: paragraph -->
This is test document 2.
"""

        doc1_file = feature_dir / "REQ-test-feature-1.md"
        doc2_file = feature_dir / "REQ-test-feature-2.md"

        doc1_file.write_text(doc1_content)
        doc2_file.write_text(doc2_content)

        return {
            "temp_root": temp_root,
            "project_id": "test-project",
            "feature_id": "test-feature",
            "doc1_path": str(doc1_file),
            "doc2_path": str(doc2_file),
        }

    @pytest.fixture
    def mock_root_dir(self, temp_root):
        """Mock the RBT_ROOT_DIR environment variable and import clear_cache."""
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import clear_cache
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, clear_cache, test_service)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    # ========== Test Case 1: Clear all cache ==========
    def test_clear_all_cache(self, setup_test_documents, mock_root_dir):
        """
        Test Case 1: Clear all cache successfully.

        Given: Multiple documents loaded in cache
        When: clear_cache() is called without file_path parameter
        Then: All cache entries should be cleared, return success message

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-015-ClearCacheTool
        """
        _, clear_cache, test_service = mock_root_dir

        # Load documents to populate cache
        from rbt_mcp_server.models import PathInfo

        path1 = PathInfo(
            project_id="test-project",
            feature_id="test-feature",
            doc_type=None,
            file_path=setup_test_documents["doc1_path"],
            is_rbt=True,
            is_new_file=False
        )
        path2 = PathInfo(
            project_id="test-project",
            feature_id="test-feature",
            doc_type=None,
            file_path=setup_test_documents["doc2_path"],
            is_rbt=True,
            is_new_file=False
        )

        # Load documents (should cache them)
        test_service.load_document(path1)
        test_service.load_document(path2)

        # Verify cache has entries
        assert test_service.cache.get(setup_test_documents["doc1_path"]) is not None
        assert test_service.cache.get(setup_test_documents["doc2_path"]) is not None

        # Clear all cache
        result = clear_cache()

        # Verify success message
        assert isinstance(result, str)
        assert "success" in result.lower()
        assert "all" in result.lower()

        # Verify cache is empty
        assert test_service.cache.get(setup_test_documents["doc1_path"]) is None
        assert test_service.cache.get(setup_test_documents["doc2_path"]) is None

    # ========== Test Case 2: Clear specific file cache ==========
    def test_clear_specific_file_cache(self, setup_test_documents, mock_root_dir):
        """
        Test Case 2: Clear specific file cache successfully.

        Given: Multiple documents loaded in cache
        When: clear_cache(file_path="...") is called with specific file path
        Then: Only that file's cache should be cleared, other cache remains

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-015-ClearCacheTool
        """
        _, clear_cache, test_service = mock_root_dir

        # Load documents to populate cache
        from rbt_mcp_server.models import PathInfo

        path1 = PathInfo(
            project_id="test-project",
            feature_id="test-feature",
            doc_type=None,
            file_path=setup_test_documents["doc1_path"],
            is_rbt=True,
            is_new_file=False
        )
        path2 = PathInfo(
            project_id="test-project",
            feature_id="test-feature",
            doc_type=None,
            file_path=setup_test_documents["doc2_path"],
            is_rbt=True,
            is_new_file=False
        )

        # Load documents (should cache them)
        test_service.load_document(path1)
        test_service.load_document(path2)

        # Verify both are cached
        assert test_service.cache.get(setup_test_documents["doc1_path"]) is not None
        assert test_service.cache.get(setup_test_documents["doc2_path"]) is not None

        # Clear only doc1
        result = clear_cache(file_path=setup_test_documents["doc1_path"])

        # Verify success message with file path
        assert isinstance(result, str)
        assert "success" in result.lower()
        assert setup_test_documents["doc1_path"] in result

        # Verify doc1 cache is cleared
        assert test_service.cache.get(setup_test_documents["doc1_path"]) is None

        # Verify doc2 cache still exists
        assert test_service.cache.get(setup_test_documents["doc2_path"]) is not None

    # ========== Test Case 3: Clear non-existent file cache ==========
    def test_clear_nonexistent_file_cache(self, setup_test_documents, mock_root_dir):
        """
        Test Case 3: Clear cache for non-existent file (no error).

        Given: Cache does not contain specified file
        When: clear_cache(file_path="...") is called
        Then: Should succeed without error (idempotent operation)

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-015-ClearCacheTool
        """
        _, clear_cache, test_service = mock_root_dir

        # Try to clear cache for a non-existent file
        non_existent_path = "/path/to/nonexistent/file.md"

        # Should not raise error
        result = clear_cache(file_path=non_existent_path)

        # Verify success message
        assert isinstance(result, str)
        assert "success" in result.lower()

    # ========== Test Case 4: Clear empty cache ==========
    def test_clear_empty_cache(self, setup_test_documents, mock_root_dir):
        """
        Test Case 4: Clear cache when cache is already empty.

        Given: Cache is empty
        When: clear_cache() is called
        Then: Should succeed without error (idempotent operation)

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-015-ClearCacheTool
        """
        _, clear_cache, test_service = mock_root_dir

        # Verify cache is empty
        # Note: We can't easily check if cache is truly empty without internal access
        # But we can verify the operation succeeds

        # Clear empty cache
        result = clear_cache()

        # Verify success message
        assert isinstance(result, str)
        assert "success" in result.lower()
        assert "all" in result.lower()

    # ========== Test Case 5: Verify cache is actually cleared ==========
    def test_cache_actually_cleared(self, setup_test_documents, mock_root_dir):
        """
        Test Case 5: Verify cache clear forces reload from disk.

        Given: Document loaded in cache
        When: clear_cache() is called, then document is loaded again
        Then: Document should be reloaded from disk (cache miss)

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-015-ClearCacheTool
        """
        _, clear_cache, test_service = mock_root_dir

        # Load document
        from rbt_mcp_server.models import PathInfo

        path1 = PathInfo(
            project_id="test-project",
            feature_id="test-feature",
            doc_type=None,
            file_path=setup_test_documents["doc1_path"],
            is_rbt=True,
            is_new_file=False
        )

        # First load (cache miss)
        doc1_first = test_service.load_document(path1)

        # Verify it's cached
        cached = test_service.cache.get(setup_test_documents["doc1_path"])
        assert cached is not None

        # Clear cache
        clear_cache(file_path=setup_test_documents["doc1_path"])

        # Verify cache is cleared
        assert test_service.cache.get(setup_test_documents["doc1_path"]) is None

        # Load again (should be cache miss, reload from disk)
        doc1_second = test_service.load_document(path1)

        # Verify documents are equivalent (loaded from same file)
        assert doc1_first["metadata"] == doc1_second["metadata"]
        assert doc1_first["title"] == doc1_second["title"]

        # Verify it's cached again
        assert test_service.cache.get(setup_test_documents["doc1_path"]) is not None
