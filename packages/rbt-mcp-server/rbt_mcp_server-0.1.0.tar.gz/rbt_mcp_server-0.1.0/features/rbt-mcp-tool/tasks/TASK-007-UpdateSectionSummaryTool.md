---
id: TASK-007-UpdateSectionSummaryTool
group_id: knowledge-smith
type: Task
title: 實作 update_section_summary MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 update_section_summary MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `update_section_summary` tool，更新指定 section 的 summary
  - 更新後儲存為 `.new.md`

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/update_section_summary.py`, tests

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (TDD)

<!-- id: blk-implementation-steps, type: list -->
**實作指引**
  - TDD Red → Green → Refactor
  - 呼叫 DocumentService.update_section_summary(section_id, new_summary)

<!-- id: blk-test-spec, type: list -->
**測試規格**
  - **TC1**: 成功更新 summary，產生 `.new.md`
  - **TC2**: section_id 不存在 → ToolError

<!-- id: sec-completion -->
### 4. 實作完成記錄

<!-- id: blk-execution-summary, type: list -->
**執行摘要**
  - **實際耗時**: 約 1 小時
  - **建立檔案**: `tests/tools/test_update_section_summary.py`（2 個測試案例）
  - **測試通過**: 2/2 測試全數通過
  - **實作內容**: 針對 MCP tool function `update_section_summary` 建立完整測試套件
  - **主要產出**:
    - TC1: 成功更新 summary 並產生 .new.md 檔案，驗證 JSON 結構和 Markdown 輸出
    - TC2: section_id 不存在時正確回傳 ToolError

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| 初始測試假設 summary 會替換 block 內容 | 理解 RBT 格式中 summary 是獨立欄位，會寫成 `[SUMMARY: ...]`，不影響原 block 內容 | 5分鐘 | ✅ 事先查看 converter 輸出格式 |

<!-- id: blk-technical-debt, type: list -->
**技術債務**: 無
