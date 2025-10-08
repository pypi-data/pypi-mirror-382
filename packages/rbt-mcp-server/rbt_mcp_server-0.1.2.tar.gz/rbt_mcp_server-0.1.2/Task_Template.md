---
id: TASK-[feature-id]-[task-name]
group_id: [project-id]
type: Task
title: [任務標題]
blueprint: BP-[feature-name]
requirement: REQ-[feature-name]
---

<!-- info-section -->
> status: Pending
> update_date: [YYYY-MM-DD]
> dependencies: []

<!-- id: sec-root -->
# Task: [任務標題]

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置 (Goal & Dependencies)

<!-- id: blk-goal, type: list -->
**目標 (Goal)**
  - [簡述本任務要達成的最終目的]

<!-- id: blk-dependencies, type: list -->
**前置任務 (Dependencies)**
  - [列出必須先完成的其他 Task ID，例如：TASK-001]

<!-- id: blk-target-modules, type: list -->
**目標模組/檔案**
  - [列出目標模組、新/舊檔案路徑]

<!-- id: sec-change-history -->
### 2. 變更記錄與風險 (Change History & Risks)

<!-- id: blk-change-history-table, type: table -->
**變更歷史追溯**
| 版本 | 變更原因 | 影響範圍 | 重新實作日期 |
|---|---|---|---|
| v1.0 | 初始版本 | N/A | [YYYY-MM-DD] |

<!-- id: blk-risks, type: list -->
**風險與關注點**
  - **上次實作定位**: `File.swift:42-58` - [功能說明] or function Name
  - **重點關注**: [這次要特別注意的技術風險和陷阱]

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (Implementation Guide & Test Specifications)

<!-- id: blk-implementation-steps, type: list -->
**實作指引 (Implementation Guide)**
  - **步驟 1**: [例如，參考 BP-XXX 的 comp-downloader 區塊]
  - **步驟 2**: [例如，實作 download 函式，簽名為...]
  - **步驟 3**: [例如，整合到主流程]

<!-- id: blk-test-spec, type: list -->
**測試規格 (Test Specifications)**
  - **Test Case 1**: [測試案例標題]
    - **Given**: [描述前置條件或狀態]
    - **When**: [描述觸發的動作]
    - **Then**: [描述預期結果]
  - **Test Case 2**: [測試案例標題]
    - **Given**: [描述前置條件或狀態]
    - **When**: [描述觸發的動作]
    - **Then**: [描述預期結果]

<!-- id: sec-completion -->
### 4. 實作完成記錄 (Implementation Completion)

<!-- id: blk-execution-summary, type: list -->
**執行摘要與產出**
  - **實際耗時**: [X]小時 (預估: [Y]小時)
  - **執行狀態**: [待填寫] ✅ 完成 / ⚠️ 部分完成 / ❌ 需重做
  - **關鍵產出**: [列出關鍵函式/類型名稱及用途簡述]
  - **程式碼變更統計**: +[X] lines, -[Y] lines, [Z] files modified

<!-- id: blk-problems-table, type: table -->
**問題與解決記錄**
| 問題描述 | 解決方案 | 耗時 | 可預防? |
|----------|----------|------|---------|
| [問題描述] | [解決方案] | [X]min | ✅/❌ |

<!-- id: blk-technical-debt, type: list -->
**技術債務與重構建議**
  - **技術債務**: [暫時的 workaround，未來需要改進]
  - **重構建議**: [程式碼結構可以優化的地方]
  - **程式碼定位指令**: `grep -r "@TASK: [this-task-id]" Sources/`
  - **關鍵檔案清單**: [Path/To/MainFile.swift] - 主要邏輯
