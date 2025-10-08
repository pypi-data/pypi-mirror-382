# RBT MCP Server

MCP Server for editing RBT documents with partial operations. **Reduces token consumption by 80-95%** compared to full file read/write operations.

## 🎯 Key Features

- **Token Optimization**: 80-95% reduction in LLM token usage
- **Structured Operations**: Edit specific sections/blocks without loading entire documents
- **Smart Caching**: LRU + TTL cache for frequently accessed documents
- **TASK Fuzzy Search**: Find TASK files by index (e.g., "001" matches "TASK-001-PathResolver.md")
- **Template-based Creation**: Auto-fill placeholders (project-id, feature-id, date)
- **13 MCP Tools**: Complete CRUD operations for RBT documents

## 📦 Installation

### Option 1: Install from source (uv)

```bash
# Clone repository
git clone https://github.com/yourusername/KnowledgeSmith.git
cd KnowledgeSmith

# Install with uv
uv pip install -e .
```

### Option 2: Direct installation

```bash
uv pip install rbt-mcp-server
```

## 🚀 Quick Start

### 1. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rbt-document-editor": {
      "type": "stdio",
      "command": "rbt-mcp-server",
      "env": {
        "RBT_ROOT_DIR": "/path/to/your/documents"
      }
    }
  }
}
```

Or use full uv command:

```json
{
  "mcpServers": {
    "rbt-document-editor": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "rbt-mcp-server"],
      "env": {
        "RBT_ROOT_DIR": "/path/to/your/documents"
      }
    }
  }
}
```

### 2. Set Environment Variable

```bash
export RBT_ROOT_DIR=/path/to/your/documents
```

### 3. Test the Server

```bash
rbt-mcp-server
```

## 📚 Available MCP Tools

1. **get_outline** - Get document structure (saves 80% tokens)
2. **read_content** - Read specific section/block (saves 90% tokens)
3. **update_info** - Update status/dependencies
4. **update_section_summary** - Update section summary
5. **create_section** - Create new sub-section
6. **create_block** - Create paragraph/code/list/table
7. **update_block** - Update block content
8. **delete_block** - Delete block
9. **append_list_item** - Add item to list
10. **update_table_row** - Update table row
11. **append_table_row** - Add table row
12. **create_document** - Create from template
13. **clear_cache** - Clear document cache

See [rbt_mcp_server/README.md](rbt_mcp_server/README.md) for detailed usage.

## 📊 Token Savings

| Operation | Traditional | MCP | Savings |
|-----------|------------|-----|---------|
| Read structure | 4,000 | 800 | **80%** |
| Update status | 8,000 | 300 | **96%** |
| Add list item | 8,000 | 1,000 | **88%** |
| Complete TASK | 44,000 | 3,000 | **93%** |

## 🧪 Development

Install development dependencies:
```bash
uv sync --dev
```

Run tests:
```bash
RBT_ROOT_DIR=/test/root uv run pytest -v
```

Test coverage:
```bash
RBT_ROOT_DIR=/test/root uv run pytest --cov=rbt_mcp_server --cov-report=html
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.
