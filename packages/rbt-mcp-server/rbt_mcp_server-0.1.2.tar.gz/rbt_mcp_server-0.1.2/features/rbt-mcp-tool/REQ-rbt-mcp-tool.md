---
id: REQ-rbt-mcp-tool
group_id: knowledge-smith
type: Requirement
feature: rbt-mcp-tool
---

<!-- info-section -->
> status: Finalized
> update_date: 2025-10-08
> summary_context: 建立 MCP Tool 協助 LLM 編輯 RBT 文件，透過局部讀寫降低 token 消耗

<!-- id: sec-root -->
# 需求文件 (Requirement): RBT 文件編輯 MCP Tool

<!-- id: sec-goal-context -->
### 1. 核心目標與背景 (Goal & Context)

<!-- id: blk-goal, type: list -->
**目標 (Goal)**
  - 建立一個 MCP Tool 協助 LLM Agent 編輯 RBT 格式文件，透過結構化的局部讀寫操作大幅降低 token 消耗

<!-- id: blk-user-story, type: list -->
**使用者故事 (User Story)**
  - 身為一個 LLM Agent，我想要透過 MCP 工具編輯 RBT JSON 文件的局部內容，以便減少每次都需要讀取/傳輸完整文件的 token 消耗
  - 身為一個開發者，我想要 LLM 可以精準更新文件特定區塊，以便避免全文重寫導致的錯誤和資源浪費

<!-- id: blk-context-desc, type: list -->
**背景說明**
  - 現有 `converter/` 模組已實作 MD ↔ JSON 雙向轉換
  - RBT 文件採用結構化設計（metadata, info, sections, blocks），所有元素都有唯一 ID
  - 目前痛點：LLM 更新文件時必須讀取完整內容並全文重寫，造成大量 token 浪費
  - 專案採用多專案架構，文件路徑遵循 `{root}/{project_id}/{feature_id}/{doc_type}.md` 或 `{root}/{project_id}/docs/{file_path}` 規範

<!-- id: sec-functional-scope -->
### 2. 功能與邊界定義 (Functional Scope)

<!-- id: blk-func-req-list, type: list -->
**功能規格 (Functional Requirements)**
  - **階層式讀取**：支援只讀取文件大綱（outline）或特定 section 詳細內容
  - **精準更新**：透過 ID 定位並更新 info、section summary、block 內容
  - **Block CRUD**：支援新增、更新、刪除 block（paragraph, code, list, table）
  - **List 操作**：支援 list block 的 item 新增
  - **Table 操作**：支援 table block 的 row 新增和更新（以 row 為單位）
  - **Section 管理**：支援新增 sub-section（一般文件或 RBT sub-section）
  - **文件建立**：支援建立新文件並寫入 metadata
  - **多專案支援**：透過 project_id 區隔不同專案，root folder 由 MCP config 設定
  - **路徑規範**：RBT 標準文件自動對應路徑，一般文件放在 docs/ 資料夾
  - **快取管理**：支援手動清除文件快取（clear_cache），優化記憶體使用
  - **.new.md 機制**：所有文件存檔一律存成 `.new.md`，讀檔優先讀 `.new.md`（支援 RAG 同步判斷）
  - **TASK 部分比對**：支援簡寫 TASK ID（如 `TASK-001`），自動補全完整檔名

<!-- id: blk-out-of-scope-list, type: list -->
**範圍外 (Out of Scope)**
  - Metadata 更新（metadata 只在建立文件時設定，後續不可更改）
  - RBT 文件的 head-section 新增（只能新增 sub-section）
  - Section/Block title 更新（title 由 template 定義）
  - 文件刪除功能
  - 版本控制與歷史記錄
  - 文件驗證與 linting
  - 跨文件操作（例如複製 section 到另一文件）

<!-- id: sec-non-functional -->
### 3. 非功能規格與限制 (Non-Functional Requirements & Constraints)

<!-- id: blk-non-func-req-list, type: list -->
**非功能規格 (Non-Functional Requirements)**
  - **效能**: 讀取 outline 的回應時間 < 1 秒（針對正常大小的文件 < 500KB）；快取機制採用 Hybrid (LRU + TTL) 策略減少重複 I/O
  - **可靠性**: 更新操作失敗時不破壞原文件，提供明確錯誤訊息
  - **易用性**: Tool description 包含清楚的參數說明、type enum、使用範例
  - **安全性**: ID 重複檢查，防止覆蓋現有內容
  - **記憶體管理**: 快取最多 10 個文件，超過 5 分鐘未存取自動釋放

<!-- id: blk-tech-constraints-list, type: list -->
**技術限制**
  - 依賴現有 `converter/` 模組（parser, builder, generator）
  - Python 3.8+ 環境
  - 使用 `uv` 管理 Python 依賴和虛擬環境（與 converter 保持一致的開發工具鏈）
  - MCP SDK 需支援 Python
  - 文件必須符合 RBT 格式規範（YAML frontmatter + info section + structured content）
  - Root folder 路徑由 MCP server 啟動參數設定，不可由 LLM 變更

<!-- id: sec-use-cases -->
### 4. 使用場景與驗收標準 (Use Cases & Acceptance)

<!-- id: blk-use-cases-list, type: list -->
**使用場景 (Use Cases)**
  - LLM 需要更新某個 section 的 summary，先用 `get_outline` 取得結構，再用 `update_section_summary` 精準更新
  - LLM 需要在 REQ 文件中新增一個 use case 項目，用 `append_list_item` 直接新增到 list block
  - LLM 需要更新 BP 文件中的某個 table row（例如 API 規格表），用 `update_table_row` 更新該列
  - LLM 需要建立新的 feature REQ 文件，用 `create_document` 建立並設定 metadata
  - 開發者需要在 governance 文件新增一個 sub-section，用 `create_section` 在指定 parent 下新增

<!-- id: blk-acceptance-list, type: list -->
**驗收標準 (Acceptance Criteria)**
  - 專案使用 `uv` 設置，包含 `pyproject.toml` 和正確的依賴定義，可透過 `uv run` 啟動 MCP server
  - `get_outline` 只回傳 metadata + info + section tree（不含 block 詳細內容），token 消耗 < 完整文件的 20%
  - `read_section` 正確回傳指定 section 的 summary 和 blocks 詳細內容
  - `update_section_summary` 成功更新 summary，原文件其他內容不變
  - `append_list_item` 成功新增 item 到指定 list block 末尾
  - `update_table_row` 成功更新指定 row，保持 table 格式正確
  - `create_section` 在 RBT 文件中嘗試新增 root section 時回傳錯誤（只允許 sub-section）
  - `create_document` 建立的文件包含正確的 YAML frontmatter 和基本結構
  - 所有更新操作在 ID 不存在時回傳明確錯誤訊息（例如 "Section 'SEC-XXX' not found"）
  - 路徑解析正確：RBT 文件對應 `{root}/{project_id}/{feature_id}/{doc_type}.md`，一般文件對應 `{root}/{project_id}/docs/{file_path}`；優先讀取 `.new.md`
  - 所有存檔操作一律存成 `.new.md` 檔案
  - `clear_cache` 可成功清除指定文件或全部快取
  - TASK ID 部分比對正確：輸入 `TASK-001` 可正確找到 `TASK-rbt-mcp-tool-001.md` 或 `TASK-rbt-mcp-tool-001.new.md`
  - Tool description 包含完整的 type enum 和使用範例，LLM 可正確理解如何呼叫
