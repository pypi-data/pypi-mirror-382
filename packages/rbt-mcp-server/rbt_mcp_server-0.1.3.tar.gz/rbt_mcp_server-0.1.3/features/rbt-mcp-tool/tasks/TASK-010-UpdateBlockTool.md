---
id: TASK-010-UpdateBlockTool
group_id: knowledge-smith
type: Task
title: 實作 update_block MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 update_block MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `update_block` tool function
  - 遵循 TDD 流程

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/update_block.py`, tests

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (TDD)

<!-- id: blk-implementation-steps, type: list -->
**實作指引**
  - **TDD Red**: 先寫測試
  - **TDD Green**: 實作功能
  - **TDD Refactor**: 重構

<!-- id: blk-test-spec, type: list -->
**測試規格**
  - **TC1**: 正常操作成功
  - **TC2**: 錯誤情況處理（ID 不存在、類型錯誤等）

<!-- id: sec-completion -->
### 4. 實作完成記錄

<!-- id: blk-execution-summary, type: list -->
**執行摘要**
  - **實際耗時**: 約 1.5 小時
  - **實作模組**:
    - `rbt_mcp_server/document_service.py`: 新增 `update_block()` 方法和 `_generate_table_markdown()` 輔助函數
    - `rbt_mcp_server/server.py`: 實作 `update_block` MCP tool function
    - `tests/tools/test_update_block.py`: 撰寫 7 個測試案例（全數通過）
  - **主要產出**:
    - DocumentService.update_block(): 支援更新 paragraph, code, list, table 四種類型 block
    - 特殊處理：table 類型需將 header/rows 轉換為 markdown table content
    - MCP tool 正確處理路徑解析和錯誤回傳
  - **測試結果**: 7/7 測試通過，涵蓋所有 block 類型和錯誤情境

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| 表格更新失敗（測試未通過） | 發現 converter 使用 `content` 欄位儲存 markdown 表格字串，而非 `header`/`rows` 結構。新增 `_generate_table_markdown()` 方法生成 markdown 表格內容 | 15 分鐘 | ✅ 若事先查看 converter 轉換邏輯可避免 |

<!-- id: blk-technical-debt, type: list -->
**技術債務**
  - 無明顯技術債務
  - 程式碼結構清晰，遵循現有模式
  - 測試覆蓋完整

<!-- id: blk-implementation-location, type: list -->
**實作定位**
  - **DocumentService**: `grep -n "def update_block" rbt_mcp_server/document_service.py`
  - **MCP Tool**: `grep -n "@mcp.tool.*update_block" rbt_mcp_server/server.py -A 2`
  - **測試**: `tests/tools/test_update_block.py`
