---
id: TASK-008-CreateSectionTool
group_id: knowledge-smith
type: Task
title: 實作 create_section MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 create_section MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `create_section` tool function
  - 遵循 TDD 流程

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/create_section.py`, tests

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
**執行摘要**:
  - 實作耗時: 約 1.5 小時
  - 建立檔案: `tests/tools/test_create_section.py` (9個測試), 修改 `rbt_mcp_server/document_service.py` (新增 `create_section` 和 `_generate_section_id` 方法及 `_get_new_md_path` 輔助方法)
  - 主要工作: TDD 開發流程 (Red → Green → Refactor)，實作 section 建立邏輯，ID 生成與衝突處理，cache 機制修正
  - 測試通過率: 9/9 (100%)

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| PathInfo 缺少 is_new_file 參數導致測試失敗 | 修正測試程式碼加入 is_new_file=False 參數 | 5分鐘 | ✅ 先查看 models.py 定義 |
| 多次 create_section 產生相同 ID | 修正 load_document 邏輯優先讀取 .new.md 檔案，確保每次操作都從最新版本讀取 | 30分鐘 | ✅ 仔細設計 cache key 策略 |

<!-- id: blk-technical-debt, type: list -->
**技術債務**: 無
