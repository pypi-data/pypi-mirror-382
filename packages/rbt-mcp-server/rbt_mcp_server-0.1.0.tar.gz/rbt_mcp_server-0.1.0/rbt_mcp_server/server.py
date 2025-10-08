"""
MCP Server for RBT Document Editing.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-004-MCP-Server-Setup

Provides MCP tool functions for partial document editing operations.
Registers 11 tool functions for structured document manipulation.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP

from .document_service import DocumentService
from .errors import ToolError


# Step 3: Read environment variable (RBT_ROOT_DIR)
def get_root_dir() -> str:
    """
    Get root directory from environment variable.

    Returns:
        Root directory path

    Raises:
        ValueError: If RBT_ROOT_DIR is not set

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup
    """
    root_dir = os.environ.get("RBT_ROOT_DIR")
    if not root_dir:
        raise ValueError(
            "RBT_ROOT_DIR environment variable is required. "
            "Please set it to the root directory of your RBT documents."
        )
    return root_dir


# Initialize MCP server
mcp = FastMCP("rbt-document-editor")

# Initialize DocumentService with root_dir from environment
root_dir = get_root_dir()
document_service = DocumentService(root_dir)


# ========== Tool Functions ==========

@mcp.tool()
def get_outline(
    project_id: str,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get document outline (structure without blocks).

    **BEST PRACTICE: Always use this FIRST before editing documents!**
    - See what sections exist
    - Find section/block IDs for editing
    - Saves tokens by not loading full content

    Returns lightweight document structure with metadata, info, and section tree.
    Significantly reduces token consumption compared to reading full document.

    Args:
        project_id: Project identifier
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)
                   **For TASK documents: supports fuzzy matching! Just provide the index number.**

    Returns:
        Document outline JSON with metadata, info, title, and sections

    Example:
        # RBT document
        get_outline(project_id="knowledge-smith", feature_id="rbt-mcp-tool", doc_type="BP")

        # TASK document (FUZZY SEARCH - just use the index!)
        get_outline(project_id="knowledge-smith", feature_id="rbt-mcp-tool",
                   doc_type="TASK", file_path="001")  # Matches TASK-001-*.md

        # General document
        get_outline(project_id="knowledge-smith", file_path="architecture/overview.md")

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-005-GetOutlineTool-Server-Setup
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Get outline
        outline = document_service.get_outline(path_info)
        return outline

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("GET_OUTLINE_ERROR", f"Failed to get outline: {str(e)}")


@mcp.tool()
def read_content(
    project_id: str,
    content_id: str,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Read section or block by ID.

    **KEY FEATURE: Read ONLY what you need!**
    - Read a single block (blk-*) → saves tokens, don't read the whole section
    - Read a section (sec-*) → gets section + all its blocks

    **TIP: Use get_outline() first to find available IDs**

    Automatically determines content type based on ID prefix:
    - sec-* → reads section with blocks and nested sections
    - blk-* → reads single block data

    Args:
        project_id: Project identifier
        content_id: Content ID (section or block ID starting with 'sec-' or 'blk-')
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Content data (section or block)

    Example:
        # Read section
        read_content(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP",
            content_id="sec-components"
        )

        # Read block
        read_content(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP",
            content_id="blk-component-table"
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-006-ReadSectionTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Read content
        content = document_service.read_content(path_info, content_id)
        return content

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("READ_CONTENT_ERROR", f"Failed to read content: {str(e)}")


@mcp.tool()
def update_section_summary(
    project_id: str,
    section_id: str,
    new_summary: str,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Update section summary text.

    Args:
        project_id: Project identifier
        section_id: Section ID to update
        new_summary: New summary text
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message

    Example:
        update_section_summary(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP",
            section_id="sec-components",
            new_summary="Updated component specifications with new requirements"
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-007-UpdateSectionSummaryTool-Server-Setup
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Update summary
        document_service.update_section_summary(path_info, section_id, new_summary)
        return f"Successfully updated summary for section '{section_id}'"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("UPDATE_SUMMARY_ERROR", f"Failed to update summary: {str(e)}")


@mcp.tool()
def create_section(
    project_id: str,
    parent_id: str,
    title: str,
    summary: Optional[str] = None,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Create new section under specified parent.

    Note: For RBT documents, cannot create root sections (only sub-sections).

    Args:
        project_id: Project identifier
        parent_id: Parent section ID
        title: Section title
        summary: Optional section summary
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        New section ID

    Example:
        create_section(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="REQ",
            parent_id="sec-use-cases",
            title="Additional Use Cases",
            summary="Extended scenarios for document editing"
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-008-CreateSectionTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Create section
        new_section_id = document_service.create_section(
            path_info=path_info,
            parent_id=parent_id,
            title=title,
            summary=summary
        )

        return new_section_id

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("CREATE_SECTION_ERROR", f"Failed to create section: {str(e)}")


@mcp.tool()
def create_block(
    project_id: str,
    section_id: str,
    block_type: str,
    content: Optional[str] = None,
    items: Optional[List[str]] = None,
    language: Optional[str] = None,
    header: Optional[List[str]] = None,
    rows: Optional[List[List[str]]] = None,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Create new block in specified section.

    **TIP: Block IDs are auto-generated, but you can identify blocks later by their content.
    Consider adding meaningful content/titles to make blocks easier to find with get_outline().**

    Args:
        project_id: Project identifier
        section_id: Section ID to add block to
        block_type: Block type - paragraph/code/list/table
        content: Content for paragraph/code blocks
        items: Items for list blocks
        language: Language for code blocks
        header: Header row for table blocks
        rows: Data rows for table blocks
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        New block ID

    Example:
        # Create paragraph
        create_block(
            project_id="knowledge-smith",
            file_path="docs/guide.md",
            section_id="sec-intro",
            block_type="paragraph",
            content="This is a new paragraph."
        )

        # Create list
        create_block(
            project_id="knowledge-smith",
            file_path="docs/guide.md",
            section_id="sec-features",
            block_type="list",
            items=["Feature 1", "Feature 2"]
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-009-CreateBlockTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Create block
        block_id = document_service.create_block(
            path_info=path_info,
            section_id=section_id,
            block_type=block_type,
            content=content,
            items=items,
            language=language,
            header=header,
            rows=rows
        )
        return block_id

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("CREATE_BLOCK_ERROR", f"Failed to create block: {str(e)}")


@mcp.tool()
def update_block(
    project_id: str,
    block_id: str,
    content: Optional[str] = None,
    title: Optional[str] = None,
    items: Optional[List[str]] = None,
    language: Optional[str] = None,
    header: Optional[List[str]] = None,
    rows: Optional[List[List[str]]] = None,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Update existing block content based on block type.

    Supports updating different block types:
    - paragraph: content
    - code: content, language (optional)
    - list: title (optional), items
    - table: header, rows

    Args:
        project_id: Project identifier
        block_id: Block ID to update
        content: New content for paragraph/code blocks
        title: New title for list blocks
        items: New items for list blocks
        language: Programming language for code blocks
        header: New header for table blocks
        rows: New rows for table blocks
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message dictionary

    Example:
        # Update paragraph block
        update_block(
            project_id="knowledge-smith",
            file_path="docs/guide.md",
            block_id="blk-paragraph-1",
            content="Updated paragraph content."
        )

        # Update list block
        update_block(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="REQ",
            block_id="blk-requirements",
            title="**Updated Requirements**",
            items=["Req 1", "Req 2", "Req 3"]
        )

        # Update code block
        update_block(
            project_id="knowledge-smith",
            file_path="docs/examples.md",
            block_id="blk-code-sample",
            content="def hello():\\n    print('Hello')",
            language="python"
        )

        # Update table block
        update_block(
            project_id="knowledge-smith",
            feature_id="test",
            doc_type="BP",
            block_id="blk-table-data",
            header=["Name", "Value"],
            rows=[["Item1", "100"], ["Item2", "200"]]
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-010-UpdateBlockTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Update block
        document_service.update_block(
            path_info=path_info,
            block_id=block_id,
            content=content,
            title=title,
            items=items,
            language=language,
            header=header,
            rows=rows
        )

        return {
            "message": f"Successfully updated block '{block_id}'"
        }

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("UPDATE_BLOCK_ERROR", f"Failed to update block: {str(e)}")


@mcp.tool()
def delete_block(
    project_id: str,
    block_id: str,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Delete block from document.

    Args:
        project_id: Project identifier
        block_id: Block ID to delete
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message

    Example:
        delete_block(
            project_id="knowledge-smith",
            file_path="docs/guide.md",
            block_id="blk-paragraph-2"
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-011-DeleteBlockTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Delete block
        document_service.delete_block(path_info, block_id)
        return f"Successfully deleted block '{block_id}'"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("DELETE_BLOCK_ERROR", f"Failed to delete block: {str(e)}")


@mcp.tool()
def append_list_item(
    project_id: str,
    block_id: str,
    item: str,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Append item to list block.

    Args:
        project_id: Project identifier
        block_id: List block ID
        item: Item text to append
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message

    Example:
        append_list_item(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="REQ",
            block_id="blk-func-req-list",
            item="New functional requirement item"
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-012-AppendListItemTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Append item to list
        document_service.append_list_item(path_info, block_id, item)
        return f"Successfully appended item to list block '{block_id}'"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("APPEND_LIST_ITEM_ERROR", f"Failed to append list item: {str(e)}")


@mcp.tool()
def update_table_row(
    project_id: str,
    block_id: str,
    row_index: int,
    row_data: List[str],
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Update specific table row.

    Args:
        project_id: Project identifier
        block_id: Table block ID
        row_index: Row index to update (0-based, excluding header)
        row_data: New row data (list of cell values)
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message

    Example:
        update_table_row(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP",
            block_id="blk-component-spec-table",
            row_index=0,
            row_data=["PathResolver", "Updated description", "new input", "new output"]
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-013-UpdateTableRowTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Update table row
        document_service.update_table_row(path_info, block_id, row_index, row_data)
        return f"Successfully updated row {row_index} in table block '{block_id}'"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("UPDATE_TABLE_ROW_ERROR", f"Failed to update table row: {str(e)}")


@mcp.tool()
def append_table_row(
    project_id: str,
    block_id: str,
    row_data: List[str],
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Append a new row to a table block.

    Args:
        project_id: Project identifier
        block_id: Table block ID
        row_data: Row data (list of cell values)
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message

    Example:
        append_table_row(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP",
            block_id="blk-component-spec-table",
            row_data=["new_tool", "New tool description", "inputs", "outputs", "TASK-XXX", "Acceptance criteria"]
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-017-AppendTableRowTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Append table row
        document_service.append_table_row(path_info, block_id, row_data)
        return f"Successfully appended row to table block '{block_id}'"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("APPEND_TABLE_ROW_ERROR", f"Failed to append table row: {str(e)}")


@mcp.tool()
def create_document(
    project_id: str,
    doc_type: str,
    replacements: dict,
    feature_id: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Create new document from template with placeholder replacement.

    Creates a new document by loading the appropriate template (Task/Blueprint/Requirement),
    auto-filling common placeholders, and saving as .new.md with complete structure.

    Auto-filled placeholders (from parameters):
    - [project-id]: From project_id parameter
    - [feature-id]: From feature_id parameter
    - [feature-name]: From feature_id parameter
    - [YYYY-MM-DD]: Current date (auto-generated)

    Custom placeholders (need to be in replacements):
    - [task-name]: Task name (for Task type)
    - [任務標題]/[需求標題]/[藍圖標題]: Document titles
    - Any other template-specific placeholders

    Args:
        project_id: Project identifier (auto-fills [project-id])
        doc_type: Document type - "Task", "Blueprint", "Requirement" for RBT documents,
                  or custom types like "General", "Architecture", "Guide", "API" for general documents.
                  doc_type serves as classification for better document organization and retrieval.
        replacements: Dictionary of custom placeholder -> value mappings
        feature_id: Feature identifier (auto-fills [feature-id] and [feature-name])
        file_path: File path within docs/ (for general documents)

    Returns:
        Success message with created file path

    Example (Task document):
        create_document(
            project_id="knowledge-smith",
            doc_type="Task",
            feature_id="rbt-mcp-tool",
            replacements={
                "task-name": "PathResolver",
                "任務標題": "實作 PathResolver 路徑解析與驗證"
            }
        )
        # project-id, feature-id, feature-name, date 會自動填入

    Example (Blueprint document):
        create_document(
            project_id="knowledge-smith",
            doc_type="Blueprint",
            feature_id="rbt-mcp-tool",
            replacements={
                "藍圖標題": "RBT 文件編輯 MCP Tool"
            }
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-014-CreateDocumentTool
    """
    try:
        # Validate path parameters for security
        if ".." in project_id or "/" in project_id or "\\" in project_id:
            raise ToolError("INVALID_PATH", "project_id contains invalid characters")
        if feature_id and (".." in feature_id or "/" in feature_id or "\\" in feature_id):
            raise ToolError("INVALID_PATH", "feature_id contains invalid characters")

        # Build PathInfo for new document (don't use resolve since file doesn't exist yet)
        from .models import PathInfo

        # Determine if this is an RBT document
        is_rbt = doc_type in ["Task", "Blueprint", "Requirement"]

        if is_rbt:
            # RBT document path
            if not feature_id:
                raise ToolError("MISSING_PARAMETER", "feature_id is required for RBT documents")

            if doc_type == "Task":
                # For Task, we need task-name from replacements
                task_name = replacements.get("task-name", "unknown")
                base_path = Path(document_service.root_dir) / project_id / "features" / feature_id / "tasks"
                filename = f"TASK-{task_name}.md"
            else:
                base_path = Path(document_service.root_dir) / project_id / "features" / feature_id
                filename = f"{doc_type.upper()}-{feature_id}.md"

            full_path = str(base_path / filename)
        else:
            # General document path
            if not file_path:
                raise ToolError("MISSING_PARAMETER", "file_path is required for general documents")

            base_path = Path(document_service.root_dir) / project_id / "docs"
            full_path = str(base_path / file_path)

        # Create PathInfo
        path_info = PathInfo(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=full_path,
            is_rbt=is_rbt,
            is_new_file=False  # Will become .new.md after creation
        )

        # Create document from template
        created_path = document_service.create_document(path_info, doc_type, replacements)
        return f"Document created successfully from template at: {created_path}"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("CREATE_DOCUMENT_ERROR", f"Failed to create document: {str(e)}")


@mcp.tool()
def update_info(
    project_id: str,
    status: Optional[str] = None,
    update_date: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    feature_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    Update info section fields (status, update_date, dependencies).

    Supports partial updates - only provided fields are updated, others remain unchanged.
    At least one field must be provided for update.

    Args:
        project_id: Project identifier
        status: Optional new status value
        update_date: Optional new update_date value (format: YYYY-MM-DD)
        dependencies: Optional new dependencies list
        feature_id: Feature identifier (for RBT documents)
        doc_type: Document type - REQ/BP/TASK (for RBT documents)
        file_path: File path relative to docs/ (for general documents)

    Returns:
        Success message

    Example:
        # Update status only
        update_info(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="TASK",
            file_path="017",
            status="Done"
        )

        # Update multiple fields
        update_info(
            project_id="knowledge-smith",
            feature_id="rbt-mcp-tool",
            doc_type="BP",
            status="In Progress",
            update_date="2025-10-08",
            dependencies=["TASK-001", "TASK-002"]
        )

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-016-UpdateInfoTool
    """
    try:
        # Resolve path
        path_info = document_service.path_resolver.resolve(
            project_id=project_id,
            feature_id=feature_id,
            doc_type=doc_type,
            file_path=file_path
        )

        # Update info
        document_service.update_info(path_info, status, update_date, dependencies)

        # Build success message
        updated_fields = []
        if status is not None:
            updated_fields.append("status")
        if update_date is not None:
            updated_fields.append("update_date")
        if dependencies is not None:
            updated_fields.append("dependencies")

        return f"Successfully updated info section fields: {', '.join(updated_fields)}"

    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError("UPDATE_INFO_ERROR", f"Failed to update info: {str(e)}")


@mcp.tool()
def clear_cache(
    file_path: Optional[str] = None
) -> str:
    """
    Clear document cache.

    Args:
        file_path: Optional file path to clear; if None, clears all cache

    Returns:
        Success message

    Example:
        # Clear specific file
        clear_cache(file_path="/path/to/document.md")

        # Clear all cache
        clear_cache()

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-015-ClearCacheTool-Server-Setup
    """
    
    try:
        document_service.clear_cache(file_path)
        if file_path:
            return f"Successfully cleared cache for {file_path}"
        else:
            return "Successfully cleared all document cache"
    except Exception as e:
        raise ToolError("CLEAR_CACHE_ERROR", f"Failed to clear cache: {str(e)}")


# ========== Main Entry Point ==========

def main():
    """
    Main entry point for MCP server.

    Runs server with stdio transport (default for FastMCP).

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-004-MCP-Server-Setup-Server-Setup
    """
    mcp.run()


if __name__ == "__main__":
    main()
