"""
DocumentService - Core CRUD logic for document operations.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-003-DocumentService

Provides document loading, saving, reading, and updating operations.
Integrates PathResolver, DocumentCache, and MarkdownConverter.
"""

import os
import copy
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

# Add converter module to path
converter_path = os.path.join(os.path.dirname(__file__), '..', 'converter')
if converter_path not in sys.path:
    sys.path.insert(0, converter_path)

from converter import MarkdownConverter
from .path_resolver import PathResolver
from .cache import DocumentCache
from .models import PathInfo
from .errors import ToolError


class DocumentService:
    """
    Core service for document CRUD operations.

    Features:
    - Load documents (with cache support)
    - Save documents (as .new.md)
    - Get outline (lightweight structure without blocks)
    - Read/update sections
    - Clear cache

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-003-DocumentService
    """

    def __init__(self, root_dir: str):
        """
        Initialize DocumentService.

        Args:
            root_dir: Root directory for all documents

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        self.root_dir = root_dir
        self.path_resolver = PathResolver(root_dir)
        self.cache = DocumentCache(max_size=10, ttl_seconds=300)
        self.converter = MarkdownConverter()

        # Start cache cleanup thread
        self.cache.start()

    def load_document(self, path_info: PathInfo) -> Dict[str, Any]:
        """
        Load document JSON from file or cache.

        Priority: Cache -> File system (.new.md first, then原檔案)
        Automatically caches loaded documents.

        Args:
            path_info: PathInfo with resolved file path

        Returns:
            Document JSON data (deep copy)

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If conversion fails

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        file_path = path_info.file_path

        # Check for .new.md version first (it takes priority)
        new_md_path = self._get_new_md_path(file_path)
        actual_file_path = new_md_path if os.path.exists(new_md_path) else file_path

        # Try to get from cache first (check both .new.md and original path)
        cached_data = self.cache.get(new_md_path)
        if cached_data is not None:
            # Return deep copy to prevent modification of cached data
            return copy.deepcopy(cached_data)

        cached_data = self.cache.get(file_path)
        if cached_data is not None:
            # Return deep copy to prevent modification of cached data
            return copy.deepcopy(cached_data)

        # Cache miss - load from file
        if not os.path.exists(actual_file_path):
            raise FileNotFoundError(f"Document not found: {actual_file_path}")

        # Read file content
        with open(actual_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert to JSON
        json_data = self.converter.to_json(md_content)

        # Store in cache (use the actual file path that was read)
        self.cache.put(actual_file_path, json_data)

        # Return deep copy
        return copy.deepcopy(json_data)

    def save_document(self, path_info: PathInfo, json_data: Dict[str, Any]) -> None:
        """
        Save document as .new.md file.

        Atomic operation: Write to .tmp first, then rename to .new.md
        Updates cache after successful save.

        Args:
            path_info: PathInfo with file path information
            json_data: Document JSON data to save

        Raises:
            Exception: If conversion or file write fails

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        # Convert JSON to Markdown
        md_content = self.converter.to_md(json_data)

        # Determine target path (.new.md)
        original_path = path_info.file_path
        if original_path.endswith(".new.md"):
            target_path = original_path
        elif original_path.endswith(".md"):
            target_path = original_path.replace(".md", ".new.md")
        else:
            target_path = original_path + ".new.md"

        # Write to temporary file first (atomic operation)
        tmp_path = target_path + ".tmp"
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            # Rename to final path (atomic on POSIX systems)
            os.rename(tmp_path, target_path)

        finally:
            # Clean up tmp file if it still exists
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        # Update cache
        self.cache.put(target_path, json_data)

    def update_info(
        self,
        path_info: PathInfo,
        status: Optional[str] = None,
        update_date: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """
        Update info section fields (status, update_date, dependencies).

        Supports partial updates - only provided fields are updated, others remain unchanged.
        At least one field must be provided for update.

        Args:
            path_info: PathInfo with file path
            status: Optional new status value
            update_date: Optional new update_date value
            dependencies: Optional new dependencies list

        Raises:
            ToolError: If no fields provided, or document doesn't have info section

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-016-UpdateInfoTool
        """
        # Validate at least one field is provided
        if status is None and update_date is None and dependencies is None:
            raise ToolError(
                "NO_FIELDS_PROVIDED",
                "At least one field (status, update_date, dependencies) must be provided"
            )

        # Load document
        json_data = self.load_document(path_info)

        # Check if info section exists (must exist and not be empty)
        if "info" not in json_data or not json_data["info"]:
            raise ToolError(
                "INFO_SECTION_NOT_FOUND",
                "Document does not have info section"
            )

        # Update provided fields
        if status is not None:
            json_data["info"]["status"] = status

        if update_date is not None:
            json_data["info"]["update_date"] = update_date

        if dependencies is not None:
            json_data["info"]["dependencies"] = dependencies

        # Save document
        self.save_document(path_info, json_data)

    def _get_new_md_path(self, file_path: str) -> str:
        """
        Get the .new.md version of a file path.

        Args:
            file_path: Original file path

        Returns:
            Path with .new.md extension

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        if file_path.endswith(".new.md"):
            return file_path
        elif file_path.endswith(".md"):
            return file_path.replace(".md", ".new.md")
        else:
            return file_path + ".new.md"

    def get_outline(self, path_info: PathInfo) -> Dict[str, Any]:
        """
        Get document outline (structure without blocks).

        Returns lightweight JSON with:
        - metadata
        - info
        - title
        - sections tree (without blocks)

        Args:
            path_info: PathInfo with file path

        Returns:
            Outline JSON (deep copy)

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        # Load full document
        json_data = self.load_document(path_info)

        # Deep copy to avoid modifying cache
        outline = copy.deepcopy(json_data)

        # Remove all blocks recursively
        def remove_blocks(sections):
            """Recursively remove blocks from sections."""
            for section in sections:
                if "blocks" in section:
                    del section["blocks"]
                if "sections" in section:
                    remove_blocks(section["sections"])

        if "sections" in outline:
            remove_blocks(outline["sections"])

        return outline

    def read_section(self, path_info: PathInfo, section_id: str) -> Dict[str, Any]:
        """
        Read specific section by ID.

        Args:
            path_info: PathInfo with file path
            section_id: Section ID to read

        Returns:
            Section data with blocks (deep copy)

        Raises:
            ToolError: If section not found

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        # Load document
        json_data = self.load_document(path_info)

        # Search for section
        def find_section(sections, target_id):
            """Recursively search for section by ID."""
            for section in sections:
                if section.get("id") == target_id:
                    return section
                if "sections" in section:
                    result = find_section(section["sections"], target_id)
                    if result:
                        return result
            return None

        section = None
        if "sections" in json_data:
            section = find_section(json_data["sections"], section_id)

        if section is None:
            raise ToolError(
                "SECTION_NOT_FOUND",
                f"Section '{section_id}' not found in document"
            )

        # Return deep copy
        return copy.deepcopy(section)

    def read_content(self, path_info: PathInfo, content_id: str) -> Dict[str, Any]:
        """
        Read section or block by ID.

        Automatically determines type based on ID prefix:
        - sec-* → reads section with blocks
        - blk-* → reads single block

        Args:
            path_info: PathInfo with file path
            content_id: Content ID (section or block ID)

        Returns:
            Content data (section or block, deep copy)

        Raises:
            ToolError: If content_id format invalid or content not found

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-006-ReadSectionTool
        """
        # Validate content_id format
        if not content_id.startswith("sec-") and not content_id.startswith("blk-"):
            raise ToolError(
                "INVALID_CONTENT_ID",
                f"Content ID must start with 'sec-' or 'blk-', got '{content_id}'"
            )

        # Load document
        json_data = self.load_document(path_info)

        # If section ID, use existing read_section logic
        if content_id.startswith("sec-"):
            def find_section(sections, target_id):
                """Recursively search for section by ID."""
                for section in sections:
                    if section.get("id") == target_id:
                        return section
                    if "sections" in section:
                        result = find_section(section["sections"], target_id)
                        if result:
                            return result
                return None

            section = None
            if "sections" in json_data:
                section = find_section(json_data["sections"], content_id)

            if section is None:
                raise ToolError(
                    "CONTENT_NOT_FOUND",
                    f"Section '{content_id}' not found in document"
                )

            return copy.deepcopy(section)

        # If block ID, search all sections for the block
        else:  # content_id.startswith("blk-")
            def find_block(sections, target_id):
                """Recursively search for block by ID in all sections."""
                for section in sections:
                    # Search blocks in current section
                    if "blocks" in section:
                        for block in section["blocks"]:
                            if block.get("id") == target_id:
                                return block
                    # Search nested sections
                    if "sections" in section:
                        result = find_block(section["sections"], target_id)
                        if result:
                            return result
                return None

            block = None
            if "sections" in json_data:
                block = find_block(json_data["sections"], content_id)

            if block is None:
                raise ToolError(
                    "CONTENT_NOT_FOUND",
                    f"Block '{content_id}' not found in document"
                )

            return copy.deepcopy(block)

    def update_section_summary(
        self,
        path_info: PathInfo,
        section_id: str,
        new_summary: str
    ) -> None:
        """
        Update section summary.

        Modifies the section's summary field and saves as .new.md

        Args:
            path_info: PathInfo with file path
            section_id: Section ID to update
            new_summary: New summary text

        Raises:
            ToolError: If section not found

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        # Load document
        json_data = self.load_document(path_info)

        # Search and update section
        def update_section(sections, target_id, summary):
            """Recursively search and update section summary."""
            for section in sections:
                if section.get("id") == target_id:
                    section["summary"] = summary
                    return True
                if "sections" in section:
                    if update_section(section["sections"], target_id, summary):
                        return True
            return False

        updated = False
        if "sections" in json_data:
            updated = update_section(json_data["sections"], section_id, new_summary)

        if not updated:
            raise ToolError(
                "SECTION_NOT_FOUND",
                f"Section '{section_id}' not found in document"
            )

        # Save document
        self.save_document(path_info, json_data)

    def create_section(
        self,
        path_info: PathInfo,
        parent_id: Optional[str],
        title: str,
        summary: Optional[str] = None
    ) -> str:
        """
        Create new section under specified parent.

        Generates a unique section ID and adds the new section to the parent's
        sections array. If parent_id is None, creates a top-level section.

        Args:
            path_info: PathInfo with file path
            parent_id: Parent section ID to add new section under (None for top-level)
            title: Section title
            summary: Optional section summary (defaults to empty string)

        Returns:
            New section ID

        Raises:
            ToolError: If parent section not found

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        # Load document
        json_data = self.load_document(path_info)

        # Generate unique section ID
        section_id = self._generate_section_id(json_data, title)

        # Create new section structure
        new_section = {
            "id": section_id,
            "title": title,
            "summary": summary if summary is not None else "",
            "blocks": [],
            "sections": []
        }

        # If parent_id is None, add to top-level sections
        if parent_id is None or parent_id == "":
            # For RBT documents, cannot create root sections
            if path_info.is_rbt:
                raise ToolError(
                    "INVALID_OPERATION",
                    "Cannot create root sections in RBT documents. Use parent_id to specify a parent section."
                )
            if "sections" not in json_data:
                json_data["sections"] = []
            json_data["sections"].append(new_section)
        else:
            # Find parent section and add new section
            def find_and_add_section(sections, target_id, new_sec):
                """Recursively search for parent and add new section."""
                for section in sections:
                    if section.get("id") == target_id:
                        # Found parent - add new section
                        if "sections" not in section:
                            section["sections"] = []
                        section["sections"].append(new_sec)
                        return True
                    if "sections" in section:
                        if find_and_add_section(section["sections"], target_id, new_sec):
                            return True
                return False

            added = False
            if "sections" in json_data:
                added = find_and_add_section(json_data["sections"], parent_id, new_section)

            if not added:
                raise ToolError(
                    "SECTION_NOT_FOUND",
                    f"Parent section '{parent_id}' not found in document"
                )

        # Save document
        self.save_document(path_info, json_data)

        return section_id

    def _generate_section_id(self, json_data: Dict[str, Any], title: str) -> str:
        """
        Generate unique section ID based on title.

        Uses format: sec-{slug} where slug is derived from title.
        If ID already exists, appends a number suffix.

        Args:
            json_data: Document JSON data
            title: Section title

        Returns:
            Unique section ID

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-008-CreateSectionTool
        """
        import re

        # Create slug from title
        # Convert to lowercase, replace spaces and special chars with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        # Limit slug length
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')

        # Collect all existing section IDs
        existing_ids = set()

        def collect_ids(sections):
            """Recursively collect all section IDs."""
            for section in sections:
                if "id" in section:
                    existing_ids.add(section["id"])
                if "sections" in section:
                    collect_ids(section["sections"])

        if "sections" in json_data:
            collect_ids(json_data["sections"])

        # Generate unique ID
        base_id = f"sec-{slug}"
        section_id = base_id

        # If ID exists, append number suffix
        counter = 1
        while section_id in existing_ids:
            section_id = f"{base_id}-{counter}"
            counter += 1

        return section_id

    def create_block(
        self,
        path_info: PathInfo,
        section_id: str,
        block_type: str,
        content: Optional[str] = None,
        items: Optional[list] = None,
        language: Optional[str] = None,
        header: Optional[list] = None,
        rows: Optional[list] = None
    ) -> str:
        """
        Create new block in specified section.

        Generates unique block ID and validates block data based on type.
        Saves document as .new.md after creation.

        Args:
            path_info: PathInfo with file path
            section_id: Section ID to add block to
            block_type: Block type (paragraph/code/list/table)
            content: Content for paragraph/code blocks
            items: Items for list blocks
            language: Language for code blocks (default: empty string)
            header: Header row for table blocks
            rows: Data rows for table blocks

        Returns:
            New block ID (e.g., "blk-paragraph-1")

        Raises:
            ToolError: If section not found, invalid block type, or missing required fields

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-009-CreateBlockTool
        """
        # Validate block type
        valid_types = ["paragraph", "code", "list", "table"]
        if block_type not in valid_types:
            raise ToolError(
                "INVALID_BLOCK_TYPE",
                f"Invalid block type '{block_type}'. Must be one of: {', '.join(valid_types)}"
            )

        # Load document
        json_data = self.load_document(path_info)

        # Find target section
        def find_section(sections, target_id):
            """Recursively search for section by ID."""
            for section in sections:
                if section.get("id") == target_id:
                    return section
                if "sections" in section:
                    result = find_section(section["sections"], target_id)
                    if result:
                        return result
            return None

        target_section = None
        if "sections" in json_data:
            target_section = find_section(json_data["sections"], section_id)

        if target_section is None:
            raise ToolError(
                "SECTION_NOT_FOUND",
                f"Section '{section_id}' not found in document"
            )

        # Generate unique block ID
        block_id = self._generate_block_id(json_data, block_type)

        # Create block based on type
        new_block = {"id": block_id, "type": block_type}

        if block_type == "paragraph":
            if content is None:
                raise ToolError(
                    "INVALID_BLOCK_DATA",
                    "Paragraph block requires 'content' field"
                )
            new_block["content"] = content

        elif block_type == "code":
            if content is None:
                raise ToolError(
                    "INVALID_BLOCK_DATA",
                    "Code block requires 'content' field"
                )
            new_block["language"] = language or ""
            new_block["content"] = content

        elif block_type == "list":
            if items is None:
                raise ToolError(
                    "INVALID_BLOCK_DATA",
                    "List block requires 'items' field"
                )
            new_block["items"] = items

        elif block_type == "table":
            if header is None or rows is None:
                raise ToolError(
                    "INVALID_BLOCK_DATA",
                    "Table block requires both 'header' and 'rows' fields"
                )
            new_block["header"] = header
            new_block["rows"] = rows

        # Add block to section
        if "blocks" not in target_section:
            target_section["blocks"] = []
        target_section["blocks"].append(new_block)

        # Save document
        self.save_document(path_info, json_data)

        return block_id

    def _generate_block_id(self, json_data: Dict[str, Any], block_type: str) -> str:
        """
        Generate unique block ID.

        Uses format: blk-{type}-{sequence_number}
        Ensures no collision with existing IDs.

        Args:
            json_data: Document JSON data
            block_type: Block type (paragraph/code/list/table)

        Returns:
            Unique block ID

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-009-CreateBlockTool
        """
        # Collect all existing block IDs
        existing_ids = set()

        def collect_block_ids(sections):
            """Recursively collect all block IDs."""
            for section in sections:
                if "blocks" in section:
                    for block in section["blocks"]:
                        if "id" in block:
                            existing_ids.add(block["id"])
                if "sections" in section:
                    collect_block_ids(section["sections"])

        if "sections" in json_data:
            collect_block_ids(json_data["sections"])

        # Generate ID with sequence number
        seq = 1
        while True:
            block_id = f"blk-{block_type}-{seq}"
            if block_id not in existing_ids:
                return block_id
            seq += 1

    def update_block(
        self,
        path_info: PathInfo,
        block_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        items: Optional[list] = None,
        language: Optional[str] = None,
        header: Optional[list] = None,
        rows: Optional[list] = None
    ) -> None:
        """
        Update block content based on block type.

        Supports updating different block types with appropriate parameters:
        - paragraph: content
        - code: content, language (optional)
        - list: title (optional), items
        - table: header, rows

        Args:
            path_info: PathInfo with file path
            block_id: Block ID to update
            content: New content (for paragraph/code blocks)
            title: New title (for list blocks)
            items: New items list (for list blocks)
            language: Code language (for code blocks)
            header: Table header row (for table blocks)
            rows: Table data rows (for table blocks)

        Raises:
            ToolError: If block not found

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        # Load document
        json_data = self.load_document(path_info)

        # Search for block and update it
        def find_and_update_block(sections, target_id):
            """Recursively search for block and update it."""
            for section in sections:
                # Search in this section's blocks
                if "blocks" in section:
                    for block in section["blocks"]:
                        if block.get("id") == target_id:
                            # Found the block - update based on type
                            block_type = block.get("type")

                            if block_type == "paragraph":
                                if content is not None:
                                    block["content"] = content

                            elif block_type == "code":
                                if content is not None:
                                    block["content"] = content
                                if language is not None:
                                    block["language"] = language

                            elif block_type == "list":
                                if title is not None:
                                    block["title"] = title
                                if items is not None:
                                    block["items"] = items

                            elif block_type == "table":
                                # Table blocks use 'content' field with markdown table syntax
                                if header is not None and rows is not None:
                                    # Generate markdown table content
                                    table_content = self._generate_table_markdown(header, rows)
                                    block["content"] = table_content

                            return True

                # Search in sub-sections
                if "sections" in section:
                    if find_and_update_block(section["sections"], target_id):
                        return True
            return False

        updated = False
        if "sections" in json_data:
            updated = find_and_update_block(json_data["sections"], block_id)

        if not updated:
            raise ToolError(
                "BLOCK_NOT_FOUND",
                f"Block '{block_id}' not found in document"
            )

        # Save document
        self.save_document(path_info, json_data)

    def _generate_table_markdown(self, header: list, rows: list) -> str:
        """
        Generate markdown table content from header and rows.

        Args:
            header: List of header cell values
            rows: List of rows, each row is a list of cell values

        Returns:
            Markdown table string

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-010-UpdateBlockTool
        """
        # Build header row
        header_row = "| " + " | ".join(str(cell) for cell in header) + " |"

        # Build separator row
        separator = "|" + "|".join("------" for _ in header) + "|"

        # Build data rows
        data_rows = []
        for row in rows:
            row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
            data_rows.append(row_str)

        # Combine all parts
        table_lines = [header_row, separator] + data_rows
        return "\n".join(table_lines)

    def delete_block(
        self,
        path_info: PathInfo,
        block_id: str
    ) -> None:
        """
        Delete block from document.

        Removes the specified block from its containing section.
        Does not affect other blocks in the section.

        Args:
            path_info: PathInfo with file path
            block_id: Block ID to delete

        Raises:
            ToolError: If block not found

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-011-DeleteBlockTool
        """
        # Load document
        json_data = self.load_document(path_info)

        # Search for block and delete it from all sections
        def find_and_delete_block(sections, target_id):
            """Recursively search for block and delete it."""
            for section in sections:
                # Search in this section's blocks
                if "blocks" in section:
                    for i, block in enumerate(section["blocks"]):
                        if block.get("id") == target_id:
                            # Found the block - delete it
                            del section["blocks"][i]
                            return True

                # Search in sub-sections
                if "sections" in section:
                    if find_and_delete_block(section["sections"], target_id):
                        return True
            return False

        deleted = False
        if "sections" in json_data:
            deleted = find_and_delete_block(json_data["sections"], block_id)

        if not deleted:
            raise ToolError(
                "BLOCK_NOT_FOUND",
                f"Block '{block_id}' not found in document"
            )

        # Save document
        self.save_document(path_info, json_data)

    def append_list_item(
        self,
        path_info: PathInfo,
        block_id: str,
        item: str
    ) -> None:
        """
        Append item to list block.

        Only works with list type blocks. Appends new item to the end of
        the items array.

        Args:
            path_info: PathInfo with file path
            block_id: Block ID (must be a list type block)
            item: Item text to append

        Raises:
            ToolError: If block not found or block is not a list type

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-012-AppendListItemTool
        """
        # Load document
        json_data = self.load_document(path_info)

        # Search for block in all sections
        def find_and_append_to_block(sections, target_id, new_item):
            """Recursively search for block and append item."""
            for section in sections:
                # Search in this section's blocks
                if "blocks" in section:
                    for block in section["blocks"]:
                        if block.get("id") == target_id:
                            # Found the block - verify it's a list type
                            block_type = block.get("type")
                            if block_type != "list":
                                raise ToolError(
                                    "INVALID_BLOCK_TYPE",
                                    f"Block '{target_id}' is type '{block_type}', not 'list'. "
                                    f"append_list_item only works with list blocks."
                                )

                            # Append item to the list
                            if "items" not in block:
                                block["items"] = []
                            block["items"].append(new_item)
                            return True

                # Search in sub-sections
                if "sections" in section:
                    if find_and_append_to_block(section["sections"], target_id, new_item):
                        return True
            return False

        found = False
        if "sections" in json_data:
            found = find_and_append_to_block(json_data["sections"], block_id, item)

        if not found:
            raise ToolError(
                "BLOCK_NOT_FOUND",
                f"Block '{block_id}' not found in document"
            )

        # Save document
        self.save_document(path_info, json_data)

    def update_table_row(
        self,
        path_info: PathInfo,
        block_id: str,
        row_index: int,
        row_data: list
    ) -> None:
        """
        Update specific row in a table block.

        Only works with table type blocks. Updates the row at the specified
        index (0-based, excluding header). Validates column count matches
        the table header. Table blocks store markdown format in 'content' field.

        Args:
            path_info: PathInfo with file path
            block_id: Block ID (must be a table type block)
            row_index: Row index to update (0-based, excluding header)
            row_data: New row data (list of cell values)

        Raises:
            ToolError: If block not found, block is not a table type,
                      row index is invalid, or column count mismatch

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-013-UpdateTableRowTool
        """
        # Validate row_index
        if row_index < 0:
            raise ToolError(
                "INVALID_ROW_INDEX",
                f"Row index must be non-negative, got {row_index}"
            )

        # Load document
        json_data = self.load_document(path_info)

        # Search for block in all sections
        def find_and_update_table_row(sections, target_id, idx, data):
            """Recursively search for block and update table row."""
            for section in sections:
                # Search in this section's blocks
                if "blocks" in section:
                    for block in section["blocks"]:
                        if block.get("id") == target_id:
                            # Found the block - verify it's a table type
                            block_type = block.get("type")
                            if block_type != "table":
                                raise ToolError(
                                    "INVALID_BLOCK_TYPE",
                                    f"Block '{target_id}' is type '{block_type}', not 'table'. "
                                    f"update_table_row only works with table blocks."
                                )

                            # Validate table structure (table blocks use 'content' field with markdown)
                            if "content" not in block:
                                raise ToolError(
                                    "INVALID_TABLE_STRUCTURE",
                                    f"Table block '{target_id}' has no content"
                                )

                            # Parse markdown table
                            lines = block["content"].split("\n")
                            if len(lines) < 3:  # Need at least header, separator, and one data row
                                raise ToolError(
                                    "INVALID_TABLE_STRUCTURE",
                                    f"Table block '{target_id}' has invalid table format"
                                )

                            # Parse header to get column count
                            header_line = lines[0].strip()
                            header_cells = [cell.strip() for cell in header_line.split("|")[1:-1]]
                            header_count = len(header_cells)

                            # Validate column count
                            data_count = len(data)
                            if data_count != header_count:
                                raise ToolError(
                                    "COLUMN_COUNT_MISMATCH",
                                    f"Row data has {data_count} columns, but table has "
                                    f"{header_count} columns. Column count must match."
                                )

                            # Data rows start from line 2 (after header and separator)
                            data_rows_start_idx = 2
                            num_data_rows = len(lines) - data_rows_start_idx

                            # Validate row index
                            if idx >= num_data_rows:
                                raise ToolError(
                                    "ROW_INDEX_OUT_OF_RANGE",
                                    f"Row index {idx} is out of range. Table has {num_data_rows} rows."
                                )

                            # Update the target row
                            target_line_idx = data_rows_start_idx + idx
                            new_row_str = "| " + " | ".join(str(cell) for cell in data) + " |"
                            lines[target_line_idx] = new_row_str

                            # Rebuild table content
                            block["content"] = "\n".join(lines)
                            return True

                # Search in sub-sections
                if "sections" in section:
                    if find_and_update_table_row(section["sections"], target_id, idx, data):
                        return True
            return False

        found = False
        if "sections" in json_data:
            found = find_and_update_table_row(json_data["sections"], block_id, row_index, row_data)

        if not found:
            raise ToolError(
                "BLOCK_NOT_FOUND",
                f"Block '{block_id}' not found in document"
            )

        # Save document
        self.save_document(path_info, json_data)

    def append_table_row(
        self,
        path_info: PathInfo,
        block_id: str,
        row_data: list
    ) -> None:
        """
        Append a new row to a table block.

        Only works with table type blocks. Appends a new row to the end of the
        table. Validates column count matches the table header. Table blocks
        store markdown format in 'content' field.

        Args:
            path_info: PathInfo with file path
            block_id: Block ID (must be a table type block)
            row_data: Row data (list of cell values)

        Raises:
            ToolError: If block not found, block is not a table type,
                      or column count mismatch

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-017-AppendTableRowTool
        """
        # Load document
        json_data = self.load_document(path_info)

        # Search for block in all sections
        def find_and_append_table_row(sections, target_id, data):
            """Recursively search for block and append table row."""
            for section in sections:
                # Search in this section's blocks
                if "blocks" in section:
                    for block in section["blocks"]:
                        if block.get("id") == target_id:
                            # Found the block - verify it's a table type
                            block_type = block.get("type")
                            if block_type != "table":
                                raise ToolError(
                                    "INVALID_BLOCK_TYPE",
                                    f"Block '{target_id}' is type '{block_type}', not 'table'. "
                                    f"append_table_row only works with table blocks."
                                )

                            # Validate table structure (table blocks use 'content' field with markdown)
                            if "content" not in block:
                                raise ToolError(
                                    "INVALID_TABLE_STRUCTURE",
                                    f"Table block '{target_id}' has no content"
                                )

                            # Parse markdown table
                            lines = block["content"].split("\n")
                            if len(lines) < 2:  # Need at least header and separator
                                raise ToolError(
                                    "INVALID_TABLE_STRUCTURE",
                                    f"Table block '{target_id}' has invalid table format"
                                )

                            # Parse header to get column count
                            header_line = lines[0].strip()
                            header_cells = [cell.strip() for cell in header_line.split("|")[1:-1]]
                            header_count = len(header_cells)

                            # Validate column count
                            data_count = len(data)
                            if data_count != header_count:
                                raise ToolError(
                                    "COLUMN_COUNT_MISMATCH",
                                    f"Row data has {data_count} columns, but table has "
                                    f"{header_count} columns. Column count must match."
                                )

                            # Build new row
                            new_row_str = "| " + " | ".join(str(cell) for cell in data) + " |"

                            # Append to table
                            lines.append(new_row_str)

                            # Rebuild table content
                            block["content"] = "\n".join(lines)
                            return True

                # Search in sub-sections
                if "sections" in section:
                    if find_and_append_table_row(section["sections"], target_id, data):
                        return True
            return False

        found = False
        if "sections" in json_data:
            found = find_and_append_table_row(json_data["sections"], block_id, row_data)

        if not found:
            raise ToolError(
                "BLOCK_NOT_FOUND",
                f"Block '{block_id}' not found in document"
            )

        # Save document
        self.save_document(path_info, json_data)

    def create_document(
        self,
        path_info: PathInfo,
        doc_type: str,
        replacements: Dict[str, str]
    ) -> str:
        """
        Create new document from template with placeholder replacement.

        Creates a new RBT document by:
        1. Loading appropriate template (Task/Blueprint/Requirement)
        2. Auto-filling common placeholders (project-id, feature-id, date, etc.)
        3. Replacing custom placeholders with provided values
        4. Converting to JSON and saving as .new.md

        Auto-filled placeholders (from path_info):
        - [project-id]: From path_info.project_id
        - [feature-id]: From path_info.feature_id
        - [feature-name]: From path_info.feature_id
        - [YYYY-MM-DD]: Current date

        Custom placeholders (need to be in replacements):
        - [task-name]: Task name (for Task type)
        - [任務標題]/[需求標題]/[藍圖標題]: Document titles
        - Any other template-specific placeholders

        File is saved as .new.md

        Args:
            path_info: PathInfo with project/feature info
            doc_type: Document type ("Task", "Blueprint", "Requirement")
            replacements: Dictionary of custom placeholder -> value mappings

        Returns:
            Created file path (.new.md)

        Raises:
            ToolError: If file already exists, template not found, or conversion fails

        Example:
            create_document(
                path_info,
                "Task",
                {
                    "task-name": "PathResolver",
                    "任務標題": "實作 PathResolver 路徑解析與驗證"
                }
            )
            # project-id, feature-id, feature-name, YYYY-MM-DD 會自動填入

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-014-CreateDocumentTool
        """
        from datetime import datetime

        # Validate doc_type (only for RBT documents)
        if path_info.is_rbt and doc_type not in ["Task", "Blueprint", "Requirement"]:
            raise ToolError(
                "INVALID_DOC_TYPE",
                f"RBT document type must be Task, Blueprint, or Requirement, got: {doc_type}"
            )

        # Determine target path (.new.md)
        original_path = path_info.file_path
        if original_path.endswith(".new.md"):
            target_path = original_path
        elif original_path.endswith(".md"):
            target_path = original_path.replace(".md", ".new.md")
        else:
            target_path = original_path + ".new.md"

        # Check if file already exists (both .md and .new.md)
        base_path = target_path.replace(".new.md", ".md")
        if os.path.exists(target_path) or os.path.exists(base_path):
            raise ToolError(
                "FILE_EXISTS",
                f"Document already exists at {target_path} or {base_path}"
            )

        # Check for duplicate TASK index (only for Task documents)
        if doc_type == "Task":
            from glob import glob
            import re

            # Extract task index from filename
            # Expected format: TASK-{index}-{name}.md or TASK-{index}-{name}.new.md
            filename = os.path.basename(base_path)
            match = re.match(r'TASK-(\d+)-', filename)

            if match:
                task_index = match.group(1)
                task_dir = os.path.dirname(base_path)

                # Search for existing TASK files with same index
                search_patterns = [
                    os.path.join(task_dir, f"TASK-{task_index}-*.md"),
                    os.path.join(task_dir, f"TASK-{task_index}-*.new.md")
                ]

                existing_files = []
                for pattern in search_patterns:
                    existing_files.extend(glob(pattern))

                # Filter out the current file (shouldn't exist yet, but just in case)
                existing_files = [f for f in existing_files if f not in [base_path, target_path]]

                if existing_files:
                    # Found duplicate index
                    existing_names = [os.path.basename(f) for f in existing_files]
                    raise ToolError(
                        "DUPLICATE_TASK_INDEX",
                        f"TASK index '{task_index}' already exists in this feature: {existing_names}"
                    )

        # Load template (only for RBT documents)
        if path_info.is_rbt:
            template_name = f"{doc_type}_Template.md"
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
            template_path = os.path.join(template_dir, template_name)

            if not os.path.exists(template_path):
                raise ToolError(
                    "TEMPLATE_NOT_FOUND",
                    f"Template not found: {template_path}"
                )

            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except Exception as e:
                raise ToolError(
                    "TEMPLATE_READ_ERROR",
                    f"Failed to read template: {str(e)}"
                )

            # Auto-fill common placeholders from path_info
            auto_replacements = {
                "project-id": path_info.project_id,
                "YYYY-MM-DD": datetime.now().strftime("%Y-%m-%d")
            }

            if path_info.feature_id:
                auto_replacements["feature-id"] = path_info.feature_id
                auto_replacements["feature-name"] = path_info.feature_id

            # Merge auto replacements with custom replacements (custom takes precedence)
            all_replacements = {**auto_replacements, **replacements}

            # Replace all placeholders
            md_content = template_content
            for key, value in all_replacements.items():
                placeholder = f"[{key}]"
                md_content = md_content.replace(placeholder, value)
        else:
            # For general documents, create a basic structure from replacements
            title = replacements.get("title", "Untitled Document")
            author = replacements.get("author", "")
            description = replacements.get("description", "")

            # Build YAML header
            yaml_lines = [
                "---",
                f"id: {replacements.get('id', path_info.project_id + '-doc')}",
                f"group_id: {path_info.project_id}",
                f"type: {doc_type}",
                f"title: {title}",
            ]
            if author:
                yaml_lines.append(f"author: {author}")
            yaml_lines.append(f"update_date: {datetime.now().strftime('%Y-%m-%d')}")
            if description:
                yaml_lines.append(f"description: {description}")
            yaml_lines.append("---")
            yaml_lines.append("")

            # Build basic content with required root section
            md_content = "\n".join(yaml_lines)
            md_content += "<!-- id: sec-root -->\n"
            md_content += f"# {title} {{#sec-title}}\n\n"

            # Add sections from replacements if provided
            if "sections" in replacements and isinstance(replacements["sections"], list):
                for i, section in enumerate(replacements["sections"], 1):
                    section_id = section.get("id", f"sec-section-{i}")
                    section_title = section.get("title", f"Section {i}")
                    md_content += f"## {i}. {section_title} {{#{section_id}}}\n\n"

        # Convert template markdown to JSON
        try:
            json_data = self.converter.to_json(md_content)
        except Exception as e:
            raise ToolError(
                "TEMPLATE_CONVERSION_ERROR",
                f"Failed to convert template to JSON: {str(e)}"
            )

        # Create directory structure if needed
        target_dir = os.path.dirname(target_path)
        os.makedirs(target_dir, exist_ok=True)

        # Write file (atomic operation)
        tmp_path = target_path + ".tmp"
        try:
            # Convert back to markdown (to ensure proper formatting)
            final_md_content = self.converter.to_md(json_data)

            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(final_md_content)

            # Rename to final path
            os.rename(tmp_path, target_path)

        finally:
            # Clean up tmp file if it still exists
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        # Update cache
        self.cache.put(target_path, json_data)

        return target_path

    def clear_cache(self, file_path: Optional[str] = None) -> None:
        """
        Clear document cache.

        Args:
            file_path: If provided, clear only this file; if None, clear all

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-003-DocumentService
        """
        self.cache.clear(file_path)

    def __del__(self):
        """Stop cache cleanup thread on destruction."""
        if hasattr(self, 'cache'):
            self.cache.stop()
