---
id: TASK-011-DeleteBlockTool
group_id: knowledge-smith
type: Task
title: 實作 delete_block MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 delete_block MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `delete_block` tool function
  - 遵循 TDD 流程

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/delete_block.py`, tests

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
**執行摘要**: 實際耗時約 1 小時
  - **實作位置**: `rbt_mcp_server/document_service.py::delete_block()` (lines 389-449), `rbt_mcp_server/server.py::delete_block()` (lines 437-485)
  - **測試位置**: `tests/tools/test_delete_block.py` (7 個測試案例，全數通過)
  - **主要產出**:
    - DocumentService.delete_block(): 遞歸搜尋並刪除指定 block
    - server.delete_block tool: MCP tool function 整合
    - 7 個測試案例涵蓋正常操作、錯誤處理、多類型 block 刪除
  - **測試覆蓋**: TC1 (正常刪除 paragraph/list/table/nested blocks)、TC2 (錯誤處理: block 不存在)、連續刪除、刪除最後一個 block

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| 無重大問題 | N/A | N/A | N/A |

<!-- id: blk-technical-debt, type: list -->
**技術債務**: 無
