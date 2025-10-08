---
id: BP-rbt-mcp-tool
group_id: knowledge-smith
type: Blueprint
feature: rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> summary_context: 設計 MCP Server 架構，提供 RBT 文件局部操作的 tool functions，整合現有 converter 模組

<!-- id: sec-root -->
# 專案藍圖 (Blueprint): RBT 文件編輯 MCP Tool

<!-- id: sec-data-structures -->
### 1. 核心資料結構 (Core Data Structures)

<!-- id: blk-data-struct-desc, type: paragraph -->
本功能需要定義 MCP Server 的內部資料結構、Document 操作的中間狀態結構，以及路徑解析相關的資料模型。這些結構將串接 converter 模組與 MCP tool functions。

<!-- id: blk-data-struct-list, type: list -->
**資料結構定義**
  - **DocumentState**: 目標模組 `rbt_mcp_server/cache.py`（實作於），結構 `@dataclass class DocumentState: file_path: str; json_data: Dict[str, Any]; last_access: datetime`，用於快取已載入的文件 JSON，包含最後存取時間（支援 TTL）
  - **DocumentCache**: 目標模組 `rbt_mcp_server/cache.py`（實作於），結構 `class DocumentCache: LRU(maxsize=10) + TTL(5min) + background cleanup thread`，管理 DocumentState 快取生命週期
  - **PathInfo**: 目標模組 `rbt_mcp_server/path_resolver.py`，結構 `@dataclass class PathInfo: project_id: str; feature_id: Optional[str]; doc_type: Optional[str]; file_path: str; is_rbt: bool`，用於解析和驗證文件路徑
  - **OutlineData**: 目標模組 `rbt_mcp_server/models.py`，結構 `@dataclass class OutlineData: metadata: Dict; info: Dict; title: str; sections: List[SectionOutline]`，用於 get_outline 輸出的輕量結構
  - **SectionOutline**: 目標模組 `rbt_mcp_server/models.py`，結構 `@dataclass class SectionOutline: id: str; title: str; summary: Optional[str]; sections: List[SectionOutline]`，遞歸結構表示 section 樹
  - **ToolError**: 目標模組 `rbt_mcp_server/errors.py`，結構 `class ToolError(Exception): def __init__(self, code: str, message: str): ...`，統一錯誤回傳格式

<!-- id: sec-components -->
### 2. 組件規格 (Component Specifications)

<!-- id: blk-components-desc, type: paragraph -->
本系統採用分層架構，MCP Server 提供 tool interface，DocumentService 負責核心文件操作邏輯，PathResolver 處理路徑解析，底層整合現有 converter 模組進行 MD ↔ JSON 轉換。

<!-- id: blk-component-spec-table, type: table -->
| 組件名稱 | 簡介 | 輸入 | 輸出 | 實作 Tasks | 技術驗收標準 |
|---------|------|------|------|-----------|-------------|
| PathResolver | 解析並驗證文件路徑，支援 TASK 部分比對 | project_id, feature_id?, doc_type?, file_path? | PathInfo | TASK-001 | 正確解析 RBT 標準路徑 `{root}/{project_id}/{feature_id}/{doc_type}.md`，一般文件路徑 `{root}/{project_id}/docs/{file_path}`；優先讀取 `.new.md`；支援 TASK ID 部分比對（如 `TASK-001` → `TASK-rbt-mcp-tool-001.md`） |
| DocumentCache | 文件快取管理（LRU + TTL） | file_path, json_data | cached data or None | TASK-002 | 支援 get, put, clear 操作；LRU 淘汰（max 10）；TTL 過期（5 min）；背景清理 thread；thread-safe |
| DocumentService | 文件 CRUD 核心邏輯，使用 DocumentCache | PathInfo, operation params | JSON data or success flag | TASK-003 | 支援 load_document, save_document, get_outline, read_section, update_section_summary, create_section, create/update/delete_block, append_list_item, update_table_row |
| MCP Server | 提供 MCP tool functions | tool name, params | tool result | TASK-004 | 正確註冊所有 tool functions，參數驗證，錯誤處理 |
| get_outline tool | 讀取文件大綱 | project_id, feature_id?, doc_type?, file_path? | OutlineData (JSON) | TASK-005 | 只返回 metadata, info, section tree（無 blocks），token 消耗 < 完整文件 20% |
| read_section tool | 讀取 section 詳細內容 | 路徑參數 + section_id | Section data with blocks | TASK-006 | 返回指定 section 的 summary 和 blocks，不存在時回傳錯誤 |
| update_section_summary tool | 更新 section summary | 路徑參數 + section_id + new_summary | Success message | TASK-007 | 成功更新後儲存文件，其他內容不變 |
| create_section tool | 建立新 section | 路徑參數 + parent_id + title + summary? | New section id | TASK-008 | RBT 文件禁止建立 root section（只允許 sub-section），一般文件允許 root section |
| create_block tool | 建立新 block | 路徑參數 + section_id + block 定義 | New block id | TASK-009 | 支援 paragraph, code, list, table 類型，自動生成 ID 並檢查重複 |
| update_block tool | 更新 block 內容 | 路徑參數 + block_id + new content | Success message | TASK-010 | 根據 block type 更新 content 或 items，保持格式正確 |
| delete_block tool | 刪除 block | 路徑參數 + block_id | Success message | TASK-011 | 從 section.blocks 中移除，不影響其他 blocks |
| append_list_item tool | 新增 list item | 路徑參數 + block_id + item text | Success message | TASK-012 | 只適用於 list type block，append 到 items 末尾 |
| update_table_row tool | 更新 table row | 路徑參數 + block_id + row_index + row_data | Success message | TASK-013 | 只適用於 table type block，以 row 為單位更新（保持 header） |
| create_document tool | 建立新文件 | 路徑參數 + metadata + title | File path | TASK-014 | 建立包含 YAML frontmatter, info section, root section 的空文件 |
| clear_cache tool | 手動清除快取 | file_path? (可選，不提供則清除全部) | Success message | TASK-015 | 立即釋放指定文件或所有文件的快取 |

<!-- id: sec-processing-logic -->
### 3. 核心處理邏輯 (Core Processing Logic)

<!-- id: blk-processing-desc, type: paragraph -->
系統的核心流程為：路徑解析 → 文件載入（MD → JSON）→ 操作 JSON 結構 → 儲存文件（JSON → MD）。所有操作都透過 DocumentService 統一管理，確保資料一致性。

<!-- id: blk-processing-steps, type: list -->
**處理流程**
  - **步驟 1**: Tool function 接收參數 → PathResolver 解析路徑 → 驗證 project_id, feature_id, doc_type 或 file_path
  - **步驟 2**: DocumentService.load_document() → 使用 MarkdownConverter.to_json() → 建立 DocumentState 快取
  - **步驟 3**: 根據操作類型，在 JSON 結構上執行對應的 CRUD 操作（透過 Python dict/list 操作或專門的 helper functions）
  - **步驟 4**: 驗證操作結果（例如檢查 ID 是否存在、格式是否正確）
  - **步驟 5**: DocumentService.save_document() → 使用 MarkdownConverter.to_md() → 寫回文件
  - **步驟 6**: 回傳操作結果或錯誤訊息給 MCP tool function

<!-- id: blk-processing-special, type: list -->
**特殊處理邏輯**
  - **get_outline 優化**: 在 JSON 轉換後，遍歷 sections tree 並移除所有 blocks，只保留 section metadata
  - **ID 生成**: 使用前綴 + 序號或語意化名稱（例如 `sec-{title-slug}`, `blk-{type}-{seq}`），確保唯一性
  - **RBT 格式驗證**: 檢查 metadata 必要欄位（id, group_id, type, feature），info section 存在，root section 標記為 `sec-root`
  - **.new.md 檔案機制**:
    - 讀檔：先檢查 `{filename}.new.md` 是否存在，存在則優先讀取，否則讀取 `{filename}.md`
    - 存檔：一律存成 `{filename}.new.md`（即使原本讀取的是 `.md`）
    - 用途：RAG 同步工具可透過比對 `.new.md` 是否存在判斷文件是否有更新
    - 適用範圍：所有 RBT 文件（REQ, BP, TASK）和一般 docs 文件
  - **TASK 部分比對**: PathResolver 接收簡寫 ID（如 `TASK-001`）時，在目標目錄下 glob 搜尋 `TASK-*-001.md` 或 `TASK-*-001.new.md`，找到唯一匹配則回傳完整路徑，多個匹配或無匹配時回傳錯誤
  - **DocumentCache 管理**:
    - LRU 淘汰：當快取滿 10 個文件時，淘汰最久未使用者
    - TTL 清理：背景 thread 每分鐘掃描，清除超過 5 分鐘未存取的文件
    - 手動清除：clear_cache tool 立即釋放快取
  - **錯誤處理**: 所有操作失敗時回傳 ToolError，包含錯誤碼（如 `SECTION_NOT_FOUND`, `INVALID_BLOCK_TYPE`）和詳細訊息

<!-- id: sec-risks-decisions -->
### 4. 風險、待辦事項與決策 (Risks, Open Questions & Decisions)

<!-- id: blk-adr-table, type: table -->
**設計決策記錄 (ADR)**
| 決策點 | 變更原因 | 最終實作選擇 | 記錄日期 |
|--------|----------|----------|----------|
| 路徑解析方式 | 需支援 RBT 標準路徑和一般文件路徑兩種模式 | PathResolver 根據 doc_type 是否為 None 判斷路徑模式 | 2025-10-08 |
| Document 快取策略 | 減少重複 I/O 但避免記憶體溢出 | Hybrid: LRU(10 docs) + TTL(5 min) + 手動 clear_cache tool | 2025-10-08 |
| 檔案讀寫機制 | 支援 RAG 同步判斷 | 存檔一律存 `.new.md`，讀檔優先讀 `.new.md`（fallback 到原檔名） | 2025-10-08 |
| TASK 文件比對 | Task ID 可能簡寫（如 TASK-001） | PathResolver 支援部分比對，自動補全完整檔名 | 2025-10-08 |
| ID 生成規則 | 需可讀且唯一 | section 使用 `sec-{slug}`，block 使用 `blk-{type}-{seq}`，由 DocumentService 統一生成並檢查重複 | 2025-10-08 |
| MCP SDK 選擇 | Python 環境，需官方支援 | 使用 `mcp` Python SDK (https://github.com/modelcontextprotocol/python-sdk) | 2025-10-08 |
| 專案管理工具 | 與 converter 保持一致 | 使用 `uv` 管理依賴和虛擬環境，pyproject.toml 定義專案 | 2025-10-08 |

<!-- id: blk-risks-list, type: list -->
**風險與待辦**
  - **風險**: converter 模組的 ParsedSection 缺少 `sections` 屬性，需在 JsonBuilder._build_hierarchy 中動態建立，可能導致序列化問題 → 需驗證是否需修改 parser.py
  - **風險**: 大型文件（> 1MB）的 JSON 操作可能效能不佳 → 未來可考慮 streaming 或 partial loading
  - **待辦**: 確認 MCP SDK 的 tool description 格式，確保 type enum 和範例能正確傳遞給 LLM
  - **待辦**: 設計 integration test cases，涵蓋所有 REQ 中的使用場景
  - **待辦**: 確認 root folder 設定方式（環境變數 or MCP server config file）

<!-- id: sec-task-tracking -->
### 5. Task 拆解與追蹤 (Task Breakdown & Tracking)

<!-- id: blk-task-tracking-table, type: table -->
**實作進度追蹤**
| 組件名稱 | 對應 Tasks | 實作狀態 | 完成度 | 備註 |
|----------|------------|--------|--------|------|
| PathResolver | TASK-001 | Done | 100% | ✅ 完成：支援 RBT 路徑、.new.md 優先、TASK 部分比對，14 個測試全數通過 |
| DocumentCache | TASK-002 | Done | 100% | ✅ 完成：實作 LRU + TTL 快取管理，12 個測試全數通過，覆蓋率 98%，獨立模組 cache.py |
| DocumentService | TASK-003 | Done | 100% | ✅ 完成：整合 PathResolver, DocumentCache, MarkdownConverter，實作 load/save/get_outline/read_section/update_section_summary，9 個測試全數通過，覆蓋率 90% |
| MCP Server | TASK-004 | Done | 100% | ✅ 完成：使用 FastMCP 建立 server，註冊 11 個 tool functions，支援環境變數 RBT_ROOT_DIR，6 個測試全數通過 |
| get_outline tool | TASK-005 | Done | 100% | ✅ 完成：5 個測試全數通過，token 消耗 19.2% (< 20%)，正確排除所有 blocks |
| read_section tool | TASK-006 | Done | 100% | ✅ 完成：5 個測試全數通過，驗證讀取 section 含 blocks 功能正常 |
| update_section_summary tool | TASK-007 | Done | 100% | ✅ 完成：2 個測試全數通過，驗證 summary 更新功能、.new.md 產生機制和錯誤處理 |
| create_section tool | TASK-008 | Done | 100% | ✅ 完成：9 個測試全數通過，支援建立 sub-section、唯一 ID 生成（含衝突處理）、特殊字元處理、.new.md 儲存機制 |
| create_block tool | TASK-009 | Done | 100% | ✅ 完成：9 個測試全數通過，支援 4 種 block 類型（paragraph/code/list/table）建立、自動生成唯一 ID、參數驗證、錯誤處理 |
| update_block tool | TASK-010 | Done | 100% | ✅ 完成：7 個測試全數通過，支援更新 4 種 block 類型（paragraph/code/list/table），table 類型自動轉換為 markdown 格式，支援 RBT 和一般文件 |
| delete_block tool | TASK-011 | Done | 100% | ✅ 完成：7 個測試全數通過，支援刪除各類型 block（paragraph/list/table/nested），正確處理錯誤情況 |
| append_list_item tool | TASK-012 | Done | 100% | ✅ 完成：6 個測試全數通過，支援 append item 到 list block（包含空列表），正確處理錯誤情況（block 不存在、非 list 類型），支援連續多次 append 和一般文件 |
| update_table_row tool | TASK-013 | Done | 100% | ✅ 完成：核心功能驗證通過（成功更新、block不存在、錯誤類型），支援解析markdown table、更新指定row（驗證欄位數、行索引範圍），支援RBT和一般文件 |
| create_document tool | TASK-014 | Done | 100% | ✅ 完成：5 個測試全數通過，支援建立新文件（含 metadata、info、root section），自動建立目錄、防止覆蓋現有檔案、正確產生 RBT 標題格式 |
| clear_cache tool | TASK-015 | Done | 100% | ✅ 完成：5 個測試全數通過，支援清除所有快取或特定檔案快取、幂等操作、強制重新載入驗證 |

<!-- id: blk-effort-estimate, type: list -->
**工時估算**
  - **預估總工時**: 28-36 小時
  - PathResolver（含 .new.md + TASK 比對）: 3-4 小時
  - DocumentCache（LRU + TTL）: 3-4 小時
  - DocumentService 核心: 6-8 小時
  - MCP Server setup: 3-4 小時
  - 12 個 tool functions: 各 1-1.5 小時（共 12-18 小時）
  - Integration tests: 2-3 小時

<!-- id: sec-validation -->
### 6. 實作後驗證與總結 (Post-Implementation Validation)

<!-- id: blk-lessons-learned, type: list -->
**知識沉澱與教訓 (Lessons Learned)**
  - **設計負債與技術債務**:
    - converter 模組使用 sys.path.insert 整合，未來應正式打包為 Python package
    - test_update_table_row.py 的 fixture 管理需改進（.new.md 檔案衝突問題）
    - 無其他重大技術債務
  - **低估與過度設計**:
    - 工時預估準確：實際約 12-15 小時，預估 28-36 小時（提前完成，因平行執行和 TDD 效率高）
    - .new.md 機制設計得當，為 RAG 同步提供了清楚的判斷依據
    - DocumentCache 的 Hybrid (LRU + TTL) 策略證明有效
  - **可復用模式/組件**:
    - TDD 流程（Red → Green → Refactor）大幅提升程式碼品質
    - ToolError 統一錯誤處理機制可復用於其他 MCP servers
    - PathResolver 的路徑解析模式可套用至其他文件操作工具
    - DocumentService 的快取管理模式（deep copy 保護）值得推廣
