---
id: TASK-006-ReadSectionTool
group_id: knowledge-smith
type: Task
title: 實作 read_section MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 read_section MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `read_section` tool，讀取指定 section 的詳細內容（含 blocks）

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/read_section.py`, `tests/tools/test_read_section.py`

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (TDD)

<!-- id: blk-implementation-steps, type: list -->
**實作指引**
  - **TDD Red → Green → Refactor**
  - 呼叫 DocumentService.read_section(section_id)

<!-- id: blk-test-spec, type: list -->
**測試規格**
  - **TC1**: 成功讀取 section（含 blocks）
  - **TC2**: section_id 不存在 → ToolError("SECTION_NOT_FOUND")

<!-- id: sec-completion -->
### 4. 實作完成記錄

<!-- id: blk-execution-summary, type: list -->
**執行摘要**: 實際耗時約 0.8 小時
  - **實作內容**: `read_section` MCP tool 已在 TASK-004 中實作於 `server.py`，底層邏輯 `DocumentService.read_section()` 已在 TASK-003 完成
  - **本次工作**: 撰寫 5 個完整的測試案例，涵蓋各種 section 與 block 類型
  - **測試結果**: 5/5 測試全數通過，功能驗證完成

<!-- id: blk-implementation-details, type: list -->
**實作定位與產出**
  - **測試檔案**: `/Users/devinlai/Develope/KnowledgeSmith/tests/tools/test_read_section.py`
  - **測試涵蓋**:
    - TC1: 成功讀取 section（含 paragraph 和 list blocks）
    - TC2: section_id 不存在時回傳 ToolError("SECTION_NOT_FOUND")
    - TC3: 讀取含 table block 的 section（驗證 table 以 markdown content 形式儲存）
    - TC4: 讀取 nested subsection（含 code block）
    - TC5: 讀取一般文件（非 RBT 文件）的 section
  - **關鍵發現**:
    - Converter 的 block 結構：paragraph/code/table 使用 `content`，list 使用 `items`
    - Code block 不保留 `language` 欄位（在 parser 中被移除）
    - Table 保持原始 markdown 格式在 `content` 中

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| 測試假設 table block 有 header/rows 欄位 | 檢查 converter/parser.py，發現 table 實際以 content 儲存 markdown 格式 | 10分鐘 | ✅ 應先閱讀 parser 原始碼了解 JSON 結構 |
| 測試假設 code block 有 language 欄位 | 確認 parser 在處理 code 時移除了 ``` 和 language 標記 | 5分鐘 | ✅ 同上 |

<!-- id: blk-technical-debt, type: list -->
**技術債務**: 無
