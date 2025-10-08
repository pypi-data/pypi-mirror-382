---
id: TASK-014-CreateDocumentTool
group_id: knowledge-smith
type: Task
title: 實作 create_document MCP Tool
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-004-MCP-Server-Setup]

<!-- id: sec-root -->
# Task: 實作 create_document MCP Tool

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置

<!-- id: blk-goal, type: list -->
**目標**
  - 實作 `create_document` tool function
  - 遵循 TDD 流程

<!-- id: blk-dependencies, type: list -->
**前置任務**: TASK-004-MCP-Server-Setup

<!-- id: blk-target-modules, type: list -->
**目標模組**: `rbt_mcp_server/tools/create_document.py`, tests

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
  - 實際耗時: 約 1小時
  - 完成項目:
    - 實作 DocumentService.create_document() 方法（約120行）
    - 實作 server.py 中的 create_document tool function（含路徑驗證）
    - 新增 6 個測試案例（test_create_document.py）
    - 支援 RBT 和一般文件建立
    - 自動建立目錄結構
    - 防止檔案覆蓋
    - 路徑安全驗證（防止 .. / \ 等危險字元）
  - 測試結果: 6/6 通過 (100%)

<!-- id: blk-problems-table, type: table -->
**問題記錄**
| 問題 | 解決 | 耗時 | 可預防? |
|------|------|------|---------|
| PathResolver.resolve() 檢查檔案存在，但 create_document 是建立新檔案 | 在 server.py 中直接構建 PathInfo 而不使用 resolve() | 15分鐘 | ✅ 應在設計階段考慮 create vs read 操作的差異 |
| Converter 解析空 info section 時返回 None 導致錯誤 | 在 create_document 中給 info 添加預設 status 欄位 | 10分鐘 | ✅ 測試時應涵蓋空 info 情況 |
| 路徑安全驗證測試失敗 | 在 server.py 中添加基本路徑驗證（檢查 .. / \\ 字元） | 5分鐘 | ✅ 安全性需求應在初期明確 |

<!-- id: blk-technical-debt, type: list -->
**技術債務**:
  - 路徑驗證目前僅檢查基本危險字元，未來可能需要更完整的路徑規範化與驗證
  - Converter 的 info section 處理應該更 robust（處理 None 情況）
  - 考慮為 create_document 添加更多參數（例如自訂 info 欄位）
