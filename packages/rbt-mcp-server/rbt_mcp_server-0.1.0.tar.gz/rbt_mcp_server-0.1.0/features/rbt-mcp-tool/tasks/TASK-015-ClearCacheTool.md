---
id: TASK-015-ClearCacheTool
group_id: knowledge-smith
type: Task
title: 實作 clear_cache MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 clear_cache MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `clear_cache` tool function
  - 遵循 TDD 流程

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/clear_cache.py`, tests

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
**執行摘要**: 實際耗時 1小時 (預估: 1-1.5小時)
  - **執行狀態**: 完成，所有測試通過 (5/5 tests passed)
  - **關鍵產出**:
    - 建立 `tests/tools/test_clear_cache.py`：5 個測試案例，涵蓋清除所有快取、清除特定檔案快取、清除不存在檔案、清除空快取、驗證快取實際被清除
    - 更新 `rbt_mcp_server/server.py` clear_cache 函式的 @TASK 註解為 TASK-015-ClearCacheTool
    - clear_cache tool 已在 TASK-004 時實作完成，本次任務主要補充完整測試覆蓋和文件
  - **測試涵蓋範圍**:
    - TC1: 清除所有快取成功 ✅
    - TC2: 清除特定檔案快取成功（其他快取保留）✅
    - TC3: 清除不存在檔案快取（幂等操作）✅
    - TC4: 清除空快取（幂等操作）✅
    - TC5: 驗證快取清除後強制重新載入 ✅

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| PathInfo 模型新增 is_new_file 參數導致測試失敗 | 在所有 PathInfo 建構式中加上 is_new_file=False | 5分鐘 | ✅ (保持測試與模型同步) |
| sed 指令誤改所有 @TASK 註解 | 改用 Edit 工具精確修改 | 10分鐘 | ✅ (使用更精確的編輯工具) |

<!-- id: blk-technical-debt, type: list -->
**技術債務**: 無
  - **程式碼定位指令**: `grep -r "@TASK: TASK-015" rbt_mcp_server/`
  - **關鍵檔案清單**:
    - `/Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/server.py` - clear_cache tool 函式（第 648-668 行）
    - `/Users/devinlai/Develope/KnowledgeSmith/tests/tools/test_clear_cache.py` - 測試套件，316 行，5 個測試案例
