---
id: TASK-003-DocumentService
group_id: knowledge-smith
type: Task
title: 實作 DocumentService 文件 CRUD 核心邏輯
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-001-PathResolver, TASK-002-DocumentCache]

<!-- id: sec-root -->
# Task: 實作 DocumentService 文件 CRUD 核心邏輯

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置 (Goal & Dependencies)

<!-- id: blk-goal, type: list -->
**目標 (Goal)**
  - 實作 DocumentService 類別，提供文件載入、儲存、讀取、更新的核心邏輯
  - 整合 PathResolver 和 DocumentCache
  - 整合現有 converter 模組（MarkdownConverter）
  - 實作 `.new.md` 存檔機制
  - 提供 get_outline, read_section, update_section_summary 等基礎操作

<!-- id: blk-dependencies, type: list -->
**前置任務 (Dependencies)**
  - TASK-001-PathResolver（路徑解析）
  - TASK-002-DocumentCache（快取管理）

<!-- id: blk-target-modules, type: list -->
**目標模組/檔案**
  - 新檔案：`rbt_mcp_server/document_service.py`
  - 新檔案：`rbt_mcp_server/errors.py`（ToolError 例外類別）
  - 新檔案：`tests/test_document_service.py`（TDD 測試先行）
  - 整合：`converter/converter.py`（已存在）

<!-- id: sec-change-history -->
### 2. 變更記錄與風險 (Change History & Risks)

<!-- id: blk-change-history-table, type: table -->
**變更歷史追溯**
| 版本 | 變更原因 | 影響範圍 | 重新實作日期 |
|---|---|---|---|
| v1.0 | 初始版本 | N/A | 2025-10-08 |

<!-- id: blk-risks, type: list -->
**風險與關注點**
  - **上次實作定位**: N/A（新功能）
  - **重點關注**:
    - converter 模組的 ParsedSection 缺少 `sections` 屬性，需在運行時動態建立
    - 存檔失敗時需確保原文件不被破壞（先寫 .tmp，成功後 rename）
    - JSON 操作需深拷貝，避免修改快取中的原始資料

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (Implementation Guide & Test Specifications)

<!-- id: blk-implementation-steps, type: list -->
**實作指引 (Implementation Guide) - TDD 流程**
  - **步驟 0 (TDD Red)**: 先在 `tests/test_document_service.py` 寫測試案例
  - **步驟 1**: 在 `rbt_mcp_server/errors.py` 定義 `ToolError` 例外
    ```python
    class ToolError(Exception):
        def __init__(self, code: str, message: str):
            self.code = code
            self.message = message
            super().__init__(f"[{code}] {message}")
    ```
  - **步驟 2**: 實作 `DocumentService` 類別
    - `__init__(self, root_dir: str)`: 初始化 PathResolver, DocumentCache, MarkdownConverter
    - `load_document(self, path_info: PathInfo) -> Dict[str, Any]`: 載入文件 JSON（優先快取）
    - `save_document(self, path_info: PathInfo, json_data: Dict[str, Any])`: 存檔為 `.new.md`
    - `get_outline(self, path_info: PathInfo) -> Dict[str, Any]`: 回傳輕量大綱（移除 blocks）
    - `read_section(self, path_info: PathInfo, section_id: str) -> Dict[str, Any]`: 讀取指定 section
    - `update_section_summary(self, path_info: PathInfo, section_id: str, new_summary: str)`: 更新 summary
    - `clear_cache(self, file_path: Optional[str] = None)`: 清除快取
  - **步驟 3**: 實作 `load_document`
    - 先嘗試從快取取得 → 命中則直接回傳（deep copy）
    - 快取未命中 → 透過 PathResolver 取得實際檔案路徑（優先 .new.md）
    - 讀取檔案 → 使用 MarkdownConverter.to_json() 轉換
    - 存入快取 → 回傳 JSON（deep copy）
  - **步驟 4**: 實作 `save_document`
    - 接收 json_data → 使用 MarkdownConverter.to_md() 轉換
    - 計算目標路徑：移除原路徑的 `.new.md` 或 `.md`，加上 `.new.md`
    - 先寫入 `.tmp` 檔案 → 成功後 rename 為 `.new.md`（原子操作）
    - 更新快取
  - **步驟 5**: 實作 `get_outline`
    - 載入完整 JSON → deep copy
    - 遞歸遍歷 sections tree，移除所有 `blocks` 欄位
    - 回傳輕量 JSON
  - **步驟 6**: 實作 `read_section` 和 `update_section_summary`
    - 載入 JSON → 遞歸搜尋 section_id
    - 找不到 → raise ToolError("SECTION_NOT_FOUND", ...)
    - update 時：修改 JSON → save_document
  - **步驟 7 (TDD Green)**: 執行測試，確保所有測試通過
  - **步驟 8 (TDD Refactor)**: 重構代碼

<!-- id: blk-test-spec, type: list -->
**測試規格 (Test Specifications) - TDD**
  - **Test Case 1**: 載入文件（無快取）
    - **Given**: 存在 REQ-test.md
    - **When**: load_document(path_info)
    - **Then**: 回傳正確的 JSON，快取中存在該文件
  - **Test Case 2**: 載入文件（命中快取）
    - **Given**: 快取中已有 REQ-test.md
    - **When**: load_document(path_info)
    - **Then**: 從快取回傳，不讀取檔案
  - **Test Case 3**: 優先讀取 .new.md
    - **Given**: 存在 REQ-test.md 和 REQ-test.new.md
    - **When**: load_document(path_info)
    - **Then**: 載入 .new.md 版本
  - **Test Case 4**: 存檔為 .new.md
    - **Given**: 載入 REQ-test.md，修改 JSON
    - **When**: save_document(path_info, modified_json)
    - **Then**: 產生 REQ-test.new.md，原檔案不變
  - **Test Case 5**: get_outline 移除 blocks
    - **Given**: 完整 JSON 包含多個 sections 和 blocks
    - **When**: get_outline(path_info)
    - **Then**: 回傳 JSON 不包含任何 blocks，但 sections tree 完整
  - **Test Case 6**: read_section 成功
    - **Given**: 文件包含 section_id="sec-goal"
    - **When**: read_section(path_info, "sec-goal")
    - **Then**: 回傳該 section 的完整資料（含 blocks）
  - **Test Case 7**: read_section 找不到
    - **Given**: 文件不包含 section_id="sec-notexist"
    - **When**: read_section(path_info, "sec-notexist")
    - **Then**: raise ToolError("SECTION_NOT_FOUND", ...)
  - **Test Case 8**: update_section_summary 成功
    - **Given**: section_id="sec-goal" 存在
    - **When**: update_section_summary(path_info, "sec-goal", "new summary")
    - **Then**: .new.md 中該 section 的 summary 被更新

<!-- id: sec-completion -->
### 4. 實作完成記錄 (Implementation Completion)

<!-- id: blk-execution-summary, type: list -->
**執行摘要與產出**
  - **實際耗時**: 約 2 小時 (預估: 6-8小時)
  - **執行狀態**: ✅ 完成
  - **關鍵產出**:
    - 新增 `rbt_mcp_server/errors.py`: ToolError 例外類別 (32 行)
    - 新增 `rbt_mcp_server/document_service.py`: DocumentService 核心邏輯 (308 行)
    - 新增 `tests/test_document_service.py`: 9 個測試案例全數通過 (314 行)
    - 修改 `pyproject.toml`: 新增 PyYAML 依賴
  - **程式碼變更統計**:
    - 新增檔案: 3 個
    - 新增程式碼: 654 行
    - 測試覆蓋率: 90% (document_service.py)
    - 測試通過率: 100% (9/9 測試通過)

<!-- id: blk-problems-table, type: table -->
**問題與解決記錄**
| 問題描述 | 解決方案 | 耗時 | 可預防? |
|----------|----------|------|---------|
| converter 模組缺少 PyYAML 依賴 | 在 pyproject.toml 新增 PyYAML>=6.0.0 依賴 | 5分鐘 | ✅ (應在專案初期確認所有依賴) |
| converter 模組 import 路徑問題 | 使用 sys.path.insert 將 converter 目錄加入 Python path | 10分鐘 | ✅ (可使用 setup.py 或 pyproject.toml 正確設定套件結構) |
| update_section_summary 測試失敗 | 更新後需從 .new.md 讀取，修正測試使用新的 PathInfo | 5分鐘 | ✅ (測試設計時應考慮 .new.md 機制) |

<!-- id: blk-technical-debt, type: list -->
**技術債務與重構建議**
  - **技術債務**:
    - converter 模組未正式整合為 Python package，目前使用 sys.path.insert 作為臨時方案
    - converter 模組應該有自己的 pyproject.toml 並作為正式依賴安裝
  - **重構建議**:
    - 考慮將 converter 發布為獨立套件或使用 editable install
    - 可以為 DocumentService 增加更多錯誤處理 (如 JSON 結構驗證)
    - 考慮增加 section 操作的 helper methods (如 find_section_by_path)
  - **程式碼定位指令**: `grep -r "@TASK: TASK-003" rbt_mcp_server/`
  - **關鍵檔案清單**:
    - `/Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/errors.py`
    - `/Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/document_service.py`
    - `/Users/devinlai/Develope/KnowledgeSmith/tests/test_document_service.py`
