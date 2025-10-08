"""
Test cases for PathResolver - TDD approach.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-001-PathResolver
"""

import os
import tempfile
import pytest
from pathlib import Path

from rbt_mcp_server.path_resolver import PathResolver
from rbt_mcp_server.models import PathInfo


class TestPathResolver:
    """Test suite for PathResolver following TDD approach."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary root directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def resolver(self, temp_root):
        """Create a PathResolver instance with temp root."""
        return PathResolver(temp_root)

    @pytest.fixture
    def setup_test_files(self, temp_root):
        """Setup test file structure."""
        # Create directory structure
        project_dir = Path(temp_root) / "knowledge-smith"
        feature_dir = project_dir / "features" / "rbt-mcp-tool"
        tasks_dir = feature_dir / "tasks"
        docs_dir = project_dir / "docs" / "governance"

        feature_dir.mkdir(parents=True, exist_ok=True)
        tasks_dir.mkdir(parents=True, exist_ok=True)
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create test files
        (feature_dir / "REQ-rbt-mcp-tool.md").write_text("# REQ")
        (feature_dir / "BP-rbt-mcp-tool.md").write_text("# BP")
        (tasks_dir / "TASK-001-PathResolver.md").write_text("# TASK-001")
        (tasks_dir / "TASK-002-DocumentService.md").write_text("# TASK-002")
        (docs_dir / "rules.md").write_text("# Rules")

        return temp_root

    def test_resolve_rbt_req_file_path(self, resolver, setup_test_files):
        """
        Test Case 1: 解析 RBT REQ 文件路徑
        Given: root="/tmp/docs", project_id="knowledge-smith", feature_id="rbt-mcp-tool", doc_type="REQ"
        When: 呼叫 resolver.resolve(project_id, feature_id, doc_type)
        Then: 回傳 PathInfo，file_path 指向 REQ-rbt-mcp-tool.md, is_rbt=True
        """
        result = resolver.resolve(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="REQ"
        )

        assert isinstance(result, PathInfo)
        assert result.project_id == "knowledge-smith"
        assert result.feature_id == "rbt-mcp-tool"
        assert result.doc_type == "REQ"
        assert result.file_path.endswith("knowledge-smith/features/rbt-mcp-tool/REQ-rbt-mcp-tool.md")
        assert result.is_rbt is True
        assert result.is_new_file is False
        assert os.path.exists(result.file_path)

    def test_resolve_rbt_bp_file_path(self, resolver, setup_test_files):
        """
        Test Case: 解析 RBT BP 文件路徑
        """
        result = resolver.resolve(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP"
        )

        assert isinstance(result, PathInfo)
        assert result.doc_type == "BP"
        assert result.file_path.endswith("knowledge-smith/features/rbt-mcp-tool/BP-rbt-mcp-tool.md")
        assert result.is_rbt is True
        assert os.path.exists(result.file_path)

    def test_resolve_task_file_with_full_name(self, resolver, setup_test_files):
        """
        Test Case 2: 解析 TASK 文件路徑（完整 feature_id）
        Given: root="/tmp/docs", project_id="knowledge-smith", feature_id="rbt-mcp-tool",
               doc_type="TASK", task_name="001-PathResolver"
        When: 呼叫 resolver.resolve(project_id, feature_id, doc_type, file_path="001-PathResolver")
        Then: 回傳 PathInfo，file_path 指向 TASK-001-PathResolver.md, is_rbt=True
        """
        result = resolver.resolve(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="TASK",
            file_path="001-PathResolver"
        )

        assert isinstance(result, PathInfo)
        assert result.doc_type == "TASK"
        assert result.file_path.endswith("tasks/TASK-001-PathResolver.md")
        assert result.is_rbt is True
        assert os.path.exists(result.file_path)

    def test_resolve_general_file_path(self, resolver, setup_test_files):
        """
        Test Case 3: 解析一般文件路徑
        Given: root="/tmp/docs", project_id="knowledge-smith", file_path="governance/rules.md"
        When: 呼叫 resolver.resolve(project_id, file_path=file_path)
        Then: 回傳 PathInfo，file_path 指向 docs/governance/rules.md, is_rbt=False
        """
        result = resolver.resolve(
            project_id="knowledge-smith",
            file_path="governance/rules.md"
        )

        assert isinstance(result, PathInfo)
        assert result.project_id == "knowledge-smith"
        assert result.feature_id is None
        assert result.doc_type is None
        assert result.file_path.endswith("knowledge-smith/docs/governance/rules.md")
        assert result.is_rbt is False
        assert result.is_new_file is False
        assert os.path.exists(result.file_path)

    def test_resolve_with_new_md_priority(self, resolver, setup_test_files):
        """
        Test Case 4: 優先讀取 .new.md
        Given: 存在 REQ-rbt-mcp-tool.md 和 REQ-rbt-mcp-tool.new.md
        When: 呼叫 resolver.resolve(...) 解析 REQ
        Then: 回傳 PathInfo，file_path 指向 .new.md，is_new_file=True
        """
        temp_root = setup_test_files
        feature_dir = Path(temp_root) / "knowledge-smith" / "features" / "rbt-mcp-tool"

        # Create .new.md file
        new_file = feature_dir / "REQ-rbt-mcp-tool.new.md"
        new_file.write_text("# REQ NEW")

        result = resolver.resolve(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="REQ"
        )

        assert result.file_path.endswith(".new.md")
        assert result.is_new_file is True
        assert os.path.exists(result.file_path)

    def test_resolve_task_partial_match_success(self, resolver, setup_test_files):
        """
        Test Case 5: TASK 部分比對成功
        Given: 存在 features/rbt-mcp-tool/tasks/TASK-001-PathResolver.md
        When: 呼叫 resolver.resolve(project_id="knowledge-smith", feature_id="001", doc_type="TASK")
        Then: 回傳 PathInfo，file_path 指向完整檔名
        """
        result = resolver.resolve(
            project_id="knowledge-smith",
            feature_id="001",
            doc_type="TASK"
        )

        assert isinstance(result, PathInfo)
        assert result.file_path.endswith("TASK-001-PathResolver.md")
        assert result.is_rbt is True
        assert os.path.exists(result.file_path)

    def test_resolve_task_partial_match_with_task_prefix(self, resolver, setup_test_files):
        """
        Test Case: TASK 部分比對（帶 TASK- 前綴）
        Given: feature_id="TASK-001"
        Then: 能正確比對到 TASK-001-PathResolver.md
        """
        result = resolver.resolve(
            project_id="knowledge-smith",
            feature_id="TASK-001",
            doc_type="TASK"
        )

        assert result.file_path.endswith("TASK-001-PathResolver.md")
        assert os.path.exists(result.file_path)

    def test_resolve_task_ambiguous_error(self, resolver, temp_root):
        """
        Test Case 6: TASK 部分比對歧義錯誤
        Given: 存在多個 TASK-001-*.md 在不同 feature 下
        When: 呼叫 resolver.resolve(project_id="test", feature_id="001", doc_type="TASK")
        Then: raise ValueError("Ambiguous TASK ID: found 2 matches")
        """
        # Create multiple matching files in different features
        project_dir = Path(temp_root) / "test"

        feature1_tasks = project_dir / "features" / "feature1" / "tasks"
        feature1_tasks.mkdir(parents=True, exist_ok=True)
        (feature1_tasks / "TASK-001-Something.md").write_text("# Task 1")

        feature2_tasks = project_dir / "features" / "feature2" / "tasks"
        feature2_tasks.mkdir(parents=True, exist_ok=True)
        (feature2_tasks / "TASK-001-Another.md").write_text("# Task 2")

        with pytest.raises(ValueError, match="Ambiguous TASK ID.*found 2 matches"):
            resolver.resolve(
                project_id="test",
                feature_id="001",
                doc_type="TASK"
            )

    def test_resolve_file_not_found_error(self, resolver, setup_test_files):
        """
        Test Case 7: 檔案不存在錯誤
        Given: 不存在任何 REQ-nonexistent.md
        When: 呼叫 resolver.resolve(...)
        Then: raise FileNotFoundError
        """
        with pytest.raises(FileNotFoundError):
            resolver.resolve(
                project_id="knowledge-smith",
                feature_id="nonexistent",
                doc_type="REQ"
            )

    def test_resolve_task_not_found(self, resolver, setup_test_files):
        """
        Test Case: TASK 部分比對找不到檔案
        """
        with pytest.raises(FileNotFoundError):
            resolver.resolve(
                project_id="knowledge-smith",
                feature_id="999",
                doc_type="TASK"
            )

    def test_resolve_general_file_not_found(self, resolver, setup_test_files):
        """
        Test Case: 一般檔案不存在
        """
        with pytest.raises(FileNotFoundError):
            resolver.resolve(
                project_id="knowledge-smith",
                file_path="nonexistent/file.md"
            )

    def test_resolve_new_md_for_general_file(self, resolver, setup_test_files):
        """
        Test Case: 一般文件也支援 .new.md 優先讀取
        """
        temp_root = setup_test_files
        docs_dir = Path(temp_root) / "knowledge-smith" / "docs" / "governance"

        # Create .new.md for general file
        new_file = docs_dir / "rules.new.md"
        new_file.write_text("# Rules NEW")

        result = resolver.resolve(
            project_id="knowledge-smith",
            file_path="governance/rules.md"
        )

        assert result.file_path.endswith("rules.new.md")
        assert result.is_new_file is True
        assert result.is_rbt is False

    def test_resolve_invalid_parameters(self, resolver):
        """
        Test Case: 參數驗證 - 必須提供 doc_type 或 file_path
        """
        with pytest.raises(ValueError, match="Either doc_type or file_path must be provided"):
            resolver.resolve(project_id="knowledge-smith")

    def test_resolve_task_without_feature_id(self, resolver):
        """
        Test Case: TASK 類型必須提供 feature_id（用於部分比對）或完整 file_path
        """
        with pytest.raises(ValueError, match="feature_id is required"):
            resolver.resolve(
                project_id="knowledge-smith",
                doc_type="TASK"
            )
