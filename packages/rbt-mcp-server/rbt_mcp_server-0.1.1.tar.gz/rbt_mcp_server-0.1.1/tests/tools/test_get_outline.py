"""
Test cases for get_outline tool - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-005-GetOutlineTool
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Import the get_outline tool function and error types
# Note: server.py requires RBT_ROOT_DIR to be set at import time
# We handle this in the fixture below
from rbt_mcp_server.errors import ToolError


class TestGetOutlineTool:
    """Test suite for get_outline tool following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def setup_test_document(self, temp_root):
        """Setup a test RBT document with comprehensive structure."""
        # Create directory structure
        project_dir = Path(temp_root) / "test-project"
        feature_dir = project_dir / "features" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Create a comprehensive RBT document with multiple sections and blocks
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
This is a test requirement document for testing get_outline tool.
It contains multiple sections with various block types to verify
that the outline correctly excludes all block content.

<!-- id: blk-goal-list, type: list -->
**Key Points**
  - Point 1: First important point
  - Point 2: Second important point
  - Point 3: Third important point
  - Point 4: Fourth important point

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

<!-- id: sec-nested -->
##### 2.1.1 Nested Subsection

<!-- id: blk-nested-para, type: paragraph -->
This is a deeply nested subsection to test hierarchy.

<!-- id: sec-details -->
### 3. Details Section

<!-- id: blk-details-list, type: list -->
**Details**
  - Detail A: This is a detailed description of item A with lots of text
  - Detail B: This is a detailed description of item B with lots of text
  - Detail C: This is a detailed description of item C with lots of text
  - Detail D: This is a detailed description of item D with lots of text
  - Detail E: This is a detailed description of item E with lots of text

<!-- id: sec-implementation -->
### 4. Implementation Section

<!-- id: blk-impl-para, type: paragraph -->
This section contains detailed implementation instructions that should be
excluded from the outline. The implementation details include various
technical specifications, code examples, and configuration settings
that are not needed when getting just the document outline.

<!-- id: blk-impl-code, type: code -->
```python
# Long code block that should be excluded from outline
class ExampleClass:
    def __init__(self):
        self.data = []

    def process(self, items):
        for item in items:
            self.data.append(item)
        return self.data

    def transform(self, func):
        return [func(x) for x in self.data]
```

<!-- id: blk-impl-table, type: table -->
| Component | Description | Status | Priority | Owner |
|-----------|-------------|--------|----------|-------|
| Module A | First module with long description | Active | High | Team 1 |
| Module B | Second module with long description | Pending | Medium | Team 2 |
| Module C | Third module with long description | Active | High | Team 1 |
| Module D | Fourth module with long description | Blocked | Low | Team 3 |

<!-- id: sec-testing -->
### 5. Testing Section

<!-- id: blk-test-para, type: paragraph -->
This section describes the testing approach and strategies.
All tests should cover unit testing, integration testing, and
end-to-end testing scenarios with comprehensive coverage.

<!-- id: blk-test-list, type: list -->
**Test Coverage**
  - Unit tests for all core functions with detailed assertions
  - Integration tests for API endpoints with mock data
  - E2E tests for critical user flows with scenarios
  - Performance tests for scalability under load
  - Security tests for vulnerabilities and penetration testing
  - Regression tests for bug fixes and patches
  - Smoke tests for deployment validation

<!-- id: sec-appendix -->
### 6. Appendix Section

<!-- id: blk-appendix-para, type: paragraph -->
This appendix contains additional reference materials, technical
specifications, and supplementary information that supports the
main document content. It includes detailed API documentation,
configuration examples, troubleshooting guides, and best practices
for implementation and maintenance.

<!-- id: blk-appendix-code, type: code -->
```json
{
  "config": {
    "database": {
      "host": "localhost",
      "port": 5432,
      "name": "testdb"
    },
    "cache": {
      "type": "redis",
      "ttl": 300
    },
    "logging": {
      "level": "info",
      "format": "json"
    }
  }
}
```

<!-- id: blk-appendix-table, type: table -->
| API Endpoint | Method | Parameters | Response | Auth |
|--------------|--------|------------|----------|------|
| /api/users | GET | page, limit | User list | Required |
| /api/users/:id | GET | id | User details | Required |
| /api/users | POST | user data | Created user | Required |
| /api/users/:id | PUT | id, user data | Updated user | Required |
| /api/users/:id | DELETE | id | Success message | Required |
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
        # Import get_outline here to avoid import-time issues
        # First set the environment variable
        original_env = os.environ.get("RBT_ROOT_DIR")
        os.environ["RBT_ROOT_DIR"] = temp_root

        try:
            # Import after setting env var
            from rbt_mcp_server.server import get_outline
            from rbt_mcp_server.document_service import DocumentService

            # Create a test service with the temp root
            test_service = DocumentService(temp_root)

            # Patch the global document_service to use our test service
            with patch('rbt_mcp_server.server.document_service', test_service):
                yield (temp_root, get_outline)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RBT_ROOT_DIR"] = original_env
            elif "RBT_ROOT_DIR" in os.environ:
                del os.environ["RBT_ROOT_DIR"]

    # ========== Test Case 1: Correct outline return (no blocks) ==========
    def test_get_outline_excludes_blocks(self, setup_test_document, mock_root_dir):
        """
        Test Case 1: Correct outline return (no blocks).

        Given: A complete RBT document with sections and blocks
        When: get_outline is called
        Then: Return JSON without blocks, only section tree structure

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-005-GetOutlineTool
        """
        # Unpack fixture
        _, get_outline = mock_root_dir

        # Call get_outline
        result = get_outline(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Verify structure
        assert result is not None
        assert isinstance(result, dict)

        # Verify metadata is present
        assert "metadata" in result
        assert result["metadata"]["id"] == "REQ-test"
        assert result["metadata"]["type"] == "Requirement"

        # Verify info is present
        assert "info" in result

        # Verify title is present
        assert "title" in result

        # Verify sections are present
        assert "sections" in result
        assert len(result["sections"]) > 0

        # Recursively verify NO blocks exist in any section
        def check_no_blocks(sections):
            """Recursively check that no section has blocks."""
            for section in sections:
                # Should NOT have blocks
                assert "blocks" not in section, f"Section {section.get('id')} still has blocks!"

                # Should have basic section info
                assert "id" in section
                assert "title" in section

                # Recursively check sub-sections
                if "sections" in section:
                    check_no_blocks(section["sections"])

        check_no_blocks(result["sections"])

        # Verify section hierarchy exists
        # The structure has all sections at the same level, not nested under sec-root
        # This is how the converter parses the document
        assert len(result["sections"]) >= 3  # At least 3 sections

    # ========== Test Case 2: File not found error ==========
    def test_get_outline_file_not_found(self, mock_root_dir):
        """
        Test Case 2: File not found error.

        Given: A non-existent document path
        When: get_outline is called
        Then: Return ToolError with appropriate message

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-005-GetOutlineTool
        """
        # Unpack fixture
        _, get_outline = mock_root_dir

        # Attempt to get outline of non-existent document
        with pytest.raises((FileNotFoundError, ToolError)) as exc_info:
            get_outline(
                project_id="test-project",
                feature_id="non-existent-feature",
                doc_type="REQ"
            )

        # Verify error message contains useful information
        error_msg = str(exc_info.value)
        assert "not found" in error_msg.lower() or "does not exist" in error_msg.lower()

    # ========== Test Case 3: Token consumption verification ==========
    def test_get_outline_token_consumption(self, setup_test_document, mock_root_dir):
        """
        Test Case 3: Token consumption < 20% of full document.

        Given: A complete RBT document
        When: get_outline is called
        Then: Token consumption should be < 20% of full document

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-005-GetOutlineTool
        """
        # Unpack fixture
        _, get_outline = mock_root_dir

        # Get outline
        outline = get_outline(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Convert to JSON strings for size comparison
        outline_json = json.dumps(outline, ensure_ascii=False)
        full_content = setup_test_document["full_content"]

        # Calculate sizes (using character count as proxy for tokens)
        outline_size = len(outline_json)
        full_size = len(full_content)

        # Verify outline is significantly smaller
        reduction_ratio = outline_size / full_size

        # Token consumption should be < 20% (0.2)
        assert reduction_ratio < 0.2, (
            f"Outline size ({outline_size} chars) is {reduction_ratio*100:.1f}% of "
            f"full document ({full_size} chars), exceeds 20% threshold!"
        )

        # Print stats for visibility
        print(f"\n=== Token Consumption Stats ===")
        print(f"Full document size: {full_size} chars")
        print(f"Outline size: {outline_size} chars")
        print(f"Reduction: {(1-reduction_ratio)*100:.1f}%")
        print(f"Ratio: {reduction_ratio*100:.1f}% (target: <20%)")

    # ========== Test Case 4: General document support ==========
    def test_get_outline_general_document(self, mock_root_dir):
        """
        Test Case 4: get_outline works with general documents (not just RBT).

        Given: A general markdown document in docs/
        When: get_outline is called with file_path parameter
        Then: Return outline without blocks

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-005-GetOutlineTool
        """
        # Unpack fixture
        temp_root, get_outline = mock_root_dir

        # Create general document
        project_dir = Path(temp_root) / "test-project"
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        general_doc = """---
id: DOC-general
type: Document
---

<!-- info-section -->
> author: Test Author

<!-- id: sec-root -->
# General Document

<!-- id: sec-intro -->
## Introduction

<!-- id: blk-intro-para, type: paragraph -->
This is a general document.

<!-- id: blk-intro-list, type: list -->
**Features**
  - Feature A
  - Feature B
"""
        doc_file = docs_dir / "general.md"
        doc_file.write_text(general_doc)

        # Get outline using file_path parameter
        result = get_outline(
            project_id="test-project",
            file_path="general.md"
        )

        # Verify result
        assert result is not None
        assert "metadata" in result
        assert "sections" in result

        # Verify no blocks
        def check_no_blocks(sections):
            for section in sections:
                assert "blocks" not in section
                if "sections" in section:
                    check_no_blocks(section["sections"])

        check_no_blocks(result["sections"])

    # ========== Test Case 5: Outline preserves section hierarchy ==========
    def test_get_outline_preserves_hierarchy(self, setup_test_document, mock_root_dir):
        """
        Test Case 5: Verify section hierarchy is preserved correctly.

        Given: A document with nested sections
        When: get_outline is called
        Then: Section hierarchy structure should be intact

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-005-GetOutlineTool
        """
        # Unpack fixture
        _, get_outline = mock_root_dir

        result = get_outline(
            project_id=setup_test_document["project_id"],
            feature_id=setup_test_document["feature_id"],
            doc_type=setup_test_document["doc_type"]
        )

        # Navigate hierarchy to verify structure
        # Find sec-scope in the flat list of sections
        scope_section = None
        for section in result["sections"]:
            if section["id"] == "sec-scope":
                scope_section = section
                break

        assert scope_section is not None, "sec-scope not found"

        # Verify subsection exists
        assert "sections" in scope_section, "sec-scope should have subsections"
        subsections = scope_section["sections"]
        assert len(subsections) > 0, "sec-scope should have at least one subsection"

        # Verify nested hierarchy
        subsection = subsections[0]
        assert subsection["id"] == "sec-subsection"

        # Verify nested subsection
        assert "sections" in subsection
        nested = subsection["sections"]
        assert len(nested) > 0
        assert nested[0]["id"] == "sec-nested"
