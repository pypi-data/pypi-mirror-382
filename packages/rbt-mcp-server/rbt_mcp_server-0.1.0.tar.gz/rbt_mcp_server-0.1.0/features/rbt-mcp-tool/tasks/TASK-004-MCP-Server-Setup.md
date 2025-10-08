---
id: TASK-004-MCP-Server-Setup
group_id: knowledge-smith
type: Task
title: 建立 MCP Server 架構與工具註冊
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-003-DocumentService]

<!-- id: sec-root -->
# Task: 建立 MCP Server 架構與工具註冊

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置 (Goal & Dependencies)

<!-- id: blk-goal, type: list -->
**目標 (Goal)**
  - 使用 MCP Python SDK 建立 MCP Server
  - 註冊所有 tool functions
  - 設定 root_dir 環境變數
  - 建立 `uv` 專案結構（pyproject.toml）
  - 提供 `uv run` 啟動指令

<!-- id: blk-dependencies, type: list -->
**前置任務 (Dependencies)**
  - TASK-003-DocumentService（核心服務層）

<!-- id: blk-target-modules, type: list -->
**目標模組/檔案**
  - 新檔案：`rbt_mcp_server/server.py`（MCP Server 主程式）
  - 新檔案：`pyproject.toml`（uv 專案配置）
  - 新檔案：`tests/test_server.py`（TDD 測試）

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (Implementation Guide & Test Specifications)

<!-- id: blk-implementation-steps, type: list -->
**實作指引 (Implementation Guide) - TDD 流程**
  - **步驟 0 (TDD Red)**: 先寫測試
  - **步驟 1**: 建立 `pyproject.toml`，設定依賴：`mcp`, `pyyaml`
  - **步驟 2**: 實作 `server.py`，註冊 tool functions（佔位符）
  - **步驟 3**: 實作環境變數讀取（`RBT_ROOT_DIR`）
  - **步驟 4 (TDD Green)**: 測試 server 可啟動
  - **步驟 5 (TDD Refactor)**: 重構

<!-- id: blk-test-spec, type: list -->
**測試規格 (Test Specifications) - TDD**
  - **Test Case 1**: Server 啟動成功
  - **Test Case 2**: Tool functions 正確註冊
  - **Test Case 3**: 環境變數讀取正確

<!-- id: sec-completion -->
### 4. 實作完成記錄 (Implementation Completion)

<!-- id: blk-execution-summary, type: list -->
**執行摘要與產出**
  - **實際耗時**: 2.5小時 (預估: 3-4小時)
  - **執行狀態**: 完成，所有測試通過 (6/6 tests passed)
  - **關鍵產出**:
    - 建立 `rbt_mcp_server/server.py`：完整 MCP Server 實作，註冊 11 個 tool functions
    - 建立 `tests/test_server.py`：6 個測試案例，覆蓋 server 初始化、tool 註冊、環境變數讀取
    - 使用 FastMCP (mcp.server.fastmcp) 實作，提供清晰的 tool decorator 架構
    - 支援 RBT_ROOT_DIR 環境變數設定，驗證必要性
    - 所有 tool functions 包含完整 docstring、type hints、範例
  - **程式碼變更統計**:
    - 新增檔案：2 個 (server.py 460 行, test_server.py 167 行)
    - 註冊工具：11 個 (get_outline, read_section, update_section_summary, create_section, create_block, update_block, delete_block, append_list_item, update_table_row, create_document, clear_cache)

<!-- id: blk-problems-table, type: table -->
**問題與解決記錄**
| 問題描述 | 解決方案 | 耗時 | 可預防? |
|----------|----------|------|---------|
| FastMCP tool 註冊後無法直接從 mcp._tools 取得 | 發現 FastMCP 將 tools 儲存在 mcp._tool_manager._tools，調整測試存取路徑 | 15分鐘 | ✅ (可透過更完整的 SDK 文件研究) |
| 測試中模組已載入，無法透過 patch.dict 重新初始化 document_service | 改為直接測試 get_root_dir() 函式讀取環境變數的正確性 | 10分鐘 | ✅ (TDD 設計時考慮模組初始化順序) |

<!-- id: blk-technical-debt, type: list -->
**技術債務與重構建議**
  - **技術債務**: 無
  - **重構建議**:
    - 考慮將 tool functions 分組到不同檔案 (如 tools/read_tools.py, tools/write_tools.py)，但目前 11 個 tools 放在單一檔案仍可維護
    - 未來可增加 tool function 的 schema validation (使用 pydantic)
  - **程式碼定位指令**: `grep -r "@TASK: TASK-004" rbt_mcp_server/`
  - **關鍵檔案清單**:
    - `/Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/server.py` - MCP Server 主程式，460 行
    - `/Users/devinlai/Develope/KnowledgeSmith/tests/test_server.py` - Server 測試套件，167 行，6 個測試案例
