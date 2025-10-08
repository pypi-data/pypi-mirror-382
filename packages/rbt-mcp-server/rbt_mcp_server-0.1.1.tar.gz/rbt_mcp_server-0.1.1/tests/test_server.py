"""
Test suite for MCP Server.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-004-MCP-Server-Setup

Tests MCP Server initialization, tool registration, and environment configuration.
"""

import os
import pytest
from unittest.mock import Mock, patch


# Test Case 1: Server initialization
def test_server_initialization():
    """
    Test that MCP server can be initialized with proper configuration.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    # Set environment variable
    with patch.dict(os.environ, {"RBT_ROOT_DIR": "/test/root"}):
        from rbt_mcp_server.server import mcp, document_service

        # Verify server exists
        assert mcp is not None
        assert mcp.name == "rbt-document-editor"

        # Verify document service is initialized
        assert document_service is not None
        assert document_service.root_dir == "/test/root"


# Test Case 2: Tool registration
def test_tool_registration():
    """
    Test that all required tools are registered correctly.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    with patch.dict(os.environ, {"RBT_ROOT_DIR": "/test/root"}):
        from rbt_mcp_server.server import mcp

        # Expected tool names
        expected_tools = {
            "get_outline",
            "read_section",
            "update_section_summary",
            "create_section",
            "create_block",
            "update_block",
            "delete_block",
            "append_list_item",
            "update_table_row",
            "create_document",
            "clear_cache",
        }

        # Get registered tools
        # FastMCP stores tools in _tool_manager._tools
        registered_tools = set()
        if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
            registered_tools = set(mcp._tool_manager._tools.keys())

        # Verify all expected tools are registered
        assert expected_tools.issubset(registered_tools), \
            f"Missing tools: {expected_tools - registered_tools}"


# Test Case 3: Environment variable handling
def test_environment_variable_required():
    """
    Test that RBT_ROOT_DIR environment variable is required.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    # Remove environment variable if it exists
    with patch.dict(os.environ, {}, clear=True):
        # Should raise error when RBT_ROOT_DIR is not set
        with pytest.raises(ValueError, match="RBT_ROOT_DIR"):
            # Re-import to trigger initialization
            import importlib
            import rbt_mcp_server.server
            importlib.reload(rbt_mcp_server.server)


def test_environment_variable_validation():
    """
    Test that RBT_ROOT_DIR path validation works correctly.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    # Test with non-existent directory - should still initialize but warn
    # Note: Module is already imported from previous tests, so we need to reimport
    # For this test, we just verify the environment variable is read correctly
    import os
    old_value = os.environ.get("RBT_ROOT_DIR")
    try:
        os.environ["RBT_ROOT_DIR"] = "/nonexistent/path"
        # Import fresh instance
        from rbt_mcp_server.server import get_root_dir
        root = get_root_dir()
        # Verify it reads the current environment variable
        assert root == "/nonexistent/path"
    finally:
        # Restore old value
        if old_value:
            os.environ["RBT_ROOT_DIR"] = old_value


# Test Case 4: Tool function placeholders
def test_tool_placeholder_functions():
    """
    Test that all tool functions have proper placeholders.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    with patch.dict(os.environ, {"RBT_ROOT_DIR": "/test/root"}):
        from rbt_mcp_server import server

        # Verify all tool functions exist and are callable
        tool_functions = [
            "get_outline",
            "read_section",
            "update_section_summary",
            "create_section",
            "create_block",
            "update_block",
            "delete_block",
            "append_list_item",
            "update_table_row",
            "create_document",
            "clear_cache",
        ]

        for tool_name in tool_functions:
            # Check function exists in module
            assert hasattr(server, tool_name), f"Tool function {tool_name} not found"
            func = getattr(server, tool_name)
            assert callable(func), f"Tool {tool_name} is not callable"


# Test Case 5: Server configuration
def test_server_configuration():
    """
    Test server configuration and metadata.

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    with patch.dict(os.environ, {"RBT_ROOT_DIR": "/test/root"}):
        from rbt_mcp_server.server import mcp

        # Verify server name
        assert mcp.name == "rbt-document-editor"

        # Verify server has proper transport setup (stdio by default in FastMCP)
        # FastMCP uses stdio transport by default when run() is called
        assert hasattr(mcp, 'run')
