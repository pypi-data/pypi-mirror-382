---
id: BP-[feature-name]
group_id: [project-id]
type: Blueprint
feature: [feature-name]
requirement: REQ-[feature-name]
---

<!-- info-section -->
> status: Draft
> update_date: [YYYY-MM-DD]
> summary_context: [用一句話總結本 BP 的核心目標和範圍]

<!-- id: sec-root -->
# 專案藍圖 (Blueprint): [功能標題]

<!-- id: sec-data-structures -->
### 1. 核心資料結構 (Core Data Structures)

<!-- id: blk-data-struct-desc, type: paragraph -->
[本區塊描述了本功能所需的關鍵資料結構定義]

<!-- id: blk-data-struct-list, type: list -->
**資料結構定義**
  - **[結構名稱 1]**: 目標模組 `[模組名稱]`，結構 `struct ... { ... }`
  - **[結構名稱 2]**: 目標模組 `[模組名稱]`，結構 `struct ... { ... }`

<!-- id: sec-components -->
### 2. 組件規格 (Component Specifications)

<!-- id: blk-components-desc, type: paragraph -->
[本區塊列出並定義了實現本 BP 所需的所有程式組件的介面與規格]

<!-- id: blk-component-spec-table, type: table -->
| 組件名稱 | 簡介 | 輸入 | 輸出 | 實作 Tasks | 技術驗收標準 |
|---------|------|------|------|-----------|-------------|
| [組件A] | [簡介] | [參數] | [返回值] | TASK-001 | [驗收標準] |
| [組件B] | [簡介] | [參數] | [返回值] | TASK-002 | [驗收標準] |

<!-- id: sec-processing-logic -->
### 3. 核心處理邏輯 (Core Processing Logic)

<!-- id: blk-processing-desc, type: paragraph -->
[詳細描述資料在系統中的流動與處理步驟，確保所有組件可以完善 requirement 需求]

<!-- id: blk-processing-steps, type: list -->
**處理流程**
  - **步驟 1**: [描述]
  - **步驟 2**: [描述]
  - **步驟 3**: [描述]

<!-- id: sec-risks-decisions -->
### 4. 風險、待辦事項與決策 (Risks, Open Questions & Decisions)

<!-- id: blk-adr-table, type: table -->
**設計決策記錄 (ADR)**
| 決策點 | 變更原因 | 最終實作選擇 | 記錄日期 |
|--------|----------|----------|----------|
| [例：資料持久化] | [資料結構複雜度] | Core Data | [YYYY-MM-DD] |

<!-- id: blk-risks-list, type: list -->
**風險與待辦**
  - **風險**: [潛在風險描述]
  - **待辦**: [未解決的問題]

<!-- id: sec-task-tracking -->
### 5. Task 拆解與追蹤 (Task Breakdown & Tracking)

<!-- id: blk-task-tracking-table, type: table -->
**實作進度追蹤**
| 組件名稱 | 對應 Tasks | 實作狀態 | 完成度 | 備註 |
|----------|------------|--------|--------|------|
| [組件A] | TASK-001, TASK-003 | Pending | 0% | |
| [組件B] | TASK-002 | Pending | 0% | |

<!-- id: blk-effort-estimate, type: list -->
**工時估算**
  - **預估總工時**: [X] 小時

<!-- id: sec-validation -->
### 6. 實作後驗證與總結 (Post-Implementation Validation)

<!-- id: blk-lessons-learned, type: list -->
**知識沉澱與教訓 (Lessons Learned)**
  - **設計負債與技術債務**: [需要重構的原因]
  - **低估與過度設計**: [哪些複雜度被低估，哪些組件是過度設計]
  - **可復用模式/組件**: [萃取成功經驗]
