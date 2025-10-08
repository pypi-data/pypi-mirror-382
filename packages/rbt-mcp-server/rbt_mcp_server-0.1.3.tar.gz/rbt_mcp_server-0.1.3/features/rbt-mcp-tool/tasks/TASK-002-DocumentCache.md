---
id: TASK-002-DocumentCache
group_id: knowledge-smith
type: Task
title: 實作 DocumentCache 快取管理（Hybrid LRU + TTL）
blueprint: BP-rbt-mcp-tool
requirement: REQ-rbt-mcp-tool
---

<!-- info-section -->
> status: Done
> update_date: 2025-10-08
> dependencies: [TASK-001-PathResolver]

<!-- id: sec-root -->
# Task: 實作 DocumentCache 快取管理（Hybrid LRU + TTL）

<!-- id: sec-goal-dependencies -->
### 1. 任務目標與前置 (Goal & Dependencies)

<!-- id: blk-goal, type: list -->
**目標 (Goal)**
  - 實作 DocumentCache 類別，管理文件 JSON 快取的生命週期
  - 支援 LRU（最多 10 個文件）淘汰策略
  - 支援 TTL（5 分鐘）過期策略
  - 支援手動清除快取（單一文件或全部）
  - 背景 thread 定期清理過期快取

<!-- id: blk-dependencies, type: list -->
**前置任務 (Dependencies)**
  - TASK-001-PathResolver（需要 PathInfo 判斷快取 key）

<!-- id: blk-target-modules, type: list -->
**目標模組/檔案**
  - 新檔案：`rbt_mcp_server/cache.py`（DocumentState, DocumentCache）
  - 新檔案：`tests/test_cache.py`（TDD 測試先行）

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
    - Thread safety：多個 tool 同時存取快取需要 lock
    - Background thread 生命週期管理（啟動、停止、清理）
    - TTL 計算需考慮時區問題（統一使用 UTC）

<!-- id: sec-implementation -->
### 3. 實作指引與測試規格 (Implementation Guide & Test Specifications)

<!-- id: blk-implementation-steps, type: list -->
**實作指引 (Implementation Guide) - TDD 流程**
  - **步驟 0 (TDD Red)**: 先在 `tests/test_cache.py` 寫測試案例
  - **步驟 1**: 在 `rbt_mcp_server/cache.py` 定義 `DocumentState` dataclass
    ```python
    @dataclass
    class DocumentState:
        file_path: str
        json_data: Dict[str, Any]
        last_access: datetime  # UTC
    ```
  - **步驟 2**: 實作 `DocumentCache` 類別
    - `__init__(self, max_size: int = 10, ttl_seconds: int = 300)`: 初始化參數
    - `_cache: OrderedDict[str, DocumentState]`: 使用 OrderedDict 實作 LRU
    - `_lock: threading.Lock`: 確保 thread safety
    - `_cleanup_thread: threading.Thread`: 背景清理 thread
    - `_stop_event: threading.Event`: 停止信號
  - **步驟 3**: 實作核心方法
    - `get(self, file_path: str) -> Optional[Dict[str, Any]]`: 取得快取，更新 last_access
    - `put(self, file_path: str, json_data: Dict[str, Any])`: 新增/更新快取，檢查 LRU 淘汰
    - `clear(self, file_path: Optional[str] = None)`: 清除指定或全部快取
    - `_cleanup_expired(self)`: 清除過期項目（TTL 檢查）
    - `_cleanup_loop(self)`: 背景 thread 每分鐘執行 _cleanup_expired
    - `start(self)`: 啟動背景 thread
    - `stop(self)`: 停止背景 thread
  - **步驟 4**: 實作 LRU 淘汰邏輯
    - 當快取滿（超過 max_size）時，移除 OrderedDict 的第一個項目（最久未使用）
    - 使用 `move_to_end(key)` 更新存取順序
  - **步驟 5 (TDD Green)**: 執行測試，確保所有測試通過
  - **步驟 6 (TDD Refactor)**: 重構代碼

<!-- id: blk-test-spec, type: list -->
**測試規格 (Test Specifications) - TDD**
  - **Test Case 1**: 基本快取存取
    - **Given**: 空的 DocumentCache
    - **When**: put("file1.md", data1)，然後 get("file1.md")
    - **Then**: 回傳 data1
  - **Test Case 2**: LRU 淘汰策略
    - **Given**: max_size=3 的 DocumentCache，已存入 3 個文件
    - **When**: put 第 4 個文件
    - **Then**: 第 1 個文件被淘汰，get 第 1 個文件回傳 None
  - **Test Case 3**: LRU 存取順序更新
    - **Given**: 快取包含 file1, file2, file3（依序加入）
    - **When**: get(file1)，然後 put(file4)
    - **Then**: file2 被淘汰（file1 因被存取而移到最後）
  - **Test Case 4**: TTL 過期清理
    - **Given**: ttl_seconds=2 的 DocumentCache，put("file1.md", data1)
    - **When**: 等待 3 秒，呼叫 _cleanup_expired()
    - **Then**: file1.md 被清除，get("file1.md") 回傳 None
  - **Test Case 5**: 手動清除指定快取
    - **Given**: 快取包含 file1, file2
    - **When**: clear("file1.md")
    - **Then**: file1 被清除，file2 仍存在
  - **Test Case 6**: 手動清除全部快取
    - **Given**: 快取包含 file1, file2, file3
    - **When**: clear()
    - **Then**: 所有快取被清除
  - **Test Case 7**: Thread safety（並發存取）
    - **Given**: DocumentCache with 5 threads
    - **When**: 5 個 threads 同時 put/get 不同文件
    - **Then**: 無 race condition，所有操作正確完成

<!-- id: sec-completion -->
### 4. 實作完成記錄 (Implementation Completion)

<!-- id: blk-execution-summary, type: list -->
**執行摘要與產出**
  - **實際耗時**: 2 小時 (預估: 3-4小時)
  - **執行狀態**: ✅ 完成
  - **關鍵產出**:
    - 新增 `rbt_mcp_server/cache.py`: DocumentState dataclass 和 DocumentCache 類別
    - 新增 `tests/test_cache.py`: 12 個測試案例全數通過
    - 測試覆蓋率: 98% (66/67 lines covered)
  - **程式碼變更統計**:
    - 新增檔案: 2 個 (cache.py, test_cache.py)
    - 程式碼行數: cache.py 約 220 行, test_cache.py 約 230 行
    - 測試案例: 12 個 (涵蓋所有 7 個規格測試案例 + 5 個額外邊界測試)

<!-- id: blk-problems-table, type: table -->
**問題與解決記錄**
| 問題描述 | 解決方案 | 耗時 | 可預防? |
|----------|----------|------|---------|
| pytest 未安裝，uv sync 移除了 pytest | 使用 `uv add --dev pytest pytest-cov` 重新安裝 | 5 分鐘 | ✅ 應在 pyproject.toml 正確配置 dev dependencies |
| README.md 不存在導致 build 失敗 | 創建基本 README.md | 2 分鐘 | ✅ 專案初始化時應建立 |
| test_lru_eviction 測試案例邏輯錯誤 | 移除不必要的 get 呼叫，讓測試符合原始意圖 | 5 分鐘 | ✅ 撰寫測試時應仔細檢查邏輯 |

<!-- id: blk-technical-debt, type: list -->
**技術債務與重構建議**
  - **技術債務**: 無
  - **重構建議**:
    - 背景清理 thread 目前每 60 秒執行一次，可考慮改為可配置參數
    - 未來可考慮增加 cache 統計功能（命中率、淘汰次數等）
  - **程式碼定位指令**: `grep -r "@TASK: TASK-002" rbt_mcp_server/`
  - **關鍵檔案清單**:
    - `/Users/devinlai/Develope/KnowledgeSmith/rbt_mcp_server/cache.py` - DocumentState 和 DocumentCache 實作
    - `/Users/devinlai/Develope/KnowledgeSmith/tests/test_cache.py` - 12 個測試案例
