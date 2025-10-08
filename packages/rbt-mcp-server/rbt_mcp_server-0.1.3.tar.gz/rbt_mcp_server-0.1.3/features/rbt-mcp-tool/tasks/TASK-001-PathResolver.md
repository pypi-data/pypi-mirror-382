---
id: TASK-001-PathResolver
group_id: knowledge-smith
type: Task
title: 實作 PathResolver 路徑解析與驗證
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: []

<!-- id: sec-root -->
# Task: 實作 PathResolver 路徑解析與驗證

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置 (Goal & Dependencies)

<!-- id: blk-goal, type: list -->
**目標 (Goal)**
  - 實作 PathResolver 類別，支援 RBT 標準路徑和一般文件路徑解析
  - 支援 `.new.md` 優先讀取機制
  - 支援 TASK ID 部分比對（如 `TASK-001` → `TASK-001-PathResolver.md`）
  - 驗證路徑合法性並回傳 PathInfo 結構

<!-- id: blk-dependencies, type: list -->
**前置任務 (Dependencies)**
  - 無（基礎組件）

<!-- id: blk-target-modules, type: list -->
**目標模組/檔案**
  - 新檔案：`rbt_mcp_server/path_resolver.py`
  - 新檔案：`rbt_mcp_server/models.py`（PathInfo dataclass）
  - 新檔案：`tests/test_path_resolver.py`（TDD 測試先行）

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
    - glob 搜尋可能匹配多個文件，需明確錯誤訊息
    - `.new.md` 和原檔案可能同時存在，需正確優先順序
    - TASK ID 簡寫比對在 `features/{feature_id}/tasks/` 目錄下搜尋

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (Implementation Guide & Test Specifications)

<!-- id: blk-implementation-steps, type: list -->
**實作指引 (Implementation Guide) - TDD 流程**
  - **步驟 0 (TDD Red)**: 先在 `tests/test_path_resolver.py` 寫測試案例，確保測試失敗
  - **步驟 1**: 在 `rbt_mcp_server/models.py` 定義 `PathInfo` dataclass
    ```python
    @dataclass
    class PathInfo:
        project_id: str
        feature_id: Optional[str]
        doc_type: Optional[str]  # REQ, BP, TASK
        file_path: str  # 完整絕對路徑
        is_rbt: bool  # True=RBT標準文件, False=一般文件
        is_new_file: bool  # True=讀取到.new.md版本
    ```
  - **步驟 2**: 在 `rbt_mcp_server/path_resolver.py` 實作 `PathResolver` 類別
    - `__init__(self, root_dir: str)`: 儲存 root 目錄路徑
    - `resolve(self, project_id: str, feature_id: Optional[str] = None, doc_type: Optional[str] = None, file_path: Optional[str] = None) -> PathInfo`: 核心解析方法
  - **步驟 3**: 實作路徑解析邏輯
    - 如果 `doc_type` 存在：
      - `doc_type == "TASK"` → `{root}/{project_id}/features/{feature_id}/tasks/TASK-{index}-{name}.md`
      - 其他 RBT 類型 → `{root}/{project_id}/features/{feature_id}/{doc_type}-{feature_id}.md`
    - 如果 `file_path` 存在 → 一般文件路徑：`{root}/{project_id}/docs/{file_path}`
    - 檢查 `.new.md` 是否存在，存在則優先使用
  - **步驟 4**: 實作 TASK 部分比對
    - 如果 `doc_type == "TASK"` 且 `feature_id` 為簡寫（如 `001` 或 `TASK-001`），使用 glob 搜尋 `{root}/{project_id}/features/*/tasks/TASK-{index}-*.md` 或 `.new.md`
    - 找到唯一匹配 → 回傳完整路徑
    - 找到多個匹配 → raise `ValueError("Ambiguous TASK ID")`
    - 找不到 → raise `FileNotFoundError`
  - **步驟 5 (TDD Green)**: 執行測試，確保所有測試通過
  - **步驟 6 (TDD Refactor)**: 重構代碼，保持測試通過

<!-- id: blk-test-spec, type: list -->
**測試規格 (Test Specifications) - TDD**
  - **Test Case 1**: 解析 RBT REQ 文件路徑
    - **Given**: root="/tmp/docs", project_id="knowledge-smith", feature_id="rbt-mcp-tool", doc_type="REQ"
    - **When**: 呼叫 `resolver.resolve(project_id, feature_id, doc_type)`
    - **Then**: 回傳 PathInfo，file_path="/tmp/docs/knowledge-smith/features/rbt-mcp-tool/REQ-rbt-mcp-tool.md", is_rbt=True
  - **Test Case 2**: 解析 TASK 文件路徑（完整 feature_id）
    - **Given**: root="/tmp/docs", project_id="knowledge-smith", feature_id="rbt-mcp-tool", doc_type="TASK", task_name="001-PathResolver"
    - **When**: 呼叫 `resolver.resolve(project_id, feature_id, doc_type, file_path="001-PathResolver")`
    - **Then**: 回傳 PathInfo，file_path="/tmp/docs/knowledge-smith/features/rbt-mcp-tool/tasks/TASK-001-PathResolver.md", is_rbt=True
  - **Test Case 3**: 解析一般文件路徑
    - **Given**: root="/tmp/docs", project_id="knowledge-smith", file_path="governance/rules.md"
    - **When**: 呼叫 `resolver.resolve(project_id, file_path=file_path)`
    - **Then**: 回傳 PathInfo，file_path="/tmp/docs/knowledge-smith/docs/governance/rules.md", is_rbt=False
  - **Test Case 4**: 優先讀取 .new.md
    - **Given**: 存在 REQ-rbt-mcp-tool.md 和 REQ-rbt-mcp-tool.new.md
    - **When**: 呼叫 `resolver.resolve(...)` 解析 REQ
    - **Then**: 回傳 PathInfo，file_path 指向 .new.md，is_new_file=True
  - **Test Case 5**: TASK 部分比對成功
    - **Given**: 存在 features/rbt-mcp-tool/tasks/TASK-001-PathResolver.md
    - **When**: 呼叫 `resolver.resolve(project_id="knowledge-smith", feature_id="001", doc_type="TASK")`
    - **Then**: 回傳 PathInfo，file_path 指向完整檔名
  - **Test Case 6**: TASK 部分比對歧義錯誤
    - **Given**: 存在多個 TASK-001-*.md 在不同 feature 下
    - **When**: 呼叫 `resolver.resolve(project_id="test", feature_id="001", doc_type="TASK")`
    - **Then**: raise ValueError("Ambiguous TASK ID: found 2 matches")
  - **Test Case 7**: 檔案不存在錯誤
    - **Given**: 不存在任何 REQ-nonexistent.md
    - **When**: 呼叫 `resolver.resolve(...)`
    - **Then**: raise FileNotFoundError

<!-- id: sec-completion -->
### 4. 實作完成記錄 (Implementation Completion)

<!-- id: blk-execution-summary, type: list -->
**執行摘要與產出**
  - **實際耗時**: 2小時 (預估: 3-4小時)
  - **執行狀態**: ✅ 完成
  - **關鍵產出**:
    - PathInfo dataclass (rbt_mcp_server/models.py)
    - PathResolver 類別 (rbt_mcp_server/path_resolver.py)
    - 完整測試套件 (tests/test_path_resolver.py) - 14個測試案例全數通過
    - 專案結構 (pyproject.toml, __init__.py)
  - **程式碼變更統計**:
    - 新增 5 個檔案
    - 約 400 行程式碼（含測試）
    - 測試覆蓋率：100%（所有核心功能都有測試）

<!-- id: blk-problems-table, type: table -->
**問題與解決記錄**
| 問題描述 | 解決方案 | 耗時 | 可預防? |
|----------|----------|------|---------|
| Python 測試環境設定（系統 Python 受保護） | 建立虛擬環境 (.venv) 並在其中安裝 pytest | 10分鐘 | ✅ |
| .new.md 檔案處理邏輯需同時考慮 .md 和非 .md 檔案 | 在 _check_new_md_version 中加入判斷，根據檔案副檔名決定 .new 版本路徑 | 15分鐘 | ✅ |

<!-- id: blk-technical-debt, type: list -->
**技術債務與重構建議**
  - **技術債務**: 無
  - **重構建議**:
    - 未來若需支援更多文件類型，可考慮將路徑解析規則抽取為可設定的 strategy pattern
    - glob 搜尋效能在大型專案可能較慢，未來可考慮建立檔案索引
  - **程式碼定位指令**: `grep -r "@TASK: TASK-001-PathResolver" rbt_mcp_server/`
  - **關鍵檔案清單**:
    - /Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/models.py
    - /Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/path_resolver.py
    - /Users/devinlai/Develope/KnowledgeSmith/tests/test_path_resolver.py
    - /Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/__init__.py
    - /Users/devinlai/Develope/KnowledgeSmith/pyproject.toml
